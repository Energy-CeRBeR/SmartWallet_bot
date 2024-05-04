from copy import deepcopy

from sqlalchemy import select, insert, delete, update

from aiogram import Router
from aiogram.filters import CommandStart, Command
from aiogram.types import Message

from src.database.database import async_session
from src.database.models import User
from src.database.users_status import users_status, user_dict_template

from src.user.lexicon import LEXICON as USER_LEXICON
from src.user.lexicon import LEXICON_COMMANDS as USER_LEXICON_COMMANDS

router = Router()


@router.message(CommandStart())
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
            users_status[message.from_user.id] = deepcopy(user_dict_template)

            await session.execute(stmt)
            await session.commit()
            await message.answer(USER_LEXICON_COMMANDS[message.text]["new_user"])


@router.message(Command(commands="help"))
async def help_info(message: Message):
    await message.answer(text=USER_LEXICON_COMMANDS[message.text])
