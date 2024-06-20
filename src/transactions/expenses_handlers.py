from datetime import datetime

from aiogram import F, Router
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.state import default_state

from sqlalchemy import select, update, insert, delete

from src.card_operations.keyboards import create_cards_keyboard, create_exit_keyboard, create_yes_no_delete_keyboard, \
    create_add_new_card_keyboard
from src.database.database import async_session
from src.database.models import Expense, ExpenseCategory, Card
from src.services.services import pagination, isValidDate, isValidDescription, unpack_expense_model, \
    unpack_card_model, unpack_ex_category_model
from src.services.settings import LIMITS
from src.services.states import AddExpenseState, ShowExpensesState
from src.transactions.categories_keyboards import create_add_new_ex_category_keyboard
from src.transactions.lexicon import LEXICON as TRANSACTIONS_LEXICON, \
    LEXICON_COMMANDS as TRANSACTIONS_LEXICON_COMMANDS, print_expense_info
from src.transactions.transactions_keyboards import create_expenses_keyboard, create_transaction_edit_keyboard, \
    create_select_category_keyboard, create_exit_transaction_edit_keyboard, create_select_card_keyboard, \
    create_yes_no_add_keyboard, create_done_keyboard, create_expense_is_create_keyboard, create_add_new_expense_keyboard

router = Router()


@router.message(Command(commands="expenses"), StateFilter(default_state))
async def get_expenses(message: Message, state: FSMContext):
    async with async_session() as session:
        query = select(Expense).where(Expense.tg_id == message.from_user.id)
        result = await session.execute(query)
        expenses = result.scalars().all()

    if expenses:
        keyboard_limit = LIMITS["max_elements_in_keyboard"]
        pages = len(expenses) // keyboard_limit + (len(expenses) % keyboard_limit != 0)
        buttons = [unpack_expense_model(expense) for expense in expenses]
        buttons.sort(key=lambda x: datetime.strptime(x["date"], '%Y-%m-%d').date(), reverse=True)

        await state.set_state(ShowExpensesState.show_expenses)
        await state.update_data(
            page=0,
            pages=pages,
            expenses=buttons
        )

        cur_buttons = pagination(buttons, 0)

        await message.answer(
            text=f'{TRANSACTIONS_LEXICON["expense"]["expenses_list"]}. Страница 1 / {pages}',
            reply_markup=create_expenses_keyboard(cur_buttons)
        )

    else:
        await state.clear()
        await message.answer(
            text=TRANSACTIONS_LEXICON["expense_transactions"]["no_expenses"],
            reply_markup=create_add_new_expense_keyboard()
        )


@router.callback_query(F.data == "show_expenses_list", StateFilter(default_state))
@router.callback_query(F.data == "show_expenses_list", StateFilter(ShowExpensesState.show_expenses))
async def get_expenses(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    try:
        expenses = data["expenses"]
    except KeyError:
        async with async_session() as session:
            query = select(Expense).where(Expense.tg_id == callback.from_user.id)
            result = await session.execute(query)
            expenses = result.scalars().all()

    if expenses:
        keyboard_limit = LIMITS["max_elements_in_keyboard"]
        pages = len(expenses) // keyboard_limit + (len(expenses) % keyboard_limit != 0)
        buttons = [unpack_expense_model(expense) for expense in expenses]
        buttons.sort(key=lambda x: datetime.strptime(x["date"], '%Y-%m-%d').date(), reverse=True)

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
            reply_markup=create_add_new_expense_keyboard()
        )


@router.callback_query(F.data == "next_page", StateFilter(ShowExpensesState.show_expenses))
async def goto_next_expenses_page(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    cur_page = data["page"] + 1
    expenses = data["expenses"]
    buttons = pagination(expenses, cur_page)
    pages = data["pages"]

    if 0 <= cur_page < pages and buttons:
        await callback.message.edit_text(
            text=f'{TRANSACTIONS_LEXICON["expense"]["expenses_list"]} Страница {cur_page + 1} / {pages}',
            reply_markup=create_expenses_keyboard(buttons)
        )

        await state.update_data(page=cur_page)


@router.callback_query(F.data == "back_page", StateFilter(ShowExpensesState.show_expenses))
async def goto_back_expenses_page(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    cur_page = data["page"] - 1
    expenses = data["expenses"]
    buttons = pagination(expenses, cur_page)
    pages = data["pages"]

    if 0 <= cur_page < pages and buttons:
        await callback.message.edit_text(
            text=f'{TRANSACTIONS_LEXICON["expense"]["expenses_list"]} Страница {cur_page + 1} / {pages}',
            reply_markup=create_expenses_keyboard(buttons)
        )

        await state.update_data(page=cur_page)


@router.callback_query(F.data[:11] == "get_expense", StateFilter(default_state))
@router.callback_query(F.data[:11] == "get_expense", StateFilter(ShowExpensesState.show_expenses))
async def get_expense_info(callback: CallbackQuery, state: FSMContext):
    expense_id = int(callback.data[11:])
    await state.set_state(ShowExpensesState.show_expenses)

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

    description = expense.description if expense.description else TRANSACTIONS_LEXICON["expense_info"]["no_description"]
    await state.update_data(
        expense=unpack_expense_model(expense),
        card=unpack_card_model(card),
        expense_category=unpack_ex_category_model(expense_category)
    )
    await callback.message.edit_text(
        text=print_expense_info(expense, card, expense_category, description),
        reply_markup=create_transaction_edit_keyboard(transaction_type="ex")
    )


@router.message(Command(commands="add_expense"), StateFilter(default_state))
async def add_expense(message: Message, state: FSMContext):
    async with async_session() as session:
        query = select(ExpenseCategory).where(ExpenseCategory.tg_id == message.from_user.id)
        result = await session.execute(query)
        categories = result.scalars().all()
        if categories:
            keyboard_limit = LIMITS["max_elements_in_keyboard"]
            pages = len(categories) // keyboard_limit + (len(categories) % keyboard_limit != 0)
            buttons = [unpack_ex_category_model(category) for category in categories]

            await state.set_state(AddExpenseState.select_category)
            await state.update_data(
                page=0,
                pages=pages,
                ex_categories=buttons,
                category_type_str="expense"
            )

            cur_buttons = pagination(buttons, 0)
            await message.answer(
                text=f"{TRANSACTIONS_LEXICON_COMMANDS[message.text]} Страница 1 / {pages}",
                reply_markup=create_select_category_keyboard(cur_buttons)
            )

        else:
            await message.answer(
                text=TRANSACTIONS_LEXICON["expense_transactions"]["no_categories"],
                reply_markup=create_add_new_ex_category_keyboard()
            )


@router.callback_query(F.data == "start_create_expense", StateFilter(default_state))
async def add_expense(callback: CallbackQuery, state: FSMContext):
    async with async_session() as session:
        query = select(ExpenseCategory).where(ExpenseCategory.tg_id == callback.from_user.id)
        result = await session.execute(query)
        categories = result.scalars().all()
        if categories:
            keyboard_limit = LIMITS["max_elements_ex_keyboard"]
            pages = len(categories) // keyboard_limit + (len(categories) % keyboard_limit != 0)
            buttons = [unpack_ex_category_model(category) for category in categories]

            await state.set_state(AddExpenseState.select_category)
            await state.update_data(
                page=0,
                pages=pages,
                ex_categories=buttons,
                category_type_str="expense"
            )

            cur_buttons = pagination(buttons, 0)
            await callback.message.edit_text(
                text=f"{TRANSACTIONS_LEXICON_COMMANDS['/add_expense']} Страница 1 / {pages}",
                reply_markup=create_select_category_keyboard(cur_buttons)
            )

        else:
            await callback.message.edit_text(
                text=TRANSACTIONS_LEXICON["expense_transactions"]["no_categories"],
                reply_markup=create_add_new_ex_category_keyboard()
            )


@router.callback_query(F.data == "next_page", StateFilter(AddExpenseState.select_category))
async def goto_next_ex_categories_page(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    cur_page = data["page"] + 1
    ex_categories = data["ex_categories"]
    buttons = pagination(ex_categories, cur_page)
    pages = data["pages"]

    if 0 <= cur_page < pages and buttons:
        await callback.message.edit_text(
            text=f'{TRANSACTIONS_LEXICON_COMMANDS["/add_expense"]} Страница {cur_page + 1} / {pages}',
            reply_markup=create_select_category_keyboard(buttons)
        )

        await state.update_data(page=cur_page)


@router.callback_query(F.data == "back_page", StateFilter(AddExpenseState.select_category))
async def goto_back_ex_categories_page(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    cur_page = data["page"] - 1
    ex_categories = data["ex_categories"]
    buttons = pagination(ex_categories, cur_page)
    pages = data["pages"]

    if 0 <= cur_page < pages and buttons:
        await callback.message.edit_text(
            text=f'{TRANSACTIONS_LEXICON_COMMANDS["/add_expense"]} Страница {cur_page + 1} / {pages}',
            reply_markup=create_select_category_keyboard(buttons)
        )

        await state.update_data(page=cur_page)


@router.callback_query(F.data[:11] == "select_card", StateFilter(AddExpenseState.select_category))
async def select_card(callback: CallbackQuery, state: FSMContext):
    category_id = int(callback.data[11:])
    await state.update_data(category_id=category_id)

    async with async_session() as session:
        query = select(Card).where(Card.tg_id == callback.from_user.id)
        result = await session.execute(query)
        cards = result.scalars().all()
        if cards:
            buttons = [card for card in cards]
            await callback.message.edit_text(
                text=TRANSACTIONS_LEXICON["card_list"],
                reply_markup=create_select_card_keyboard(buttons)
            )
            await state.set_state(AddExpenseState.add_date)

        else:
            await state.clear()
            await callback.message.edit_text(
                text=TRANSACTIONS_LEXICON["no_cards"],
                reply_markup=create_add_new_card_keyboard()
            )


@router.callback_query(F.data[:8] == "add_date", StateFilter(AddExpenseState.add_date))
async def yes_no_add_card(callback: CallbackQuery, state: FSMContext):
    card_id = int(callback.data[8:])
    await state.update_data(card_id=card_id)
    await callback.message.edit_text(
        text=TRANSACTIONS_LEXICON["add_date"],
        reply_markup=create_yes_no_add_keyboard()
    )


@router.callback_query(F.data == "YES", StateFilter(AddExpenseState.add_date))
async def get_date(callback: CallbackQuery, state: FSMContext):
    await state.set_state(AddExpenseState.add_amount)
    await callback.message.edit_text(
        text=TRANSACTIONS_LEXICON["get_date"],
        reply_markup=create_exit_keyboard()
    )


@router.callback_query(F.data == "NO", StateFilter(AddExpenseState.add_date))
async def no_add_date(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    category_type_str = data["category_type_str"]
    transactions = "income_transactions" if category_type_str == "income" else "expense_transactions"
    await callback.message.edit_text(
        text=TRANSACTIONS_LEXICON[transactions]["amount"],
        reply_markup=create_exit_keyboard()
    )
    await state.set_state(AddExpenseState.add_description)


@router.message(StateFilter(AddExpenseState.add_amount))
async def add_amount(message: Message, state: FSMContext):
    date = message.text.strip()
    if isValidDate(date):
        await state.update_data(date=date)
        data = await state.get_data()
        category_type_str = data["category_type_str"]
        transactions = "income_transactions" if category_type_str == "income" else "expense_transactions"
        await message.answer(
            text=TRANSACTIONS_LEXICON[transactions]["amount"],
            reply_markup=create_exit_keyboard()
        )
        await state.set_state(AddExpenseState.add_description)

    else:
        await message.answer(
            text=TRANSACTIONS_LEXICON["incorrect_date"],
            reply_markup=create_exit_transaction_edit_keyboard()
        )


@router.message(StateFilter(AddExpenseState.add_description))
async def add_description(message: Message, state: FSMContext):
    data = await state.get_data()
    category_type_str = data["category_type_str"]
    transactions = "income_transactions" if category_type_str == "income" else "expense_transactions"

    try:
        amount = float(message.text.strip())

        if amount > 0:
            await state.update_data(amount=amount)
            await message.answer(
                text=TRANSACTIONS_LEXICON["description"],
                reply_markup=create_yes_no_add_keyboard()
            )
            await state.set_state(AddExpenseState.get_description)

        else:
            await message.answer(
                text=TRANSACTIONS_LEXICON[transactions]["incorrect_amount"],
                reply_markup=create_exit_keyboard()
            )

    except ValueError:
        await message.answer(
            text=TRANSACTIONS_LEXICON[transactions]["incorrect_amount"],
            reply_markup=create_exit_keyboard()
        )


@router.callback_query(F.data == "YES", StateFilter(AddExpenseState.get_description))
async def get_description_from_user(callback: CallbackQuery, state: FSMContext):
    await callback.message.delete()
    await callback.message.answer(TRANSACTIONS_LEXICON["get_description"])
    await state.set_state(AddExpenseState.set_description)


@router.callback_query(F.data == "NO", StateFilter(AddExpenseState.get_description))
async def no_description(callback: CallbackQuery, state: FSMContext):
    await state.update_data(description="")
    await state.set_state(AddExpenseState.set_data)
    await callback.message.edit_text(
        text=TRANSACTIONS_LEXICON["commit_transaction"],
        reply_markup=create_done_keyboard()
    )


@router.message(StateFilter(AddExpenseState.set_description))
async def set_description(message: Message, state: FSMContext):
    description = message.text.strip()
    if isValidDescription(description):
        await state.update_data(description=description)
        await state.set_state(AddExpenseState.set_data)
        await message.answer(
            text=TRANSACTIONS_LEXICON["set_description"],
            reply_markup=create_done_keyboard()
        )

    else:
        await message.answer(
            text=TRANSACTIONS_LEXICON["incorrect_description"],
            reply_markup=create_exit_keyboard()
        )


@router.callback_query(F.data == "commit_transaction", StateFilter(AddExpenseState.set_data))
async def set_transaction(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    amount = data["amount"]
    async with async_session() as session:
        if "date" in data:
            date = datetime.strptime(data["date"], '%d.%m.%Y').date()
            stmt = insert(Expense).values(
                tg_id=callback.from_user.id,
                category_id=data["category_id"],
                card_id=data["card_id"],
                date=date,
                amount=amount,
                description=data["description"]
            )
        else:
            stmt = insert(Expense).values(
                tg_id=callback.from_user.id,
                category_id=data["category_id"],
                card_id=data["card_id"],
                amount=amount,
                description=data["description"]
            )

        card_update = update(Card).where(
            Card.id == data["card_id"]).values(
            balance=Card.balance - amount
        )

        await session.execute(stmt)
        await session.execute(card_update)
        await session.commit()

        query = select(Expense).where(Expense.tg_id == callback.from_user.id)
        result = await session.execute(query)
        current_expense = result.scalars().all()[-1]

    await state.clear()
    await callback.message.delete()
    await callback.message.answer(
        text=TRANSACTIONS_LEXICON["expense_transactions"]["expense_is_create"],
        reply_markup=create_expense_is_create_keyboard(current_expense.id)
    )


@router.callback_query(F.data == "edit_ex_category", StateFilter(ShowExpensesState.show_expenses))
async def change_expense_category(callback: CallbackQuery, state: FSMContext):
    async with async_session() as session:
        query = select(ExpenseCategory).where(ExpenseCategory.tg_id == callback.from_user.id)
        result = await session.execute(query)
        categories = result.scalars().all()

    buttons = [unpack_ex_category_model(category) for category in categories]

    await state.set_state(ShowExpensesState.set_new_category)
    await callback.message.edit_text(
        text=TRANSACTIONS_LEXICON["edit_expense"]["new_category"],
        reply_markup=create_select_category_keyboard(buttons, edit=True)
    )


@router.callback_query(F.data[:12] == "set_category", StateFilter(ShowExpensesState.set_new_category))
async def set_new_category(callback: CallbackQuery, state: FSMContext):
    category_id = int(callback.data[12:])
    data = await state.get_data()
    expense_id = data["expense"]["id"]
    async with (async_session() as session):
        stmt = update(Expense).where(Expense.id == expense_id).values(category_id=category_id)
        await session.execute(stmt)
        await session.commit()

    await callback.message.delete()
    await state.set_state(ShowExpensesState.show_expenses)
    await callback.message.answer(
        text=TRANSACTIONS_LEXICON["edit_expense"]["category_is_update"],
        reply_markup=create_expense_is_create_keyboard(expense_id)
    )


@router.callback_query(F.data == "edit_ex_card", StateFilter(ShowExpensesState.show_expenses))
async def change_expense_card(callback: CallbackQuery, state: FSMContext):
    async with async_session() as session:
        query = select(Card).where(Card.tg_id == callback.from_user.id)
        result = await session.execute(query)
        cards = result.scalars().all()
        buttons = [card for card in cards]

    await state.set_state(ShowExpensesState.set_new_card)
    await callback.message.edit_text(
        text=TRANSACTIONS_LEXICON["edit_expense"]["new_card"],
        reply_markup=create_cards_keyboard(buttons, edit=True)
    )


@router.callback_query(F.data[:8] == "set_card", StateFilter(ShowExpensesState.set_new_card))
async def set_new_card(callback: CallbackQuery, state: FSMContext):
    card_id = int(callback.data[8:])
    data = await state.get_data()
    expense = data["expense"]

    async with (async_session() as session):
        query = select(Card).where(Card.id == expense["card_id"])
        result = await session.execute(query)
        card = result.scalars().first()

        new_balance = card.balance + expense["amount"]
        stmt = update(Card).where(Card.id == card.id).values(balance=new_balance)
        await session.execute(stmt)
        await session.commit()

        stmt = update(Expense).where(Expense.id == expense["id"]).values(card_id=card_id)
        await session.execute(stmt)
        await session.commit()

        query = select(Card).where(Card.id == card_id)
        result = await session.execute(query)
        card = result.scalars().first()

        new_balance = card.balance - expense["amount"]
        stmt = update(Card).where(Card.id == card.id).values(balance=new_balance)
        await session.execute(stmt)
        await session.commit()

    await callback.message.delete()
    await state.set_state(ShowExpensesState.show_expenses)
    await callback.message.answer(
        text=TRANSACTIONS_LEXICON["edit_expense"]["card_is_update"],
        reply_markup=create_expense_is_create_keyboard(expense["id"])
    )


@router.callback_query(F.data == "edit_ex_amount", StateFilter(ShowExpensesState.show_expenses))
async def edit_expense_amount(callback: CallbackQuery, state: FSMContext):
    await callback.message.edit_text(
        text=TRANSACTIONS_LEXICON["edit_expense"]["new_amount"],
        reply_markup=create_exit_transaction_edit_keyboard()
    )
    await state.set_state(ShowExpensesState.set_new_amount)


@router.message(StateFilter(ShowExpensesState.set_new_amount))
async def set_new_expense_amount(message: Message, state: FSMContext):
    try:
        amount = float(message.text.strip())

        if amount > 0:
            data = await state.get_data()
            expense = data["expense"]
            card = data["card"]

            d = amount - expense["amount"]
            new_balance = card["balance"] - d
            card["balance"] = new_balance
            async with (async_session() as session):
                stmt = update(Expense).where(Expense.id == expense["id"]).values(amount=amount)
                await session.execute(stmt)
                await session.commit()

                stmt = update(Card).where(Card.id == card["id"]).values(balance=new_balance)
                await session.execute(stmt)
                await session.commit()

            await state.set_state(ShowExpensesState.show_expenses)
            await message.answer(
                text=TRANSACTIONS_LEXICON["edit_expense"]["amount_is_update"],
                reply_markup=create_expense_is_create_keyboard(expense["id"])
            )
        else:
            await message.answer(
                text=TRANSACTIONS_LEXICON["expense_transactions"]["incorrect_amount"],
                reply_markup=create_exit_transaction_edit_keyboard()
            )

    except ValueError:
        await message.answer(
            text=TRANSACTIONS_LEXICON["expense_transactions"]["incorrect_amount"],
            reply_markup=create_exit_transaction_edit_keyboard()
        )


@router.callback_query(F.data == "edit_ex_date", StateFilter(ShowExpensesState.show_expenses))
async def edit_expense_date(callback: CallbackQuery, state: FSMContext):
    await callback.message.edit_text(
        text=TRANSACTIONS_LEXICON["edit_expense"]["new_date"],
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
            stmt = update(Expense).where(Expense.id == expense["id"]).values(date=date)
            await session.execute(stmt)
            await session.commit()

        await state.set_state(ShowExpensesState.show_expenses)
        await message.answer(
            text=TRANSACTIONS_LEXICON["edit_expense"]["date_is_update"],
            reply_markup=create_expense_is_create_keyboard(expense["id"])
        )

    else:
        await message.answer(
            text=TRANSACTIONS_LEXICON["incorrect_date"],
            reply_markup=create_exit_transaction_edit_keyboard()
        )


@router.callback_query(F.data == "edit_ex_description", StateFilter(ShowExpensesState.show_expenses))
async def edit_expense_description(callback: CallbackQuery, state: FSMContext):
    await callback.message.edit_text(
        text=TRANSACTIONS_LEXICON["edit_expense"]["new_description"],
        reply_markup=create_exit_transaction_edit_keyboard()
    )
    await state.set_state(ShowExpensesState.set_new_description)


@router.message(StateFilter(ShowExpensesState.set_new_description))
async def set_new_expense_description(message: Message, state: FSMContext):
    description = message.text.strip()
    if isValidDescription(description):
        data = await state.get_data()
        expense = data["expense"]
        async with async_session() as session:
            stmt = update(Expense).where(Expense.id == expense["id"]).values(description=description)
            await session.execute(stmt)
            await session.commit()

        await state.set_state(ShowExpensesState.show_expenses)
        await message.answer(
            text=TRANSACTIONS_LEXICON["edit_expense"]["description_is_update"],
            reply_markup=create_expense_is_create_keyboard(expense["id"])
        )

    else:
        await message.answer(
            text=TRANSACTIONS_LEXICON["incorrect_description"],
            reply_markup=create_exit_transaction_edit_keyboard()
        )


@router.callback_query(F.data == "del_ex", StateFilter(ShowExpensesState.show_expenses))
async def del_expense(callback: CallbackQuery, state: FSMContext):
    await state.set_state(ShowExpensesState.del_expense)
    await callback.message.edit_text(
        text=TRANSACTIONS_LEXICON["edit_expense"]["confirm_del"],
        reply_markup=create_yes_no_delete_keyboard()
    )


@router.callback_query(F.data == "NO", StateFilter(ShowExpensesState.del_expense))
async def no_delete_card(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    expense = data["expense"]

    await state.clear()
    await callback.message.edit_text(
        text=TRANSACTIONS_LEXICON["edit_expense"]["cancel_del"],
        reply_markup=create_expense_is_create_keyboard(expense.id)
    )


@router.callback_query(F.data == "YES", StateFilter(ShowExpensesState.del_expense))
async def yes_delete_card(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    expense = data["expense"]

    async with async_session() as session:
        to_delete_expense = delete(Expense).where(Expense.id == expense["id"])
        await session.execute(to_delete_expense)
        await session.commit()

        amount = expense["amount"]
        stmt = select(Card).where(Card.id == expense["card_id"])
        result = await session.execute(stmt)
        card = result.scalars().first()
        new_balance = card.balance + amount

        to_update_card = update(Card).where(Card.id == card.id).values(balance=new_balance)
        await session.execute(to_update_card)
        await session.commit()

    await state.clear()
    await callback.message.delete()
    await callback.message.answer(TRANSACTIONS_LEXICON["edit_expense"]["is_delete"])
