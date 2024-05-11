from aiogram import Router, F
from aiogram.filters import StateFilter
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext

from sqlalchemy import select, insert, update, delete

from src.database.database import async_session
from src.database.models import Card, IncomeCategory, ExpenseCategory

from src.services.states import AddCategoryState, UpdCategoryState

from src.transactions.lexicon import LEXICON as TRANSACTIONS_LEXICON


from src.transactions.transactions_keyboards import (
    create_select_card_keyboard,
    create_description_keyboard,
    create_done_keyboard
)
from src.card_operations.keyboards import create_exit_keyboard, create_exit_show_card_keyboard

router = Router()


@router.message(StateFilter(UpdCategoryState.upd_name))
async def set_upd_category_name(message: Message, state: FSMContext):
    data = await state.get_data()
    async with async_session() as session:
        category_id: int = data["category_id"]
        category = data["category_type"]
        stmt = update(category).where(category.id == category_id).values(name=message.text)
        await session.execute(stmt)
        await session.commit()

    await state.clear()
    await message.answer(TRANSACTIONS_LEXICON["successful_upd_category_name"])


@router.callback_query(F.data[:11] == "select_card", StateFilter(AddCategoryState.select_card))
async def select_card(callback: CallbackQuery, state: FSMContext):
    category_id = int(callback.data[11:])
    await state.update_data(category_id=category_id)

    async with async_session() as session:
        query = select(Card)
        result = await session.execute(query)
        cards = result.scalars().all()
        if cards:
            buttons = [card for card in cards]
            await callback.message.edit_text(
                text=TRANSACTIONS_LEXICON["card_list"],
                reply_markup=create_select_card_keyboard(buttons)
            )
            await state.set_state(AddCategoryState.add_amount)

        else:
            await callback.message.answer(TRANSACTIONS_LEXICON["no_cards"])
            await state.clear()


@router.callback_query(F.data[:10] == "add_amount", StateFilter(AddCategoryState.add_amount))
async def add_amount(callback: CallbackQuery, state: FSMContext):
    card_id = int(callback.data[10:])
    await state.update_data(card_id=card_id)

    await callback.message.delete()

    data = await state.get_data()
    category_type_str = data["category_type_str"]
    transactions = "income_transactions" if category_type_str == "income" else "expense_transactions"
    await callback.message.answer(
        text=TRANSACTIONS_LEXICON[transactions]["amount"],
        reply_markup=create_exit_keyboard()
    )

    await state.set_state(AddCategoryState.add_description)


@router.message(StateFilter(AddCategoryState.add_description))
async def add_description(message: Message, state: FSMContext):
    data = await state.get_data()
    category_type_str = data["category_type_str"]
    transactions = "income_transactions" if category_type_str == "income" else "expense_transactions"

    try:
        amount = float(message.text.strip())
        await state.update_data(amount=amount)
        await message.answer(
            text=TRANSACTIONS_LEXICON["description"],
            reply_markup=create_description_keyboard()
        )
        await state.set_state(AddCategoryState.get_description)

    except ValueError:
        await message.answer(
            text=TRANSACTIONS_LEXICON[transactions]["incorrect_amount"],
            reply_markup=create_exit_keyboard()
        )


@router.callback_query(F.data == "YES", StateFilter(AddCategoryState.get_description))
async def get_description_from_user(callback: CallbackQuery, state: FSMContext):
    await callback.message.delete()
    await callback.message.answer(TRANSACTIONS_LEXICON["get_description"])
    await state.set_state(AddCategoryState.set_description)


@router.callback_query(F.data == "NO", StateFilter(AddCategoryState.get_description))
async def no_description(callback: CallbackQuery, state: FSMContext):
    await state.update_data(description="")
    await state.set_state(AddCategoryState.set_data)
    await callback.message.edit_text(
        text=TRANSACTIONS_LEXICON["commit_transaction"],
        reply_markup=create_done_keyboard()
    )


@router.message(StateFilter(AddCategoryState.set_description))
async def set_description(message: Message, state: FSMContext):
    await state.update_data(description=message.text)
    await state.set_state(AddCategoryState.set_data)
    await message.answer(
        text=TRANSACTIONS_LEXICON["set_description"],
        reply_markup=create_done_keyboard()
    )


@router.callback_query(F.data == "commit_transaction", StateFilter(AddCategoryState.set_data))
async def set_transaction(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    category_type_str = data["category_type_str"]
    transactions = "income_transactions" if category_type_str == "income" else "expense_transactions"
    amount = data["amount"]
    category_type = data["category_type"]

    async with async_session() as session:
        stmt = insert(category_type).values(
            tg_id=callback.from_user.id,
            category_id=data["category_id"],
            card_id=data["card_id"],
            amount=amount,
            description=data["description"]
        )

        card_update = update(Card).where(
            Card.id == data["card_id"]).values(
            balance=Card.balance + amount if category_type_str == "income" else Card.balance - amount
        )

        await session.execute(stmt)
        await session.execute(card_update)
        await session.commit()

        await state.clear()
        await callback.message.delete()
        await callback.message.answer(text=TRANSACTIONS_LEXICON[transactions]["income_is_create"])


@router.callback_query(F.data == "exit")
async def create_exit_router(callback: CallbackQuery, state: FSMContext):
    await callback.message.delete()
    await state.clear()


@router.callback_query(F.data == "cancel_edit_transaction")
async def create_cancel_edit_transaction(callback: CallbackQuery, state: FSMContext):
    await callback.message.delete()
    await callback.message.answer(TRANSACTIONS_LEXICON["exit_from_edit"])
    await state.clear()
