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
from src.database.models import Income, IncomeCategory, Card
from src.services.services import pagination, isValidDate, isValidDescription, unpack_income_model, unpack_card_model, \
    unpack_in_category_model
from src.services.settings import LIMITS
from src.services.states import ShowIncomesState, AddIncomeState
from src.transactions.categories_keyboards import create_add_new_in_category_keyboard
from src.transactions.lexicon import LEXICON as TRANSACTIONS_LEXICON, \
    LEXICON_COMMANDS as TRANSACTIONS_LEXICON_COMMANDS, print_income_info
from src.transactions.transactions_keyboards import create_incomes_keyboard, create_transaction_edit_keyboard, \
    create_select_category_keyboard, create_exit_transaction_edit_keyboard, create_select_card_keyboard, \
    create_yes_no_add_keyboard, create_done_keyboard, create_income_is_create_keyboard, create_add_new_income_keyboard

router = Router()


@router.message(Command(commands="incomes"), StateFilter(default_state))
async def get_incomes(message: Message, state: FSMContext):
    async with async_session() as session:
        query = select(Income).where(Income.tg_id == message.from_user.id)
        result = await session.execute(query)
        incomes = result.scalars().all()

    if incomes:
        keyboard_limit = LIMITS["max_elements_in_keyboard"]
        pages = len(incomes) // keyboard_limit + (len(incomes) % keyboard_limit != 0)
        buttons = [unpack_income_model(income) for income in incomes]
        buttons.sort(key=lambda x: datetime.strptime(x["date"], '%Y-%m-%d').date(), reverse=True)

        await state.set_state(ShowIncomesState.show_incomes)
        await state.update_data(
            page=0,
            pages=pages,
            incomes=buttons
        )

        cur_buttons = pagination(buttons, 0)

        await message.answer(
            text=f'{TRANSACTIONS_LEXICON["income"]["incomes_list"]} Страница 1 / {pages}',
            reply_markup=create_incomes_keyboard(cur_buttons)
        )

    else:
        await state.clear()
        await message.answer(
            text=TRANSACTIONS_LEXICON["income_transactions"]["no_incomes"],
            reply_markup=create_add_new_income_keyboard()
        )


@router.callback_query(F.data == "show_incomes_list", StateFilter(default_state))
@router.callback_query(F.data == "show_incomes_list", StateFilter(ShowIncomesState.show_incomes))
async def get_incomes(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    try:
        incomes = data["incomes"]
    except KeyError:
        async with async_session() as session:
            query = select(Income).where(Income.tg_id == callback.from_user.id)
            result = await session.execute(query)
            incomes = result.scalars().all()

    if incomes:
        keyboard_limit = LIMITS["max_elements_in_keyboard"]
        pages = len(incomes) // keyboard_limit + (len(incomes) % keyboard_limit != 0)
        buttons = [unpack_income_model(income) for income in incomes]
        buttons.sort(key=lambda x: datetime.strptime(x["date"], '%Y-%m-%d').date(), reverse=True)

        await state.set_state(ShowIncomesState.show_incomes)
        await state.update_data(
            page=0,
            pages=pages,
            incomes=buttons
        )

        cur_buttons = pagination(buttons, 0)

        await callback.message.edit_text(
            text=f'{TRANSACTIONS_LEXICON["income"]["incomes_list"]} Страница 1 / {pages}',
            reply_markup=create_incomes_keyboard(cur_buttons)
        )

    else:
        await state.clear()
        await callback.message.edit_text(
            text=TRANSACTIONS_LEXICON["income_transactions"]["no_incomes"],
            reply_markup=create_add_new_income_keyboard()
        )


@router.callback_query(F.data == "next_page", StateFilter(ShowIncomesState.show_incomes))
async def goto_next_incomes_page(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    cur_page = data["page"] + 1
    incomes = data["incomes"]
    buttons = pagination(incomes, cur_page)
    pages = data["pages"]

    if 0 <= cur_page < pages and buttons:
        await callback.message.edit_text(
            text=f'{TRANSACTIONS_LEXICON["income"]["incomes_list"]} Страница {cur_page + 1} / {pages}',
            reply_markup=create_incomes_keyboard(buttons)
        )

        await state.update_data(page=cur_page)


@router.callback_query(F.data == "back_page", StateFilter(ShowIncomesState.show_incomes))
async def goto_back_incomes_page(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    cur_page = data["page"] - 1
    incomes = data["incomes"]
    buttons = pagination(incomes, cur_page)
    pages = data["pages"]

    if 0 <= cur_page < pages and buttons:
        await callback.message.edit_text(
            text=f'{TRANSACTIONS_LEXICON["income"]["incomes_list"]} Страница {cur_page + 1} / {pages}',
            reply_markup=create_incomes_keyboard(buttons)
        )

        await state.update_data(page=cur_page)


@router.callback_query(F.data[:10] == "get_income", StateFilter(default_state))
@router.callback_query(F.data[:10] == "get_income", StateFilter(ShowIncomesState.show_incomes))
async def get_income_info(callback: CallbackQuery, state: FSMContext):
    income_id = int(callback.data[10:])
    await state.set_state(ShowIncomesState.show_incomes)

    async with async_session() as session:
        query = select(Income).where(Income.id == income_id)
        result = await session.execute(query)
        income = result.scalars().first()

        query = select(IncomeCategory).where(IncomeCategory.id == income.category_id)
        result = await session.execute(query)
        income_category = result.scalars().first()

        query = select(Card).where(Card.id == income.card_id)
        result = await session.execute(query)
        card = result.scalars().first()

    description = income.description if income.description else TRANSACTIONS_LEXICON["income_info"]["no_description"]
    await state.update_data(
        income=unpack_income_model(income),
        card=unpack_card_model(card),
        income_category=unpack_in_category_model(income_category)
    )
    await callback.message.edit_text(
        text=print_income_info(income, income_category, card, description),
        reply_markup=create_transaction_edit_keyboard(transaction_type="in")
    )


@router.message(Command(commands="add_income"), StateFilter(default_state))
async def add_income(message: Message, state: FSMContext):
    async with async_session() as session:
        query = select(IncomeCategory).where(IncomeCategory.tg_id == message.from_user.id)
        result = await session.execute(query)
        categories = result.scalars().all()
        if categories:
            keyboard_limit = LIMITS["max_elements_in_keyboard"]
            pages = len(categories) // keyboard_limit + (len(categories) % keyboard_limit != 0)
            buttons = [unpack_in_category_model(category) for category in categories]

            await state.set_state(AddIncomeState.select_category)
            await state.update_data(
                page=0,
                pages=pages,
                in_categories=buttons,
                category_type_str="income"
            )

            cur_buttons = pagination(buttons, 0)
            await message.answer(
                text=f"{TRANSACTIONS_LEXICON_COMMANDS[message.text]} Страница 1 / {pages}",
                reply_markup=create_select_category_keyboard(cur_buttons)
            )

        else:
            await message.answer(
                text=TRANSACTIONS_LEXICON["income_transactions"]["no_categories"],
                reply_markup=create_add_new_in_category_keyboard()
            )


@router.callback_query(F.data == "start_create_income", StateFilter(default_state))
async def add_income(callback: CallbackQuery, state: FSMContext):
    async with async_session() as session:
        query = select(IncomeCategory).where(IncomeCategory.tg_id == callback.from_user.id)
        result = await session.execute(query)
        categories = result.scalars().all()
        if categories:
            keyboard_limit = LIMITS["max_elements_in_keyboard"]
            pages = len(categories) // keyboard_limit + (len(categories) % keyboard_limit != 0)
            buttons = [unpack_in_category_model(category) for category in categories]

            await state.set_state(AddIncomeState.select_category)
            await state.update_data(
                page=0,
                pages=pages,
                in_categories=buttons,
                category_type_str="income"
            )

            cur_buttons = pagination(buttons, 0)
            await callback.message.edit_text(
                text=f"{TRANSACTIONS_LEXICON_COMMANDS['/add_income']} Страница 1 / {pages}",
                reply_markup=create_select_category_keyboard(cur_buttons)
            )

        else:
            await callback.message.edit_text(
                text=TRANSACTIONS_LEXICON["income_transactions"]["no_categories"],
                reply_markup=create_add_new_in_category_keyboard()
            )


@router.callback_query(F.data == "next_page", StateFilter(AddIncomeState.select_category))
async def goto_next_in_categories_page(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    cur_page = data["page"] + 1
    in_categories = data["in_categories"]
    buttons = pagination(in_categories, cur_page)
    pages = data["pages"]

    if 0 <= cur_page < pages and buttons:
        await callback.message.edit_text(
            text=f'{TRANSACTIONS_LEXICON_COMMANDS["/add_income"]} Страница {cur_page + 1} / {pages}',
            reply_markup=create_select_category_keyboard(buttons)
        )

        await state.update_data(page=cur_page)


@router.callback_query(F.data == "back_page", StateFilter(AddIncomeState.select_category))
async def goto_back_in_categories_page(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    cur_page = data["page"] - 1
    in_categories = data["in_categories"]
    buttons = pagination(in_categories, cur_page)
    pages = data["pages"]

    if 0 <= cur_page < pages and buttons:
        await callback.message.edit_text(
            text=f'{TRANSACTIONS_LEXICON_COMMANDS["/add_income"]} Страница {cur_page + 1} / {pages}',
            reply_markup=create_select_category_keyboard(buttons)
        )

        await state.update_data(page=cur_page)


@router.callback_query(F.data[:11] == "select_card", StateFilter(AddIncomeState.select_category))
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
            await state.set_state(AddIncomeState.add_date)

        else:
            await state.clear()
            await callback.message.edit_text(
                text=TRANSACTIONS_LEXICON["no_cards"],
                reply_markup=create_add_new_card_keyboard()
            )


@router.callback_query(F.data[:8] == "add_date", StateFilter(AddIncomeState.add_date))
async def yes_no_add_card(callback: CallbackQuery, state: FSMContext):
    card_id = int(callback.data[8:])
    await state.update_data(card_id=card_id)
    await callback.message.edit_text(
        text=TRANSACTIONS_LEXICON["add_date"],
        reply_markup=create_yes_no_add_keyboard()
    )


@router.callback_query(F.data == "YES", StateFilter(AddIncomeState.add_date))
async def get_date(callback: CallbackQuery, state: FSMContext):
    await state.set_state(AddIncomeState.add_amount)
    await callback.message.edit_text(
        text=TRANSACTIONS_LEXICON["get_date"],
        reply_markup=create_exit_keyboard()
    )


@router.callback_query(F.data == "NO", StateFilter(AddIncomeState.add_date))
async def no_add_date(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    category_type_str = data["category_type_str"]
    transactions = "income_transactions" if category_type_str == "income" else "expense_transactions"
    await callback.message.edit_text(
        text=TRANSACTIONS_LEXICON[transactions]["amount"],
        reply_markup=create_exit_keyboard()
    )
    await state.set_state(AddIncomeState.add_description)


@router.message(StateFilter(AddIncomeState.add_amount))
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
        await state.set_state(AddIncomeState.add_description)

    else:
        await message.answer(
            text=TRANSACTIONS_LEXICON["incorrect_date"],
            reply_markup=create_exit_transaction_edit_keyboard()
        )


@router.message(StateFilter(AddIncomeState.add_description))
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
            await state.set_state(AddIncomeState.get_description)

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


@router.callback_query(F.data == "YES", StateFilter(AddIncomeState.get_description))
async def get_description_from_user(callback: CallbackQuery, state: FSMContext):
    await callback.message.delete()
    await callback.message.answer(TRANSACTIONS_LEXICON["get_description"])
    await state.set_state(AddIncomeState.set_description)


@router.callback_query(F.data == "NO", StateFilter(AddIncomeState.get_description))
async def no_description(callback: CallbackQuery, state: FSMContext):
    await state.update_data(description="")
    await state.set_state(AddIncomeState.set_data)
    await callback.message.edit_text(
        text=TRANSACTIONS_LEXICON["commit_transaction"],
        reply_markup=create_done_keyboard()
    )


@router.message(StateFilter(AddIncomeState.set_description))
async def set_description(message: Message, state: FSMContext):
    description = message.text.strip()
    if isValidDescription(description):
        await state.update_data(description=description)
        await state.set_state(AddIncomeState.set_data)
        await message.answer(
            text=TRANSACTIONS_LEXICON["set_description"],
            reply_markup=create_done_keyboard()
        )

    else:
        await message.answer(
            text=TRANSACTIONS_LEXICON["incorrect_description"],
            reply_markup=create_exit_keyboard()
        )


@router.callback_query(F.data == "commit_transaction", StateFilter(AddIncomeState.set_data))
async def set_transaction(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    amount = data["amount"]
    async with async_session() as session:
        if "date" in data:
            date = datetime.strptime(data["date"], '%d.%m.%Y').date()
            stmt = insert(Income).values(
                tg_id=callback.from_user.id,
                category_id=data["category_id"],
                card_id=data["card_id"],
                date=date,
                amount=amount,
                description=data["description"]
            )
        else:
            stmt = insert(Income).values(
                tg_id=callback.from_user.id,
                category_id=data["category_id"],
                card_id=data["card_id"],
                amount=amount,
                description=data["description"]
            )

        card_update = update(Card).where(
            Card.id == data["card_id"]).values(
            balance=Card.balance + amount
        )

        await session.execute(stmt)
        await session.execute(card_update)
        await session.commit()

        query = select(Income).where(Income.tg_id == callback.from_user.id)
        result = await session.execute(query)
        current_income = result.scalars().all()[-1]

    await state.clear()
    await callback.message.delete()
    await callback.message.answer(
        text=TRANSACTIONS_LEXICON["income_transactions"]["income_is_create"],
        reply_markup=create_income_is_create_keyboard(current_income.id)
    )


@router.callback_query(F.data == "edit_in_category", StateFilter(ShowIncomesState.show_incomes))
async def change_income_category(callback: CallbackQuery, state: FSMContext):
    async with async_session() as session:
        query = select(IncomeCategory).where(IncomeCategory.tg_id == callback.from_user.id)
        result = await session.execute(query)
        categories = result.scalars().all()

    buttons = [unpack_in_category_model(category) for category in categories]

    await state.set_state(ShowIncomesState.set_new_category)
    await callback.message.edit_text(
        text=TRANSACTIONS_LEXICON["edit_income"]["new_category"],
        reply_markup=create_select_category_keyboard(buttons, edit=True)
    )


@router.callback_query(F.data[:12] == "set_category", StateFilter(ShowIncomesState.set_new_category))
async def set_new_category(callback: CallbackQuery, state: FSMContext):
    category_id = int(callback.data[12:])
    data = await state.get_data()
    income_id = data["income"]["id"]
    async with (async_session() as session):
        stmt = update(Income).where(Income.id == income_id).values(category_id=category_id)
        await session.execute(stmt)
        await session.commit()

    await callback.message.delete()
    await state.set_state(ShowIncomesState.show_incomes)
    await callback.message.answer(
        text=TRANSACTIONS_LEXICON["edit_income"]["category_is_update"],
        reply_markup=create_income_is_create_keyboard(income_id)
    )


@router.callback_query(F.data == "edit_in_card", StateFilter(ShowIncomesState.show_incomes))
async def change_income_card(callback: CallbackQuery, state: FSMContext):
    async with async_session() as session:
        query = select(Card).where(Card.tg_id == callback.from_user.id)
        result = await session.execute(query)
        cards = result.scalars().all()
        buttons = [card for card in cards]

    await state.set_state(ShowIncomesState.set_new_card)
    await callback.message.edit_text(
        text=TRANSACTIONS_LEXICON["edit_income"]["new_card"],
        reply_markup=create_cards_keyboard(buttons, edit=True)
    )


@router.callback_query(F.data[:8] == "set_card", StateFilter(ShowIncomesState.set_new_card))
async def set_new_card(callback: CallbackQuery, state: FSMContext):
    card_id = int(callback.data[8:])
    data = await state.get_data()
    income = data["income"]

    async with (async_session() as session):
        query = select(Card).where(Card.id == income["card_id"])
        result = await session.execute(query)
        card = result.scalars().first()

        new_balance = card.balance - income["amount"]
        stmt = update(Card).where(Card.id == card.id).values(balance=new_balance)
        await session.execute(stmt)
        await session.commit()

        stmt = update(Income).where(Income.id == income["id"]).values(card_id=card_id)
        await session.execute(stmt)
        await session.commit()

        query = select(Card).where(Card.id == card_id)
        result = await session.execute(query)
        card = result.scalars().first()

        new_balance = card.balance + income["amount"]
        stmt = update(Card).where(Card.id == card.id).values(balance=new_balance)
        await session.execute(stmt)
        await session.commit()

    await callback.message.delete()
    await state.set_state(ShowIncomesState.show_incomes)
    await callback.message.answer(
        text=TRANSACTIONS_LEXICON["edit_income"]["card_is_update"],
        reply_markup=create_income_is_create_keyboard(income["id"])
    )


@router.callback_query(F.data == "edit_in_amount", StateFilter(ShowIncomesState.show_incomes))
async def edit_income_amount(callback: CallbackQuery, state: FSMContext):
    await callback.message.edit_text(
        text=TRANSACTIONS_LEXICON["edit_income"]["new_amount"],
        reply_markup=create_exit_transaction_edit_keyboard()
    )
    await state.set_state(ShowIncomesState.set_new_amount)


@router.message(StateFilter(ShowIncomesState.set_new_amount))
async def set_new_income_amount(message: Message, state: FSMContext):
    try:
        amount = float(message.text.strip())

        if amount > 0:
            data = await state.get_data()
            income = data["income"]
            card = data["card"]

            d = amount - income["amount"]
            new_balance = card["balance"] + d
            card["balance"] = new_balance
            async with (async_session() as session):
                stmt = update(Income).where(Income.id == income["id"]).values(amount=amount)
                await session.execute(stmt)
                await session.commit()

                stmt = update(Card).where(Card.id == card["id"]).values(balance=new_balance)
                await session.execute(stmt)
                await session.commit()

            await state.set_state(ShowIncomesState.show_incomes)
            await message.answer(
                text=TRANSACTIONS_LEXICON["edit_income"]["amount_is_update"],
                reply_markup=create_income_is_create_keyboard(income["id"])
            )
        else:
            await message.answer(
                text=TRANSACTIONS_LEXICON["income_transactions"]["incorrect_amount"],
                reply_markup=create_exit_transaction_edit_keyboard()
            )

    except ValueError:
        await message.answer(
            text=TRANSACTIONS_LEXICON["income_transactions"]["incorrect_amount"],
            reply_markup=create_exit_transaction_edit_keyboard()
        )


@router.callback_query(F.data == "edit_in_date", StateFilter(ShowIncomesState.show_incomes))
async def edit_income_date(callback: CallbackQuery, state: FSMContext):
    await callback.message.edit_text(
        text=TRANSACTIONS_LEXICON["edit_income"]["new_date"],
        reply_markup=create_exit_transaction_edit_keyboard()
    )
    await state.set_state(ShowIncomesState.set_new_date)


@router.message(StateFilter(ShowIncomesState.set_new_date))
async def set_new_income_date(message: Message, state: FSMContext):
    date = message.text.strip()
    if isValidDate(date):
        date = datetime.strptime(date, '%d.%m.%Y').date()
        data = await state.get_data()
        income = data["income"]
        async with async_session() as session:
            stmt = update(Income).where(Income.id == income["id"]).values(date=date)
            await session.execute(stmt)
            await session.commit()

        await state.set_state(ShowIncomesState.show_incomes)
        await message.answer(
            text=TRANSACTIONS_LEXICON["edit_income"]["date_is_update"],
            reply_markup=create_income_is_create_keyboard(income["id"])
        )

    else:
        await message.answer(
            text=TRANSACTIONS_LEXICON["incorrect_date"],
            reply_markup=create_exit_transaction_edit_keyboard()
        )


@router.callback_query(F.data == "edit_in_description", StateFilter(ShowIncomesState.show_incomes))
async def edit_income_description(callback: CallbackQuery, state: FSMContext):
    await callback.message.edit_text(
        text=TRANSACTIONS_LEXICON["edit_income"]["new_description"],
        reply_markup=create_exit_transaction_edit_keyboard()
    )
    await state.set_state(ShowIncomesState.set_new_description)


@router.message(StateFilter(ShowIncomesState.set_new_description))
async def set_new_income_description(message: Message, state: FSMContext):
    description = message.text.strip()
    if isValidDescription(description):
        data = await state.get_data()
        income = data["income"]
        async with async_session() as session:
            stmt = update(Income).where(Income.id == income["id"]).values(description=description)
            await session.execute(stmt)
            await session.commit()

        await state.set_state(ShowIncomesState.show_incomes)
        await message.answer(
            text=TRANSACTIONS_LEXICON["edit_income"]["description_is_update"],
            reply_markup=create_income_is_create_keyboard(income["id"])
        )

    else:
        await message.answer(
            text=TRANSACTIONS_LEXICON["incorrect_description"],
            reply_markup=create_exit_transaction_edit_keyboard()
        )


@router.callback_query(F.data == "del_in", StateFilter(ShowIncomesState.show_incomes))
async def del_income(callback: CallbackQuery, state: FSMContext):
    await state.set_state(ShowIncomesState.del_income)
    await callback.message.edit_text(
        text=TRANSACTIONS_LEXICON["edit_income"]["confirm_del"],
        reply_markup=create_yes_no_delete_keyboard()
    )


@router.callback_query(F.data == "NO", StateFilter(ShowIncomesState.del_income))
async def no_delete_card(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    income = data["income"]

    await state.clear()
    await callback.message.edit_text(
        text=TRANSACTIONS_LEXICON["edit_income"]["cancel_del"],
        reply_markup=create_income_is_create_keyboard(income.id)
    )


@router.callback_query(F.data == "YES", StateFilter(ShowIncomesState.del_income))
async def yes_delete_card(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    income = data["income"]

    async with async_session() as session:
        to_delete_income = delete(Income).where(Income.id == income["id"])
        await session.execute(to_delete_income)
        await session.commit()

        amount = income["amount"]
        stmt = select(Card).where(Card.id == income["card_id"])
        result = await session.execute(stmt)
        card = result.scalars().first()
        new_balance = card.balance - amount

        to_update_card = update(Card).where(Card.id == card.id).values(balance=new_balance)
        await session.execute(to_update_card)
        await session.commit()

    await state.clear()
    await callback.message.delete()
    await callback.message.answer(TRANSACTIONS_LEXICON["edit_income"]["is_delete"])
