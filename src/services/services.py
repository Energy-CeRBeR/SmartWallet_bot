import re


def _is_number(s: str) -> bool:
    s = s.replace(",", ".")

    if s.count(".") > 1:
        return False
    if re.match(r'\d+', s):
        return True
    elif re.match(r'\d+(\.\d+)?', s):
        return True
    else:
        return False


def isValidBalance(s: list) -> bool:
    if len(s) > 1:
        return False
    return _is_number(s[0])


def transaction_pagination(transactions: list, cur_page: int, to_do: str, limit: int = 9) -> list:
    if to_do == "next":
        return transactions[cur_page * limit: cur_page * limit + 9]
    else:
        return transactions[(cur_page - 9) * limit:(cur_page - 9) * limit + 9]
