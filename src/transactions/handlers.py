from copy import deepcopy

from aiogram import Router, F
from aiogram.filters import Command, CommandObject
from aiogram.types import Message, CallbackQuery

from sqlalchemy import select, insert, delete, update

from src.database.database import async_session
from src.database.database import (
    IncomeCategory,
    ExpenseCategory,
    Income,
    Expense
)

from src.database.users_status import users_status, user_dict_template

from src.transactions.lexicon import (
    LEXICON as USER_LEXICON,
    LEXICON_COMMANDS as USER_LEXICON_COMMANDS,
    print_category_info
)

from src.transactions.keyboards import (
    create_income_categories_keyboard,
    create_expense_categories_keyboard,
    create_category_actions_keyboard
)

router = Router()


@router.message(Command(commands="in_categories"))
async def get_income_categories(message: Message):
    async with async_session() as session:
        query = select(IncomeCategory).where(IncomeCategory.tg_id == message.from_user.id)
        result = await session.execute(query)
        categories = result.scalars().all()
        if categories:
            buttons = [category for category in categories]
            await message.answer(
                text=USER_LEXICON["income"]["categories_list"],
                reply_markup=create_income_categories_keyboard(buttons)
            )
        else:
            await message.answer(USER_LEXICON["income"]["no_categories"])


@router.message(Command(commands="ex_categories"))
async def get_expense_categories(message: Message):
    async with async_session() as session:
        query = select(ExpenseCategory).where(ExpenseCategory.tg_id == message.from_user.id)
        result = await session.execute(query)
        categories = result.scalars().all()
        if categories:
            buttons = [category for category in categories]
            await message.answer(
                text=USER_LEXICON["expense"]["categories_list"],
                reply_markup=create_expense_categories_keyboard(buttons)
            )
        else:
            await message.answer(USER_LEXICON["expense"]["no_categories"])


@router.callback_query(F.data[:15] == "get_in_category")
async def show_income_category(callback: CallbackQuery):
    category_id = int(callback.data[15:])
    async with async_session() as session:
        query = select(IncomeCategory).where(IncomeCategory.id == category_id)
        result = await session.execute(query)
        category = result.scalars().first()
        text = print_category_info(category)
        await callback.message.edit_text(
            text=text,
            reply_markup=create_category_actions_keyboard(category_id, "in")
        )


@router.callback_query(F.data[:15] == "get_ex_category")
async def show_expense_category(callback: CallbackQuery):
    category_id = int(callback.data[15:])
    async with async_session() as session:
        query = select(ExpenseCategory).where(ExpenseCategory.id == category_id)
        result = await session.execute(query)
        category = result.scalars().first()
        text = print_category_info(category)
        await callback.message.edit_text(
            text=text,
            reply_markup=create_category_actions_keyboard(category_id, "ex")
        )


@router.message(Command(commands="add_in_category"))
async def add_income_category(message: Message, command: CommandObject):
    if command.args is None:
        await message.answer(USER_LEXICON["income"]["empty_category"])
        return

    async with async_session() as session:
        stmt = insert(IncomeCategory).values(
            name=command.args,
            tg_id=message.from_user.id
        )
        await session.execute(stmt)
        await session.commit()

    await message.answer(USER_LEXICON["income"]["category_is_create"])


@router.message(Command(commands="add_ex_category"))
async def add_expense_category(message: Message, command: CommandObject):
    if command.args is None:
        await message.answer(USER_LEXICON["expense"]["empty_category"])
        return

    async with async_session() as session:
        stmt = insert(ExpenseCategory).values(
            name=command.args,
            tg_id=message.from_user.id
        )
        await session.execute(stmt)
        await session.commit()

    await message.answer(USER_LEXICON["expense"]["category_is_create"])


@router.callback_query(F.text[:12] == "del_category")
async def delete_category(callback: CallbackQuery):
    category_type = callback.data[12: 14]
    category_id = int(callback.data[14:])
    category = IncomeCategory if category_type == "in" else ExpenseCategory
    async with async_session() as session:
        to_delete = delete(category).where(category.id == category_id)
        await session.execute(to_delete)
        await session.commit()

    await callback.message.delete()
    await callback.message.answer(USER_LEXICON["successful_del_category"])
    # Доделать данный роутер. Не переходит в хэндлер
