from aiogram import F, Router
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import default_state
from aiogram.types import Message, CallbackQuery
from sqlalchemy import select, insert, delete, update

from src.card_operations.keyboards import create_exit_keyboard, create_exit_show_card_keyboard, \
    create_yes_no_delete_keyboard
from src.database.database import async_session
from src.database.models import ExpenseCategory, Expense
from src.services.services import pagination, isValidName
from src.services.settings import LIMITS
from src.services.states import ShowExpensesCategoryState, AddExpenseCategoryState, UpdCategoryState, ShowExpensesState
from src.transactions.categories_keyboards import create_expense_categories_keyboard, \
    create_category_actions_keyboard, create_ex_category_is_create_keyboard, create_add_new_ex_category_keyboard
from src.transactions.lexicon import LEXICON as TRANSACTIONS_LEXICON, print_category_info
from src.transactions.transactions_keyboards import create_expenses_keyboard

router = Router()


@router.message(Command(commands="ex_categories"), StateFilter(default_state))
async def get_expense_categories(message: Message, state: FSMContext):
    async with async_session() as session:
        query = select(ExpenseCategory).where(ExpenseCategory.tg_id == message.from_user.id)
        result = await session.execute(query)
        categories = result.scalars().all()
        if categories:
            keyboard_limit = LIMITS["max_elements_in_keyboard"]
            pages = len(categories) // keyboard_limit + (len(categories) % keyboard_limit != 0)
            buttons = [category for category in categories]

            await state.set_state(ShowExpensesCategoryState.show_category)
            await state.update_data(
                page=0,
                pages=pages,
                ex_categories=buttons
            )

            cur_buttons = pagination(buttons, 0)

            await message.answer(
                text=f'{TRANSACTIONS_LEXICON["expense"]["categories_list"]} Страница 1 / {pages}',
                reply_markup=create_expense_categories_keyboard(cur_buttons)
            )
        else:
            await state.clear()
            await message.answer(
                text=TRANSACTIONS_LEXICON["expense"]["no_categories"],
                reply_markup=create_add_new_ex_category_keyboard()
            )


@router.callback_query(F.data == "next_page", StateFilter(ShowExpensesCategoryState.show_category))
async def goto_next_ex_categories_page(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    cur_page = data["page"] + 1
    ex_categories = data["ex_categories"]
    buttons = pagination(ex_categories, cur_page)
    pages = data["pages"]

    if 0 <= cur_page < pages and buttons:
        await callback.message.edit_text(
            text=f'{TRANSACTIONS_LEXICON["expense"]["categories_list"]} Страница {cur_page + 1} / {pages}',
            reply_markup=create_expense_categories_keyboard(buttons)
        )

        await state.update_data(page=cur_page)


@router.callback_query(F.data == "back_page", StateFilter(ShowExpensesCategoryState.show_category))
async def goto_back_ex_categories_page(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    cur_page = data["page"] - 1
    ex_categories = data["ex_categories"]
    buttons = pagination(ex_categories, cur_page)
    pages = data["pages"]

    if 0 <= cur_page < pages and buttons:
        await callback.message.edit_text(
            text=f'{TRANSACTIONS_LEXICON["expense"]["categories_list"]} Страница {cur_page - 1} / {pages}',
            reply_markup=create_expense_categories_keyboard(buttons)
        )

        await state.update_data(page=cur_page)


@router.callback_query(F.data == "show_ex_categories_list", StateFilter(default_state))
@router.callback_query(F.data == "show_ex_categories_list", StateFilter(ShowExpensesCategoryState.show_category))
async def get_expense_categories(callback: CallbackQuery, state: FSMContext):
    async with async_session() as session:
        query = select(ExpenseCategory).where(ExpenseCategory.tg_id == callback.from_user.id)
        result = await session.execute(query)
        categories = result.scalars().all()
        if categories:
            keyboard_limit = LIMITS["max_elements_in_keyboard"]
            pages = len(categories) // keyboard_limit + (len(categories) % keyboard_limit != 0)
            buttons = [category for category in categories]

            await state.set_state(ShowExpensesCategoryState.show_category)
            await state.update_data(
                page=0,
                pages=pages,
                ex_categories=buttons
            )

            cur_buttons = pagination(buttons, 0)

            await callback.message.edit_text(
                text=f'{TRANSACTIONS_LEXICON["expense"]["categories_list"]} Страница 1 / {pages}',
                reply_markup=create_expense_categories_keyboard(cur_buttons)
            )
        else:
            await state.clear()
            await callback.message.edit_text(
                text=TRANSACTIONS_LEXICON["expense"]["no_categories"],
                reply_markup=create_add_new_ex_category_keyboard()
            )


@router.callback_query(F.data[:15] == "get_ex_category", StateFilter(default_state))
@router.callback_query(F.data[:15] == "get_ex_category", StateFilter(ShowExpensesCategoryState.show_category))
async def show_expense_category(callback: CallbackQuery, state: FSMContext):
    category_id = int(callback.data[15:])
    await state.set_state(ShowExpensesCategoryState.show_category)

    async with async_session() as session:
        query = select(ExpenseCategory).where(ExpenseCategory.id == category_id)
        result = await session.execute(query)
        category = result.scalars().first()
        text = print_category_info(category)

    await callback.message.edit_text(
        text=text,
        reply_markup=create_category_actions_keyboard(category_id, "ex")
    )


@router.message(Command(commands="add_ex_category"), StateFilter(default_state))
async def add_expense_category(message: Message, state: FSMContext):
    async with async_session() as session:
        query = select(ExpenseCategory).where(ExpenseCategory.tg_id == message.from_user.id)
        result = await session.execute(query)
        ex_categories = result.scalars().all()

    if len(ex_categories) < LIMITS["max_number_of_categories"]:
        await message.answer(
            text=TRANSACTIONS_LEXICON["expense"]["add_expense_category"],
            reply_markup=create_exit_keyboard()
        )
        await state.set_state(AddExpenseCategoryState.add_name)

    else:
        await message.answer(TRANSACTIONS_LEXICON["ex_categories_limit"])


@router.callback_query(F.data == "start_create_ex_category", StateFilter(default_state))
async def add_expense_category(callback: CallbackQuery, state: FSMContext):
    async with async_session() as session:
        query = select(ExpenseCategory).where(ExpenseCategory.tg_id == callback.from_user.id)
        result = await session.execute(query)
        ex_categories = result.scalars().all()

    if len(ex_categories) < LIMITS["max_number_of_categories"]:
        await callback.message.edit_text(
            text=TRANSACTIONS_LEXICON["expense"]["add_expense_category"],
            reply_markup=create_exit_keyboard()
        )
        await state.set_state(AddExpenseCategoryState.add_name)

    else:
        await callback.message.edit_text(TRANSACTIONS_LEXICON["ex_categories_limit"])


@router.message(StateFilter(AddExpenseCategoryState.add_name))
async def set_expense_category(message: Message, state: FSMContext):
    category_name = message.text.strip()
    if isValidName(category_name):
        async with async_session() as session:
            stmt = insert(ExpenseCategory).values(
                name=category_name,
                tg_id=message.from_user.id
            )
            await session.execute(stmt)
            await session.commit()

            query = select(ExpenseCategory).where(ExpenseCategory.tg_id == message.from_user.id)
            result = await session.execute(query)
            current_ex_category = result.scalars().all()[-1]

        await state.clear()
        await message.answer(
            text=TRANSACTIONS_LEXICON["expense"]["category_is_create"],
            reply_markup=create_ex_category_is_create_keyboard(current_ex_category.id)
        )

    else:
        await message.answer(
            text=TRANSACTIONS_LEXICON["expense"]["incorrect_name"],
            reply_markup=create_exit_keyboard()
        )


@router.callback_query(F.data[:12] == "del_category", StateFilter(ShowExpensesCategoryState.show_category))
async def del_category(callback: CallbackQuery, state: FSMContext):
    category_id = int(callback.data[14:])

    await state.update_data(category_id=category_id)
    await state.set_state(UpdCategoryState.del_ex_category)
    await callback.message.edit_text(
        text=TRANSACTIONS_LEXICON["edit_expense"]["confirm_del_category"],
        reply_markup=create_yes_no_delete_keyboard()
    )


@router.callback_query(F.data == "NO", StateFilter(UpdCategoryState.del_ex_category))
async def no_delete_card(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    category_id = data["category_id"]

    await state.clear()
    await callback.message.edit_text(
        text=TRANSACTIONS_LEXICON["edit_expense"]["cancel_del_category"],
        reply_markup=create_ex_category_is_create_keyboard(category_id)
    )


@router.callback_query(F.data == "YES", StateFilter(UpdCategoryState.del_ex_category))
async def yes_delete_card(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    category_id = data["category_id"]
    async with async_session() as session:
        to_delete_category = delete(ExpenseCategory).where(ExpenseCategory.id == category_id)
        to_delete_expense = delete(Expense).where(Expense.category_id == category_id)

        await session.execute(to_delete_category)
        await session.execute(to_delete_expense)

        await session.commit()

    await state.clear()
    await callback.message.delete()
    await callback.message.answer(TRANSACTIONS_LEXICON["edit_expense"]["success_del_category"])


@router.callback_query(F.data[:12] == "upd_category", StateFilter(ShowExpensesCategoryState.show_category))
async def upd_category_name(callback: CallbackQuery, state: FSMContext):
    category_id = int(callback.data[14:])
    await state.update_data(
        category_type=ExpenseCategory,
        category_id=category_id
    )
    await state.set_state(UpdCategoryState.upd_ex_category_name)

    await callback.message.edit_text(
        text=TRANSACTIONS_LEXICON["update_category_name"],
        reply_markup=create_exit_show_card_keyboard("exit_update")
    )


@router.message(StateFilter(UpdCategoryState.upd_ex_category_name))
async def set_upd_ex_category_name(message: Message, state: FSMContext):
    new_category_name = message.text.strip()
    if isValidName(new_category_name):
        data = await state.get_data()
        category_id: int = data["category_id"]
        async with async_session() as session:
            stmt = update(ExpenseCategory).where(ExpenseCategory.id == category_id).values(name=new_category_name)
            await session.execute(stmt)
            await session.commit()

        await state.clear()
        await message.answer(
            text=TRANSACTIONS_LEXICON["successful_upd_category_name"],
            reply_markup=create_ex_category_is_create_keyboard(category_id)
        )

    else:
        await message.answer(
            text=TRANSACTIONS_LEXICON["expense"]["incorrect_name"],
            reply_markup=create_exit_keyboard()
        )


@router.callback_query(F.data[:12] == "get_expenses", StateFilter(ShowExpensesCategoryState.show_category))
async def get_expenses(callback: CallbackQuery, state: FSMContext):
    category_id = int(callback.data[12:])
    async with async_session() as session:
        query = select(Expense).where(Expense.category_id == category_id)
        result = await session.execute(query)
        expenses = result.scalars().all()

    if expenses:
        keyboard_limit = LIMITS["max_elements_in_keyboard"]
        pages = len(expenses) // keyboard_limit + (len(expenses) % keyboard_limit != 0)
        buttons = [expense for expense in expenses]
        buttons.sort(key=lambda x: x.date, reverse=True)

        await state.set_state(ShowExpensesState.show_expenses)
        await state.update_data(
            page=0,
            pages=pages,
            expenses=buttons
        )

        cur_buttons = pagination(buttons, 0)
        await callback.message.edit_text(
            text=f'{TRANSACTIONS_LEXICON["expense"]["expenses_list"]} Страница 1 / {pages}',
            reply_markup=create_expenses_keyboard(cur_buttons)
        )

    else:
        await state.clear()
        await callback.message.edit_text(
            text=TRANSACTIONS_LEXICON["expense_transactions"]["no_expenses"],
            reply_markup=create_ex_category_is_create_keyboard(category_id)
        )
