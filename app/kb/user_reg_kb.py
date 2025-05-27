from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder


finish_reg_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Завершить регистрацию")],
        [KeyboardButton(text="Начать заново")]
    ],
    resize_keyboard=True,
    one_time_keyboard=True
)


def reg_users_dashboard():
    builder = InlineKeyboardBuilder()

    builder.button(text="🚨 Нарушение", callback_data="dashboard")
    builder.button(text="📩 Уведомление", callback_data="violationlist_editor")
    builder.button(text="ℹ️ Информация", callback_data="useful_info")

    builder.adjust(2)

    return builder.as_markup()
