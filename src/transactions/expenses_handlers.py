from aiogram import F
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery
from sqlalchemy import select

from src.database.database import async_session
from src.database.models import Expense, ExpenseCategory
from src.services.services import transaction_pagination
from src.services.states import ShowExpenseState, AddCategoryState
from src.transactions.lexicon import LEXICON as USER_LEXICON, LEXICON_COMMANDS as USER_LEXICON_COMMANDS
from src.transactions.general_handlers import router
from src.transactions.transactions_keyboards import create_expenses_keyboard, create_transaction_edit_keyboard, \
    create_select_category_keyboard


@router.message(Command(commands="expenses"))
async def get_expenses(message: Message, state: FSMContext):
    async with async_session() as session:
        query = select(Expense).where(Expense.tg_id == message.from_user.id)
        result = await session.execute(query)
        expenses = result.scalars().all()

    if expenses:
        pages = len(expenses) // 9 + (len(expenses) % 9 != 0)
        buttons = [expense for expense in expenses]
        buttons.reverse()

        await state.set_state(ShowExpenseState.show_expenses)
        await state.update_data(
            page=1,
            pages=pages,
            expenses=buttons
        )

        cur_buttons = transaction_pagination(buttons, 0, "next")

        await message.answer(
            text=f'{USER_LEXICON["expense"]["expenses_list"]}. Страница 1 / {pages}',
            reply_markup=create_expenses_keyboard(cur_buttons)
        )
    else:
        await message.answer(USER_LEXICON["expense_transactions"]["no_expenses"])


@router.callback_query(F.data == "next_page", StateFilter(ShowExpenseState.show_expenses))
async def goto_next_expenses_page(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    cur_page = data["page"]
    expenses = data["expenses"]
    buttons = transaction_pagination(expenses, cur_page, "next")
    pages = data["pages"]

    if cur_page > 0 and buttons:
        await callback.message.edit_text(
            text=f'{USER_LEXICON["expense"]["expenses_list"]} Страница {cur_page + 1} / {pages}',
            reply_markup=create_expenses_keyboard(buttons)
        )

        await state.update_data(page=cur_page + 1)


@router.callback_query(F.data == "back_page", StateFilter(ShowExpenseState.show_expenses))
async def goto_back_expenses_page(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    cur_page = data["page"]
    expenses = data["expenses"]
    buttons = transaction_pagination(expenses, cur_page, "back")
    pages = data["pages"]

    if cur_page > 0 and buttons:
        await callback.message.edit_text(
            text=f'{USER_LEXICON["expense"]["expenses_list"]} Страница {cur_page - 1} / {pages}',
            reply_markup=create_expenses_keyboard(buttons)
        )

        await state.update_data(page=cur_page - 1)


@router.callback_query(F.data[:11] == "get_expense", StateFilter(ShowExpenseState.show_expenses))
async def get_expense_info(callback: CallbackQuery):
    expense_id = int(callback.data[11:])
    async with async_session() as session:
        query = select(Expense).where(Expense.id == expense_id)
        result = await session.execute(query)
        expense = result.scalars().first()

        query = select(ExpenseCategory).where(ExpenseCategory.id == expense.category_id)
        result = await session.execute(query)
        expense_category = result.scalars().first()

    description = expense.description if expense.description else USER_LEXICON["expense_info"]["no_description"]
    await callback.message.edit_text(
        text=(
            f'{USER_LEXICON["expense_info"]["info"]}\n'
            f'{USER_LEXICON["expense_info"]["category"]}: {expense_category.name}\n'
            f'{USER_LEXICON["expense_info"]["amount"]}: {expense.amount}\n'
            f'{USER_LEXICON["expense_info"]["date"]}: {expense.date}\n'
            f'{USER_LEXICON["expense_info"]["description"]}: {description}'
        ),
        reply_markup=create_transaction_edit_keyboard(transaction_type="in")
    )


@router.message(Command(commands="add_expense"))
async def select_expense_type(message: Message, state: FSMContext):
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

            await state.set_state(AddCategoryState.select_card)
            await state.update_data(
                category_type=Expense,
                category_type_str="expense"
            )

        else:
            await message.answer(USER_LEXICON["expense_transactions"]["no_categories"])
