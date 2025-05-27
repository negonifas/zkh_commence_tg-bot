import requests
import io
import os
import smtplib
import pytz

from aiogram.types import CallbackQuery
from aiogram import Router, F, types
from aiogram.fsm.context import FSMContext
from app.functions.cloud import pdf_to_cloud
from app.kb.violation_kb import (build_main_kb, build_violation_kb,
                                 ViolationCbData, VIOLATIONS, build_confirm_kb,
                                 build_review_kb, is_text_without_emoji, build_review_address_kb,
                                 build_edit_main_data_kb, back_to_button, back_to_main_menu_button,
                                 )
from aiogram.types import Message
from PIL import Image
from app.functions.UFO_pdf import (delete_temp_directory,
                                   generate_qr_code,
                                   create_pdf_body,
                                   get_full_violation_composition, )
from aiogram.utils.chat_action import ChatActionSender
from app.db.postgresql import select_user_id, add_violation, number_of_violations
from app.functions.send_email import send_email
from app.kb.user_reg_kb import reg_users_dashboard
from app.kb.one_back_button import inline_back_to_button
from datetime import datetime
from loguru import logger
from app.etc.data import violations_list_extended, ViolationFSM
from app.functions.address import address_cleaner

router = Router(name=__name__)


# Обрабатываем любые события в состоянии "ViolationFSM.dashboard" кроме нажатия кнопки
@router.message(ViolationFSM.dashboard)
async def wrong_input(message: Message, state: FSMContext):
    # Обрабатываем любые текстовые сообщения, которые не являются нажатием кнопки
    wrong_input_after_dashboard_msg_id = await message.answer(
        text="Ошибка ввода. Пожалуйста, используйте кнопки для взаимодействия.",
        reply_markup=reg_users_dashboard()
    )
    logger.error(f"TG ID: {message.from_user.id}, тут надо было жать на кнопку 'Нарушение, Уведомление, Информация'\n"
                 f"FSM: {await state.get_state()}")


# обрабатываем нажатие на кнопку "Нарушение ⛑"
# Меняем сотояние с "ViolationFSM.dashboard" на "ViolationFSM.address"
@router.callback_query(F.data == "dashboard")
async def main_menu(callback: CallbackQuery, state: FSMContext):
    # await state.clear()
    # Зачем эта информация?
    # logger.debug(f"'PRINT': нарушений со статусом 1: {(await number_of_violations(callback.from_user.id))[0]}")
    if (await number_of_violations(callback.from_user.id))[0] <= 150:
        start_violation_msg = await callback.message.edit_text(
            text=f"Введите точный, полный адрес нарушения\n"
                 f"Например:\n"
                 f"Смоленская область, г. Сафоново, ул. Строителей, д. 28, корп. 2, кв.155",
            reply_markup=back_to_main_menu_button(),
        )
        await state.update_data(
            start_violation_msg_id=start_violation_msg.message_id,
            current_chat_id=start_violation_msg.chat.id
        )
        await callback.answer()
        await state.set_state(ViolationFSM.address)
        logger.debug(f"TG ID: {callback.from_user.id}, Вводит адрес для нарушения ===>\n"
                     f"FSM: {await state.get_state()}")
    else:
        await callback.message.edit_text(
            text=f"У вас больше 15 не подтверждённых нарушений.\n"
                 f"Для продолжения подтвердите хотя бы одно размещение.\n",
            reply_markup=inline_back_to_button(callback_data="start_again", ),
        )
        logger.error(f"TG ID: {callback.from_user.id}, больше 15 не подтверждённых нарушений.\n"
                     f"FSM: {await state.get_state()}")


# Проверяем введённый текст на соответствие "адрес"
# Забирает введённый адрес и сохраняет его в состояние
@router.message(ViolationFSM.address)
async def handle_address(message: Message, state: FSMContext):
    # Проверка на наличие текста и исключение эмодзи и изображений
    if not is_text_without_emoji(message.text) or message.photo or message.document:
        await message.answer(
            text=f"Ошибка ввода. Пожалуйста, отправляйте только текстовый адрес без эмодзи и изображений.\n\n"
                 f"Введите точный, полный адрес нарушения\n"
                 f"Например:\n"
                 f"Смоленская область, г. Сафоново, ул. Строителей, д. 28, корп. 2, кв.155",
        )
        logger.error(
            f"TG ID: {message.from_user.id}, wrong_input на вводе адреса\n"
            f"FSM: {await state.get_state()}"
        )
        return

    address = await address_cleaner(message.text)
    if not address:
        await message.answer(
            text="Вы ввели некорректный адрес. Пожалуйста, проверьте его и отправьте заново.",
        )
        logger.error(
            f"TG ID: {message.from_user.id}, wrong_input не распознал адрес\n"
            f"FSM: {await state.get_state()}"
        )
    else:
        await message.answer(
            text=f"Вы ввели адрес: {address}\n"
                 f"Все верно? Подтвердите или введите по новой.",
            reply_markup=build_review_address_kb(),
        )
        # Сохранение адреса в состояние
        await state.update_data(address=address)
        logger.debug(
            f"TG ID: {message.from_user.id}, введен и распознан адрес: {address}\n"
            f"Две кнопки с подтверждением и 'на главную' ===>\n"
            f"FSM: {await state.get_state()}"
        )


# Тут спрашиваем номер подъезда
@router.callback_query(F.data == "confirm_address")
async def handle_only_digits(callback: types.CallbackQuery, state: FSMContext):
    await state.set_state(ViolationFSM.entrance)
    await callback.message.edit_text(text="Введите номер подъезда\n",
                                     reply_markup=back_to_main_menu_button())
    logger.debug(f"TG ID: {callback.from_user.id}\n"
                 f"Нажал подтвердить адрес и теперь вводит номер подъезда ===>\n"
                 f"FSM: {await state.get_state()}")


# Принимает номер подъезда
# Выводим кнопки с видами нарушений
@router.message(ViolationFSM.entrance, F.text.isdigit())
async def handle_entrance_only_digits(message: types.Message, state: FSMContext):
    # Сохраняем номер подъезда в состояние
    entrance = message.text
    await state.update_data(entrance=entrance)

    # Отправляем сообщение пользователю
    await message.answer(
        text="На каком этаже обнаружили нарушение?\n",
        reply_markup=back_to_button(),
    )

    await state.set_state(ViolationFSM.floor)
    logger.debug(f"TG ID: {message.from_user.id}, сохранён подъезд: {entrance}\n"
                 f"Спрашиваем на каком этаже обнаружили нарушение ===>\n"
                 f"FSM: {await state.get_state()}")
@router.message(ViolationFSM.entrance)
async def handle_entrance_only_digits(message: types.Message, state: FSMContext):
    await message.answer(
        text=f"Ошибка ввода. Пожалуйста, отправляйте только цифры.\n"
             f"Введите номер подъезда\n",
        reply_markup=back_to_main_menu_button(),
    )
    logger.error(f"TG ID: {message.from_user.id}, wrong_input\n"
                 f"FSM: {await state.get_state()}")


# Скармливаем № этажа, выводим кнопки с нурушениями и обрабатываем исключения
@router.message(ViolationFSM.floor, F.text.isdigit())
async def handle_floor_only_digits(message: types.Message, state: FSMContext):
    floor = message.text
    await state.update_data(floor=floor)
    data = await state.get_data()
    address, entrance, floor = data.get("address"), data.get("entrance"), data.get("floor")
    await message.answer(
        text=f"Для объект:\n{address}, подъезд: {entrance}, этаж: {floor}\n"
             f"Какое обнаружили нарушение? 👇",
        reply_markup=build_main_kb(),
    )

    logger.debug(f"TG ID: {message.from_user.id}, сохранён этаж: {floor}\n"
                 f"Показали меню с кнопками нарушений ===>\n"
                 f"FSM: {await state.get_state()}")
    await state.set_state(ViolationFSM.main_menu)
@router.message(ViolationFSM.floor)
async def wrong_input(message: types.Message, state: FSMContext):
    await message.answer(
        text=f"Ошибка ввода. Пожалуйста, отправляйте только цифры.\n"
             f"Введите номер этажа",
    )
    logger.error(f"TG ID: {message.from_user.id}, wrong_input\n"
                 f"FSM: {await state.get_state()}"
                 )


# Возвращает из любого места на главную
@router.callback_query(F.data == "start_again")
async def start_again(callback_query: CallbackQuery, state: FSMContext):
    start_again_violation_msg = await callback_query.message.edit_text(
        f"Выберите действие 👇\n\n",
        reply_markup=reg_users_dashboard(),
    )


# обрабатывает любое действие кроме нажатия на кнопку
@router.message(ViolationFSM.main_menu)
async def wrong_input(message: Message, state: FSMContext):
    await message.answer(
        text="Ошибка ввода. Пожалуйста, используйте кнопки для взаимодействия.",
        reply_markup=build_main_kb()
    )
    logger.error(f"TG ID: {message.from_user.id}, wrong_input\n"
                 f"FSM: {await state.get_state()}")


@router.callback_query(ViolationCbData.filter())
async def handle_violation(callback: CallbackQuery, callback_data: ViolationCbData, state: FSMContext):
    # Получаем данные о нарушении из словаря VIOLATIONS
    area_text = VIOLATIONS.get(callback_data.area, {})
    violation_data = VIOLATIONS[callback_data.area].get(callback_data.detail, {})
    detail_text = violation_data.get("detail", "Неизвестное нарушение")
    violation_url = violation_data.get("url", "")

    # Сохраняем данные в состояние
    await state.update_data(
        violation_type=detail_text,
        main_category=callback_data.area,
        violation_url=violation_url
    )

    data = await state.get_data()
    address, entrance, floor = data.get("address"), data.get("entrance"), data.get("floor")

    # Формируем сообщение для пользователя
    text = (
        f"Для объекта:\n{address}, подъезд: {entrance}, этаж: {floor}\n"
        f"Выбрано нарушение: {detail_text}. \n"
        f"Теперь отправьте мне фото нарушения, а в подписи укажите номер квартиры."
    )
    await callback.message.edit_text(text=text,
                                     reply_markup=back_to_button(),
                                     )

    # Устанавливаем состояние для загрузки фото
    await state.set_state(ViolationFSM.final_photo_state)

    # Логируем действие
    logger.debug(
        f"TG ID: {callback.from_user.id}\n"
        f"Для объекта:\n{address}, подъезд: {entrance}, этаж: {floor}\nВыбрано нарушение: {detail_text}\n"
        f"Теперь отправьте мне фото нарушения, а в подписи укажите номер квартиры ===>\n"
        f"FSM: {await state.get_state()}"
    )


@router.message(ViolationFSM.final_photo_state, F.photo & F.caption)
# @router.message(F.photo & F.caption)
# @router.callback_query(F.data == "confirm")
async def process_photo(message: types.Message, state: FSMContext):
    # Соединяемся с базой данных и получаем данные пользователя (email)
    user_data = await select_user_id(message.from_user.id)
    user_email = user_data[2]
    # print(user_email)
    logger.debug(f"'PRINT': User email: {user_email}")

    # Извлекаем комментарий, сохраняем в состояние
    # caption = ", ".join(message.caption.split())
    caption = message.caption.split()
    caption = ", ".join(caption)
    await state.update_data(photo_caption=caption)

    # Извлекаем фото
    file_id = message.photo[-1].file_id
    URI_INFO = f"https://api.telegram.org/bot{message.bot.token}/getFile?file_id={file_id}"
    resp = requests.get(URI_INFO)
    img_path = resp.json()['result']['file_path']
    URI = f"https://api.telegram.org/file/bot{message.bot.token}/"
    URI_full = f"https://api.telegram.org/file/bot{message.bot.token}/{img_path}"
    img = requests.get(URI_full).content
    image = Image.open(io.BytesIO(img))

    # print(f"Current state data in process_photo: {data}")
    # logger.debug(f"'PRINT': Current state data in process_photo: {data}")

    # Подготовка данных / извлекаем данные из состояния
    data = await state.get_data()
    pdf_title = "УВЕДОМЛЕНИЕ!"
    main_menu_text = data.get("main_category", "Не указано")
    violation_details = data.get("violation_type", "Не указано")
    floor = data.get("floor", "Не указан")
    entrance = data.get("entrance", "Не указан")

    logger.debug(f"\nTG ID: {message.from_user.id}\n"
                 f"этаж: {data.get('floor', 'Не указан')}\n"
                 f"подъезд: {data.get('entrance', 'Не указан')}\n\n")

    # print(f"Violation details: {violation_details}")
    # logger.debug(f"'PRINT': Violation details: {violation_details}")
    violation_complete_details = get_full_violation_composition(
        violations_list_extended,
        violation_details, )
    # print(f"Теперь Violation details: {violation_details}")
    # logger.debug(f"'PRINT': Теперь Violation details: {violation_details}")
    # address = data.get("address", "Не указан")
    address = f"{data['address']}, квартира {caption}"
    violation_url = data.get("violation_url", "Ошибка извлечения URL")
    font_path = "Roboto-Regular.ttf"
    font_path_bold = "times_bold.ttf"
    font_path_regular = "times_regular.ttf"
    logo_img = "revizor_logo-original-from-template.jpg"

    # # Анимация и сообщение о ожидании
    async with ChatActionSender.upload_document(bot=message.bot, chat_id=message.chat.id):
        waiting_message = await message.answer("Пожалуйста, подождите...")
        qr_code_img = generate_qr_code(violation_url)
        pdf_file, temp_dir = create_pdf_body(
            message.from_user.id,
            pdf_title,
            main_menu_text,
            violation_complete_details,
            address,
            image,
            qr_code_img,
            font_path_regular,
            font_path_bold,
            logo_img,
        )
        SMTP_SERVER = 'smtp.mail.ru'
        SMTP_PORT = 587
        SMTP_USER = os.getenv('SMTP_USER')
        SMTP_PASSWORD = os.getenv('SMTP_PASSWORD')

        moscow_timezone = pytz.timezone('Europe/Moscow')
        current_time = datetime.now(moscow_timezone).strftime("%d-%m-%Y_%H:%M")

        # Добавляем нарушение в базу данных
        try:
            new_violation_id = await add_violation(message.from_user.id,
                                                   main_menu_text, violation_details,
                                                   address, floor, entrance,)
        except Exception as e:
            logger.error(f"TG ID: {message.from_user.id}, Ошибка добавления нарушения в базу данных: {e}"
                         f"FSM: {await state.get_state()}")
        # print(f"Новый ID нарушения {new_violation_id}\nДля пользователя с ID {message.from_user.id}")
        # logger.debug(f"Новый ID нарушения {new_violation_id}\nДля пользователя с ID {message.from_user.id}")

        # Отправляем PDF на email
        try:
            send_email(
                message.from_user.id,
                subject=f'Уведомление о нарушении - "{violation_details}", по адресу {address}',
                from_name="ОЗПП Ревизор ЖКХ",

                body='Прикреплено уведомление по нарушению в формате PDF.',
                to_email=user_email,
                file_path=pdf_file,
                smtp_server=SMTP_SERVER,
                smtp_port=SMTP_PORT,
                smtp_user=SMTP_USER,
                smtp_password=SMTP_PASSWORD,
            )
        except smtplib.SMTPRecipientsRefused as e:
            # print(f"Ошибка отправки письма: {e}")
            logger.error(f"TG ID: {message.from_user.id}, Ошибка отправки письма: {e}")

        # Отправляю PDF в G-облако
        try:
            pdf_to_cloud(message.from_user.id,
                         pdf_file,
                         f"{message.from_user.id} - {message.from_user.username}",
                         f"ViolationID: {new_violation_id} - PDF - Date: {current_time}")
        except Exception as e:
            logger.error(f"TG ID: {message.from_user.id}, Ошибка отправки PDF в G-облако: {e}"
                         f"FSM: {await state.get_state()}")

        await waiting_message.delete()

    # Удаляем временные файлы
    delete_temp_directory(message.from_user.id, temp_dir)

    # await message.answer_photo(photo=message.photo[-1].file_id, caption='Фото которое вы отправили')
    await message.answer(text=f"Уведомление о нарушении {main_menu_text}, {violation_details}, {address}\n"
                              f"отправлено на {user_email}\n"
                              f"１) Разместите его на двери нарушителя.\n"
                              f"２) Сделайте фото.\n"
                              f"３) Подтвердите размещение в боте\n"
                              f"нажав кнопку '📩 Уведомление'.\n\n"
                              f"Можно изменить 👇",
                         # reply_markup=reg_users_dashboard(),
                         reply_markup=build_edit_main_data_kb(),
                         )
    logger.debug(f"TG ID: {message.from_user.id}, Уведомление о нарушении отправлено на {user_email}\n"
                 f"Можно изменить ===>\n"
                 f"FSM: {await state.get_state()}")
    # # Очищаем состояние
    # await state.clear()
@router.message(ViolationFSM.final_photo_state)
async def handle_incorrect_photo(message: types.Message, state: FSMContext):
    await message.reply(f"Некорректное изображение. Пожалуйста, отвляйте только фото.\n"
                        f"В коментарии укажите номер квартиры.")
    logger.error(f"TG ID: {message.from_user.id}, некорректное изображение. Пожалуйста, отправьте фото."
                 f"FSM: {await state.get_state()}")


@router.callback_query(F.data == "useful_info")
async def userful_info_callback(callback_query: CallbackQuery, state: FSMContext):
    # await state.clear()
    try:
        await callback_query.message.edit_text(
            text=f"📓 Оформлено: {(await number_of_violations(callback_query.from_user.id))[2]}\n"
                 f"📌 Размещенно: {(await number_of_violations(callback_query.from_user.id))[1]}\n"
                 f"💰 Выплачено: 0\n\n"
                 f"| <a href='https://t.me/Terranova495'>⁉️ Задать вопрос</a> "
                 f"| <a href='https://t.me/Terranova495'>💸 Оформить выплату</a> "
                 f"| <a href='https://t.me/revizorgh_fixchat'>📜 Инструкция</a> |",
            reply_markup=inline_back_to_button(callback_data="start_again", ),
            disable_web_page_preview=True,
        )
    except Exception as e:
        # print(e)
        logger.error(f"TG ID: {callback_query.from_user.id}, Error: {e}"
                     f"FSM: {await state.get_state()}")


@router.callback_query(F.data == "edit_entrance")
async def handle_another_entrance(callback: CallbackQuery, state: FSMContext):
    # Переводим пользователя в состояние ввода подъезда
    await state.set_state(ViolationFSM.edit_entrance)
    await callback.message.edit_text(
        text="👇 Введите новый номер подъезда 👇",
    )
    logger.debug(f"TG ID: {callback.from_user.id}, вводит 'Другой подъезд' ===>\n"
                 f"FSM: {await state.get_state()}")

@router.message(ViolationFSM.edit_entrance, F.text.isdigit())
async def handle_edit_entrance(message: Message, state: FSMContext):
    # Сохраняем новый номер подъезда в состояние
    entrance = message.text

    # Обновляем данные в состоянии
    await state.update_data(entrance=entrance)

    # Формируем сообщение для пользователя
    await message.answer(
        text="Опять сообщите на каком этаже обнаружили нарушение?",
        reply_markup=back_to_button(),
    )

    # Переводим пользователя в состояние ввода этажа, сам обработчик выше
    await state.set_state(ViolationFSM.floor)

    logger.debug(f"TG ID: {message.from_user.id}, сохранён новый подъезд: {entrance}\n"
                 f"Запросил новый этаж ===>\n"
                 f"FSM: {await state.get_state()}")
@router.message(ViolationFSM.edit_entrance)
async def wrong_input(message: Message, state: FSMContext):
    await message.answer(text=f"Ошибка ввода. Пожалуйста, отправляйте только цифры.\n"
                              f"Введите номер подъезда\n",
                         reply_markup=back_to_main_menu_button(),
                         )
    logger.error(f"TG ID: {message.from_user.id}, Ошибка ввода. Пожалуйста, отправляйте только цифры."
                 f"FSM: {await state.get_state()}")


@router.callback_query(F.data == "edit_floor")
async def handle_another_floor(callback: CallbackQuery, state: FSMContext):
    # Переводим пользователя в состояние ввода этажа
    await state.set_state(ViolationFSM.edit_floor)

    # Отправляем сообщение пользователю
    await callback.message.edit_text(
        text="👇 Введите новый номер этажа 👇",
        reply_markup=back_to_button(),
    )

    logger.debug(f"TG ID: {callback.from_user.id}, вводит 'Другой этаж' ===>\n"
                 f"FSM: {await state.get_state()}")

@router.message(ViolationFSM.edit_floor, F.text.isdigit())
async def handle_edit_floor(message: Message, state: FSMContext):
    # Сохраняем новый номер этажа в состояние
    floor = message.text
    await state.update_data(floor=floor)

    # Переводим пользователя в состояние загрузки фото
    await state.set_state(ViolationFSM.final_photo_state)

    # Получаем текущие данные из состояния
    data = await state.get_data()
    address, entrance = data.get("address"), data.get("entrance")

    # Формируем сообщение для пользователя
    text = (
        f"Для объекта:\n{address}, подъезд: {entrance}, этаж: {floor}\n"
        f"Теперь отправьте мне фото нарушения, а в подписи укажите номер квартиры."
    )
    await message.answer(text=text,
                         reply_markup=back_to_button(),
                         )

    logger.debug(f"TG ID: {message.from_user.id}, сохранён новый этаж: {floor}\n"
                 f"Переход к загрузке фото ===>\n"
                 f"FSM: {await state.get_state()}")
@router.message(ViolationFSM.edit_floor)
async def wrong_input(message: Message, state: FSMContext):
    await message.answer(f"Ошибка ввода. Пожалуйста, отправляйте только цифры.\n"
                         f"Введите номер этажа")
    logger.error(f"TG ID: {message.from_user.id}, Ошибка ввода. Пожалуйста, отправляйте только цифры."
                 f"FSM: {await state.get_state()}")


@router.callback_query(F.data == "edit_violation")
async def handle_another_violation(callback: CallbackQuery, state: FSMContext):
    # Переводим пользователя в состояние выбора нарушения
    await state.set_state(ViolationFSM.main_menu)
    await callback.message.edit_text(
        text="👇 Где нарушение? 👇",
        reply_markup=build_main_kb(),
    )
    logger.debug(f"TG ID: {callback.from_user.id}, выбирает 'Другое нарушение' ===>\n"
                 f"FSM: {await state.get_state()}")


# ============================================================================================================

# Обрабатываем нажатие на кнопку "Выбрать заново" Вернёт к "👇 Где нарушение? 👇"
@router.callback_query(F.data == "reset")
async def reset_violation(callback_query: CallbackQuery, state: FSMContext) -> None:
    # Переносим пользователя в главное меню
    await state.set_state(ViolationFSM.main_menu)
    await callback_query.message.edit_text(
        text="👇 Где нарушение? 👇",
        reply_markup=build_main_kb(),
    )
    logger.debug(f"TG ID: {callback_query.from_user.id}, не подтвердил нарушение, вернулся в root\n"
                 f"FSM: {await state.get_state()}")


# Обрабатывает любые событи кроме нажатия на кнопку в состоянии ViolationFSM.details_menu
@router.message(ViolationFSM.details_menu)
async def handle_invalid_message_in_details(message: Message, state: FSMContext):
    # Получаем из состояния, какая категория нарушения была выбрана
    data = await state.get_data()
    selected_area = data.get("selected_area")

    if not selected_area or selected_area not in VIOLATIONS:
        await message.answer(
            text="Ошибка в выборе категории. Пожалуйста, выберите категорию заново.",
            reply_markup=build_main_kb()
        )
        return

    # Показываем сообщение об ошибке и возвращаем текущее меню
    await message.answer(
        text="Ошибка ввода. Пожалуйста, используйте кнопки для выбора нарушения.",
        reply_markup=build_violation_kb(selected_area)
    )
    logger.error(f"TG ID: {message.from_user.id}, wrong_input\n"
                 f"FSM: {await state.get_state()}")


# Обрабатывает любые событи кроме нажатия на кнопку в состоянии ViolationFSM.confirm
@router.message(ViolationFSM.confirm)
async def handle_invalid_message_in_confirm(message: Message, state: FSMContext):
    # Получаем информацию о выбранном нарушении из состояния
    data = await state.get_data()
    violation_type = data.get("violation_type")

    if not violation_type:
        await message.answer(
            text="Ошибка. Пожалуйста, подтвердите свой выбор или выберите заново.",
            reply_markup=build_confirm_kb()
        )
        return

    # Показываем сообщение об ошибке и снова выводим клавиатуру с кнопками
    await message.answer(
        text="Ошибка ввода. Пожалуйста, подтвердите свой выбор или выберите заново.",
        reply_markup=build_confirm_kb()
    )
    logger.error(f"TG ID: {message.from_user.id}, wrong_input\n"
                 f"FSM: {await state.get_state()}")
