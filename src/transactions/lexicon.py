def print_category_info(category) -> str:
    text = (f"Текущая категория: {category.name}\n"
            f"Выберите действия:")
    return text


LEXICON: dict = {
    "income": {
        "empty_category_name": "Название категории не может быть пустым! Повторите попытку.",
        "add_income_category": "Введите название новой категории доходов:",
        "category_is_create": "Новая категория доходов успешно создана!",
        "no_categories": "Пока что у вас нет ни одной категории доходов!",
        "incomes_list": "Ваш список доходов:",
        "categories_list": "Ваши категории доходов:"
    },
    "expense": {
        "empty_category_name": "Название категории не может быть пустым! Повторите попытку.",
        "add_expense_category": "Введите название новой категории расходов:",
        "category_is_create": "Новая категория расходов успешно создана!",
        "no_categories": "Пока что у вас нет ни одной категории расходов!",
        "expenses_list": "Ваш список расходов:",
        "categories_list": "Ваши категории расходов:"
    },

    "income_transactions": {
        "no_categories": "Вам нужно добавить хотя бы одну категорию доходов для выполнения данной операции!",
        "amount": "Введите размер дохода",
        "empty_amount": "Размер дохода не может быть пустым!",
        "income_is_create": "Доход успешно добавлен!",
        "incorrect_amount": "Размер дохода должен иметь целочисленный тип данных!",
        "no_incomes": "У вас пока что нет ни одного дохода!"
    },
    "expense_transactions": {
        "no_categories": "Вам нужно добавить хотя бы одну категорию расходов для выполнения данной операции!",
        "amount": "Введите размер расхода",
        "empty_amount": "Размер расхода не может быть пустым!",
        "income_is_create": "Расход успешно добавлен!",
        "incorrect_amount": "Размер расхода должен иметь целочисленный тип данных!"
    },

    "income_info": {
        "info": "Информация о доходе:",
        "category": "Категория дохода",
        "date": "Дата операции",
        "amount": "Размер дохода",
        "description": "Описание дохода",
        "no_description": "Отсутствует",
    },

    "expense_info": {
        "info": "Информация о расходе:",
        "category": "Категория расхода:",
        "date": "Дата операции:",
        "amount": "Размер расхода:",
        "description": "Описание расхода:",
        "no_description": "Отсутствует",
    },

    "edit_income": {
        "new_category": "Выберите новую категорию дохода:",
        "category_is_update": "Категория дохода успешно обновлена!",
        "new_amount": "Введите новый размер дохода:",
        "amount_is_update": "Размер дохода успешно обновлен!",
    },

    "description": "Хотите Добавить описание к транзакции?",
    "get_description": "Введите описание транзакции:",
    "set_description": "Описание успешно добавлено!",
    "commit_transaction": "Добавить транзакцию",
    "no_cards": "Вам нужно добавить хотя бы одну карту для выполнения данной операции!",
    "back_show_categories": "Выйти из просмотра",
    "category_name_update": "Изменить название категории",
    "category_delete": "Удалить категорию",
    "successful_del_category": "Категория успешно удалена!",
    "successful_upd_category_name": "Название категории успешно обновлено!",
    "update_category_name": "Введите название категории: ",
    "card_list": "Выберите карту из списка:",
    "access_error": "Отказано в доступе!",
    "cancel_create": "Отменить создание!",
    "cancel_edit": "Отменить изменение!",
    "exit_from_exit": "Операция изменения отменена!",
    "back_page": "<<",
    "next_page": ">>"
}

LEXICON_COMMANDS: dict = {
    "/add_income": "Выберите категорию для вашего дохода:",
    "/add_expense": "Выберите категорию для вашего расхода:"
}
