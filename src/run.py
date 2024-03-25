import asyncio

from aiogram import Dispatcher, Bot

from config_data.config import Config, load_config
from src.database.database import async_main

from src.user.handlers import router as user_router
from src.card_operations.handlers import router as card_router
from src.transactions.categories_handlers import router as categories_router
from src.transactions.transactions_handlers import router as transactions_router


async def main():
    await async_main()
    config: Config = load_config(".env")
    bot = Bot(token=config.tg_bot.token)
    dp = Dispatcher()

    dp.include_routers(
        user_router,
        card_router,
        categories_router,
        transactions_router
    )

    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
