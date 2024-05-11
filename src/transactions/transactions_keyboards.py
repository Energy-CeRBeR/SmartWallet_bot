from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from src.transactions.lexicon import LEXICON as TRANSACTIONS_LEXICON
from src.database.models import IncomeCategory, ExpenseCategory, Card, Income, Expense
from aiogram.utils.keyboard import InlineKeyboardBuilder

from src.services.services import pagination


def create_exit_transaction_edit_keyboard() -> InlineKeyboardMarkup:
    back_button = InlineKeyboardButton(
        text=TRANSACTIONS_LEXICON["cancel_edit"],
        callback_data="cancel_edit_transaction"
    )
    keyboard = InlineKeyboardMarkup(inline_keyboard=[[back_button]])

    return keyboard


def create_incomes_keyboard(incomes: list[Income]) -> InlineKeyboardMarkup:
    buttons = list()
    for income in incomes:
        cur_income = InlineKeyboardButton(
            text=f"Дата: {income.date}, Сумма: {income.amount}",
            callback_data=f"get_income{income.id}"
        )
        buttons.append([cur_income])

    exit_button = InlineKeyboardButton(
        text=TRANSACTIONS_LEXICON["exit"],
        callback_data="exit"
    )
    back_page_button = InlineKeyboardButton(
        text=TRANSACTIONS_LEXICON["back_page"],
        callback_data="back_page"
    )
    next_page_button = InlineKeyboardButton(
        text=TRANSACTIONS_LEXICON["next_page"],
        callback_data="next_page"
    )

    keyboard = InlineKeyboardMarkup(inline_keyboard=[*buttons, [back_page_button, exit_button, next_page_button]])

    return keyboard


def create_expenses_keyboard(expenses: list[Expense]) -> InlineKeyboardMarkup:
    buttons = list()
    for expense in expenses:
        cur_expense = InlineKeyboardButton(
            text=f"Дата: {expense.date}, Сумма: {expense.amount}",
            callback_data=f"get_expense{expense.id}"
        )
        buttons.append([cur_expense])

    exit_button = InlineKeyboardButton(
        text=TRANSACTIONS_LEXICON["exit"],
        callback_data="exit"
    )
    back_page_button = InlineKeyboardButton(
        text=TRANSACTIONS_LEXICON["back_page"],
        callback_data="back_page"
    )
    next_page_button = InlineKeyboardButton(
        text=TRANSACTIONS_LEXICON["next_page"],
        callback_data="next_page"
    )

    keyboard = InlineKeyboardMarkup(inline_keyboard=[*buttons, [back_page_button, exit_button, next_page_button]])

    return keyboard


def create_transaction_edit_keyboard(transaction_type: str) -> InlineKeyboardMarkup:
    edit_category_button = InlineKeyboardButton(
        text="Изменить категорию",
        callback_data=f"edit_{transaction_type}_category"
    )
    edit_card_button = InlineKeyboardButton(
        text="Изменить карту",
        callback_data=f"edit_{transaction_type}_card"
    )
    edit_amount_button = InlineKeyboardButton(
        text="Изменить сумму",
        callback_data=f"edit_{transaction_type}_amount"
    )
    edit_date_button = InlineKeyboardButton(
        text="Изменить дату",
        callback_data=f"edit_{transaction_type}_date"
    )
    edit_description_button = InlineKeyboardButton(
        text="Изменить / добавить описание",
        callback_data=f"edit_{transaction_type}_description"
    )

    exit_button = InlineKeyboardButton(
        text=TRANSACTIONS_LEXICON["exit"],
        callback_data="exit"
    )

    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [edit_category_button],
            [edit_card_button],
            [edit_amount_button],
            [edit_date_button],
            [edit_description_button],
            [exit_button]
        ]
    )

    return keyboard


def create_select_category_keyboard(categories: list, edit=False) -> InlineKeyboardMarkup:
    buttons = list()
    for category in categories:
        callback_data = f"select_card{category.id}" if not edit else f"set_category{category.id}"
        cur_category = InlineKeyboardButton(
            text=category.name,
            callback_data=callback_data
        )
        buttons.append([cur_category])

    text = TRANSACTIONS_LEXICON["cancel_create"] if not edit else TRANSACTIONS_LEXICON["cancel_edit"]
    buttons.append(
        [
            InlineKeyboardButton(
                text=text,
                callback_data="cancel"
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
            InlineKeyboardButton(text=TRANSACTIONS_LEXICON["cancel_create"], callback_data="exit")
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
        text=TRANSACTIONS_LEXICON["back_show_categories"],
        callback_data="cancel"
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
