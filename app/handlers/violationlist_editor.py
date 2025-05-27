# from aiogram import Router, F, types
# from aiogram.fsm.context import FSMContext
# from aiogram.types import CallbackQuery
# from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
# from aiogram.fsm.state import StatesGroup, State
#
# from app.db.postgresql import get_user_violations_list, get_violations_info_by_id, update_violation_status
# from app.functions.message_deleter import delete_messages_by_names, delete_messages_by_id
# from app.kb.user_reg_kb import reg_users_dashboard
# from app.kb.violationlist_editor_kb import change_violationstatus_button
# # from aiogram.utils.keyboard import InlineKeyboardBuilder
# # from aiogram.filters.callback_data import CallbackData
#
# router = Router(name=__name__)
#
#
# class ViolationListEditorStates(StatesGroup):
#     violations_list = State()
#     violation_details = State()
#     violation_photo_confirm = State()
#
#
# @router.callback_query(F.data == "violationlist_editor")
# async def editor_welcome_message(callback: CallbackQuery, state: FSMContext):
#     await state.set_state(ViolationListEditorStates.violations_list)
#     user_tg_id = callback.from_user.id
#     violations = await get_user_violations_list(user_tg_id)
#     print(f"your violations: {violations}")
#
#     if violations:
#         # message_text = "Ваши нарушения:\n\n"
#         message_text = "\n\n"
#         message_ids = []  # Список для хранения message_id
#
#         for violation in violations:
#             violation_id, violation_type, addition_date, short_address, status = violation
#
#             # Формируем текст для каждого нарушения
#             message_text += (
#                 f"Тип: {violation_type}\n"
#                 f"Дата добавления: {addition_date}\n"
#                 f"Адрес: {short_address}\n"
#                 # f"Статус размещения: {'❌ НЕТ' if status == 1 else '✅ ДА'}\n"
#                 f"Статус размещения: ❌ НЕТ\n"
#             )
#
#             # Формируем текст для кнопки изменения статуса
#             # Создаем инлайн-кнопку для изменения статуса
#             change_status_button = InlineKeyboardButton(
#                 text="Изменить статус",
#                 callback_data=f"change_status_{violation_id}"
#             )
#
#             # Отправляем сообщение и сохраняем его в message_ids
#             # sent_message = await callback.message.answer(message_text, reply_markup=inline_kb)
#             sent_message = await callback.message.answer(message_text,
#                                                          reply_markup=change_violationstatus_button(violation_id))
#             message_ids.append(sent_message.message_id)  # Сохраняем message_id
#
#             # Очищаем текст сообщения для следующего нарушения
#             message_text = ""
#
#         # Сохраняем список message_id в состоянии, если это необходимо
#         await state.update_data(violation_message_ids=message_ids)
#
#     else:
#         await callback.message.answer(text="У вас нет нарушений.",
#                                       reply_markup=reg_users_dashboard(),)
#
#     await callback.answer()
#
#     # data = await state.get_data()
#     # violation_message_ids = data.get("violation_message_ids")
#     # print("Список violation_message_ids:", violation_message_ids)
#
#     await state.set_state(ViolationListEditorStates.violation_details)
#
#
# # #----------------------------------------------------------------------------
#
# @router.callback_query(F.data.startswith("change_status_"),
#                        ViolationListEditorStates.violation_details)
# async def change_status_handler(callback_query: CallbackQuery, state: FSMContext):
#     # Извлекаем ID нарушения из callback_data
#     violation_id = callback_query.data.split("_")[2]  # Получаем часть после "change_status_"
#
#     # await callback_query.message.answer(f"Вы выбрали изменение статуса нарушения ID: {violation_id}")
#
#     violations_info_by_id = await get_violations_info_by_id(violation_id)
#     violation_id, violation_type, addition_date, short_address, status = violations_info_by_id
#     await callback_query.message.answer(
#                                         f"Тип: {violation_type}\n"
#                                         f"Дата добавления: {addition_date}\n"
#                                         f"Адрес: {short_address}\n"
#                                         f"Статус размещения: {'❌ НЕТ' if status == 1 else '✅ ДА'}\n"
#                                         f"👇Прикрепите фото размещения уведомления:\n"
#                                         )
#
#     data = await state.get_data()
#     # await delete_messages_by_names(state,
#     #                                "your_violations_list_msg_id", )
#     violation_message_ids = data.get("violation_message_ids")
#     print("\nСписок violation_message_ids:", violation_message_ids, "\n")
#     for violation_message_id in violation_message_ids:
#         await delete_messages_by_id(state, violation_message_id)
#
#     await state.update_data(violation_id=violation_id)
#     await state.set_state(ViolationListEditorStates.violation_photo_confirm)
#
#
# @router.message(ViolationListEditorStates.violation_details)
# async def violation_details_wrong_input(message: types.Message, state: FSMContext):
#     data = await state.get_data()
#     violation_message_ids = data.get("violation_message_ids")
#     wrong_input_after_violation_details = await message.answer(
#         text="Надо было использовать кнопку 'Изменить статус'. Попробуйте ещё раз.",
#         reply_markup=reg_users_dashboard()
#     )
#     await state.update_data(wrong_input_after_violation_details_msg_id=wrong_input_after_violation_details.message_id)
#     for violation_message_id in violation_message_ids:
#         await delete_messages_by_id(state, violation_message_id)
#
#
# @router.message(ViolationListEditorStates.violation_photo_confirm, F.photo)
# async def violation_photo_confirm(message: types.Message, state: FSMContext):
#     viaolation_id = (await state.get_data()).get("violation_id")
#     print(f"viaolation_id: {viaolation_id}")
#     await update_violation_status(viaolation_id, 2)
#     await state.clear()
#     violation_photo_confirm_success = await message.answer(
#         text="Фото успешно добавлено!\n"
#              "Статус уведомления изменён."
#              "Выберите действие:",
#         reply_markup=reg_users_dashboard()
#     )
#
#
# @router.message(ViolationListEditorStates.violation_photo_confirm)
# async def wrong_input(message: types.Message, state: FSMContext):
#     await message.answer("Прикрепите фото подтверждение.")
