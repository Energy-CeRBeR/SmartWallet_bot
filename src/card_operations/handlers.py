from aiogram import Router
from aiogram.filters import Command, CommandObject
from aiogram.types import Message

from sqlalchemy import select, insert, delete, update

from src.database import async_session
from src.database import Card, CardType

from src.card_operations.lexicon import LEXICON as USER_LEXICON
from src.card_operations.lexicon import LEXICON_COMMANDS as USER_LEXICON_COMMANDS

from src.card_operations.keyboards import TypeKeyboard

router = Router()


@router.message(Command(commands="cards"))
async def get_card(message: Message):
    async with async_session() as session:
        query = select(Card).where(Card.tg_id == message.from_user.id)
        result = await session.execute(query)
        cards = result.mappings().all()
        if cards:
            print(cards)
            await message.answer(USER_LEXICON_COMMANDS[message.text]["card_list"])
        else:
            await message.answer(USER_LEXICON_COMMANDS[message.text]["no_cards"])


@router.message(Command(commands="add_card"))
async def add_card(message: Message):
    await message.answer(
        text=USER_LEXICON_COMMANDS[message.text],
        reply_markup=TypeKeyboard.create_keyboard()
    )





