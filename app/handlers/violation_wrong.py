import os
import re
from aiogram import Router, types, F
from aiogram.fsm.context import FSMContext
from aiogram.filters import Command
from aiogram.fsm.state import State, StatesGroup
from aiogram.filters.callback_data import CallbackData
from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.types import Message
from app.db.sqLight import Database


router = Router(name=__name__)


# Regular expression to check for emojis
EMOJI_PATTERN = re.compile("[\U00010000-\U0010FFFF]", flags=re.UNICODE)
ADDRESS_REGEX = r'^[\w\s,.№-]{5,}$'  # Basic street address validation


# Function to check if text contains no emojis
def is_text_without_emoji(text: str) -> bool:
    return not EMOJI_PATTERN.search(text)


class AreaOfViolation:
    front = "Фасад"
    entrance = "Подъезд"
    apartment = "Квартира"


class ViolationDetails:
    front = {
        "1": "остекление балкона",
        "2": "спутниковая тарелка",
        "3": "блок кондиционера",
        "4": "вентиляционная установка",
        "5": "вентиляция (трубы)",
        "6": "реклама",
        "7": "отсутствие пандусов",
    }
    entrance = {
        "1": "тамбурные двери"
    }
    apartment = {
        "1": "непроектные радиаторы",
        "2": "перепланировка",
        "3": "нет двери на кухню с газом",
    }


class AreaOfViolationCbData(CallbackData, prefix="v"):
    action: str
    detail: str


area_mapping = {
    AreaOfViolation.front: "front",
    AreaOfViolation.entrance: "entrance",
    AreaOfViolation.apartment: "apartment"
}


def build_violation_kb(area: str) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    details = getattr(ViolationDetails, area_mapping[area])
    for key, detail in details.items():
        callback_data = AreaOfViolationCbData(action=area, detail=key).pack()
        builder.button(
            text=detail,
            callback_data=callback_data,
        )
    builder.button(
        # text="🔙 Вернуться в главное меню",
        text="🔙 Назад",
        callback_data=AreaOfViolationCbData(action="root", detail="").pack(),
    )
    builder.adjust(1)
    return builder.as_markup()


def build_main_kb() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    for area in [AreaOfViolation.front, AreaOfViolation.entrance, AreaOfViolation.apartment]:
        builder.button(
            text=area,
            callback_data=AreaOfViolationCbData(action=area, detail="").pack(),
        )
    builder.adjust(1)
    return builder.as_markup()


class ViolationFSM(StatesGroup):
    main_menu = State()
    details_menu = State()
    address = State()
    photo = State()
    final = State()


# Handle text messages in the main menu
@router.message(ViolationFSM.main_menu)
async def handle_text_messages(message: types.Message, state: FSMContext):
    current_state = await state.get_state()
    if current_state == ViolationFSM.main_menu:
        if is_text_without_emoji(message.text):
            await message.answer(
                text="Ошибка ввода. Пожалуйста, используйте кнопки для взаимодействия.",
                reply_markup=build_main_kb()
            )
        else:
            await message.answer(
                text="Ошибка ввода. Не отправляйте текст или эмодзи. Используйте кнопки.",
                reply_markup=build_main_kb()
            )


# Handle callback queries for choosing a violation area
@router.callback_query(AreaOfViolationCbData.filter(F.detail == ""))
async def get_violation_details(callback_query: types.CallbackQuery, callback_data: AreaOfViolationCbData,
                                state: FSMContext) -> None:
    if callback_data.action == "root":
        await state.set_state(ViolationFSM.main_menu)
        await callback_query.message.edit_text(
            text="👇 Где нарушение? 👇",
            reply_markup=build_main_kb(),
        )
    else:
        await state.set_state(ViolationFSM.details_menu)
        await callback_query.message.edit_text(
            text=f"👇 Выберите конкретное нарушение для {callback_data.action}: 👇",
            reply_markup=build_violation_kb(callback_data.action),
        )


# Handle callback queries for specific violation details
@router.callback_query(AreaOfViolationCbData.filter(F.detail != ""))
async def handle_violation_detail(callback_query: types.CallbackQuery, callback_data: AreaOfViolationCbData,
                                  state: FSMContext) -> None:

    details = getattr(ViolationDetails, area_mapping[callback_data.action])
    detail_text = details[callback_data.detail]

    # Store the selected violation detail in the state
    await state.update_data(violation_type=detail_text)

    # Ask for the violation address
    # await callback_query.message.answer("Введите адрес нарушения 👇")
    await message.answer("Введите адрес нарушения 👇")
    await state.set_state(ViolationFSM.address)


# Handle the address input
@router.message(ViolationFSM.address)
async def get_violation_address(message: types.Message, state: FSMContext):
    if len(message.text) < 5:  # Assuming valid addresses have at least 5 characters
        await message.answer("Введите корректный адрес (минимум 5 символов) 👇")
        return

    # Store the address in the state
    await state.update_data(address=message.text)

    # Ask the user to send a photo of the violation
    await message.answer("Отправьте фото нарушения 👇")
    await state.set_state(ViolationFSM.photo)


# Handle the photo input
@router.message(ViolationFSM.photo, F.content_type == "photo")
async def get_violation_photo(message: types.Message, state: FSMContext):
    # Get the highest resolution photo
    photo_id = message.photo[-1].file_id

    # Store the photo in the state
    await state.update_data(photo=photo_id)

    # Retrieve all data for review
    data = await state.get_data()

    # Offer users a chance to review their data
    await message.answer(f"Ваши данные:\n"
                         f"Тип нарушения: {data['violation_type']}\n"
                         f"Адрес: {data['address']}\n"
                         f"Фото: получено.\n"
                         f"Нажмите 'дальше' для завершения или 'начать заново'.",
                         reply_markup=types.ReplyKeyboardMarkup(
                             keyboard=[
                                 [types.KeyboardButton(text="дальше")],
                                 [types.KeyboardButton(text="начать заново")]
                             ], resize_keyboard=True))

    await state.set_state(ViolationFSM.final)


# Handle final confirm
@router.message(ViolationFSM.final, F.text == "дальше")
async def finish_violation_report(message: types.Message, state: FSMContext):
    data = await state.get_data()

    # Send confirm to the user
    await message.answer(f"Нарушение успешно зарегистрировано!\n"
                         f"Тип нарушения: {data['violation_type']}\n"
                         f"Адрес: {data['address']}\n"
                         f"Фото: {data['photo']}",
                         reply_markup=types.ReplyKeyboardRemove())

    # Clear the state after completion
    await state.clear()


# Handle restart of the violation process
@router.message(ViolationFSM.final, F.text == "начать заново")
async def restart_violation_process(message: types.Message, state: FSMContext):
    await message.answer("Начнем заново. Где нарушение? 👇", reply_markup=build_main_kb())
    await state.set_state(ViolationFSM.main_menu)
