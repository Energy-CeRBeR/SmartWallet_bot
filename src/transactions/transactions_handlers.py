from copy import deepcopy

from aiogram import Router, F
from aiogram.filters import Command, CommandObject
from aiogram.types import Message, CallbackQuery

from sqlalchemy import select, insert, delete, update

from src.database.database import async_session
from src.database.database import Income, Expense, IncomeCategory, ExpenseCategory

from src.database.users_status import users_status, user_dict_template

from src.transactions.lexicon import (
    LEXICON as USER_LEXICON,
    LEXICON_COMMANDS as USER_LEXICON_COMMANDS
)

from src.transactions.transactions_keyboards import (
    create_select_category_keyboard
)

router = Router()


@router.message(Command(commands="add_income"))
async def create_type(message: Message):
    async with async_session() as session:
        query = select(IncomeCategory)
        result = await session.execute(query)
        categories = result.scalars().all()
        if categories:
            buttons = [category for category in categories]
            await message.answer(
                text=USER_LEXICON_COMMANDS[message.text],
                reply_markup=create_select_category_keyboard(buttons)
            )

        else:
            await message.answer(USER_LEXICON["income_transactions"]["no_categories"])
