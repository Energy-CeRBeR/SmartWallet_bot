commands_dict = {
    '/start': 'Запуск бота',
    '/help': 'Информация о боте',
    '/cards': 'Список добавленных карт',
    '/add_card': 'Добавить карту',
    '/in_categories': 'Список категорий доходов',
    '/ex_categories': 'Список категорий расходов',
    '/add_in_category': 'Добавить категорию дохода',
    '/add_ex_category': 'Добавить категорию расхода',
    '/incomes': 'Список всех доходов',
    '/expenses': 'Список всех расходов',
    '/add_income': 'Добавить доход',
    '/add_expense': 'Добавить расход'
}

LIMITS: dict[str, int] = {
    "max_elements_in_keyboard": 10,
    "max_elements_ex_keyboard": 10,
    "max_number_of_cards": 10,
    "max_number_of_categories": 100,
}
