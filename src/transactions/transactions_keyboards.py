from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from src.transactions.lexicon import LEXICON
from src.database.models import IncomeCategory, ExpenseCategory, Card, Income, Expense
from aiogram.utils.keyboard import InlineKeyboardBuilder

from src.services.services import transaction_pagination


def create_incomes_keyboard(incomes: list[Income]) -> InlineKeyboardMarkup:
    buttons = list()
    for income in incomes:
        cur_income = InlineKeyboardButton(
            text=f"Размер дохода: {income.amount}",
            callback_data=f"get_income{income.id}"
        )
        buttons.append([cur_income])

    exit_button = InlineKeyboardButton(
        text=LEXICON["back_show_categories"],
        callback_data="cancel[create_card]"
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


def create_expenses_keyboard(expenses: list[Expense], cur_page) -> InlineKeyboardMarkup:
    buttons = list()
    for expense in expenses:
        cur_expense = InlineKeyboardButton(
            text=f"Размер расхода: {expense.amount}",
            callback_data=f"get_expense{expense.id}"
        )
        buttons.append([cur_expense])

    exit_button = InlineKeyboardButton(
        text=LEXICON["back_show_categories"],
        callback_data="cancel[create_card]"
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
