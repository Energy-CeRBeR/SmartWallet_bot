from aiogram import F, Router
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import default_state
from aiogram.types import Message, CallbackQuery
from sqlalchemy import select, insert

from src.card_operations.keyboards import create_exit_keyboard
from src.database.database import async_session
from src.database.models import IncomeCategory
from src.services.services import pagination
from src.services.states import ShowIncomesCategoryState, AddIncomeCategoryState
from src.transactions.categories_keyboards import create_income_categories_keyboard, create_category_actions_keyboard
from src.transactions.lexicon import LEXICON as USER_LEXICON, print_category_info

router = Router()


@router.message(Command(commands="in_categories"), StateFilter(default_state))
async def get_income_categories(message: Message, state: FSMContext):
    async with async_session() as session:
        query = select(IncomeCategory).where(IncomeCategory.tg_id == message.from_user.id)
        result = await session.execute(query)
        categories = result.scalars().all()
        if categories:
            pages = len(categories) // 9 + (len(categories) % 9 != 0)
            buttons = [category for category in categories]

            await state.set_state(ShowIncomesCategoryState.show_category)
            await state.update_data(
                page=1,
                pages=pages
            )

            cur_buttons = pagination(buttons, 0, "next")

            # Допилить функционал с переключением страниц + добавить его в модуль с расходами
            await message.answer(
                text=USER_LEXICON["income"]["categories_list"],
                reply_markup=create_income_categories_keyboard(cur_buttons, 0, "next")
            )
        else:
            await message.answer(USER_LEXICON["income"]["no_categories"])


@router.callback_query(F.data[:15] == "get_in_category", StateFilter(ShowIncomesCategoryState.show_category))
async def show_income_category(callback: CallbackQuery):
    category_id = int(callback.data[15:])
    async with async_session() as session:
        query = select(IncomeCategory).where(IncomeCategory.id == category_id)
        result = await session.execute(query)
        category = result.scalars().first()
        text = print_category_info(category)
        await callback.message.edit_text(
            text=text,
            reply_markup=create_category_actions_keyboard(category_id, "in")
        )


@router.message(Command(commands="add_in_category"), StateFilter(ShowIncomesCategoryState.show_category))
async def add_income_category(message: Message, state: FSMContext):
    await message.answer(
        text=USER_LEXICON["income"]["add_income_category"],
        reply_markup=create_exit_keyboard()
    )
    await state.set_state(AddIncomeCategoryState.add_name)


@router.message(StateFilter(AddIncomeCategoryState.add_name))
async def set_income_category(message: Message, state: FSMContext):
    async with async_session() as session:
        stmt = insert(IncomeCategory).values(
            name=message.text,
            tg_id=message.from_user.id
        )
        await session.execute(stmt)
        await session.commit()

    await message.answer(USER_LEXICON["income"]["category_is_create"])
    await state.clear()
