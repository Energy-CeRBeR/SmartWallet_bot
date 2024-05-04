from aiogram import Router, F
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery

from sqlalchemy import select, insert, delete, update

from src.database.database import async_session
from src.database.models import Card

from src.services.states import AddCardState, UpdCardState

from src.card_operations.lexicon import (
    LEXICON as USER_LEXICON,
    LEXICON_COMMANDS as USER_LEXICON_COMMANDS,
    print_card_info
)

from src.card_operations.keyboards import (
    TypeKeyboard,
    create_exit_keyboard,
    create_cards_keyboard,
    create_card_actions_keyboard,
    create_card_update_keyboard,
    create_exit_show_card_keyboard
)

router = Router()


@router.message(Command(commands="cards"))
async def get_cards(message: Message):
    async with async_session() as session:
        query = select(Card).where(Card.tg_id == message.from_user.id)
        result = await session.execute(query)
        cards = result.scalars().all()
        if cards:
            buttons = [card for card in cards]
            await message.answer(
                text=USER_LEXICON_COMMANDS[message.text]["card_list"],
                reply_markup=create_cards_keyboard(buttons)
            )
        else:
            await message.answer(USER_LEXICON_COMMANDS[message.text]["no_cards"])


@router.callback_query(F.data[:8] == "get_card")
async def show_card(callback: CallbackQuery):
    card_id = int(callback.data[8:])
    async with async_session() as session:
        query = select(Card).where(Card.id == card_id)
        result = await session.execute(query)
        card = result.scalars().first()
        text = print_card_info(card)
        await callback.message.edit_text(
            text=text,
            reply_markup=create_card_actions_keyboard(card_id)
        )


@router.message(Command(commands="add_card"))
async def create_type(message: Message, state: FSMContext):
    await message.answer(
        text=USER_LEXICON_COMMANDS[message.text],
        reply_markup=TypeKeyboard.create_keyboard()
    )

    await state.set_state(AddCardState.add_type)


@router.callback_query(F.data[:6] == "cancel")
async def cancel_operation(callback: CallbackQuery, state: FSMContext):
    await state.clear()

    await callback.message.delete()
    if len(USER_LEXICON[callback.data]) > 0:
        await callback.message.answer(USER_LEXICON[callback.data])


@router.callback_query(F.data == "credit_card", StateFilter(AddCardState.add_type))
async def temp_function_for_credit_card(callback: CallbackQuery):
    await callback.message.delete()
    await callback.message.answer("Данный тип карт в разработке!")


@router.callback_query(F.data == "debit_card", StateFilter(AddCardState.add_type))
async def create_name(callback: CallbackQuery, state: FSMContext):
    await state.update_data(card_type="debit_card")

    await callback.message.edit_text(
        text=USER_LEXICON["card_name"]["name"],
        reply_markup=create_exit_keyboard()
    )

    await state.set_state(AddCardState.add_name)


@router.callback_query(StateFilter(AddCardState.add_type))
async def error_card_type(message: Message):
    await message.answer(USER_LEXICON["card_types"]["incorrect_action"])


@router.message(StateFilter(AddCardState.add_name))
async def set_card_name(message: Message, state: FSMContext):
    await state.update_data(card_name=message.text.strip())

    await message.answer(
        text=USER_LEXICON["card_balance"]["balance"],
        reply_markup=create_exit_keyboard()
    )

    await state.set_state(AddCardState.add_balance)


@router.message(StateFilter(AddCardState.add_balance))
async def set_card_balance(message: Message, state: FSMContext):
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
        await state.clear()
        await message.answer(text=USER_LEXICON["card_is_create"])

    except ValueError:
        await message.answer(USER_LEXICON["card_balance"]["incorrect_balance"])


@router.callback_query(F.data[:8] == "del_card")
async def del_card(callback: CallbackQuery):
    card_id = int(callback.data[8:])
    async with async_session() as session:
        to_delete = delete(Card).where(Card.id == card_id)
        await session.execute(to_delete)
        await session.commit()

    await callback.message.delete()
    await callback.message.answer(USER_LEXICON["success_del_card"])


@router.callback_query(F.data[:8] == "upd_card")
async def upd_card(callback: CallbackQuery):
    card_id = int(callback.data[8:])
    await callback.message.edit_text(
        text=USER_LEXICON["update_elem_in_card"],
        reply_markup=create_card_update_keyboard(card_id)
    )


@router.callback_query(F.data[:8] == "upd_name")
async def upd_card_name(callback: CallbackQuery, state: FSMContext):
    card_id = int(callback.data[8:])

    await state.update_data(card_id=card_id)
    await state.set_state(UpdCardState.upd_name)

    await callback.message.edit_text(
        text=USER_LEXICON["update_card_name"]["name"],
        reply_markup=create_exit_show_card_keyboard("exit_update")
    )


@router.message(StateFilter(UpdCardState.upd_name))
async def set_upd_card_name(message: Message, state: FSMContext):
    data = await state.get_data()
    async with async_session() as session:
        card_id = data["card_id"]
        stmt = update(Card).where(Card.id == card_id).values(name=message.text)
        await session.execute(stmt)
        await session.commit()

    await state.clear()
    await message.answer(USER_LEXICON["update_card_name"]["successful_upd"])


@router.callback_query(F.data[:8] == "upd_bala")
async def upd_card_balance(callback: CallbackQuery, state: FSMContext):
    card_id = int(callback.data[8:])

    await state.update_data(card_id=card_id)
    await state.set_state(UpdCardState.upd_balance)

    await callback.message.edit_text(
        text=USER_LEXICON["update_card_balance"]["balance"],
        reply_markup=create_exit_show_card_keyboard("exit_update")
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

        await message.answer(USER_LEXICON["update_card_balance"]["successful_upd"])
        await state.clear()

    except ValueError:
        await message.answer(USER_LEXICON["update_card_balance"]["incorrect_balance"])
