from aiogram import Bot
from aiogram.types import BotCommand

async def set_main_menu(bot: Bot) -> None:
    main_menu_commands = [
        BotCommand(command='/registration',
                   description='Регистрация'),
        BotCommand(command='/routes',
                   description='Мои маршруты'),
        BotCommand(command='/about',
                   description='Подробнее о боте'),
        BotCommand(command='/start',
                   description='Приветствие бота'),
        BotCommand(command='/help',
                   description='Помощь'),
        BotCommand(command='/support',
                   description='Служба поддержки'),
    ]
    await bot.set_my_commands(main_menu_commands)