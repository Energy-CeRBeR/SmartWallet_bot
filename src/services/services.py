from src.database.models import Income, Expense, IncomeCategory, ExpenseCategory, Card
from src.services.settings import LIMITS


def isValidDate(date: str) -> bool:
    try:
        day, month, year = map(int, date.split('.'))

        if year < 0:
            return False

        if month < 1 or month > 12:
            return False

        days_in_month = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]

        if year % 4 == 0 and (year % 100 != 0 or year % 400 == 0):
            days_in_month[1] = 29

        if day < 1 or day > days_in_month[month - 1]:
            return False

        return True

    except ValueError:
        return False


def pagination(data: list, cur_page: int, limit: int = LIMITS["max_elements_in_keyboard"]) -> list:
    return data[cur_page * limit: (cur_page + 1) * limit]


def isValidName(name: str) -> bool:
    if name[0] != "/" and 0 < len(name) < 64:
        return True
    return False


def isValidDescription(description: str) -> bool:
    print(len(description))
    if description[0] != "/" and 0 < len(description) < 500:
        return True
    return False


def unpack_in_category_model(in_category: IncomeCategory) -> dict:
    try:
        result = {
            "id": in_category.id,
            "name": in_category.name,
            "tg_id": in_category.tg_id
        }
        return result

    except AttributeError:
        in_category: dict
        return in_category


def unpack_ex_category_model(ex_category: ExpenseCategory) -> dict:
    try:
        result = {
            "id": ex_category.id,
            "name": ex_category.name,
            "tg_id": ex_category.tg_id
        }
        return result

    except AttributeError:
        ex_category: dict
        return ex_category


def unpack_income_model(income: Income) -> dict:
    try:
        result = {
            "id": income.id,
            "tg_id": income.tg_id,
            "category_id": income.category_id,
            "card_id": income.card_id,
            "amount": income.amount,
            "description": income.description,
            "date": str(income.date)
        }
        return result

    except AttributeError:
        income: dict
        return income


def unpack_expense_model(expense: Expense) -> dict:
    try:
        result = {
            "id": expense.id,
            "tg_id": expense.tg_id,
            "category_id": expense.category_id,
            "card_id": expense.card_id,
            "amount": expense.amount,
            "description": expense.description,
            "date": str(expense.date)
        }
        return result

    except AttributeError:
        expense: dict
        return expense


def unpack_card_model(card: Card) -> dict:
    try:
        result = {
            "id": card.id,
            "name": card.name,
            "card_type": str(card.card_type),
            "tg_id": card.tg_id,
            "balance": card.balance
        }
        return result

    except AttributeError:
        card: dict
        return card
