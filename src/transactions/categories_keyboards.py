from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from src.transactions.lexicon import LEXICON
from src.database.models import IncomeCategory, ExpenseCategory


def create_income_categories_keyboard(categories: list[IncomeCategory]) -> InlineKeyboardMarkup:
    buttons = list()
    for category in categories:
        cur_category = InlineKeyboardButton(
            text=category.name,
            callback_data=f"get_in_category{category.id}"
        )
        buttons.append([cur_category])

    exit_button = InlineKeyboardButton(
        text="Выход",
        callback_data="exit"
    )
    back_page_button = InlineKeyboardButton(
        text=LEXICON["back_page"],
        callback_data="back_page"
    )
    next_page_button = InlineKeyboardButton(
        text=LEXICON["next_page"],
        callback_data="next_page"
    )

    keyboard = InlineKeyboardMarkup(inline_keyboard=[*buttons, [back_page_button, exit_button, next_page_button]])
    return keyboard


def create_expense_categories_keyboard(categories: list[ExpenseCategory]) -> InlineKeyboardMarkup:
    buttons = list()
    for category in categories:
        cur_category = InlineKeyboardButton(
            text=category.name,
            callback_data=f"get_ex_category{category.id}"
        )
        buttons.append([cur_category])

    buttons.append(
        [
            InlineKeyboardButton(text=LEXICON["back_show_categories"], callback_data="cancel[show_card]")
        ]
    )

    keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
    return keyboard


def create_category_actions_keyboard(category_id: int, category_type: str):
    update_button = InlineKeyboardButton(
        text=LEXICON["category_name_update"],
        callback_data=f"upd_category{category_type}{category_id}"
    )
    delete_button = InlineKeyboardButton(
        text=LEXICON["category_delete"],
        callback_data=f"del_category{category_type}{category_id}"
    )
    back_button = InlineKeyboardButton(
        text=LEXICON["back_show_categories"],
        callback_data="cancel[show_card]"
    )
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [update_button],
            [delete_button],
            [back_button]
        ]
    )

    return keyboard
