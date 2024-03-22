from copy import deepcopy

from aiogram import Router, F
from aiogram.filters import Command, CommandObject
from aiogram.types import Message, CallbackQuery

from sqlalchemy import select, insert, delete, update

from src.database.database import async_session
from src.database.database import Card
from src.database.users_status import users_status, user_dict_template

from src.services.services import isValidBalance

from src.card_operations.lexicon import LEXICON as USER_LEXICON
from src.card_operations.lexicon import LEXICON_COMMANDS as USER_LEXICON_COMMANDS

from src.card_operations.keyboards import TypeKeyboard, create_exit_keyboard

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
async def create_type(message: Message):
    await message.answer(
        text=USER_LEXICON_COMMANDS[message.text],
        reply_markup=TypeKeyboard.create_keyboard()
    )


@router.callback_query(F.data == "cancel")
async def back_to_menu(callback: CallbackQuery):
    users_status[callback.from_user.id] = deepcopy(user_dict_template)

    await callback.message.delete()
    await callback.message.answer(USER_LEXICON["cancel_operation"])


@router.callback_query(F.data == "credit_card")
async def temp_function_for_credit_card(callback: CallbackQuery):
    await callback.message.answer("Данный тип карт в разработке!")


@router.callback_query(F.data == "debit_card")
async def create_name(callback: CallbackQuery):
    await callback.message.edit_text(
        text=USER_LEXICON["card_name"]["name"],
        reply_markup=create_exit_keyboard()
    )
    if callback.from_user.id not in users_status:
        users_status[callback.from_user.id] = deepcopy(user_dict_template)

    users_status[callback.from_user.id]["card"]["card_type"] = "debit_card"
    users_status[callback.from_user.id]["card"]["create_name"] = True


@router.message(Command(commands="card_name"))
async def set_card_name(message: Message, command: CommandObject):
    if message.from_user.id not in users_status:
        users_status[message.from_user.id] = deepcopy(user_dict_template)

    if not users_status[message.from_user.id]["card"]["create_name"]:
        await message.answer(USER_LEXICON["access_error"])
        return

    if command.args is None:
        await message.answer(USER_LEXICON["card_name"]["empty_name"])
        return

    users_status[message.from_user.id]["card"]["card_name"] = command.args
    users_status[message.from_user.id]["card"]["create_name"] = False
    users_status[message.from_user.id]["card"]["create_balance"] = True

    await message.answer(
        text=USER_LEXICON["card_balance"]["balance"],
        reply_markup=create_exit_keyboard()
    )


@router.message(Command(commands="card_balance"))
async def set_card_balance(message: Message, command: CommandObject):
    if message.from_user.id not in users_status:
        users_status[message.from_user.id] = deepcopy(user_dict_template)

    if not users_status[message.from_user.id]["card"]["create_balance"]:
        await message.answer(USER_LEXICON["access_error"])
        return

    if command.args is None:
        await message.answer(USER_LEXICON["card_balance"]["empty_balance"])
        return

    if not isValidBalance(command.args.split()):
        await message.answer(USER_LEXICON["card_balance"]["incorrect_balance"])
        return

    users_status[message.from_user.id]["card"]["card_balance"] = command.args

    async with async_session() as session:
        stmt = insert(Card).values(
            name=users_status[message.from_user.id]["card"]["card_name"],
            card_type=users_status[message.from_user.id]["card"]["card_type"],
            tg_id=message.from_user.id,
            balance=float()
            # Переделать проверка типа через try - except, добавить баланс, закоммитить изменения
        )

    users_status[message.from_user.id] = deepcopy(user_dict_template)

    await message.answer(text=USER_LEXICON["card_is_create"])
