from datetime import datetime

from aiogram import F, Router
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.state import default_state

from sqlalchemy import select, update

from src.card_operations.keyboards import create_cards_keyboard
from src.database.database import async_session
from src.database.models import Income, IncomeCategory, Card
from src.services.services import pagination, isValidDate
from src.services.states import ShowIncomesState, AddCategoryState
from src.transactions.lexicon import LEXICON as USER_LEXICON, LEXICON_COMMANDS as USER_LEXICON_COMMANDS, \
    print_income_info
from src.transactions.transactions_keyboards import create_incomes_keyboard, create_transaction_edit_keyboard, \
    create_select_category_keyboard, create_exit_transaction_edit_keyboard

router = Router()


@router.message(Command(commands="incomes"), StateFilter(default_state))
async def get_incomes(message: Message, state: FSMContext):
    async with async_session() as session:
        query = select(Income).where(Income.tg_id == message.from_user.id)
        result = await session.execute(query)
        incomes = result.scalars().all()

    if incomes:
        pages = len(incomes) // 9 + (len(incomes) % 9 != 0)
        buttons = [income for income in incomes]
        buttons.sort(key=lambda x: x.date, reverse=True)

        await state.set_state(ShowIncomesState.show_incomes)
        await state.update_data(
            page=1,
            pages=pages,
            incomes=buttons
        )

        cur_buttons = pagination(buttons, 0, "next")

        await message.answer(
            text=f'{USER_LEXICON["income"]["incomes_list"]} Страница 1 / {pages}',
            reply_markup=create_incomes_keyboard(cur_buttons)
        )
    else:
        await message.answer(USER_LEXICON["income_transactions"]["no_incomes"])


@router.callback_query(F.data == "next_page", StateFilter(ShowIncomesState.show_incomes))
async def goto_next_incomes_page(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    cur_page = data["page"]
    incomes = data["incomes"]
    buttons = pagination(incomes, cur_page, "next")
    pages = data["pages"]

    if cur_page > 0 and buttons:
        await callback.message.edit_text(
            text=f'{USER_LEXICON["income"]["incomes_list"]} Страница {cur_page + 1} / {pages}',
            reply_markup=create_incomes_keyboard(buttons)
        )

        await state.update_data(page=cur_page + 1)


@router.callback_query(F.data == "back_page", StateFilter(ShowIncomesState.show_incomes))
async def goto_back_incomes_page(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    cur_page = data["page"]
    incomes = data["incomes"]
    buttons = pagination(incomes, cur_page, "back")
    pages = data["pages"]

    if cur_page > 0 and buttons:
        await callback.message.edit_text(
            text=f'{USER_LEXICON["income"]["incomes_list"]} Страница {cur_page - 1} / {pages}',
            reply_markup=create_incomes_keyboard(buttons)
        )

        await state.update_data(page=cur_page - 1)


@router.callback_query(F.data[:10] == "get_income", StateFilter(ShowIncomesState.show_incomes))
async def get_income_info(callback: CallbackQuery, state: FSMContext):
    income_id = int(callback.data[10:])
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

    description = income.description if income.description else USER_LEXICON["income_info"]["no_description"]
    await state.update_data(
        income=income,
        card=card,
        income_category=income_category
    )
    await callback.message.edit_text(
        text=print_income_info(income, income_category, card, description),
        reply_markup=create_transaction_edit_keyboard(transaction_type="in")
    )


@router.message(Command(commands="add_income"), StateFilter(default_state))
async def select_income_type(message: Message, state: FSMContext):
    async with async_session() as session:
        query = select(IncomeCategory).where(IncomeCategory.tg_id == message.from_user.id)
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
                category_type=Income,
                category_type_str="income"
            )

        else:
            await message.answer(USER_LEXICON["income_transactions"]["no_categories"])


@router.callback_query(F.data == "edit_in_category", StateFilter(ShowIncomesState.show_incomes))
async def change_income_category(callback: CallbackQuery, state: FSMContext):
    async with async_session() as session:
        query = select(IncomeCategory).where(IncomeCategory.tg_id == callback.from_user.id)
        result = await session.execute(query)
        categories = result.scalars().all()

    buttons = [category for category in categories]

    await state.set_state(ShowIncomesState.set_new_category)
    await callback.message.edit_text(
        text=USER_LEXICON["edit_income"]["new_category"],
        reply_markup=create_select_category_keyboard(buttons, edit=True)
    )


@router.callback_query(F.data[:12] == "set_category", StateFilter(ShowIncomesState.set_new_category))
async def set_new_category(callback: CallbackQuery, state: FSMContext):
    category_id = int(callback.data[12:])
    data = await state.get_data()
    income_id = data["income"].id
    async with (async_session() as session):
        stmt = update(Income).where(Income.id == income_id).values(category_id=category_id)
        await session.execute(stmt)
        await session.commit()

    await callback.message.delete()
    await state.set_state(ShowIncomesState.show_incomes)
    await callback.message.answer(USER_LEXICON["edit_income"]["category_is_update"])


@router.callback_query(F.data == "edit_in_card", StateFilter(ShowIncomesState.show_incomes))
async def change_income_card(callback: CallbackQuery, state: FSMContext):
    async with async_session() as session:
        query = select(Card).where(Card.tg_id == callback.from_user.id)
        result = await session.execute(query)
        cards = result.scalars().all()
        buttons = [card for card in cards]

    await state.set_state(ShowIncomesState.set_new_card)
    await callback.message.edit_text(
        text=USER_LEXICON["edit_income"]["new_card"],
        reply_markup=create_cards_keyboard(buttons, edit=True)
    )


@router.callback_query(F.data[:8] == "set_card", StateFilter(ShowIncomesState.set_new_card))
async def set_new_card(callback: CallbackQuery, state: FSMContext):
    card_id = int(callback.data[8:])
    data = await state.get_data()
    income = data["income"]

    async with (async_session() as session):
        query = select(Card).where(Card.id == income.card_id)
        result = await session.execute(query)
        card = result.scalars().first()

        new_balance = card.balance - income.amount
        stmt = update(Card).where(Card.id == card.id).values(balance=new_balance)
        await session.execute(stmt)
        await session.commit()

        stmt = update(Income).where(Income.id == income.id).values(card_id=card_id)
        await session.execute(stmt)
        await session.commit()

        query = select(Card).where(Card.id == card_id)
        result = await session.execute(query)
        card = result.scalars().first()

        new_balance = card.balance + income.amount
        stmt = update(Card).where(Card.id == card.id).values(balance=new_balance)
        await session.execute(stmt)
        await session.commit()

    await callback.message.delete()
    await state.set_state(ShowIncomesState.show_incomes)
    await callback.message.answer(USER_LEXICON["edit_income"]["card_is_update"])


@router.callback_query(F.data == "edit_in_amount", StateFilter(ShowIncomesState.show_incomes))
async def edit_income_amount(callback: CallbackQuery, state: FSMContext):
    await callback.message.edit_text(
        text=USER_LEXICON["edit_income"]["new_amount"],
        reply_markup=create_exit_transaction_edit_keyboard()
    )
    await state.set_state(ShowIncomesState.set_new_amount)


@router.message(StateFilter(ShowIncomesState.set_new_amount))
async def set_new_income_amount(message: Message, state: FSMContext):
    try:
        amount = float(message.text.strip())
        data = await state.get_data()
        income = data["income"]
        card = data["card"]

        d = amount - income.amount
        new_balance = card.balance + d
        card.balance = new_balance
        async with (async_session() as session):
            stmt = update(Income).where(Income.id == income.id).values(amount=amount)
            await session.execute(stmt)
            await session.commit()

            stmt = update(Card).where(Card.id == card.id).values(balance=new_balance)
            await session.execute(stmt)
            await session.commit()

        await state.set_state(ShowIncomesState.show_incomes)
        await message.answer(USER_LEXICON["edit_income"]["amount_is_update"])

    except ValueError:
        await message.answer(
            text=USER_LEXICON["income_transactions"]["incorrect_amount"],
            reply_markup=create_exit_transaction_edit_keyboard()
        )


@router.callback_query(F.data == "edit_in_date", StateFilter(ShowIncomesState.show_incomes))
async def edit_income_date(callback: CallbackQuery, state: FSMContext):
    await callback.message.edit_text(
        text=USER_LEXICON["edit_income"]["new_date"],
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
            stmt = update(Income).where(Income.id == income.id).values(date=date)
            await session.execute(stmt)
            await session.commit()

        await state.set_state(ShowIncomesState.show_incomes)
        await message.answer(USER_LEXICON["edit_income"]["date_is_update"])

    else:
        await message.answer(
            text=USER_LEXICON["incorrect_date"],
            reply_markup=create_exit_transaction_edit_keyboard()
        )


@router.callback_query(F.data == "edit_in_description", StateFilter(ShowIncomesState.show_incomes))
async def edit_income_description(callback: CallbackQuery, state: FSMContext):
    await callback.message.edit_text(
        text=USER_LEXICON["edit_income"]["new_description"],
        reply_markup=create_exit_transaction_edit_keyboard()
    )
    await state.set_state(ShowIncomesState.set_new_description)


@router.message(StateFilter(ShowIncomesState.set_new_description))
async def set_new_income_description(message: Message, state: FSMContext):
    data = await state.get_data()
    income = data["income"]
    async with async_session() as session:
        stmt = update(Income).where(Income.id == income.id).values(description=message.text)
        await session.execute(stmt)
        await session.commit()

    await state.set_state(ShowIncomesState.show_incomes)
    await message.answer(USER_LEXICON["edit_income"]["description_is_update"])

# Добавить возможность добавления даты в транзакцию при создании
