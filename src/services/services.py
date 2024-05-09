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


def transaction_pagination(transactions: list, cur_page: int, to_do: str, limit: int = 9) -> list:
    if to_do == "next":
        return transactions[cur_page * limit: cur_page * limit + 9]
    else:
        return transactions[(cur_page - 9) * limit:(cur_page - 9) * limit + 9]
