import requests
import io
from aiogram import Router, F, types
from aiogram.types import CallbackQuery
from aiogram.exceptions import TelegramBadRequest
from aiogram.fsm.context import FSMContext
from app.db.postgresql import (get_user_violations_list, get_violations_info_by_id,
                               update_violation_status, number_of_violations)
from app.functions.cloud import file_stream_to_cloud
from app.kb.one_back_button import inline_back_to_button
from app.kb.user_reg_kb import reg_users_dashboard
from app.pagination.paginator_kb import paginator, Pagination
from contextlib import suppress
from datetime import datetime
from aiogram.utils.chat_action import ChatActionSender
from app.etc.data import ViolationPaginatorEditorStates
from loguru import logger


router = Router(name=__name__)


@router.callback_query(F.data == "violationlist_editor")
async def start(call: CallbackQuery, state: FSMContext):
    if (await number_of_violations(call.from_user.id))[0] > 0:
        user_tg_id = call.from_user.id
        violations = await get_user_violations_list(user_tg_id)
        total_items = len(violations)

        await call.message.edit_text(
            f"🏠 Тип: {violations[0][1]}\n"
            f"🗓️ Дата добавления: {violations[0][2]}\n"
            f"📍 Адрес: {violations[0][3]}",
            reply_markup=paginator(violations[0][0], page=0, total_items=total_items),
        )
        # print(violations[0][0])
        logger.debug(f"TG ID: {call.from_user.id}, violation ID: {violations[0][0]}")

        await state.update_data(violations=violations)
        await state.set_state(ViolationPaginatorEditorStates.details)
    else:
        await call.message.edit_text(text="Нет уведомлений для редактирования.\n"
                                          "Вернитетесь назад и создайте новое уведомление.",
                                     reply_markup=inline_back_to_button(callback_data="start_again", )
                                     )


@router.callback_query(Pagination.filter(F.action.in_(["prev", "next"])),
                       ViolationPaginatorEditorStates.details)
async def pagination_handler(call: CallbackQuery, callback_data: Pagination, state: FSMContext):
    page_num = int(callback_data.page)
    page = page_num - 1 if page_num > 0 else 0
    data = await state.get_data()
    violations = data.get("violations")
    total_items = len(violations)

    if callback_data.action == "next":
        page = page_num + 1 if page_num < (len(violations) - 1) else page_num

    with suppress(TelegramBadRequest):
        await call.message.edit_text(
            f"🏠 Тип: {violations[page][1]}\n"
            f"🗓️ Дата добавления: {violations[page][2]}\n"
            f"📍 Адрес: {violations[page][3]}",
            # reply_markup=paginator(violations[page][0], page),
            reply_markup=paginator(violations[page][0], page=page, total_items=total_items),
        )
        # print(violations[page][0])
        logger.debug(f"TG ID: {call.from_user.id}, violation ID: {violations[page][0]}")
    await call.answer()
    await state.set_state(ViolationPaginatorEditorStates.details)


@router.message(ViolationPaginatorEditorStates.details)
async def wrong_input(message: types.Message, state: FSMContext):
    data = await state.get_data()
    violations = data.get("violations", [])
    total_items = len(violations)

    await message.answer(
                        text=(
                            "Выберите действие из меню!\n"
                            f"🏠 Тип: {violations[0][1]}\n"
                            f"🗓️ Дата добавления: {violations[0][2]}\n"
                            f"📍 Адрес: {violations[0][3]}"
                        ),
                        reply_markup=paginator(violations[0][0], page=0, total_items=total_items),
                        )
    # print(violations[0][0])
    logger.debug(f"TG ID: {message.from_user.id}, violation ID: {violations[0][0]}")


@router.callback_query(F.data.startswith("change_status_"),
                       ViolationPaginatorEditorStates.details)
async def change_status_handler(callback_query: CallbackQuery, state: FSMContext):
    # Извлекаем ID нарушения из callback_data
    violation_id = callback_query.data.split("_")[2]  # Получаем часть после "change_status_"
    violations_info_by_id = await get_violations_info_by_id(callback_query.from_user.id, violation_id)
    violation_id, violation_type, addition_date, short_address, status = violations_info_by_id
    await callback_query.message.edit_text(
        # f"🏠 Тип: {violation_type}\n"
        # f"🗓️ Дата добавления: {addition_date}\n"
        # f"📍 Адрес: {short_address}\n"
        f"📎Прикрепите фото размещения уведомления:\n"
    )
    await state.update_data(violation_id=violation_id)
    await state.set_state(ViolationPaginatorEditorStates.confirm)


@router.message(ViolationPaginatorEditorStates.confirm, F.photo)
async def violation_photo_confirm(message: types.Message, state: FSMContext):
    async with ChatActionSender.upload_document(bot=message.bot, chat_id=message.chat.id):
        waiting_message = await message.answer("Пожалуйста, подождите...")

        viaolation_id = (await state.get_data()).get("violation_id")
        # print(f"viaolation_id: {viaolation_id}")
        logger.debug(f"TG ID: {message.from_user.id}, viaolation ID: {viaolation_id}")
        await update_violation_status(message.from_user.id, viaolation_id, 2)
        await state.clear()

        # Извлекаем фото-поток
        file_id = message.photo[-1].file_id
        URI_INFO = f"https://api.telegram.org/bot{message.bot.token}/getFile?file_id={file_id}"
        resp = requests.get(URI_INFO)
        img_path = resp.json()['result']['file_path']
        URI_full = f"https://api.telegram.org/file/bot{message.bot.token}/{img_path}"
        img = requests.get(URI_full).content
        current_time = datetime.now().strftime("%d-%m-%Y_%H:%M")

        # Отправляем фото-поток в G-облако
        file_stream_to_cloud(message.from_user.id,
                             io.BytesIO(img),
                             f"{message.from_user.id} - {message.from_user.username}",
                             f"ViolationID: {viaolation_id} - confirm - Date: {current_time}")
        await waiting_message.delete()

    await message.answer(
        text="Фото успешно добавлено ✊\n"
             "Статус уведомления изменён на \"Размещено\".\n"
             "Выберите дальнейшее действие:",
        reply_markup=reg_users_dashboard()
    )


@router.message(ViolationPaginatorEditorStates.confirm)
async def wrong_input(message: types.Message):
    await message.answer("Прикрепите фото подтверждение.")
    logger.error(f"TG ID: {message.from_user.id}, прикрепите фото подтверждение.")
