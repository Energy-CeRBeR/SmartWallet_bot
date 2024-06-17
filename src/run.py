import asyncio

from aiogram import Dispatcher, Bot
from aiogram.fsm.storage.redis import RedisStorage, Redis

from config_data.config import Config, load_config

from src.user.handlers import router as user_router
from src.card_operations.handlers import router as card_router
from src.transactions.in_categories_handlers import router as in_categories_router
from src.transactions.ex_categories_handlers import router as ex_categories_router
from src.transactions.incomes_handlers import router as income_transactions_router
from src.transactions.expenses_handlers import router as expenses_transactions_router


async def main():
    config: Config = load_config(".env")
    bot = Bot(token=config.tg_bot.token, parse_mode="HTML")
    redis = Redis(host=config.tg_bot.redis_host)
    storage = RedisStorage(redis=redis)
    dp = Dispatcher(storage=storage)

    dp.include_routers(
        card_router,
        in_categories_router,
        ex_categories_router,
        income_transactions_router,
        expenses_transactions_router,
        user_router
    )

    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
