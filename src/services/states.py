from aiogram.fsm.state import StatesGroup, State


class AddCardState(StatesGroup):
    add_type = State()
    add_name = State()
    add_balance = State()


class UpdCardState(StatesGroup):
    upd_name = State()
    upd_balance = State()
