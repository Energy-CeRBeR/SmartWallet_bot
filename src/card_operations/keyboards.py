from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from src.card_operations.lexicon import LEXICON


class TypeKeyboard:
    @staticmethod
    def create_keyboard():
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
            callback_data="cancel"
        )
        keyboard = InlineKeyboardMarkup(
            inline_keyboard=[
                [debit_card_button,
                 credit_card_button,
                 back_button
                 ]
            ]
        )

        return keyboard
