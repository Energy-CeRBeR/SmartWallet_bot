from aiogram.fsm.state import StatesGroup, State


class ShowCardState(StatesGroup):
    show_card = State()


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


class AddIncomeState(StatesGroup):
    select_category = State()
    select_card = State()
    add_date = State()
    set_date = State()
    add_amount = State()
    add_description = State()
    get_description = State()
    set_description = State()
    set_data = State()


class AddExpenseState(StatesGroup):
    select_category = State()
    select_card = State()
    add_date = State()
    set_date = State()
    add_amount = State()
    add_description = State()
    get_description = State()
    set_description = State()
    set_data = State()


class ShowIncomesCategoryState(StatesGroup):
    show_category = State()


class ShowExpensesCategoryState(StatesGroup):
    show_category = State()


class ShowIncomesState(StatesGroup):
    show_incomes = State()
    set_new_category = State()
    set_new_card = State()
    set_new_amount = State()
    set_new_description = State()
    set_new_date = State()


class ShowExpensesState(StatesGroup):
    show_expenses = State()
    set_new_category = State()
    set_new_card = State()
    set_new_amount = State()
    set_new_description = State()
    set_new_date = State()
