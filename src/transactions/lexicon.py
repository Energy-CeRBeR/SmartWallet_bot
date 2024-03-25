def print_category_info(category) -> str:
    text = (f"Текущая категория: {category.name}\n"
            f"Выберите действия:")
    return text


LEXICON: dict = {
    "income": {
        "empty_category_name": "Название категории не может быть пустым! Повторите попытку.",
        "category_is_create": "Новая категория доходов успешно создана!",
        "no_categories": "Пока что у вас нет ни одной категории доходов!",
        "categories_list": "Ваши категории доходов:"
    },
    "expense": {
        "empty_category_name": "Название категории не может быть пустым! Повторите попытку.",
        "category_is_create": "Новая категория расходов успешно создана!",
        "no_categories": "Пока что у вас нет ни одной категории расходов!",
        "categories_list": "Ваши категории расходов:"
    },
    "back_show_categories": "Выйти из просмотра",
    "category_name_update": "Изменить название категории",
    "category_delete": "Удалить категорию",
    "successful_del_category": "Категория успешно удалена!",
    "successful_upd_category_name": "Название категории успешно обновлено!",
    "update_category_name": "Введите название категории командой\n"
                            "/upd_category_name <Новое название категории>:",
    "access_error": "Отказано в доступе!"
}

LEXICON_COMMANDS: dict = {

}
