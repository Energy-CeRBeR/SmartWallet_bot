from aiogram import F
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery
from sqlalchemy import select

from src.database.database import async_session
from src.database.models import Income, IncomeCategory
from src.services.services import transaction_pagination
from src.services.states import ShowIncomesState, AddCategoryState
from src.transactions.lexicon import LEXICON as USER_LEXICON, LEXICON_COMMANDS as USER_LEXICON_COMMANDS
from src.transactions.general_handlers import router
from src.transactions.transactions_keyboards import create_incomes_keyboard, create_transaction_edit_keyboard, \
    create_select_category_keyboard


@router.message(Command(commands="incomes"))
async def get_incomes(message: Message, state: FSMContext):
    async with async_session() as session:
        query = select(Income).where(Income.tg_id == message.from_user.id)
        result = await session.execute(query)
        incomes = result.scalars().all()

    if incomes:
        pages = len(incomes) // 9 + (len(incomes) % 9 != 0)
        await state.set_state(ShowIncomesState.show_incomes)
        buttons = [income for income in incomes]
        buttons.reverse()

        await state.update_data(
            page=1,
            pages=pages,
            incomes=buttons
        )

        cur_buttons = transaction_pagination(buttons, 0, "next")

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
    buttons = transaction_pagination(incomes, cur_page, "next")
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
    buttons = transaction_pagination(incomes, cur_page, "back")
    pages = data["pages"]

    if cur_page > 0 and buttons:
        await callback.message.edit_text(
            text=f'{USER_LEXICON["income"]["incomes_list"]} Страница {cur_page - 1} / {pages}',
            reply_markup=create_incomes_keyboard(buttons)
        )

        await state.update_data(page=cur_page - 1)


@router.callback_query(F.data[:10] == "get_income", StateFilter(ShowIncomesState.show_incomes))
async def get_income_info(callback: CallbackQuery):
    income_id = int(callback.data[10:])
    async with async_session() as session:
        query = select(Income).where(Income.id == income_id)
        result = await session.execute(query)
        income = result.scalars().first()

        query = select(IncomeCategory).where(IncomeCategory.id == income.category_id)
        result = await session.execute(query)
        income_category = result.scalars().first()

    description = income.description if income.description else USER_LEXICON["income_info"]["no_description"]
    await callback.message.edit_text(
        text=(
            f'{USER_LEXICON["income_info"]["info"]}\n'
            f'{USER_LEXICON["income_info"]["category"]}: {income_category.name}\n'
            f'{USER_LEXICON["income_info"]["amount"]}: {income.amount}\n'
            f'{USER_LEXICON["income_info"]["date"]}: {income.date}\n'
            f'{USER_LEXICON["income_info"]["description"]}: {description}'
        ),
        reply_markup=create_transaction_edit_keyboard(transaction_type="in")
    )


@router.message(Command(commands="add_income"))
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
