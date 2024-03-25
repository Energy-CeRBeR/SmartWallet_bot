from copy import deepcopy

from aiogram import Router, F
from aiogram.filters import Command, CommandObject
from aiogram.types import Message, CallbackQuery

from sqlalchemy import select, insert, delete, update

from src.database.database import async_session
from src.database.database import IncomeCategory, ExpenseCategory

from src.database.users_status import users_status, user_dict_template

from src.transactions.lexicon import (
    LEXICON as USER_LEXICON,
    print_category_info
)

from src.transactions.categories_keyboards import (
    create_income_categories_keyboard,
    create_expense_categories_keyboard,
    create_category_actions_keyboard
)
from src.card_operations.keyboards import create_exit_show_card_keyboard

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
        await message.answer(USER_LEXICON["income"]["empty_category_name"])
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
        await message.answer(USER_LEXICON["expense"]["empty_category_name"])
        return

    async with async_session() as session:
        stmt = insert(ExpenseCategory).values(
            name=command.args,
            tg_id=message.from_user.id
        )
        await session.execute(stmt)
        await session.commit()

    await message.answer(USER_LEXICON["expense"]["category_is_create"])


@router.callback_query(F.data[:12] == "del_category")
async def del_category(callback: CallbackQuery):
    category_type = callback.data[12: 14]
    category_id = int(callback.data[14:])
    category = IncomeCategory if category_type == "in" else ExpenseCategory
    async with async_session() as session:
        to_delete = delete(category).where(category.id == category_id)
        await session.execute(to_delete)
        await session.commit()

    await callback.message.delete()
    await callback.message.answer(USER_LEXICON["successful_del_category"])


@router.callback_query(F.data[:12] == "upd_category")
async def upd_category_name(callback: CallbackQuery):
    category_type = callback.data[12: 14]
    category_id = int(callback.data[14:])
    category = IncomeCategory if category_type == "in" else ExpenseCategory

    if callback.from_user.id not in users_status:
        users_status[callback.from_user.id] = deepcopy(user_dict_template)
    users_status[callback.from_user.id]["upd_category"]["category_id"] = category_id
    users_status[callback.from_user.id]["upd_category"]["category_type"] = category

    await callback.message.edit_text(
        text=USER_LEXICON["update_category_name"],
        reply_markup=create_exit_show_card_keyboard("exit_update")
    )


@router.message(Command(commands="upd_category_name"))
async def set_upd_category_name(message: Message, command: CommandObject):
    if message.from_user.id not in users_status:
        users_status[message.from_user.id] = deepcopy(user_dict_template)

    if not users_status[message.from_user.id]["upd_category"]["category_type"]:
        await message.answer(USER_LEXICON["access_error"])
        return

    if command.args is None:
        await message.answer(USER_LEXICON["income"]["empty_category_name"])
        return

    async with async_session() as session:
        category_id = users_status[message.from_user.id]["upd_category"]["category_id"]
        category = users_status[message.from_user.id]["upd_category"]["category_type"]
        stmt = update(category).where(category.id == category_id).values(name=command.args)
        await session.execute(stmt)
        await session.commit()

    users_status[message.from_user.id]["upd_category"]["category_id"] = 0
    users_status[message.from_user.id]["upd_category"]["category_type"] = None

    await message.answer(USER_LEXICON["successful_upd_category_name"])
