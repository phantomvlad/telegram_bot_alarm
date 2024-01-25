from aiogram import Bot
from aiogram.types import BotCommand

async def set_main_menu(bot: Bot) -> None:
    main_menu_commands = [
        BotCommand(command='/help',
                   description='Справка по работе бота'),
        BotCommand(command='/support',
                   description='Поддержка'),
        BotCommand(command='/contacts',
                   description='Другие способы связи'),
        BotCommand(command='/start',
                   description='Приветствие бота')
    ]

    await bot.set_my_commands(main_menu_commands)