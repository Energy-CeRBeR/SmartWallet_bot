from aiogram import F, Router
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import default_state
from aiogram.types import Message, CallbackQuery
from sqlalchemy import select, insert

from src.card_operations.keyboards import create_exit_keyboard
from src.database.database import async_session
from src.database.models import ExpenseCategory
from src.services.states import ShowExpensesCategoryState, AddExpenseCategoryState
from src.transactions.categories_keyboards import create_expense_categories_keyboard, create_category_actions_keyboard
from src.transactions.lexicon import LEXICON as USER_LEXICON, print_category_info

router = Router()


@router.message(Command(commands="ex_categories"), StateFilter(default_state))
async def get_expense_categories(message: Message, state: FSMContext):
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
            await state.set_state(ShowExpensesCategoryState.show_category)
        else:
            await message.answer(USER_LEXICON["expense"]["no_categories"])


@router.callback_query(F.data[:15] == "get_ex_category", StateFilter(ShowExpensesCategoryState.show_category))
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


@router.message(Command(commands="add_ex_category"), StateFilter(ShowExpensesCategoryState.show_category))
async def add_expense_category(message: Message, state: FSMContext):
    await message.answer(
        text=USER_LEXICON["expense"]["add_expense_category"],
        reply_markup=create_exit_keyboard()
    )
    await state.set_state(AddExpenseCategoryState.add_name)


@router.message(StateFilter(AddExpenseCategoryState.add_name))
async def set_expense_category(message: Message, state: FSMContext):
    async with async_session() as session:
        stmt = insert(ExpenseCategory).values(
            name=message.text,
            tg_id=message.from_user.id
        )
        await session.execute(stmt)
        await session.commit()

    await message.answer(USER_LEXICON["expense"]["category_is_create"])
    await state.clear()
