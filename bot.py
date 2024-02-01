from aiogram import Bot, Dispatcher
from aiogram.utils.callback_answer import CallbackAnswerMiddleware
from aiogram.fsm.storage.redis import RedisStorage, Redis

from database.models.user import User
from database.models.route import Route
from keyboards.set_menu import set_main_menu
import asyncio

from config.config import load_config, Config
from handlers import other_handlers, user_handlers, registration_handlers
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from database.models.base import Base
from middlewares.db import DbSessionMiddleware

connect_postgres = None

async def main() -> None:
    config: Config = load_config('.env')

    engine = create_async_engine(url=f'postgresql+asyncpg://{config.db.db_user}:{config.db.db_password}@{config.db.db_host}:{config.db.db_port}/{config.db.database}', echo=True)
    sessionmaker = async_sessionmaker(engine, expire_on_commit=False)

    bot = Bot(token=config.tg_bot.token)
    redis = Redis(host='redis')
    storage = RedisStorage(redis=redis)

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    dp = Dispatcher(storage=storage)
    dp.update.middleware(DbSessionMiddleware(session_pool=sessionmaker))
    dp.callback_query.middleware(CallbackAnswerMiddleware())
    dp.include_router(registration_handlers.router)
    dp.include_router(user_handlers.router)
    dp.include_router(other_handlers.router)

    await set_main_menu(bot)

    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())