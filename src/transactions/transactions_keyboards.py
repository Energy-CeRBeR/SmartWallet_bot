from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from src.transactions.lexicon import LEXICON as TRANSACTIONS_LEXICON
from src.database.models import Card


def create_exit_transaction_edit_keyboard() -> InlineKeyboardMarkup:
    back_button = InlineKeyboardButton(
        text=TRANSACTIONS_LEXICON["cancel_edit"],
        callback_data="cancel_edit_transaction"
    )
    keyboard = InlineKeyboardMarkup(inline_keyboard=[[back_button]])

    return keyboard


def create_incomes_keyboard(incomes: list[dict]) -> InlineKeyboardMarkup:
    buttons = list()
    for income in incomes:
        cur_income = InlineKeyboardButton(
            text=f"Дата: {income['date']}, Сумма: {income['amount']}",
            callback_data=f"get_income{income['id']}"
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


def create_expenses_keyboard(expenses: list[dict]) -> InlineKeyboardMarkup:
    buttons = list()
    for expense in expenses:
        cur_expense = InlineKeyboardButton(
            text=f"Дата: {expense['date']}, Сумма: {expense['amount']}",
            callback_data=f"get_expense{expense['id']}"
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


def create_add_new_income_keyboard() -> InlineKeyboardMarkup:
    create_ex_category_button = InlineKeyboardButton(
        text=TRANSACTIONS_LEXICON["create_income"],
        callback_data="start_create_income"
    )

    keyboard = InlineKeyboardMarkup(inline_keyboard=[[create_ex_category_button]])
    return keyboard


def create_add_new_expense_keyboard() -> InlineKeyboardMarkup:
    create_ex_category_button = InlineKeyboardButton(
        text=TRANSACTIONS_LEXICON["create_expense"],
        callback_data="start_create_expense"
    )

    keyboard = InlineKeyboardMarkup(inline_keyboard=[[create_ex_category_button]])
    return keyboard


def create_income_is_create_keyboard(income_id: int) -> InlineKeyboardMarkup:
    current_income_button = InlineKeyboardButton(
        text=TRANSACTIONS_LEXICON["get_current_income"],
        callback_data=f"get_income{income_id}"
    )

    incomes_list_button = InlineKeyboardButton(
        text=TRANSACTIONS_LEXICON["get_incomes_list"],
        callback_data="show_incomes_list"
    )

    keyboard = InlineKeyboardMarkup(inline_keyboard=[[current_income_button], [incomes_list_button]])

    return keyboard


def create_expense_is_create_keyboard(expense_id: int) -> InlineKeyboardMarkup:
    current_expense_button = InlineKeyboardButton(
        text=TRANSACTIONS_LEXICON["get_current_expense"],
        callback_data=f"get_expense{expense_id}"
    )

    expenses_list_button = InlineKeyboardButton(
        text=TRANSACTIONS_LEXICON["get_expenses_list"],
        callback_data="show_expenses_list"
    )

    keyboard = InlineKeyboardMarkup(inline_keyboard=[[current_expense_button], [expenses_list_button]])

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
    delete_transaction_button = InlineKeyboardButton(
        text="Удалить транзакцию",
        callback_data=f"del_{transaction_type}"
    )
    transactions_list_button = InlineKeyboardButton(
        text=TRANSACTIONS_LEXICON[f"goto_{transaction_type}_list"],
        callback_data="show_incomes_list" if transaction_type == "in" else "show_expenses_list"
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
            [delete_transaction_button],
            [transactions_list_button],
            [exit_button]
        ]
    )

    return keyboard


def create_select_category_keyboard(categories: list[dict], edit=False) -> InlineKeyboardMarkup:
    buttons = list()
    for category in categories:
        callback_data = f"select_card{category['id']}" if not edit else f"set_category{category['id']}"
        cur_category = InlineKeyboardButton(
            text=category["name"],
            callback_data=callback_data
        )
        buttons.append([cur_category])

    text = TRANSACTIONS_LEXICON["cancel_create"] if not edit else TRANSACTIONS_LEXICON["cancel_edit"]

    exit_button = InlineKeyboardButton(
        text=text,
        callback_data="cancel"
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


def create_select_card_keyboard(cards: list[Card]) -> InlineKeyboardMarkup:
    buttons = list()
    for card in cards:
        cur_card = InlineKeyboardButton(
            text=card.name,
            callback_data=f"add_date{card.id}"
        )
        buttons.append([cur_card])

    buttons.append(
        [
            InlineKeyboardButton(text=TRANSACTIONS_LEXICON["cancel_create"], callback_data="exit")
        ]
    )

    keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
    return keyboard


def create_yes_no_add_keyboard() -> InlineKeyboardMarkup:
    yes_button = InlineKeyboardButton(
        text="Да",
        callback_data=f"YES"
    )
    no_button = InlineKeyboardButton(
        text="Нет",
        callback_data=f"NO"
    )
    back_button = InlineKeyboardButton(
        text=TRANSACTIONS_LEXICON["cancel_create"],
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
