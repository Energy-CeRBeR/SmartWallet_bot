from aiogram import Router, F
from aiogram.filters import CommandStart, Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import default_state
from aiogram.types import Message, CallbackQuery
from sqlalchemy import select, insert

from src.database.database import async_session
from src.database.models import User
# from src.database.models import all_models
from src.transactions.lexicon import LEXICON as TRANSACTIONS_LEXICON
from src.user.keyboards import create_stop_keyboard
from src.user.lexicon import LEXICON as USER_LEXICON
from src.user.lexicon import LEXICON_COMMANDS as USER_LEXICON_COMMANDS
from src.services.settings import commands_dict

router = Router()


@router.message(CommandStart(), StateFilter(default_state))
async def start_bot(message: Message):
    async with async_session() as session:
        query = select(User).where(User.tg_id == message.from_user.id)
        result = await session.execute(query)
        user = result.mappings().all()
        if not user:
            stmt = insert(User).values(
                tg_id=message.from_user.id,
                first_name=message.from_user.first_name
            )
            await session.execute(stmt)
            await session.commit()

        await message.answer(USER_LEXICON_COMMANDS[message.text])


@router.message(Command(commands="help"), StateFilter(default_state))
async def help_info(message: Message):
    await message.answer(text=USER_LEXICON_COMMANDS[message.text])


@router.message(Command(commands=[command[1:] for command in commands_dict]))
async def error_directory_handler(message: Message):
    await message.answer(
        text=USER_LEXICON["access_error"],
        reply_markup=create_stop_keyboard()
    )


# @router.message(F.text == "DROP ALL")
# async def drop_database(message: Message):
#     async with async_session() as session:
#         for table in all_models:
#             stmt = delete(table)
#             await session.execute(stmt)
#             await session.commit()
#
#     await message.answer("DROP DATABASE!!!")


@router.message()
async def unknown_command_handler(message: Message):
    await message.answer(text=USER_LEXICON["unknown_command"])


@router.callback_query(F.data == "stop_all_processes")
async def stop_all_process(callback: CallbackQuery, state: FSMContext):
    await callback.message.delete()
    await state.clear()
    await callback.message.answer(USER_LEXICON["stop_all_processes"])


@router.callback_query(F.data == "cancel")
async def cancel_operation(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.delete()
    await callback.message.answer(USER_LEXICON["operation_is_cancel"])


@router.callback_query(F.data == "exit")
async def create_exit_router(callback: CallbackQuery, state: FSMContext):
    await callback.message.delete()
    await state.clear()


@router.callback_query(F.data == "cancel_edit_transaction")
async def create_cancel_edit_transaction(callback: CallbackQuery, state: FSMContext):
    await callback.message.delete()
    await callback.message.answer(TRANSACTIONS_LEXICON["exit_from_edit"])
    await state.clear()
