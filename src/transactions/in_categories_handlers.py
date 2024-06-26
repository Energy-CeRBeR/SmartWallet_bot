from datetime import datetime

from aiogram import F, Router
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import default_state
from aiogram.types import Message, CallbackQuery
from sqlalchemy import select, insert, delete, update

from src.card_operations.keyboards import create_exit_keyboard, create_exit_show_card_keyboard, \
    create_yes_no_delete_keyboard
from src.database.database import async_session
from src.database.models import IncomeCategory, Income
from src.services.services import pagination, isValidName, unpack_in_category_model, unpack_income_model
from src.services.settings import LIMITS
from src.services.states import ShowIncomesCategoryState, AddIncomeCategoryState, UpdCategoryState, ShowIncomesState
from src.transactions.categories_keyboards import create_income_categories_keyboard, create_category_actions_keyboard, \
    create_in_category_is_create_keyboard, create_add_new_in_category_keyboard
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
            keyboard_limit = LIMITS["max_elements_in_keyboard"]
            pages = len(categories) // keyboard_limit + (len(categories) % keyboard_limit != 0)
            buttons = [unpack_in_category_model(category) for category in categories]

            await state.set_state(ShowIncomesCategoryState.show_category)
            await state.update_data(
                page=0,
                pages=pages,
                in_categories=buttons
            )

            cur_buttons = pagination(buttons, 0)

            await message.answer(
                text=f'{TRANSACTIONS_LEXICON["income"]["categories_list"]} Страница 1 / {pages}',
                reply_markup=create_income_categories_keyboard(cur_buttons)
            )
        else:
            await state.clear()
            await message.answer(
                text=TRANSACTIONS_LEXICON["income"]["no_categories"],
                reply_markup=create_add_new_in_category_keyboard()
            )


@router.callback_query(F.data == "next_page", StateFilter(ShowIncomesCategoryState.show_category))
async def goto_next_in_categories_page(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    cur_page = data["page"] + 1
    in_categories = data["in_categories"]
    buttons = pagination(in_categories, cur_page)
    pages = data["pages"]

    if 0 <= cur_page < pages and buttons:
        await callback.message.edit_text(
            text=f'{TRANSACTIONS_LEXICON["income"]["categories_list"]} Страница {cur_page + 1} / {pages}',
            reply_markup=create_income_categories_keyboard(buttons)
        )

        await state.update_data(page=cur_page)


@router.callback_query(F.data == "back_page", StateFilter(ShowIncomesCategoryState.show_category))
async def goto_back_in_categories_page(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    cur_page = data["page"] - 1
    in_categories = data["in_categories"]
    buttons = pagination(in_categories, cur_page)
    pages = data["pages"]

    if 0 <= cur_page < pages and buttons:
        await callback.message.edit_text(
            text=f'{TRANSACTIONS_LEXICON["income"]["categories_list"]} Страница {cur_page + 1} / {pages}',
            reply_markup=create_income_categories_keyboard(buttons)
        )

        await state.update_data(page=cur_page)


@router.callback_query(F.data == "show_in_categories_list", StateFilter(default_state))
@router.callback_query(F.data == "show_in_categories_list", StateFilter(ShowIncomesCategoryState.show_category))
async def get_income_categories(callback: CallbackQuery, state: FSMContext):
    async with async_session() as session:
        query = select(IncomeCategory).where(IncomeCategory.tg_id == callback.from_user.id)
        result = await session.execute(query)
        categories = result.scalars().all()
        if categories:
            keyboard_limit = LIMITS["max_elements_in_keyboard"]
            pages = len(categories) // keyboard_limit + (len(categories) % keyboard_limit != 0)
            buttons = [unpack_in_category_model(category) for category in categories]

            await state.set_state(ShowIncomesCategoryState.show_category)
            await state.update_data(
                page=0,
                pages=pages,
                in_categories=buttons
            )

            cur_buttons = pagination(buttons, 0)

            await callback.message.edit_text(
                text=f'{TRANSACTIONS_LEXICON["income"]["categories_list"]} Страница 1 / {pages}',
                reply_markup=create_income_categories_keyboard(cur_buttons)
            )
        else:
            await state.clear()
            await callback.message.edit_text(
                text=TRANSACTIONS_LEXICON["income"]["no_categories"],
                reply_markup=create_add_new_in_category_keyboard()
            )


@router.callback_query(F.data[:15] == "get_in_category", StateFilter(default_state))
@router.callback_query(F.data[:15] == "get_in_category", StateFilter(ShowIncomesCategoryState.show_category))
async def show_income_category(callback: CallbackQuery, state: FSMContext):
    category_id = int(callback.data[15:])
    await state.set_state(ShowIncomesCategoryState.show_category)

    async with async_session() as session:
        query = select(IncomeCategory).where(IncomeCategory.id == category_id)
        result = await session.execute(query)
        category = result.scalars().first()
        text = print_category_info(category)

    await callback.message.edit_text(
        text=text,
        reply_markup=create_category_actions_keyboard(category_id, "in")
    )


@router.message(Command(commands="add_in_category"), StateFilter(default_state))
async def add_income_category(message: Message, state: FSMContext):
    async with async_session() as session:
        query = select(IncomeCategory).where(IncomeCategory.tg_id == message.from_user.id)
        result = await session.execute(query)
        in_categories = result.scalars().all()

    if len(in_categories) < LIMITS["max_number_of_categories"]:
        await message.answer(
            text=TRANSACTIONS_LEXICON["income"]["add_income_category"],
            reply_markup=create_exit_keyboard()
        )
        await state.set_state(AddIncomeCategoryState.add_name)

    else:
        await message.answer(TRANSACTIONS_LEXICON["in_categories_limit"])


@router.callback_query(F.data == "start_create_in_category", StateFilter(default_state))
async def add_income_category(callback: CallbackQuery, state: FSMContext):
    async with async_session() as session:
        query = select(IncomeCategory).where(IncomeCategory.tg_id == callback.from_user.id)
        result = await session.execute(query)
        in_categories = result.scalars().all()

    if len(in_categories) < LIMITS["max_number_of_categories"]:
        await callback.message.edit_text(
            text=TRANSACTIONS_LEXICON["income"]["add_income_category"],
            reply_markup=create_exit_keyboard()
        )
        await state.set_state(AddIncomeCategoryState.add_name)

    else:
        await callback.message.edit_text(TRANSACTIONS_LEXICON["in_categories_limit"])


@router.message(StateFilter(AddIncomeCategoryState.add_name))
async def set_income_category(message: Message, state: FSMContext):
    category_name = message.text.strip()
    if isValidName(category_name):
        async with async_session() as session:
            stmt = insert(IncomeCategory).values(
                name=category_name,
                tg_id=message.from_user.id
            )
            await session.execute(stmt)
            await session.commit()

            query = select(IncomeCategory).where(IncomeCategory.tg_id == message.from_user.id)
            result = await session.execute(query)
            current_in_category = result.scalars().all()[-1]

        await state.clear()
        await message.answer(
            text=TRANSACTIONS_LEXICON["income"]["category_is_create"],
            reply_markup=create_in_category_is_create_keyboard(current_in_category.id)
        )

    else:
        await message.answer(
            text=TRANSACTIONS_LEXICON["income"]["incorrect_name"],
            reply_markup=create_exit_keyboard()
        )


@router.callback_query(F.data[:12] == "del_category", StateFilter(ShowIncomesCategoryState.show_category))
async def del_category(callback: CallbackQuery, state: FSMContext):
    category_id = int(callback.data[14:])

    await state.update_data(category_id=category_id)
    await state.set_state(UpdCategoryState.del_in_category)
    await callback.message.edit_text(
        text=TRANSACTIONS_LEXICON["edit_income"]["confirm_del_category"],
        reply_markup=create_yes_no_delete_keyboard()
    )


@router.callback_query(F.data == "NO", StateFilter(UpdCategoryState.del_in_category))
async def no_delete_card(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    category_id = data["category_id"]

    await state.clear()
    await callback.message.edit_text(
        text=TRANSACTIONS_LEXICON["edit_income"]["cancel_del_category"],
        reply_markup=create_in_category_is_create_keyboard(category_id)
    )


@router.callback_query(F.data == "YES", StateFilter(UpdCategoryState.del_in_category))
async def yes_delete_card(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    category_id = data["category_id"]
    async with async_session() as session:
        to_delete_category = delete(IncomeCategory).where(IncomeCategory.id == category_id)
        to_delete_income = delete(Income).where(Income.category_id == category_id)

        await session.execute(to_delete_category)
        await session.execute(to_delete_income)

        await session.commit()

    await state.clear()
    await callback.message.delete()
    await callback.message.answer(TRANSACTIONS_LEXICON["edit_income"]["success_del_category"])


@router.callback_query(F.data[:12] == "upd_category", StateFilter(ShowIncomesCategoryState.show_category))
async def upd_category_name(callback: CallbackQuery, state: FSMContext):
    category_id = int(callback.data[14:])
    await state.update_data(
        category_id=category_id
    )
    await state.set_state(UpdCategoryState.upd_in_category_name)
    await callback.message.edit_text(
        text=TRANSACTIONS_LEXICON["update_category_name"],
        reply_markup=create_exit_show_card_keyboard("exit_update")
    )


@router.message(StateFilter(UpdCategoryState.upd_in_category_name))
async def set_upd_in_category_name(message: Message, state: FSMContext):
    new_category_name = message.text.strip()
    if isValidName(new_category_name):
        data = await state.get_data()
        category_id: int = data["category_id"]
        async with async_session() as session:
            stmt = update(IncomeCategory).where(IncomeCategory.id == category_id).values(name=new_category_name)
            await session.execute(stmt)
            await session.commit()

        await state.clear()
        await message.answer(
            text=TRANSACTIONS_LEXICON["successful_upd_category_name"],
            reply_markup=create_in_category_is_create_keyboard(category_id)
        )

    else:
        await message.answer(
            text=TRANSACTIONS_LEXICON["income"]["incorrect_name"],
            reply_markup=create_exit_keyboard()
        )


@router.callback_query(F.data[:11] == "get_incomes", StateFilter(ShowIncomesCategoryState.show_category))
async def get_incomes(callback: CallbackQuery, state: FSMContext):
    category_id = int(callback.data[11:])
    async with async_session() as session:
        query = select(Income).where(Income.category_id == category_id)
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
            reply_markup=create_in_category_is_create_keyboard(category_id)
        )
