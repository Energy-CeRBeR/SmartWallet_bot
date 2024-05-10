from aiogram.fsm.context import FSMContext
from sqlalchemy import select, insert

from aiogram import Router, F
from aiogram.filters import CommandStart, Command, StateFilter
from aiogram.fsm.state import default_state
from aiogram.types import Message, CallbackQuery

from src.database.database import async_session
from src.database.models import User
from src.user.keyboards import create_stop_keyboard

from src.user.lexicon import LEXICON_COMMANDS as USER_LEXICON_COMMANDS
from src.user.lexicon import LEXICON as USER_LEXICON

router = Router()


@router.message(CommandStart(), StateFilter(default_state))
async def start_bot(message: Message):
    async with async_session() as session:
        query = select(User).where(User.tg_id == message.from_user.id)
        result = await session.execute(query)
        user = result.mappings().all()
        if user:
            await message.answer(USER_LEXICON_COMMANDS[message.text]["old_user"])
        else:
            stmt = insert(User).values(
                tg_id=message.from_user.id,
                first_name=message.from_user.first_name
            )

            await session.execute(stmt)
            await session.commit()
            await message.answer(USER_LEXICON_COMMANDS[message.text]["new_user"])


@router.message(Command(commands="help"), StateFilter(default_state))
async def help_info(message: Message):
    await message.answer(text=USER_LEXICON_COMMANDS[message.text])


@router.message()
async def error_directory_handler(message: Message):
    await message.answer(
        text=USER_LEXICON["access_error"],
        reply_markup=create_stop_keyboard()
    )


@router.callback_query(F.data == "stop_all_processes")
async def stop_all_process(callback: CallbackQuery, state: FSMContext):
    await callback.message.delete()
    await state.clear()
    await callback.message.answer(USER_LEXICON["stop_all_processes"])
