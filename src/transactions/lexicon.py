from src.database.models import Income, IncomeCategory, Card, Expense, ExpenseCategory


def print_category_info(category) -> str:
    text = (f"Текущая категория: {category.name}\n"
            f"Выберите действия:")
    return text


def print_income_info(income: Income, income_category: IncomeCategory, card: Card, description: str) -> str:
    text = f"""
{LEXICON["income_info"]["info"]}


{LEXICON["income_info"]["category"]}:    <b>{income_category.name}</b>

{LEXICON["income_info"]["card"]}:    <b>{card.name}</b>

{LEXICON["income_info"]["amount"]}:    <b>{income.amount} ₽</b>

{LEXICON["income_info"]["date"]}:    <b>{income.date}</b>

{LEXICON["income_info"]["description"]}:    <b>{description}</b>
"""

    return text


def print_expense_info(expense: Expense, expense_category: ExpenseCategory, card: Card, description: str) -> str:
    text = f"""
{LEXICON["expense_info"]["info"]}


{LEXICON["expense_info"]["category"]}:    <b>{expense_category.name}</b>

{LEXICON["expense_info"]["card"]}:    <b>{card.name}</b>

{LEXICON["expense_info"]["amount"]}:    <b>{expense.amount} ₽</b>

{LEXICON["expense_info"]["date"]}:    <b>{expense.date}</b>

{LEXICON["expense_info"]["description"]}:    <b>{description}</b>
"""

    return text


LEXICON: dict = {
    "income": {
        "empty_category_name": "⛔ Название категории дохода не может быть пустым! Повторите попытку 👇",
        "incorrect_name": "⛔ Длина названия категории не должна превышать 64 символа! Повторите попытку 👇",
        "add_income_category": "💬 Введите название новой категории доходов 👇",
        "category_is_create": "✅ Новая категория доходов успешно создана!",
        "no_categories": "🤔 Пока что у вас нет ни одной категории доходов!",
        "incomes_list": "📋 Ваш список доходов 📋",
        "categories_list": "📋 Ваши категории доходов 📋"
    },
    "expense": {
        "empty_category_name": "⛔ Название категории расхода не может быть пустым! Повторите попытку 👇",
        "incorrect_name": "⛔ Длина названия категории не должна превышать 64 символа! Повторите попытку 👇",
        "add_expense_category": "💬 Введите название новой категории расходов 👇",
        "category_is_create": "✅ Новая категория расходов успешно создана!",
        "no_categories": "🤔 Пока что у вас нет ни одной категории расходов!",
        "expenses_list": "📋 Ваш список расходов 📋",
        "categories_list": "📋 Ваши категории расходов 📋"
    },

    "income_transactions": {
        "no_categories": "❗ Вам нужно добавить хотя бы одну категорию доходов для выполнения данной операции!",
        "amount": "💲 Введите размер дохода 💲",
        "empty_amount": "⛔ Размер дохода не может быть пустым! Повторите попытку 👇",
        "income_is_create": "✅ Доход успешно добавлен!",
        "incorrect_amount": "⛔ Размер дохода должен иметь целочисленный положительный тип данных! "
                            "Повторите попытку 👇",
        "no_incomes": "🤔 У вас пока что нет ни одного дохода!"
    },
    "expense_transactions": {
        "no_categories": "❗ Вам нужно добавить хотя бы одну категорию расходов для выполнения данной операции!",
        "amount": "💲 Введите размер расхода 💲",
        "empty_amount": "⛔ Размер расхода не может быть пустым! Повторите попытку 👇",
        "expense_is_create": "✅ Расход успешно добавлен!",
        "incorrect_amount": "⛔ Размер расхода должен иметь целочисленный положительный тип данных! "
                            "Повторите попытку 👇",
        "no_expenses": "🤔 У вас пока что нет ни одного расхода!"
    },

    "income_info": {
        "info": "<b>Информация о доходе 📈:</b>",
        "category": "<b>Категория дохода 📥</b> ",
        "card": "<b>Название карты 💳</b>",
        "date": "<b>Дата операции 🗓️</b>",
        "amount": "<b>Размер дохода 💰</b>",
        "description": "<b>Описание дохода 📝</b>",
        "no_description": "<b>Отсутствует 🤷🏻‍♂️‍</b> ️",
    },

    "expense_info": {
        "info": "<b>Информация о расходе 📉:</b>",
        "category": "<b>Категория расхода 📥</b>",
        "card": "<b>Название карты 💳</b>",
        "date": "<b>Дата операции 🗓️</b>",
        "amount": "<b>Размер расхода 💸</b>",
        "description": "<b>Описание расхода 📝</b>",
        "no_description": "<b>Отсутствует 🤷🏻‍♂️‍</b> ️",
    },

    "edit_income": {
        "new_category": "📁 Выберите новую категорию дохода 👇",
        "category_is_update": "✅ Категория дохода успешно обновлена!",
        "new_amount": "💰 Введите новый размер дохода 👇",
        "amount_is_update": "✅ Размер дохода успешно обновлен!",
        "new_description": "📝 Введите новое описание дохода 👇",
        "description_is_update": "✅ Описание дохода успешно обновлено",
        "new_date": "🗓️ Введите новую дату операции в формате: дд.мм.гггг 👇",
        "date_is_update": "✅ Дата операции успешно обновлена!",
        "new_card": "💳 Выберите новую карту из списка👇",
        "card_is_update": "✅ Карта успешно обновлена!",
    },
    "edit_expense": {
        "new_category": "📁 Выберите новую категорию расхода 👇",
        "category_is_update": "✅ Категория расхода успешно обновлена!",
        "new_amount": "💰 Введите новый размер расхода 👇",
        "amount_is_update": "✅ Размер расхода успешно обновлен!",
        "new_description": "📝 Введите новое описание расхода 👇",
        "description_is_update": "✅ Описание расхода успешно обновлено",
        "new_date": "🗓️ Введите новую дату операции в формате: дд.мм.гггг 👇",
        "date_is_update": "✅ Дата операции успешно обновлена!",
        "new_card": "💳 Выберите новую карту из списка 👇",
        "card_is_update": "✅ Карта успешно обновлена!",
    },

    "incomes": "📋 Список доходов 📋",
    "expenses": "📋 Список расходов 📋",

    "get_current_in_category": "🔙 К текущей категории дохода",
    "get_current_ex_category": "🔙 К текущей категории расхода",
    "get_in_categories_list": "📋 Просмотреть список категорий доходов 📋",
    "get_ex_categories_list": "📋 Просмотреть список категорий расходов 📋",
    "goto_in_categories_list": "🔙 К списку категорий доходов",
    "goto_ex_categories_list": "🔙 К списку категорий расходов",

    "get_current_income": "🔙 К текущему доходу",
    "get_current_expense": "🔙 К текущему расходу",
    "get_incomes_list": "📋 Просмотреть список доходов 📋",
    "get_expenses_list": "📋 Просмотреть список расходов📋 ",
    "goto_in_list": "🔙 К списку доходов",
    "goto_ex_list": "🔙 К списку расходов",

    "incorrect_date": "⛔ Дата операции должна быть в формате: дд.мм.гггг. Повторите попытку 👇",
    "add_date": "🗓️ Вы хотите добавить дату? По умолчанию будет выбрана текущая дата",
    "get_date": "🗓️ Введите новую дату операции в формате: дд.мм.гггг 👇",
    "description": "❓ Хотите Добавить описание к транзакции?",
    "incorrect_description": "⛔ Длина описания к транзакции не должна превышать 500 символов! Повторите попытку 👇",
    "get_description": "📝 Введите описание транзакции 👇",
    "set_description": "✅ Описание успешно добавлено!",
    "commit_transaction": "➕ Добавить транзакцию",
    "no_cards": "⛔ Вам нужно добавить хотя бы одну карту для выполнения данной операции!",
    "back_show_categories": "❌ Выйти из просмотра ❌",
    "category_name_update": "Изменить название категории",
    "category_delete": "Удалить категорию",
    "successful_del_category": "✅ Категория успешно удалена!",
    "successful_upd_category_name": "✅ Название категории успешно обновлено!",
    "update_category_name": "💬 Введите название категории 👇",
    "card_list": "💳 Выберите карту из списка 👇",
    "access_error": "⛔ Отказано в доступе! ⛔",
    "cancel_create": "❌ Отменить создание! ❌",
    "cancel_edit": "❌ Отменить изменение! ❌",
    "exit_from_edit": "✅ Операция изменения отменена!",
    "exit": "❌ Выход ❌",
    "back_page": "◀️",
    "next_page": "▶️"
}

LEXICON_COMMANDS: dict = {
    "/add_income": "📁 Выберите категорию для вашего дохода 👇",
    "/add_expense": "📁 Выберите категорию для вашего расхода 👇"
}
