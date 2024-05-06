from aiogram.fsm.state import StatesGroup, State


class AddCardState(StatesGroup):
    add_type = State()
    add_name = State()
    add_balance = State()


class UpdCardState(StatesGroup):
    upd_name = State()
    upd_balance = State()


class AddIncomeCategoryState(StatesGroup):
    add_name = State()


class AddExpenseCategoryState(StatesGroup):
    add_name = State()


class UpdCategoryState(StatesGroup):
    upd_name = State()


class AddCategoryState(StatesGroup):
    select_card = State()
    add_amount = State()
    add_description = State()
    get_description = State()
    set_description = State()
    set_data = State()


class ShowIncomesState(StatesGroup):
    show_incomes = State()


class ShowExpenseState(StatesGroup):
    show_expenses = State()
