from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from src.card_operations.lexicon import CARD_OPERATIONS_LEXICON
from src.database.models import Card


def create_exit_keyboard() -> InlineKeyboardMarkup:
    back_button = InlineKeyboardButton(
        text=CARD_OPERATIONS_LEXICON["card_types"]["back"],
        callback_data="cancel"
    )
    keyboard = InlineKeyboardMarkup(inline_keyboard=[[back_button]])

    return keyboard


def create_cancel_update_keyboard() -> InlineKeyboardMarkup:
    back_button = InlineKeyboardButton(
        text=CARD_OPERATIONS_LEXICON["exit_update"],
        callback_data="cancel"
    )

    keyboard = InlineKeyboardMarkup(inline_keyboard=[[back_button]])

    return keyboard


def create_exit_show_card_keyboard(text: str) -> InlineKeyboardMarkup:
    back_button = InlineKeyboardButton(
        text=CARD_OPERATIONS_LEXICON[text],
        callback_data="exit"
    )

    keyboard = InlineKeyboardMarkup(inline_keyboard=[[back_button]])

    return keyboard


def card_is_create_keyboard(card_id: int) -> InlineKeyboardMarkup:
    current_card_button = InlineKeyboardButton(
        text=CARD_OPERATIONS_LEXICON["get_current_card"],
        callback_data=f"get_card{card_id}"
    )

    cards_list_button = InlineKeyboardButton(
        text=CARD_OPERATIONS_LEXICON["get_cards_list"],
        callback_data="show_cards_list"
    )

    keyboard = InlineKeyboardMarkup(inline_keyboard=[[current_card_button], [cards_list_button]])

    return keyboard


def create_yes_no_delete_keyboard() -> InlineKeyboardMarkup:
    yes_button = InlineKeyboardButton(
        text="Да",
        callback_data=f"YES"
    )
    no_button = InlineKeyboardButton(
        text="Нет",
        callback_data=f"NO"
    )

    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [yes_button],
            [no_button],
        ]
    )

    return keyboard


def create_cards_keyboard(cards: list[Card], edit=False) -> InlineKeyboardMarkup:
    buttons = list()
    for card in cards:
        cur_card = InlineKeyboardButton(
            text=card.name,
            callback_data=f"get_card{card.id}" if not edit else f"set_card{card.id}"
        )
        buttons.append([cur_card])

    text = CARD_OPERATIONS_LEXICON["back_show_card"] if not edit else CARD_OPERATIONS_LEXICON["cancel_edit"]
    callback_data = "exit" if not edit else "cancel"
    buttons.append(
        [
            InlineKeyboardButton(
                text=text,
                callback_data=callback_data
            )
        ]
    )

    keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
    return keyboard


def create_card_actions_keyboard(card_id: int) -> InlineKeyboardMarkup:
    incomes_button = InlineKeyboardButton(
        text=CARD_OPERATIONS_LEXICON["incomes"],
        callback_data=f"get_incomes{card_id}"
    )
    expenses_button = InlineKeyboardButton(
        text=CARD_OPERATIONS_LEXICON["expenses"],
        callback_data=f"get_expenses{card_id}"
    )
    update_button = InlineKeyboardButton(
        text=CARD_OPERATIONS_LEXICON["card_update"],
        callback_data=f"upd_card{card_id}"
    )
    delete_button = InlineKeyboardButton(
        text=CARD_OPERATIONS_LEXICON["card_delete"],
        callback_data=f"del_card{card_id}"
    )
    cards_list_button = InlineKeyboardButton(
        text=CARD_OPERATIONS_LEXICON["goto_cards_list"],
        callback_data="show_cards_list"
    )
    back_button = InlineKeyboardButton(
        text=CARD_OPERATIONS_LEXICON["back_show_card"],
        callback_data="exit"
    )
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [incomes_button],
            [expenses_button],
            [update_button],
            [delete_button],
            [cards_list_button],
            [back_button]
        ]
    )

    return keyboard


def create_card_update_keyboard(card_id: int) -> InlineKeyboardMarkup:
    name_button = InlineKeyboardButton(
        text=CARD_OPERATIONS_LEXICON["card_info"]["name"],
        callback_data=f"upd_name{card_id}"
    )
    balance_button = InlineKeyboardButton(
        text=CARD_OPERATIONS_LEXICON["card_info"]["balance"],
        callback_data=f"upd_bala{card_id}"
    )

    cards_list_button = InlineKeyboardButton(
        text=CARD_OPERATIONS_LEXICON["goto_cards_list"],
        callback_data="show_cards_list"
    )

    back_button = InlineKeyboardButton(
        text=CARD_OPERATIONS_LEXICON["exit_update"],
        callback_data="cancel"
    )
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [name_button],
            [balance_button],
            [cards_list_button],
            [back_button]
        ]
    )

    return keyboard


class TypeKeyboard:
    @staticmethod
    def create_keyboard() -> InlineKeyboardMarkup:
        debit_card_button = InlineKeyboardButton(
            text=CARD_OPERATIONS_LEXICON["card_types"]["debit_card"],
            callback_data="debit_card"
        )
        credit_card_button = InlineKeyboardButton(
            text=CARD_OPERATIONS_LEXICON["card_types"]["credit_card"],
            callback_data="credit_card"
        )
        back_button = InlineKeyboardButton(
            text=CARD_OPERATIONS_LEXICON["card_types"]["back"],
            callback_data="cancel"
        )
        keyboard = InlineKeyboardMarkup(
            inline_keyboard=[
                [debit_card_button],
                [credit_card_button],
                [back_button]
            ]
        )

        return keyboard
