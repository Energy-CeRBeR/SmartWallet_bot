from src.database.models import Card

'''def card_list(text: str, card: Card) -> str:
    text = (f"{text}\n\n"
            f"Название карты: {card.name}\n"
            f"Тип карты: Дебетовая\n"
            f"Баланс: {card.balance}")
    return text'''


def print_card_info(card: Card) -> str:
    text = (f"Название карты: {card.name}\n"
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
    "update_card_name": {
        "name": "Введите название вашей карты командой\n"
                "/upd_card_name <Новое название карты>:",
        "back": "Отменить создание",
        "empty_name": "Название карты не можем быть пустым! Повторите попытку",
        "successful_upd": "Название карты успешно обновлено!"
    },
    "card_balance": {
        "balance": "Введите баланс вашей карты командой\n"
                   "/card_balance <баланс карты>",
        "empty_balance": "Баланс не может быть пустым! Повторите попытку",
        "incorrect_balance": "Баланс должен иметь численный тип данных!"
    },
    "update_card_balance": {
        "balance": "Введите баланс вашей карты командой\n"
                   "/upd_card_balance <Новый баланс карты>",
        "empty_balance": "Баланс не может быть пустым! Повторите попытку",
        "incorrect_balance": "Баланс должен иметь численный тип данных!",
        "successful_upd": "Баланс карты успешно обновлён!"
    },
    "card_info": {
        "name": "Название карты",
        "type": "Тип карты",
        "balance": "Баланс карты"
    },
    "card_is_create": "Ваша карта успешно создана!\n"
                      "/cards для просмотра всех карт",
    "back_show_card": "Выйти из просмотра",
    "exit_update": "Отменить обновление",
    "cancel[show_card]": "",
    "cancel[create_card]": "Операция создания отменена!",
    "success_del_card": "Карта успешно удалена!",
    "card_update": "Обновить карту",
    "card_delete": "Удалить карту",
    "update_elem_in_card": "Выберите, что хотите обновить",
    "access_error": "Отказано в доступе!"
}

LEXICON_COMMANDS: dict = {
    "/cards": {
        "card_list": "Вот ваш список карт:",
        "no_cards": "Пока что у вас нет ни одной карты!"
    },
    "/add_card": "Давайте приступим! Для начала выберите тип карты"
}
