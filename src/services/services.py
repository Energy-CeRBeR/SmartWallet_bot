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


def pagination(data: list, cur_page: int, limit: int = 9) -> list:
    return data[cur_page * limit: cur_page * limit + 9]
