from aiogram import Router, F
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.state import default_state

from sqlalchemy import select, insert, delete, update

from src.database.database import async_session
from src.database.models import Card, Income, Expense
from src.services.services import pagination, isValidName

from src.services.states import AddCardState, UpdCardState, ShowCardState, ShowIncomesState, ShowExpensesState
from src.services.settings import LIMITS

from src.card_operations.lexicon import (
    CARD_OPERATIONS_LEXICON as CARD_OPERATIONS_LEXICON,
    LEXICON_COMMANDS as CARD_OPERATIONS_LEXICON_COMMANDS,
    print_card_info
)
from src.transactions.lexicon import LEXICON as TRANSACTIONS_LEXICON

from src.card_operations.keyboards import (
    TypeKeyboard,
    create_exit_keyboard,
    create_cards_keyboard,
    create_card_actions_keyboard,
    create_card_update_keyboard,
    create_cancel_update_keyboard, create_card_is_create_keyboard, create_yes_no_delete_keyboard
)
from src.transactions.transactions_keyboards import create_incomes_keyboard, create_expenses_keyboard

router = Router()


@router.message(Command(commands="cards"), StateFilter(default_state))
async def get_cards(message: Message, state: FSMContext):
    async with async_session() as session:
        query = select(Card).where(Card.tg_id == message.from_user.id)
        result = await session.execute(query)
        cards = result.scalars().all()
        if cards:
            buttons = [card for card in cards]
            await message.answer(
                text=CARD_OPERATIONS_LEXICON_COMMANDS[message.text]["card_list"],
                reply_markup=create_cards_keyboard(buttons)
            )
            await state.set_state(ShowCardState.show_card)
        else:
            await state.clear()
            await message.answer(CARD_OPERATIONS_LEXICON_COMMANDS[message.text]["no_cards"])


@router.callback_query(F.data == "show_cards_list", StateFilter(default_state))
@router.callback_query(F.data == "show_cards_list", StateFilter(ShowCardState.show_card))
async def get_cards(callback: CallbackQuery, state: FSMContext):
    async with async_session() as session:
        query = select(Card).where(Card.tg_id == callback.from_user.id)
        result = await session.execute(query)
        cards = result.scalars().all()
        if cards:
            buttons = [card for card in cards]
            await callback.message.edit_text(
                text=CARD_OPERATIONS_LEXICON_COMMANDS["/cards"]["card_list"],
                reply_markup=create_cards_keyboard(buttons)
            )
            await state.set_state(ShowCardState.show_card)
        else:
            await state.clear()
            await callback.message.delete()
            await callback.message.answer(CARD_OPERATIONS_LEXICON_COMMANDS[callback.message.text]["no_cards"])


@router.callback_query(F.data[:8] == "get_card", StateFilter(ShowCardState.show_card))
@router.callback_query(F.data[:8] == "get_card", StateFilter(default_state))
async def show_card(callback: CallbackQuery, state: FSMContext):
    card_id = int(callback.data[8:])
    await state.set_state(ShowCardState.show_card)
    async with async_session() as session:
        query = select(Card).where(Card.id == card_id)
        result = await session.execute(query)
        card = result.scalars().first()
        text = print_card_info(card)
        await callback.message.edit_text(
            text=text,
            reply_markup=create_card_actions_keyboard(card_id)
        )


@router.message(Command(commands="add_card"), StateFilter(default_state))
async def create_card(message: Message, state: FSMContext):
    async with async_session() as session:
        query = select(Card).where(Card.tg_id == message.from_user.id)
        result = await session.execute(query)
        cards = result.scalars().all()

    if len(cards) < LIMITS["max_number_of_cards"]:
        await message.answer(
            text=CARD_OPERATIONS_LEXICON_COMMANDS[message.text],
            reply_markup=TypeKeyboard.create_keyboard()
        )

        await state.set_state(AddCardState.add_type)

    else:
        await message.answer(CARD_OPERATIONS_LEXICON_COMMANDS[message.text]["max_number_of_cards"])


@router.callback_query(F.data == "credit_card", StateFilter(AddCardState.add_type))
async def temp_function_for_credit_card(callback: CallbackQuery):
    await callback.message.delete()
    await callback.message.answer(
        text=CARD_OPERATIONS_LEXICON["no_credit_card"],
        reply_markup=create_exit_keyboard()
    )


@router.callback_query(F.data == "debit_card", StateFilter(AddCardState.add_type))
async def create_name(callback: CallbackQuery, state: FSMContext):
    await state.update_data(card_type="debit_card")

    await callback.message.edit_text(
        text=CARD_OPERATIONS_LEXICON["card_name"]["name"],
        reply_markup=create_exit_keyboard()
    )

    await state.set_state(AddCardState.add_name)


@router.message(StateFilter(AddCardState.add_name))
async def set_card_name(message: Message, state: FSMContext):
    card_name = message.text.strip()
    if isValidName(card_name):
        await state.update_data(card_name=card_name)

        await message.answer(
            text=CARD_OPERATIONS_LEXICON["card_balance"]["balance"],
            reply_markup=create_exit_keyboard()
        )

        await state.set_state(AddCardState.add_balance)

    else:
        await message.answer(
            text=CARD_OPERATIONS_LEXICON["card_name"]["incorrect_name"],
            reply_markup=create_exit_keyboard()
        )


@router.message(StateFilter(AddCardState.add_balance))
async def set_card(message: Message, state: FSMContext):
    try:
        balance = float(message.text.strip())
        await state.update_data(card_balance=balance)

        data = await state.get_data()

        async with async_session() as session:
            stmt = insert(Card).values(
                name=data["card_name"],
                card_type=data["card_type"],
                tg_id=message.from_user.id,
                balance=data["card_balance"]
            )

            await session.execute(stmt)
            await session.commit()

            query = select(Card).where(Card.tg_id == message.from_user.id)
            result = await session.execute(query)
            current_card = result.scalars().all()[-1]

        await state.clear()
        await message.answer(
            text=CARD_OPERATIONS_LEXICON["card_is_create"],
            reply_markup=create_card_is_create_keyboard(current_card.id)
        )

    except ValueError:
        await message.answer(
            text=CARD_OPERATIONS_LEXICON["card_balance"]["incorrect_balance"],
            reply_markup=create_exit_keyboard()
        )


@router.callback_query(F.data[:8] == "del_card", StateFilter(ShowCardState.show_card))
async def del_card(callback: CallbackQuery, state: FSMContext):
    card_id = int(callback.data[8:])

    await state.update_data(card_id=card_id)
    await state.set_state(UpdCardState.del_card)
    await callback.message.edit_text(
        text=CARD_OPERATIONS_LEXICON["confirm_del_card"],
        reply_markup=create_yes_no_delete_keyboard()
    )


@router.callback_query(F.data == "NO", StateFilter(UpdCardState.del_card))
async def no_delete_card(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    card_id = data["card_id"]

    await state.clear()
    await callback.message.edit_text(
        text=CARD_OPERATIONS_LEXICON["cancel_del_card"],
        reply_markup=create_card_is_create_keyboard(card_id)
    )


@router.callback_query(F.data == "YES", StateFilter(UpdCardState.del_card))
async def yes_delete_card(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    card_id = data["card_id"]

    async with async_session() as session:
        to_delete_card = delete(Card).where(Card.id == card_id)
        to_delete_income = delete(Income).where(Income.card_id == card_id)
        to_delete_expense = delete(Expense).where(Expense.card_id == card_id)

        await session.execute(to_delete_card)
        await session.execute(to_delete_income)
        await session.execute(to_delete_expense)

        await session.commit()

    await state.clear()
    await callback.message.delete()
    await callback.message.answer(CARD_OPERATIONS_LEXICON["success_del_card"])


@router.callback_query(F.data[:8] == "upd_card", StateFilter(ShowCardState.show_card))
async def upd_card(callback: CallbackQuery):
    card_id = int(callback.data[8:])
    await callback.message.edit_text(
        text=CARD_OPERATIONS_LEXICON["update_elem_in_card"],
        reply_markup=create_card_update_keyboard(card_id)
    )


@router.callback_query(F.data[:8] == "upd_name", StateFilter(ShowCardState.show_card))
async def upd_card_name(callback: CallbackQuery, state: FSMContext):
    card_id = int(callback.data[8:])

    await state.update_data(card_id=card_id)
    await state.set_state(UpdCardState.upd_name)

    await callback.message.edit_text(
        text=CARD_OPERATIONS_LEXICON["update_card_name"]["name"],
        reply_markup=create_cancel_update_keyboard()
    )


@router.message(StateFilter(UpdCardState.upd_name))
async def set_upd_card_name(message: Message, state: FSMContext):
    card_name = message.text.strip()
    if isValidName(card_name):
        data = await state.get_data()
        async with async_session() as session:
            card_id = data["card_id"]
            stmt = update(Card).where(Card.id == card_id).values(name=card_name)
            await session.execute(stmt)
            await session.commit()

        await state.clear()
        await message.answer(
            text=CARD_OPERATIONS_LEXICON["update_card_name"]["successful_upd"],
            reply_markup=create_card_is_create_keyboard(card_id)
        )

    else:
        await message.answer(
            text=CARD_OPERATIONS_LEXICON["update_card_name"]["incorrect_name"],
            reply_markup=create_cancel_update_keyboard()
        )


@router.callback_query(F.data[:8] == "upd_bala", StateFilter(ShowCardState.show_card))
async def upd_card_balance(callback: CallbackQuery, state: FSMContext):
    card_id = int(callback.data[8:])

    await state.update_data(card_id=card_id)
    await state.set_state(UpdCardState.upd_balance)
    await callback.message.edit_text(
        text=CARD_OPERATIONS_LEXICON["update_card_balance"]["balance"],
        reply_markup=create_cancel_update_keyboard()
    )


@router.message(StateFilter(UpdCardState.upd_balance))
async def set_upd_card_balance(message: Message, state: FSMContext):
    try:
        balance = float(message.text.strip())
        data = await state.get_data()
        async with async_session() as session:
            card_id = data["card_id"]
            stmt = update(Card).where(Card.id == card_id).values(balance=balance)
            await session.execute(stmt)
            await session.commit()

        await state.clear()
        await message.answer(
            text=CARD_OPERATIONS_LEXICON["update_card_balance"]["successful_upd"],
            reply_markup=create_card_is_create_keyboard(card_id)
        )

    except ValueError:
        await message.answer(
            text=CARD_OPERATIONS_LEXICON["update_card_balance"]["incorrect_balance"],
            reply_markup=create_exit_keyboard()
        )


@router.callback_query(F.data[:11] == "get_incomes", StateFilter(ShowCardState.show_card))
async def get_incomes(callback: CallbackQuery, state: FSMContext):
    card_id = int(callback.data[11:])
    async with async_session() as session:
        query = select(Income).where(Income.card_id == card_id)
        result = await session.execute(query)
        incomes = result.scalars().all()

    if incomes:
        keyboard_limit = LIMITS["max_elements_in_keyboard"]
        pages = len(incomes) // keyboard_limit + (len(incomes) % keyboard_limit != 0)
        buttons = [income for income in incomes]
        buttons.sort(key=lambda x: x.date, reverse=True)

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
            reply_markup=create_card_is_create_keyboard(card_id)
        )


@router.callback_query(F.data[:12] == "get_expenses", StateFilter(ShowCardState.show_card))
async def get_expenses(callback: CallbackQuery, state: FSMContext):
    card_id = int(callback.data[12:])
    async with async_session() as session:
        query = select(Expense).where(Expense.card_id == card_id)
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
            reply_markup=create_card_is_create_keyboard(card_id)
        )
