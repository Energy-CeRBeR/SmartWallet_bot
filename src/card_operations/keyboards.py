from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from src.card_operations.lexicon import LEXICON
from src.database.models import Card


def create_exit_keyboard() -> InlineKeyboardMarkup:
    back_button = InlineKeyboardButton(
        text=LEXICON["card_types"]["back"],
        callback_data="cancel[create_card]"
    )
    keyboard = InlineKeyboardMarkup(inline_keyboard=[[back_button]])

    return keyboard


def create_exit_show_card_keyboard(text: str) -> InlineKeyboardMarkup:
    back_button = InlineKeyboardButton(
        text=LEXICON[text],
        callback_data="cancel[show_card]"
    )

    keyboard = InlineKeyboardMarkup(inline_keyboard=[[back_button]])

    return keyboard


def create_cards_keyboard(cards: list[Card], edit=False) -> InlineKeyboardMarkup:
    buttons = list()
    for card in cards:
        cur_card = InlineKeyboardButton(
            text=card.name,
            callback_data=f"get_card{card.id}" if not edit else f"set_card{card.id}"
        )
        buttons.append([cur_card])

    text = LEXICON["back_show_card"] if not edit else LEXICON["cancel_edit"]
    callback_data = "cancel[show_card]" if not edit else "cancel[create_card]"
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
        text=LEXICON["incomes"],
        callback_data=f"get_incomes{card_id}"
    )
    expenses_button = InlineKeyboardButton(
        text=LEXICON["expenses"],
        callback_data=f"get_expenses{card_id}"
    )
    update_button = InlineKeyboardButton(
        text=LEXICON["card_update"],
        callback_data=f"upd_card{card_id}"
    )
    delete_button = InlineKeyboardButton(
        text=LEXICON["card_delete"],
        callback_data=f"del_card{card_id}"
    )
    back_button = InlineKeyboardButton(
        text=LEXICON["back_show_card"],
        callback_data="cancel[show_card]"
    )
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [incomes_button],
            [expenses_button],
            [update_button],
            [delete_button],
            [back_button]
        ]
    )

    return keyboard


def create_card_update_keyboard(card_id: int) -> InlineKeyboardMarkup:
    name_button = InlineKeyboardButton(
        text=LEXICON["card_info"]["name"],
        callback_data=f"upd_name{card_id}"
    )
    balance_button = InlineKeyboardButton(
        text=LEXICON["card_info"]["balance"],
        callback_data=f"upd_bala{card_id}"
    )
    back_button = InlineKeyboardButton(
        text=LEXICON["exit_update"],
        callback_data="cancel[show_card]"
    )
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [name_button],
            [balance_button],
            [back_button]
        ]
    )

    return keyboard


class TypeKeyboard:
    @staticmethod
    def create_keyboard() -> InlineKeyboardMarkup:
        debit_card_button = InlineKeyboardButton(
            text=LEXICON["card_types"]["debit_card"],
            callback_data="debit_card"
        )
        credit_card_button = InlineKeyboardButton(
            text=LEXICON["card_types"]["credit_card"],
            callback_data="credit_card"
        )
        back_button = InlineKeyboardButton(
            text=LEXICON["card_types"]["back"],
            callback_data="cancel[create_card]"
        )
        keyboard = InlineKeyboardMarkup(
            inline_keyboard=[
                [debit_card_button],
                [credit_card_button],
                [back_button]
            ]
        )

        return keyboard
