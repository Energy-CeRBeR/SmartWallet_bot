from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from src.transactions.lexicon import LEXICON
from src.database.database import Income, Expense, IncomeCategory, ExpenseCategory, Card


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
