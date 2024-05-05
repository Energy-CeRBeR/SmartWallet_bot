from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from src.transactions.lexicon import LEXICON
from src.database.models import IncomeCategory, ExpenseCategory, Card, Income, Expense


def create_select_category_keyboard(categories: list) -> InlineKeyboardMarkup:
    buttons = list()
    for category in categories:
        cur_category = InlineKeyboardButton(
            text=category.name,
            callback_data=f"select_card{category.id}"
        )
        buttons.append([cur_category])
    buttons.append(
        [
            InlineKeyboardButton(
                text=LEXICON["cancel_create"],
                callback_data="cancel[create_card]"
            )
        ]
    )

    keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
    return keyboard


def create_select_card_keyboard(cards: list[Card]) -> InlineKeyboardMarkup:
    buttons = list()
    for card in cards:
        cur_card = InlineKeyboardButton(
            text=card.name,
            callback_data=f"add_amount{card.id}"
        )
        buttons.append([cur_card])

    buttons.append(
        [
            InlineKeyboardButton(text=LEXICON["cancel_create"], callback_data="cancel[show_card]")
        ]
    )

    keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
    return keyboard


def create_description_keyboard() -> InlineKeyboardMarkup:
    yes_button = InlineKeyboardButton(
        text="Да",
        callback_data=f"YES"
    )
    no_button = InlineKeyboardButton(
        text="Нет",
        callback_data=f"NO"
    )
    back_button = InlineKeyboardButton(
        text=LEXICON["back_show_categories"],
        callback_data="cancel[create_card]"
    )
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [yes_button],
            [no_button],
            [back_button]
        ]
    )

    return keyboard


def create_done_keyboard() -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Подтвердить создание", callback_data="commit_transaction")]
    ])
    return keyboard
