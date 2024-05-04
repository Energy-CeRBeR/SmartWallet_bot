from aiogram import Router, F
from aiogram.filters import Command, StateFilter
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext

from sqlalchemy import select, insert, delete, update

from src.database.database import async_session
from src.database.models import IncomeCategory, ExpenseCategory, Card, Income, Expense

from src.services.states import AddCategoryState

from src.transactions.lexicon import (
    LEXICON as USER_LEXICON,
    LEXICON_COMMANDS as USER_LEXICON_COMMANDS
)

from src.transactions.transactions_keyboards import (
    create_select_category_keyboard,
    create_select_card_keyboard
)
from src.card_operations.keyboards import create_exit_keyboard

router = Router()


@router.message(Command(commands="add_income"))
async def select_income_type(message: Message, state: FSMContext):
    async with async_session() as session:
        query = select(IncomeCategory)
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
                text=USER_LEXICON["card_list"],
                reply_markup=create_select_card_keyboard(buttons)
            )
            await state.set_state(AddCategoryState.add_amount)

        else:
            await callback.message.answer(USER_LEXICON["no_cards"])
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
        text=USER_LEXICON[transactions]["amount"],
        reply_markup=create_exit_keyboard()
    )

    await state.set_state(AddCategoryState.set_data)


@router.message(StateFilter(AddCategoryState.set_data))
async def set_amount(message: Message, state: FSMContext):
    data = await state.get_data()
    category_type_str = data["category_type_str"]
    transactions = "income_transactions" if category_type_str == "income" else "expense_transactions"

    try:
        amount = float(message.text.strip())
        category_type = data["category_type"]
        async with async_session() as session:
            stmt = insert(category_type).values(
                tg_id=message.from_user.id,
                category_id=data["category_id"],
                card_id=data["card_id"],
                amount=amount,
                description=""
            )

            card_update = update(Card).where(
                Card.id == data["card_id"]).values(
                balance=Card.balance + amount if category_type_str == "income" else Card.balance - amount
            )

            await session.execute(stmt)
            await session.execute(card_update)
            await session.commit()
            await state.clear()
            await message.answer(text=USER_LEXICON[transactions]["income_is_create"])

    except ValueError:
        await message.answer(
            text=USER_LEXICON[transactions]["incorrect_amount"],
            reply_markup=create_exit_keyboard()
        )
