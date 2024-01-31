from aiogram.filters import Command
from aiogram.types import Message, InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import ReplyKeyboardBuilder
from aiogram import Router
from lexicon.lexicon import LEXICON_RU
from keyboards.create_inline_keyboard import create_inline_kb
from config.config import Config, load_config

router = Router()

config: Config = load_config('.env')

url_button_creator = InlineKeyboardButton(
    text='Написать разработчику',
    url=f'tg://user?id={config.tg_bot.creator}'
)

keyboard = InlineKeyboardMarkup(inline_keyboard=[[url_button_creator]])

@router.message(Command(commands='start'))
async def process_start_command(message: Message) -> None:
    await message.answer(text=LEXICON_RU['/start'])

@router.message(Command(commands='help'))
async def process_help_command(message: Message) -> None:
    await message.answer(text=LEXICON_RU['/help'])

@router.message(Command(commands='menu'))
async def process_menu_command(message: Message) -> None:
    await message.answer(text=LEXICON_RU['/menu'])

@router.message(Command(commands='about'))
async def process_about_command(message: Message) -> None:
    await message.answer(text=LEXICON_RU['/about'])

@router.message(Command(commands='support'))
async def process_about_command(message: Message) -> None:
    await message.answer(text=LEXICON_RU['/support'], reply_markup=keyboard)