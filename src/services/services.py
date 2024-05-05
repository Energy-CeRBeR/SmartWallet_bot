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


def transaction_pagination(transactions: list, cur_page: int, pages: int, limit=10) -> list:
    if len(transactions) > limit * (cur_page + 1):
        return transactions[(cur_page + 1) * limit: (cur_page + 2) * limit]
    else:
        return []
