from copy import deepcopy

from aiogram import Router, F
from aiogram.filters import Command, CommandObject
from aiogram.types import Message, CallbackQuery

from sqlalchemy import select, insert, delete, update

from src.database.database import async_session
from src.database.models import CardType, Card
from src.database.users_status import users_status, user_dict_template

from src.card_operations.lexicon import (
    LEXICON as USER_LEXICON,
    LEXICON_COMMANDS as USER_LEXICON_COMMANDS,
    print_card_info
)

from src.card_operations.keyboards import (
    TypeKeyboard,
    create_exit_keyboard,
    create_cards_keyboard,
    create_card_actions_keyboard,
    create_card_update_keyboard,
    create_exit_show_card_keyboard
)

router = Router()


@router.message(Command(commands="cards"))
async def get_cards(message: Message):
    async with async_session() as session:
        query = select(Card).where(Card.tg_id == message.from_user.id)
        result = await session.execute(query)
        cards = result.scalars().all()
        if cards:
            buttons = [card for card in cards]
            await message.answer(
                text=USER_LEXICON_COMMANDS[message.text]["card_list"],
                reply_markup=create_cards_keyboard(buttons)
            )
        else:
            await message.answer(USER_LEXICON_COMMANDS[message.text]["no_cards"])


@router.callback_query(F.data[:8] == "get_card")
async def show_card(callback: CallbackQuery):
    card_id = int(callback.data[8:])
    async with async_session() as session:
        query = select(Card).where(Card.id == card_id)
        result = await session.execute(query)
        card = result.scalars().first()
        text = print_card_info(card)
        await callback.message.edit_text(
            text=text,
            reply_markup=create_card_actions_keyboard(card_id)
        )


@router.message(Command(commands="add_card"))
async def create_type(message: Message):
    await message.answer(
        text=USER_LEXICON_COMMANDS[message.text],
        reply_markup=TypeKeyboard.create_keyboard()
    )


@router.callback_query(F.data[:6] == "cancel")
async def cancel_operation(callback: CallbackQuery):
    users_status[callback.from_user.id] = deepcopy(user_dict_template)
    await callback.message.delete()
    if len(USER_LEXICON[callback.data]) > 0:
        await callback.message.answer(USER_LEXICON[callback.data])


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

    try:
        balance = float(command.args.strip())
        users_status[message.from_user.id]["card"]["card_balance"] = balance

        async with async_session() as session:
            stmt = insert(Card).values(
                name=users_status[message.from_user.id]["card"]["card_name"],
                card_type=CardType.debit_card,
                tg_id=message.from_user.id,
                balance=balance
            )

        users_status[message.from_user.id] = deepcopy(user_dict_template)
        await session.execute(stmt)
        await session.commit()
        await message.answer(text=USER_LEXICON["card_is_create"])

    except ValueError:
        await message.answer(USER_LEXICON["card_balance"]["incorrect_balance"])


@router.callback_query(F.data[:8] == "del_card")
async def del_card(callback: CallbackQuery):
    card_id = int(callback.data[8:])
    async with async_session() as session:
        to_delete = delete(Card).where(Card.id == card_id)
        await session.execute(to_delete)
        await session.commit()

    await callback.message.delete()
    await callback.message.answer(USER_LEXICON["success_del_card"])


@router.callback_query(F.data[:8] == "upd_card")
async def upd_card(callback: CallbackQuery):
    card_id = int(callback.data[8:])
    await callback.message.edit_text(
        text=USER_LEXICON["update_elem_in_card"],
        reply_markup=create_card_update_keyboard(card_id)
    )


@router.callback_query(F.data[:8] == "upd_name")
async def upd_card_name(callback: CallbackQuery):
    card_id = int(callback.data[8:])
    if callback.from_user.id not in users_status:
        users_status[callback.from_user.id] = deepcopy(user_dict_template)
    users_status[callback.from_user.id]["upd_card"]["create_name"] = True
    users_status[callback.from_user.id]["upd_card"]["card_id"] = card_id

    await callback.message.edit_text(
        text=USER_LEXICON["update_card_name"]["name"],
        reply_markup=create_exit_show_card_keyboard("exit_update")
    )


@router.message(Command(commands="upd_card_name"))
async def set_upd_card_name(message: Message, command: CommandObject):
    if message.from_user.id not in users_status:
        users_status[message.from_user.id] = deepcopy(user_dict_template)

    if not users_status[message.from_user.id]["upd_card"]["create_name"]:
        await message.answer(USER_LEXICON["access_error"])
        return

    if command.args is None:
        await message.answer(USER_LEXICON["update_card_name"]["empty_name"])
        return

    async with async_session() as session:
        card_id = users_status[message.from_user.id]["upd_card"]["card_id"]
        stmt = update(Card).where(Card.id == card_id).values(name=command.args)
        await session.execute(stmt)
        await session.commit()

    users_status[message.from_user.id]["card"]["create_name"] = False
    users_status[message.from_user.id]["upd_card"]["card_id"] = 0

    await message.answer(USER_LEXICON["update_card_name"]["successful_upd"])


@router.callback_query(F.data[:8] == "upd_bala")
async def upd_card_balance(callback: CallbackQuery):
    card_id = int(callback.data[8:])
    if callback.from_user.id not in users_status:
        users_status[callback.from_user.id] = deepcopy(user_dict_template)
    users_status[callback.from_user.id]["upd_card"]["create_balance"] = True
    users_status[callback.from_user.id]["upd_card"]["card_id"] = card_id

    await callback.message.edit_text(
        text=USER_LEXICON["update_card_balance"]["balance"],
        reply_markup=create_exit_show_card_keyboard("exit_update")
    )


@router.message(Command(commands="upd_card_balance"))
async def set_upd_card_balance(message: Message, command: CommandObject):
    if message.from_user.id not in users_status:
        users_status[message.from_user.id] = deepcopy(user_dict_template)

    if not users_status[message.from_user.id]["upd_card"]["create_balance"]:
        await message.answer(USER_LEXICON["access_error"])
        return

    if command.args is None:
        await message.answer(USER_LEXICON["upd_card_balance"]["empty_balance"])
        return

    try:
        balance = float(command.args.strip())

        async with async_session() as session:
            card_id = users_status[message.from_user.id]["upd_card"]["card_id"]
            stmt = update(Card).where(Card.id == card_id).values(balance=balance)
            await session.execute(stmt)
            await session.commit()

        users_status[message.from_user.id]["card"]["create_balance"] = False
        users_status[message.from_user.id]["upd_card"]["card_id"] = 0

        await message.answer(USER_LEXICON["update_card_balance"]["successful_upd"])

    except ValueError:
        await message.answer(USER_LEXICON["update_card_balance"]["incorrect_balance"])
