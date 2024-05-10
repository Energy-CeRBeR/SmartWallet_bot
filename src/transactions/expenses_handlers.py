from datetime import datetime

from aiogram import F, Router
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.state import default_state

from sqlalchemy import select, update

from src.card_operations.keyboards import create_cards_keyboard
from src.database.database import async_session
from src.database.models import Expense, ExpenseCategory, Card
from src.services.services import transaction_pagination, isValidDate
from src.services.states import AddCategoryState, ShowExpensesState
from src.transactions.lexicon import LEXICON as USER_LEXICON, LEXICON_COMMANDS as USER_LEXICON_COMMANDS
from src.transactions.transactions_keyboards import create_expenses_keyboard, create_transaction_edit_keyboard, \
    create_select_category_keyboard, create_exit_transaction_edit_keyboard

router = Router()


@router.message(Command(commands="expenses"), StateFilter(default_state))
async def get_expenses(message: Message, state: FSMContext):
    async with async_session() as session:
        query = select(Expense).where(Expense.tg_id == message.from_user.id)
        result = await session.execute(query)
        expenses = result.scalars().all()

    if expenses:
        pages = len(expenses) // 9 + (len(expenses) % 9 != 0)
        buttons = [expense for expense in expenses]
        buttons.sort(key=lambda x: x.date, reverse=True)

        await state.set_state(ShowExpensesState.show_expenses)
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


@router.callback_query(F.data == "next_page", StateFilter(ShowExpensesState.show_expenses))
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


@router.callback_query(F.data == "back_page", StateFilter(ShowExpensesState.show_expenses))
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


@router.callback_query(F.data[:11] == "get_expense", StateFilter(ShowExpensesState.show_expenses))
async def get_expense_info(callback: CallbackQuery, state: FSMContext):
    expense_id = int(callback.data[11:])
    async with async_session() as session:
        query = select(Expense).where(Expense.id == expense_id)
        result = await session.execute(query)
        expense = result.scalars().first()

        query = select(ExpenseCategory).where(ExpenseCategory.id == expense.category_id)
        result = await session.execute(query)
        expense_category = result.scalars().first()

        query = select(Card).where(Card.id == expense.card_id)
        result = await session.execute(query)
        card = result.scalars().first()

    description = expense.description if expense.description else USER_LEXICON["expense_info"]["no_description"]
    await state.update_data(
        expense=expense,
        card=card,
        expense_category=expense_category
    )
    await callback.message.edit_text(
        text=(
            f'{USER_LEXICON["expense_info"]["info"]}\n'
            f'{USER_LEXICON["expense_info"]["category"]}: {expense_category.name}\n'
            f'{USER_LEXICON["expense_info"]["card"]}: {card.name}\n'
            f'{USER_LEXICON["expense_info"]["amount"]}: {expense.amount}\n'
            f'{USER_LEXICON["expense_info"]["date"]}: {expense.date}\n'
            f'{USER_LEXICON["expense_info"]["description"]}: {description}'
        ),
        reply_markup=create_transaction_edit_keyboard(transaction_type="ex")
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


@router.callback_query(F.data == "edit_ex_category", StateFilter(ShowExpensesState.show_expenses))
async def change_expense_category(callback: CallbackQuery, state: FSMContext):
    async with async_session() as session:
        query = select(ExpenseCategory).where(ExpenseCategory.tg_id == callback.from_user.id)
        result = await session.execute(query)
        categories = result.scalars().all()

    buttons = [category for category in categories]

    await state.set_state(ShowExpensesState.set_new_category)
    await callback.message.edit_text(
        text=USER_LEXICON["edit_expense"]["new_category"],
        reply_markup=create_select_category_keyboard(buttons, edit=True)
    )


@router.callback_query(F.data[:12] == "set_category", StateFilter(ShowExpensesState.set_new_category))
async def set_new_category(callback: CallbackQuery, state: FSMContext):
    category_id = int(callback.data[12:])
    data = await state.get_data()
    expense_id = data["expense"].id
    async with (async_session() as session):
        stmt = update(Expense).where(Expense.id == expense_id).values(category_id=category_id)
        await session.execute(stmt)
        await session.commit()

    await callback.message.delete()
    await state.set_state(ShowExpensesState.show_expenses)
    await callback.message.answer(USER_LEXICON["edit_expense"]["category_is_update"])


@router.callback_query(F.data == "edit_ex_card", StateFilter(ShowExpensesState.show_expenses))
async def change_expense_card(callback: CallbackQuery, state: FSMContext):
    async with async_session() as session:
        query = select(Card).where(Card.tg_id == callback.from_user.id)
        result = await session.execute(query)
        cards = result.scalars().all()
        buttons = [card for card in cards]

    await state.set_state(ShowExpensesState.set_new_card)
    await callback.message.edit_text(
        text=USER_LEXICON["edit_expense"]["new_card"],
        reply_markup=create_cards_keyboard(buttons, edit=True)
    )


@router.callback_query(F.data[:8] == "set_card", StateFilter(ShowExpensesState.set_new_card))
async def set_new_card(callback: CallbackQuery, state: FSMContext):
    card_id = int(callback.data[8:])
    data = await state.get_data()
    expense = data["expense"]

    async with (async_session() as session):
        query = select(Card).where(Card.id == expense.card_id)
        result = await session.execute(query)
        card = result.scalars().first()

        new_balance = card.balance + expense.amount
        stmt = update(Card).where(Card.id == card.id).values(balance=new_balance)
        await session.execute(stmt)
        await session.commit()

        stmt = update(Expense).where(Expense.id == expense.id).values(card_id=card_id)
        await session.execute(stmt)
        await session.commit()

        query = select(Card).where(Card.id == card_id)
        result = await session.execute(query)
        card = result.scalars().first()

        new_balance = card.balance - expense.amount
        stmt = update(Card).where(Card.id == card.id).values(balance=new_balance)
        await session.execute(stmt)
        await session.commit()

    await callback.message.delete()
    await state.set_state(ShowExpensesState.show_expenses)
    await callback.message.answer(USER_LEXICON["edit_expense"]["card_is_update"])


@router.callback_query(F.data == "edit_ex_amount", StateFilter(ShowExpensesState.show_expenses))
async def edit_expense_amount(callback: CallbackQuery, state: FSMContext):
    await callback.message.edit_text(
        text=USER_LEXICON["edit_expense"]["new_amount"],
        reply_markup=create_exit_transaction_edit_keyboard()
    )
    await state.set_state(ShowExpensesState.set_new_amount)


@router.message(StateFilter(ShowExpensesState.set_new_amount))
async def set_new_expense_amount(message: Message, state: FSMContext):
    try:
        amount = float(message.text.strip())
        data = await state.get_data()
        expense = data["expense"]
        card = data["card"]

        d = amount - expense.amount
        new_balance = card.balance - d
        card.balance = new_balance
        async with (async_session() as session):
            stmt = update(Expense).where(Expense.id == expense.id).values(amount=amount)
            await session.execute(stmt)
            await session.commit()

            stmt = update(Card).where(Card.id == card.id).values(balance=new_balance)
            await session.execute(stmt)
            await session.commit()

        await state.set_state(ShowExpensesState.show_expenses)
        await message.answer(USER_LEXICON["edit_expense"]["amount_is_update"])

    except ValueError:
        await message.answer(
            text=USER_LEXICON["expense"]["incorrect_amount"],
            reply_markup=create_exit_transaction_edit_keyboard()
        )


@router.callback_query(F.data == "edit_ex_date", StateFilter(ShowExpensesState.show_expenses))
async def edit_expense_date(callback: CallbackQuery, state: FSMContext):
    await callback.message.edit_text(
        text=USER_LEXICON["edit_expense"]["new_date"],
        reply_markup=create_exit_transaction_edit_keyboard()
    )
    await state.set_state(ShowExpensesState.set_new_date)


@router.message(StateFilter(ShowExpensesState.set_new_date))
async def set_new_expense_date(message: Message, state: FSMContext):
    date = message.text.strip()
    if isValidDate(date):
        date = datetime.strptime(date, '%d.%m.%Y').date()
        data = await state.get_data()
        expense = data["expense"]
        async with async_session() as session:
            stmt = update(Expense).where(Expense.id == expense.id).values(date=date)
            await session.execute(stmt)
            await session.commit()

        await state.set_state(ShowExpensesState.show_expenses)
        await message.answer(USER_LEXICON["edit_expense"]["date_is_update"])

    else:
        await message.answer(
            text=USER_LEXICON["incorrect_date"],
            reply_markup=create_exit_transaction_edit_keyboard()
        )


@router.callback_query(F.data == "edit_ex_description", StateFilter(ShowExpensesState.show_expenses))
async def edit_expense_description(callback: CallbackQuery, state: FSMContext):
    await callback.message.edit_text(
        text=USER_LEXICON["edit_expense"]["new_description"],
        reply_markup=create_exit_transaction_edit_keyboard()
    )
    await state.set_state(ShowExpensesState.set_new_description)


@router.message(StateFilter(ShowExpensesState.set_new_description))
async def set_new_expense_description(message: Message, state: FSMContext):
    data = await state.get_data()
    expense = data["expense"]
    async with async_session() as session:
        stmt = update(Expense).where(Expense.id == expense.id).values(description=message.text)
        await session.execute(stmt)
        await session.commit()

    await state.set_state(ShowExpensesState.show_expenses)
    await message.answer(USER_LEXICON["edit_expense"]["description_is_update"])
