import re
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.filters.callback_data import CallbackData
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.types import Message


EMOJI_PATTERN = re.compile("[\U00010000-\U0010FFFF]", flags=re.UNICODE)
ADDRESS_REGEX = r'^[\w\s,.№-]{5,}$'  # Basic street address validation


def is_text_without_emoji(text: str) -> bool:
    if not isinstance(text, str):
        return False  # Возвращаем False, если text не является строкой
    return not EMOJI_PATTERN.search(text)


# Function to check if message contains media
def contains_media(message: Message) -> bool:
    return bool(message.photo or message.document)


# # VIOLATIONS со старыми ссылками
# VIOLATIONS = {
#     "Фасад": {
#         "1": {"detail": "Заложено окно", "url": "https://example.com/zalozheno_okno"},
#         "2": {"detail": "Изменен размер окна", "url": "https://example.com/izmenen_razmer_okna"},
#         "3": {"detail": "Изменен цвет оконной рамы", "url": "https://example.com/izmenen_cveta_okonnoy_ramy"},
#         "4": {"detail": "Изменена раскладка окна", "url": "https://example.com/izmenena_raskladka_okna"},
#         "5": {"detail": "Сооружен козырек балкона", "url": "https://example.com/sooruzhen_kozyrek_balkona"},
#         "6": {"detail": "Сооружен балкон", "url": "https://example.com/sooruzhen_balkon"},
#         "7": {"detail": "Увеличена площадь балкона", "url": "https://example.com/uvelichena_ploshchad_balkona"},
#         "8": {"detail": "Остекление балкона", "url": "https://example.com/osteklenie_balkona"},
#         "9": {"detail": "Использование балкона", "url": "https://example.com/ispolzovanie_balkona"},
#         "10": {"detail": "Объединение балкона с квартирой", "url": "https://example.com/obedinenie_balkona"},
#         "11": {"detail": "Удалено ограждение балкона", "url": "https://example.com/udaleno_ograzhdenie_balkona"},
#         "12": {"detail": "Изменен фартук балкона", "url": "https://example.com/izmenen_fartuk_balkona"},
#         "13": {"detail": "Сооружена лоджия", "url": "https://example.com/sooruzhena_lodzhiya"},
#         "14": {"detail": "Увеличена площадь лоджии", "url": "https://example.com/uvelichena_ploshchad_lodzhii"},
#         "15": {"detail": "Остекление лоджии", "url": "https://example.com/osteklenie_lodzhii"},
#         "16": {"detail": "Использование лоджии", "url": "https://example.com/ispolzovanie_lodzhii"},
#         "17": {"detail": "Объединение лоджии с квартирой", "url": "https://example.com/obedinenie_lodzhii"},
#         "18": {"detail": "Удалено ограждение лоджии", "url": "https://example.com/udaleno_ograzhdenie_lodzhii"},
#         "19": {"detail": "Изменен фартук лоджии", "url": "https://example.com/izmenen_fartuk_lodzhii"},
#         "20": {"detail": "Спутниковая антенна", "url": "https://example.com/sputnikovaya_antenna"},
#         "21": {"detail": "Телевизионная антенна", "url": "https://example.com/televizionnaya_antenna"},
#         "22": {"detail": "Видеокамера на фасаде", "url": "https://example.com/videokamera_na_fasade"},
#         "23": {"detail": "Кондиционер", "url": "https://example.com/konditsioner"},
#         "24": {"detail": "Вентиляционная установка", "url": "https://example.com/ventilyatsionnaya_ustanovka"},
#         "25": {"detail": "Отверстие в фасаде", "url": "https://example.com/otverstie_na_fasade"},
#     },
#     "Подъезд": {
#         "1": {"detail": "Тамбурная дверь", "url": "https://example.com/tamburnye_dveri"},
#         "2": {"detail": "Тамбурная решетка", "url": "https://example.com/tamburnaya_reshetka"},
#         "3": {"detail": "Вынос квартирной двери", "url": "https://example.com/vynos_kvartirnoy_dveri"},
#         "4": {"detail": "Замок на двери к лестнице", "url": "https://example.com/zamok_na_lestnitse"},
#         "5": {"detail": "Остекление балкона лестницы", "url": "https://example.com/osteklenie_balkona_lestnitsy"},
#         "6": {"detail": "Видеокамера в подъезде", "url": "https://example.com/videokamera_v_podezde"},
#     }
# }
VIOLATIONS = {
    "Фасад": {
    #     "1": {"detail": "Заложено окно", "url": "https://ozpprevizor.ru/l/zalozhenookno"},
    #     "2": {"detail": "Изменен размер окна", "url": "https://ozpprevizor.ru/l/izmenenrazmerokna"},
    #     "3": {"detail": "Изменен цвет оконной рамы", "url": "https://ozpprevizor.ru/l/izmenencvetokonnoyrami"},
    #     "4": {"detail": "Изменена раскладка окна", "url": "https://ozpprevizor.ru/l/izmenenaraskladkaokna"},
    #     "5": {"detail": "Сооружен козырек балкона", "url": "https://ozpprevizor.ru/l/kozirekbalkona"},
    #     "6": {"detail": "Сооружен балкон", "url": "https://ozpprevizor.ru/l/sooruzhenbalkon"},
    #     "7": {"detail": "Увеличена площадь балкона", "url": "https://ozpprevizor.ru/l/uvelichenaploshadbalkona"},
        "8": {"detail": "Остекление балкона", "url": "https://ozpprevizor.ru/l/ostekleniebalkona"},
    #     "9": {"detail": "Использование балкона", "url": "https://ozpprevizor.ru/l/ispolzovaniebalkona"},
    #     "10": {"detail": "Объединение балкона с квартирой", "url": "https://ozpprevizor.ru/l/obiedineniebalkona"},
    #     "11": {"detail": "Удалено ограждение балкона", "url": "https://ozpprevizor.ru/l/udalenoograzhdeniebalkona"},
    #     "12": {"detail": "Изменен фартук балкона", "url": "https://ozpprevizor.ru/l/izmenenfartukbalkona"},
    #     "13": {"detail": "Сооружена лоджия", "url": "https://ozpprevizor.ru/l/sooruzhenalodzhiya"},
    #     "14": {"detail": "Увеличена площадь лоджии", "url": "https://ozpprevizor.ru/l/uvelichenalodzhiya"},
    #     "15": {"detail": "Остекление лоджии", "url": "https://ozpprevizor.ru/l/osteklenielodzhii"},
    #     "16": {"detail": "Использование лоджии", "url": "https://ozpprevizor.ru/l/ispolzovanielodzhii"},
    #     "17": {"detail": "Объединение лоджии с квартирой", "url": "https://ozpprevizor.ru/l/obiedinenielodzhii"},
    #     "18": {"detail": "Удалено ограждение лоджии", "url": "https://ozpprevizor.ru/l/ograzhdenielodzhii"},
    #     "19": {"detail": "Изменен фартук лоджии", "url": "https://ozpprevizor.ru/l/izmenenfartuklodzhii"},
    #     "20": {"detail": "Спутниковая антенна", "url": "https://ozpprevizor.ru/l/sputnikovayaantena"},
    #     "21": {"detail": "Телевизионная антенна", "url": "https://ozpprevizor.ru/l/tvantena"},
    #     "22": {"detail": "Видеокамера на фасаде", "url": "https://ozpprevizor.ru/l/videokameranafasade"},
    #     "23": {"detail": "Кондиционер", "url": "https://ozpprevizor.ru/l/conditsionernafasade"},
    #     "24": {"detail": "Вентиляционная установка", "url": "https://ozpprevizor.ru/l/fvunafasade"},
    #     "25": {"detail": "Отверстие в фасаде", "url": "https://ozpprevizor.ru/l/otverstievfasade"},
    },
    "Подъезд": {
        "1": {"detail": "Тамбурная дверь", "url": "https://ozpprevizor.ru/l/tamburnayadver"},
        # "2": {"detail": "Тамбурная решетка", "url": "https://ozpprevizor.ru/l/tamburnayareshetka"},
        # "3": {"detail": "Вынос квартирной двери", "url": "https://ozpprevizor.ru/l/vinosdverikvartiri"},
        # "4": {"detail": "Замок на двери к лестнице", "url": "https://ozpprevizor.ru/l/zamoknadverilestnici"},
        # "5": {"detail": "Остекление балкона лестницы", "url": "https://ozpprevizor.ru/l/ostekleniebalkonalestnici"},
        # "6": {"detail": "Видеокамера в подъезде", "url": "https://ozpprevizor.ru/l/videokameravpodyezde"},
    }
}


class ViolationCbData(CallbackData, prefix="v"):
    area: str
    detail: str


# # Упрощение создания клавиатуры с деталями нарушений
# def build_violation_kb(area: str) -> InlineKeyboardMarkup:
#     builder = InlineKeyboardBuilder()
#     details = VIOLATIONS[area]
#
#     # Проходим по нарушениям в выбранной области и создаем кнопки
#     for key, detail in details.items():
#         callback_data = ViolationCbData(area=area, detail=key).pack()
#         builder.button(text=detail, callback_data=callback_data)
#
#     # Добавляем кнопку для возврата в главное меню
#     builder.button(text="🔙 Вернуться в главное меню", callback_data=ViolationCbData(area="root", detail="").pack())
#     builder.adjust(1)
#     return builder.as_markup()
def build_violation_kb(area: str) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    details = VIOLATIONS[area]

    # Создаем кнопки для каждого нарушения
    for key, value in details.items():
        detail = value['detail']
        callback_data = ViolationCbData(area=area, detail=key).pack()
        builder.button(text=detail, callback_data=callback_data)

    # Кнопка для возврата в главное меню
    builder.button(
                   # text="🔙 Вернуться в главное меню",
                   text="🔙 Назад",
                   callback_data=ViolationCbData(area="root", detail="").pack()
                   )
    builder.adjust(1)
    return builder.as_markup()


# Упрощение создания главного меню

# def build_main_kb() -> InlineKeyboardMarkup:
#     builder = InlineKeyboardBuilder()
#
#     # Проходим по областям и создаем кнопки для каждой
#     for area in VIOLATIONS.keys():
#         builder.button(text=area, callback_data=ViolationCbData(area=area, detail="").pack())
#
#     builder.button(text="Начать заново↩️", callback_data="start_again")
#
#     builder.adjust(1)
#     return builder.as_markup()
def build_main_kb() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()

    # Проходим по всем категориям и нарушениям в словаре VIOLATIONS
    for area, details in VIOLATIONS.items():
        for key, value in details.items():
            detail_text = value['detail']
            callback_data = ViolationCbData(area=area, detail=key).pack()
            builder.button(text=detail_text, callback_data=callback_data)

    # Кнопка для возврата в главное меню
    # builder.button(text="Начать заново↩️", callback_data="start_again")
    builder.button(text="Начать заново↩️", callback_data="confirm_address")

    builder.adjust(1)
    return builder.as_markup()


# Функция для создания клавиатуры подтверждения
def build_confirm_kb() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text="Подтвердить", callback_data="confirm")
    builder.button(text="Выбрать заново", callback_data="reset")
    builder.adjust(1)
    return builder.as_markup()


#  Клавиатура для подтверждения всей текстовой информации или возврата в главное меню
def build_review_kb():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Подтвердить", callback_data="confirm_review")],
        [InlineKeyboardButton(text="Начать заново", callback_data="reset_review")]
    ])


# Клвиатура для подтверждения адреса в V2 2025 версии
def build_review_address_kb():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Подтвердить", callback_data="confirm_address")],
        [InlineKeyboardButton(text="☰", callback_data="start_again")]  # Возвращает из любого места на главную
    ])


# Клавиатура для редактирования ранее выбраных нарушений
def build_edit_main_data_kb():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Другой подъезд", callback_data="edit_entrance")],
        [InlineKeyboardButton(text="Другой этаж", callback_data="edit_floor")],
        [InlineKeyboardButton(text="Другое нарушение", callback_data="edit_violation")],
        [InlineKeyboardButton(text="🏁хватит🚧🧱", callback_data="start_again")],
    ])

# Кнопка для возврата на этап выбора подъезда
def back_to_button() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Начать заново↩️", callback_data="confirm_address")]
    ])


def back_to_main_menu_button() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="☰", callback_data="start_again")]
    ])
