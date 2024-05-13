from aiogram import Router, F
from aiogram.filters import StateFilter
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext

from sqlalchemy import update

from src.database.database import async_session

from src.services.states import UpdCategoryState

from src.transactions.lexicon import LEXICON as TRANSACTIONS_LEXICON

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


@router.callback_query(F.data == "exit")
async def create_exit_router(callback: CallbackQuery, state: FSMContext):
    await callback.message.delete()
    await state.clear()


@router.callback_query(F.data == "cancel_edit_transaction")
async def create_cancel_edit_transaction(callback: CallbackQuery, state: FSMContext):
    await callback.message.delete()
    await callback.message.answer(TRANSACTIONS_LEXICON["exit_from_edit"])
    await state.clear()
