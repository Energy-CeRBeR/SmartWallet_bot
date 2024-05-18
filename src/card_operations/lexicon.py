from src.database.models import Card


def print_card_info(card: Card) -> str:
    text = f"""
    💳 <b>Информация о карте:</b>
    
Название карты: <b>{card.name}</b>
Тип карты: <b>Дебетовая</b>
Баланс: <b>{card.balance} ₽</b>
"""

    return text


CARD_OPERATIONS_LEXICON: dict = {
    "card_types": {
        "debit_card": "Дебетовая карта",
        "credit_card": "Кредитная карта",
        "incorrect_action": "❗ Для выбора типа карты нажмите на кнопку!",
        "back": "❌ Отменить создание ❌"
    },
    "card_name": {
        "name": "💬 Введите название вашей карты 👇",
        "back": "❌ Отменить создание ❌",
        "empty_name": "⛔ Название карты не можем быть пустым! Повторите попытку 👇",
        "incorrect_name": "⛔ Длина названия карты не должна превышать 64 символа! Повторите попытку 👇",
    },
    "update_card_name": {
        "name": "💬 Введите новое название вашей карты 👇",
        "incorrect_name": "⛔ Длина названия карты не должна превышать 64 символа! Повторите попытку 👇",
        "back": "❌ Отменить создание ❌",
        "empty_name": "⛔ Название карты не можем быть пустым! Повторите попытку 👇",
        "successful_upd": "✅ Название карты успешно обновлено!"
    },
    "card_balance": {
        "balance": "💰 Введите начальный баланс вашей карты 👇",
        "empty_balance": "⛔ Баланс не может быть пустым! Повторите попытку 👇",
        "incorrect_balance": "⛔ Баланс должен иметь численный тип данных! Повторите попытку 👇",
    },
    "update_card_balance": {
        "balance": "💰 Введите новый баланс вашей карты 👇",
        "empty_balance": "⛔ Баланс не может быть пустым! Повторите попытку 👇",
        "incorrect_balance": "⛔ Баланс должен иметь численный тип данных! Повторите попытку 👇",
        "successful_upd": "✅ Баланс карты успешно обновлён!"
    },
    "card_info": {
        "name": "Название карты",
        "type": "Тип карты",
        "balance": "Баланс карты"
    },
    "get_current_card": "💳 Просмотреть текущую карту 💳",
    "get_cards_list": "📋 Просмотреть список карт 📋",
    "incomes": "📋 Список доходов 📋",
    "expenses": "📋 Список расходов 📋",
    "card_is_create": "✅ Ваша карта успешно создана!",
    "goto_cards_list": "🔙 Вернуться к списку карт",
    "back_show_card": "❌ Выйти из просмотра ❌",
    "exit_update": "❌ Отменить обновление ❌",
    "cancel[show_card]": "",
    "cancel[create_card]": "✅ Операция создания отменена!",
    "cancel_edit": "❌ Отменить изменение! ❌",
    "success_del_card": "✅ Карта успешно удалена!",
    "card_update": "Обновить карту",
    "card_delete": "Удалить карту",
    "update_elem_in_card": "🔄 Выберите, что хотите обновить 🔄",
    "access_error": "⛔ Отказано в доступе! ⛔",
    "no_credit_card": "⏳ Данный тип карт в разработке! ⏳"
}

LEXICON_COMMANDS: dict = {
    "/cards": {
        "card_list": "📋 Вот ваш список карт 📋",
        "no_cards": "🤔 Пока что у вас нет ни одной карты!"
    },
    "/add_card": "⚡ Давайте приступим! Для начала выберите тип карты 👇"
}
