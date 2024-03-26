user_dict_template: dict = {
    "card": {
        "create_name": False,
        "card_type": "debit_card",
        "card_name": "",
        "create_balance": False,
        "balance": 0
    },
    "upd_card": {
        "card_id": 0,
        "create_name": False,
        "create_balance": False,
    },
    "upd_category": {
        "category_id": 0,
        "category_type": None
    },
    "transactions": {
        "category_type": None,
        "category_type_str": None,
        "category_id": 0,
        "card_id": 0,
        "amount": 0
    }
}

users_status: dict = {}
