from aiogram.utils.keyboard import InlineKeyboardBuilder


def inline_back_to_button(callback_data="back_to"):
    builder = InlineKeyboardBuilder()
    builder.button(text="Вернуться назад", callback_data=callback_data)
    builder.adjust(1)
    return builder.as_markup()
