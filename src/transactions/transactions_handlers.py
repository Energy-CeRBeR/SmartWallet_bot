from copy import deepcopy

from aiogram import Router, F
from aiogram.filters import Command, CommandObject
from aiogram.types import Message, CallbackQuery

from sqlalchemy import select, insert, delete, update

from src.database.database import async_session
from src.database.database import Income, Expense, IncomeCategory, ExpenseCategory, Card

from src.database.users_status import users_status, user_dict_template

from src.transactions.lexicon import (
    LEXICON as USER_LEXICON,
    LEXICON_COMMANDS as USER_LEXICON_COMMANDS
)

from src.transactions.transactions_keyboards import (
    create_select_category_keyboard,
    create_select_card_keyboard
)
from src.card_operations.keyboards import create_exit_keyboard

router = Router()


@router.message(Command(commands="add_income"))
async def select_income_type(message: Message):
    users_status[message.from_user.id] = deepcopy(user_dict_template)
    users_status[message.from_user.id]["transactions"]["category_type"] = Income
    users_status[message.from_user.id]["transactions"]["category_type_str"] = "income"

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


@router.message(Command(commands="add_expense"))
async def select_expense_type(message: Message):
    users_status[message.from_user.id] = deepcopy(user_dict_template)
    users_status[message.from_user.id]["transactions"]["category_type"] = Expense
    users_status[message.from_user.id]["transactions"]["category_type_str"] = "expense"

    async with async_session() as session:
        query = select(ExpenseCategory)
        result = await session.execute(query)
        categories = result.scalars().all()
        if categories:
            buttons = [category for category in categories]
            await message.answer(
                text=USER_LEXICON_COMMANDS[message.text],
                reply_markup=create_select_category_keyboard(buttons)
            )

        else:
            await message.answer(USER_LEXICON["expense_transactions"]["no_categories"])


@router.callback_query(F.data[:11] == "select_card")
async def select_card(callback: CallbackQuery):
    if callback.from_user.id not in users_status:
        users_status[callback.from_user.id] = deepcopy(user_dict_template)

    category_id = int(callback.data[11:])
    users_status[callback.from_user.id]["transactions"]["category_id"] = category_id

    async with async_session() as session:
        query = select(Card)
        result = await session.execute(query)
        cards = result.scalars().all()
        if cards:
            buttons = [card for card in cards]
            await callback.message.edit_text(
                text=USER_LEXICON["card_list"],
                reply_markup=create_select_card_keyboard(buttons)
            )

        else:
            category_type = users_status[callback.from_user.id]["transactions"]["category_type_str"]
            transactions = "income_transactions" if category_type == "income" else "expense_transactions"
            await callback.message.answer(USER_LEXICON[transactions]["no_cards"])


@router.callback_query(F.data[:10] == "add_amount")
async def add_amount(callback: CallbackQuery):
    if callback.from_user.id not in users_status:
        users_status[callback.from_user.id] = deepcopy(user_dict_template)

    card_id = int(callback.data[10:])
    users_status[callback.from_user.id]["transactions"]["card_id"] = card_id

    await callback.message.delete()

    category_type = users_status[callback.from_user.id]["transactions"]["category_type_str"]
    transactions = "income_transactions" if category_type == "income" else "expense_transactions"
    await callback.message.answer(
        text=USER_LEXICON[transactions]["amount"],
        reply_markup=create_exit_keyboard()
    )


@router.message(Command(commands="add_amount"))
async def set_amount(message: Message, command: CommandObject):
    if message.from_user.id not in users_status:
        users_status[message.from_user.id] = deepcopy(user_dict_template)

    if not users_status[message.from_user.id]["transactions"]["category_type"]:
        await message.answer(USER_LEXICON["access_error"])
        return

    category_type_str = users_status[message.from_user.id]["transactions"]["category_type_str"]
    transactions = "income_transactions" if category_type_str == "income" else "expense_transactions"

    if command.args is None:
        await message.answer(USER_LEXICON[transactions]["empty_amount"])
        return

    try:
        amount = float(command.args.strip())
        users_status[message.from_user.id]["transactions"]["amount"] = amount
        category_type = users_status[message.from_user.id]["transactions"]["category_type"]
        async with async_session() as session:
            stmt = insert(category_type).values(
                category_id=users_status[message.from_user.id]["transactions"]["category_id"],
                card_id=users_status[message.from_user.id]["transactions"]["card_id"],
                amount=amount,
                description=""
            )
            users_status[message.from_user.id] = deepcopy(user_dict_template)
            await session.execute(stmt)
            await session.commit()
            await message.answer(text=USER_LEXICON[transactions]["income_is_create"])

    except ValueError:
        await message.answer(
            text=USER_LEXICON[transactions]["incorrect_amount"],
            reply_markup=create_exit_keyboard()
        )

# Добавить обновление баланса карты при добавлении расхода / дохода
