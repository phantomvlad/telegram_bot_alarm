from aiogram import Bot, Dispatcher
from keyboards.set_menu import set_main_menu
import asyncio

from config.config import load_config, Config
from handlers import other_handlers, user_handlers

async def main() -> None:
    config: Config = load_config('.env')

    bot = Bot(token=config.tg_bot.token)
    dp = Dispatcher()

    dp.include_router(user_handlers.router)
    dp.include_router(other_handlers.router)

    await set_main_menu(bot)

    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())