from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder


def change_violationstatus_button(violation_id):
    builder = InlineKeyboardBuilder()

    builder.button(text="Уведомление размещено", callback_data=f"change_status_{violation_id}")
    builder.button(text="Начать заново", callback_data="start_again")

    builder.adjust(1)

    return builder.as_markup()

