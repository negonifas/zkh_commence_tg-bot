from aiogram.types import (
    InlineKeyboardButton,
    )
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.filters.callback_data import CallbackData

class Pagination(CallbackData, prefix="pag"):
    action: str
    page: int


# def paginator(violation_id: int, page: int = 0):
#     print(f'Создание кнопок пагинации с параметрами: violation_id={violation_id}, page={page}')
#     print(f'Callback data для кнопки "⬅️": {Pagination(action="prev", page=page).pack()}')
#     print(f'Callback data для кнопки "➡️": {Pagination(action="next", page=page).pack()}')
#     print(f'Callback data для кнопки "Изменить статус": change_status_{violation_id}')
#
#     builder = InlineKeyboardBuilder()
#     builder.row(
#         InlineKeyboardButton(text="⬅️", callback_data=Pagination(action="prev", page=page).pack()),
#         InlineKeyboardButton(text="Изменить статус", callback_data=f"change_status_{violation_id}"),
#         InlineKeyboardButton(text="➡️", callback_data=Pagination(action="next", page=page).pack()),
#         width=3,
#     )
#     return builder.as_markup()
def paginator(violation_id: int, page: int = 0, total_items: int = 1):
    # Вычисление текста для кнопки с текущей страницей и общим количеством
    current_page_text = f"           {page + 1} / {total_items}           "

    # Строим клавиатуру
    builder = InlineKeyboardBuilder()

    builder.row(
        InlineKeyboardButton(text="       ⬅️       ", callback_data=Pagination(action="prev", page=page).pack()),
        InlineKeyboardButton(text=current_page_text, callback_data="noop"),
        InlineKeyboardButton(text="       ➡️       ", callback_data=Pagination(action="next", page=page).pack()),
        width=3
    )

    builder.row(
        InlineKeyboardButton(text="Изменить статус", callback_data=f"change_status_{violation_id}")
    )

    builder.row(
        InlineKeyboardButton(text="Начать заново", callback_data="start_again")
    )

    return builder.as_markup()
