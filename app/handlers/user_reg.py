import re
import os

from aiogram import Router, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import Message, ReplyKeyboardRemove
from dotenv import load_dotenv
from loguru import logger
from app.db.postgresql import add_user, get_name_in_db
from app.kb.user_reg_kb import finish_reg_keyboard, reg_users_dashboard
from app.handlers.violation import ViolationFSM
from app.functions.message_deleter import delete_message_after_delay

router = Router(name=__name__)
load_dotenv()

EMAIL_REGEX = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z]{2,}$'
NAME_REGEX = r'^[A-Za-zА-Яа-яЁё\s-]+$'
PHONE_REGEX = r'^\+7\d{10}$'


class RegistrationState(StatesGroup):
    start = State()
    waiting_for_name = State()
    waiting_for_email = State()
    waiting_for_phone = State()
    confirm = State()


@router.message(Command(commands=["start"]))
async def cmd_start(message: Message, state: FSMContext):
    try:
        await message.bot.send_message(os.getenv('ADMIN_TG_ID'),
                                       text=f"Пользователь с ID: {message.from_user.id}\n"
                                            f"TG username: {message.from_user.username}\n"
                                            f"Запустил бота.")
        logger.debug(f"TG ID: {message.from_user.id}, cообщение о 'СТАРТЕ' отправлено админу.")
    except Exception as e:
        logger.error(f"TG ID: {message.from_user.id}, ошибка при отправке сообщения админу: {e}")
    await state.clear()
    # # Хозяйке на заметку
    # print(f"ID сообщения: {greeting_message.message_id}\n"
    #       f"ID чата: {greeting_message.chat.id}\n")
    greeting_message = await message.answer("Бот для заработка на фиксации нарушений приветствует вас!",
                                            reply_markup=ReplyKeyboardRemove(),
                                            )
    # Удаления сообщения через 3 секунды
    await delete_message_after_delay(message.from_user.id, greeting_message, delay=5)

    user_name = await get_name_in_db(message.from_user.id)
    if user_name:
        msg = await message.answer(
            f"Рады тебя видеть <b>{user_name}</b> 🙌\n"
            "Выберите действие:",
            reply_markup=reg_users_dashboard()
        )
        await state.update_data(registered_msg_id=msg.message_id)
        await state.set_state(ViolationFSM.dashboard)
        logger.debug(f"TG ID: {message.from_user.id}, текущее FSM: {await state.get_state()}")
    else:
        await message.answer(f"Сообщите мне своё имя 👇",
                             reply_markup=ReplyKeyboardRemove())
        await state.set_state(RegistrationState.waiting_for_name)
        logger.debug(f"TG ID: {message.from_user.id}, текущее FSM: {await state.get_state()}")


# @router.message(Command(commands=["start"]))
# async def cmd_start(message: Message, state: FSMContext):
#     # Проверяем, вызван ли /start впервые или после нажатия кнопки "Назад"
#     data = await state.get_data()
#     success_reg_msg_id = data.get('success_reg_msg_id', None)
#
#     # Получаем информацию о пользователе
#     user = await select_user_id(message.from_user.id)
#
#     if user:
#         # Если это возврат на старт через кнопку "Назад"
#         if success_reg_msg_id:
#             greeting_message = await message.answer(
#                 "Давайте начнём заново.",
#                 reply_markup=ReplyKeyboardRemove(),
#             )
#         else:
#             # Исходное приветствие при первом запуске
#             greeting_message = await message.answer(
#                 f"Рады тебя видеть <b>{message.from_user.first_name}</b> 🙌\n"
#                 f"Вами уже оформлено нарушений: {await number_of_violations(message.from_user.id)}\n",
#                 reply_markup=ReplyKeyboardRemove(),
#             )
#
#         # Обновляем клавиатуру с действиями для зарегистрированных пользователей
#         await message.answer(
#             text="Выберите действие:",
#             reply_markup=reg_users_dashboard()
#         )
#
#         # Сохраняем сообщение приветствия для идентификации возврата
#         await state.update_data(success_reg_msg_id=greeting_message.message_id)
#
#     else:
#         # Если пользователь не зарегистрирован, предложить зарегистрироваться
#         await message.answer(
#             f"Привет, ваш Telegram ID: {message.from_user.id}\n"
#             f"Сообщите мне своё имя 👇",
#             reply_markup=ReplyKeyboardRemove()
#         )
#         await state.set_state(RegistrationState.waiting_for_name)


@router.message(RegistrationState.waiting_for_name, F.text)
async def process_name(message: Message, state: FSMContext):
    name = message.text
    if re.match(NAME_REGEX, name):
        logger.debug(f"TG ID: {message.from_user.id}, введено имя: {name}")
        await state.update_data(name=name)
        await message.answer(f"Привет, {name}! Теперь введите свой email 👇")
        await state.set_state(RegistrationState.waiting_for_email)
        logger.debug(f"TG ID: {message.from_user.id}, текущее FSM: {await state.get_state()}")
    else:
        await message.reply("Пожалуйста, введите корректное имя (только буквы и пробелы).")
        logger.error(f"TG ID: {message.from_user.id}, ввели некорректное имя.")

@router.message(RegistrationState.waiting_for_name)
async def wrong_input(message: Message):
    logger.error(f"TG ID: {message.from_user.id}, ввели некорректное имя.")
    await message.reply("Пожалуйста, введите корректное имя (только буквы и пробелы).")


@router.message(RegistrationState.waiting_for_email, F.text)
async def process_email(message: Message, state: FSMContext):
    email = message.text
    if re.match(EMAIL_REGEX, email):
        logger.debug(f"TG ID: {message.from_user.id}, введен email: {email}")
        await state.update_data(email=email)
        await message.answer("Email принят. Теперь введите свой телефон в формате +71234567890 👇")
        await state.set_state(RegistrationState.waiting_for_phone)
        logger.debug(f"TG ID: {message.from_user.id}, текущее FSM: {await state.get_state()}")
    else:
        await message.reply("Пожалуйста, введите корректный адрес электронной почты.")
        logger.error(f"TG ID: {message.from_user.id}, ввели некорректный email.")

@router.message(RegistrationState.waiting_for_email)
async def wrong_input(message: Message):
    logger.error(f"TG ID: {message.from_user.id}, ввели некорректный email.")
    await message.reply("Пожалуйста, введите корректный адрес электронной почты.")


@router.message(RegistrationState.waiting_for_phone, F.text)
async def process_phone(message: Message, state: FSMContext):
    phone = message.text
    if re.match(PHONE_REGEX, phone):
        logger.debug(f"TG ID: {message.from_user.id}, введен телефон: {phone}")
        user_data = await state.get_data()
        await state.update_data(phone=phone)
        await message.answer("Телефон принят.\n"
                             "Теперь проверьте введенные данные 👇")
        await message.answer(f"Ваши данные:\n"
                             f"Имя: {user_data['name']}\n"
                             f"Email: {user_data['email']}\n"
                             f"Телефон: {phone}\n\n"
                             f"Если всё верно, нажмите кнопку \"Завершить регистрацию\"\n"
                             f"Если хотите изменить данные, нажмите кнопку \"Начать заново\"",
                             reply_markup=finish_reg_keyboard,
                             )
        await state.set_state(RegistrationState.confirm)
        logger.debug(f"TG ID: {message.from_user.id}, текущее FSM: {await state.get_state()}")
    else:
        await message.reply("Пожалуйста, введите корректный номер телефона в формате +71234567890.")
        logger.error(f"TG ID: {message.from_user.id}, ввели некорректный номер телефона.")

@router.message(RegistrationState.waiting_for_phone)
async def wrong_input(message: Message):
    logger.error(f"TG ID: {message.from_user.id}, ввели некорректный номер телефона.")
    await message.reply("Пожалуйста, введите корректный номер телефона в формате +71234567890.")


@router.message(RegistrationState.confirm, F.text == "Завершить регистрацию")
async def process_confirm(message: Message, state: FSMContext):
    user_data = await state.get_data()
    try:
        # Попытка добавить пользователя в базу данных
        await add_user(user_data['name'],
                       user_data['email'],
                       user_data['phone'],
                       message.from_user.id,
                       message.from_user.first_name,
                       message.from_user.last_name,
                       message.from_user.username,
                       message.from_user.language_code,
                       message.from_user.is_premium
                       )
        logger.info(f"Пользователь {user_data['name'], user_data['email'], user_data['phone']},"
                    f" добавлен в базу данных.")
        try:
            await message.bot.send_message(os.getenv('ADMIN_TG_ID'),
                                           text=f"Пользователь с ID: {message.from_user.id}\n"
                                                f"TG username: {message.from_user.username}\n"
                                                f"Добавился в таблицу 'users'.")
        except Exception as e:
            logger.error(f"TG ID: {message.from_user.id}, ошибка при отправке сообщения админу: {e}")
    except Exception as e:
        # Ловим любое исключение и выводим сообщение об ошибке в терминал
        logger.error(f"TG ID: {message.from_user.id}, ошибка при добавлении пользователя в базу данных: {e}")
        # Сообщаем пользователю о проблеме (опционально)
        await message.answer("Произошла ошибка при регистрации. Попробуйте позже.")
        # Завершаем обработку
        return

    # await state.set_state(ViolationFSM.dashboard) # Зачем это тут сейчас делать?
    success_reg_msg = await message.answer(text="Регистрация завершена!\n",
                                           # reply_markup=build_main_kb(),
                                           reply_markup=ReplyKeyboardRemove(),
                                           )

    # Сохраняем ID сообщения в состояние
    await state.update_data(success_reg_msg_id=success_reg_msg.message_id)

    # Удаление сообщения через 5 секунд
    await delete_message_after_delay(message.from_user.id, success_reg_msg, delay=5)

    what_can_you_do_now = await message.answer(text="Теперь вы можете 👇",
                                               reply_markup=reg_users_dashboard(),
                                               )
    await state.update_data(what_can_you_do_now_id=what_can_you_do_now.message_id)
    # await state.clear() # Это лишнее, если сразу задавать новое состояние
    await state.set_state(ViolationFSM.dashboard)
    logger.debug(f"TG ID: {message.from_user.id}, текущее FSM: {await state.get_state()}")

@router.message(RegistrationState.confirm, F.text == "Начать заново")
async def start_again(message: Message, state: FSMContext):
    await state.clear()
    await state.set_state(RegistrationState.waiting_for_name)
    await message.answer(f"Сообщите мне своё имя 👇",
                         reply_markup=ReplyKeyboardRemove())
    logger.debug(f"TG ID: {message.from_user.id}, текущее FSM: {await state.get_state()}")

@router.message(RegistrationState.confirm)
async def wrong_input(message: Message, state: FSMContext):
    logger.error(f"TG ID: {message.from_user.id}, некорректное действие, не соответствует кнопкам.")
    await message.reply("Пожалуйста, используйте кнопки чтобы завершить регистрацию или\n"
                        "начните заново",
                        # reply_markup=finish_reg_keyboard,
                        )
    logger.debug(f"TG ID: {message.from_user.id}, текущее FSM: {await state.get_state()}")
