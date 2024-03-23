from src.database.database import Card


def card_list(text: str, card: Card) -> str:
    text = (f"{text}\n\n"
            f"Название карты: {card.name}\n"
            f"Тип карты: Дебетовая\n"
            f"Баланс: {card.balance}")
    return text


LEXICON: dict = {
    "card_types": {
        "debit_card": "Дебетовая карта",
        "credit_card": "Кредитная карта",
        "back": "Отменить создание"
    },
    "card_name": {
        "name": "Введите название вашей карты командой\n"
                "/card_name <Название карты>:",
        "back": "Отменить создание",
        "empty_name": "Название карты не можем быть пустым! Повторите попытку"
    },
    "card_balance": {
        "balance": "Введите баланс вашей карты командой\n"
                   "/card_balance <баланс карты>",
        "empty_balance": "Баланс не может быть пустым! Повторите попытку",
        "incorrect_balance": "Баланс должен иметь численный тип данных!"
    },
    "card_is_create": "Ваша карта успешно создана!\n"
                      "/cards для просмотра всех карт",

    "cancel_operation": "Операция создания отменена!",
    "access_error": "Отказано в доступе!"
}

LEXICON_COMMANDS: dict = {
    "/cards": {
        "card_list": "Вот ваш список карт:",
        "no_cards": "Пока что у вас нет ни одной карты!"
    },
    "/add_card": "Давайте приступим! Для начала выберите тип карты"
}
