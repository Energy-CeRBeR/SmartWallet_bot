from aiogram import F, Router
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import default_state
from aiogram.types import Message, CallbackQuery
from sqlalchemy import select, insert, delete

from src.card_operations.keyboards import create_exit_keyboard, create_exit_show_card_keyboard
from src.database.database import async_session
from src.database.models import IncomeCategory, Income
from src.services.services import pagination
from src.services.states import ShowIncomesCategoryState, AddIncomeCategoryState, UpdCategoryState, ShowIncomesState
from src.transactions.categories_keyboards import create_income_categories_keyboard, create_category_actions_keyboard
from src.transactions.lexicon import LEXICON as TRANSACTIONS_LEXICON, print_category_info
from src.transactions.transactions_keyboards import create_incomes_keyboard

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
                pages=pages,
                in_categories=buttons
            )

            cur_buttons = pagination(buttons, 0, "next")

            await message.answer(
                text=TRANSACTIONS_LEXICON["income"]["categories_list"],
                reply_markup=create_income_categories_keyboard(cur_buttons)
            )
        else:
            await message.answer(TRANSACTIONS_LEXICON["income"]["no_categories"])


@router.callback_query(F.data == "next_page", StateFilter(ShowIncomesCategoryState.show_category))
async def goto_next_in_categories_page(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    cur_page = data["page"]
    in_categories = data["in_categories"]
    buttons = pagination(in_categories, cur_page, "next")
    pages = data["pages"]

    if cur_page > 0 and buttons:
        await callback.message.edit_text(
            text=f'{TRANSACTIONS_LEXICON["income"]["categories_list"]} Страница {cur_page + 1} / {pages}',
            reply_markup=create_income_categories_keyboard(buttons)
        )

        await state.update_data(page=cur_page + 1)


@router.callback_query(F.data == "back_page", StateFilter(ShowIncomesCategoryState.show_category))
async def goto_back_in_categories_page(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    cur_page = data["page"]
    in_categories = data["in_categories"]
    buttons = pagination(in_categories, cur_page, "back")
    pages = data["pages"]

    if cur_page > 0 and buttons:
        await callback.message.edit_text(
            text=f'{TRANSACTIONS_LEXICON["income"]["categories_list"]} Страница {cur_page - 1} / {pages}',
            reply_markup=create_income_categories_keyboard(buttons)
        )

        await state.update_data(page=cur_page - 1)


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
        text=TRANSACTIONS_LEXICON["income"]["add_income_category"],
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

    await message.answer(TRANSACTIONS_LEXICON["income"]["category_is_create"])
    await state.clear()


@router.callback_query(F.data[:12] == "del_category", StateFilter(ShowIncomesCategoryState.show_category))
async def del_category(callback: CallbackQuery, state: FSMContext):
    category_id = int(callback.data[14:])
    async with async_session() as session:
        to_delete = delete(IncomeCategory).where(IncomeCategory.id == category_id)
        await session.execute(to_delete)
        await session.commit()

    await state.clear()
    await callback.message.delete()
    await callback.message.answer(TRANSACTIONS_LEXICON["successful_del_category"])


@router.callback_query(F.data[:12] == "upd_category", StateFilter(ShowIncomesCategoryState.show_category))
async def upd_category_name(callback: CallbackQuery, state: FSMContext):
    category_id = int(callback.data[14:])
    await state.update_data(
        category_type=IncomeCategory,
        category_id=category_id
    )
    await state.set_state(UpdCategoryState.upd_name)

    await callback.message.edit_text(
        text=TRANSACTIONS_LEXICON["update_category_name"],
        reply_markup=create_exit_show_card_keyboard("exit_update")
    )


@router.callback_query(F.data[:11] == "get_incomes", StateFilter(ShowIncomesCategoryState.show_category))
async def get_incomes(callback: CallbackQuery, state: FSMContext):
    category_id = int(callback.data[11:])
    async with async_session() as session:
        query = select(Income).where(Income.category_id == category_id)
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
        await callback.message.edit_text(
            text=f'{TRANSACTIONS_LEXICON["income"]["incomes_list"]} Страница 1 / {pages}',
            reply_markup=create_incomes_keyboard(cur_buttons)
        )

    else:
        await state.clear()
        await callback.message.delete()
        await callback.message.answer(TRANSACTIONS_LEXICON["income_transactions"]["no_incomes"])