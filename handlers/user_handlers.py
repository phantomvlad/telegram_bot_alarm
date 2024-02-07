from aiogram.filters import Command
from aiogram.types import Message, InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery
from aiogram import Router, F

from lexicon.lexicon import LEXICON_RU
from config.config import ConfigResult

router = Router()

config: ConfigResult = ConfigResult('./.env')

url_button_creator = InlineKeyboardButton(
    text='Написать разработчику',
    url=f'tg://user?id={config.tg_bot.creator}'
)
btn_routes_back_menu = InlineKeyboardButton(text='Вернуться в меню', callback_data='menu_routes_back_menu')

keyboard = InlineKeyboardMarkup(inline_keyboard=[[url_button_creator], [btn_routes_back_menu]])
keyboard_back = InlineKeyboardMarkup(inline_keyboard=[[btn_routes_back_menu]])

@router.message(Command(commands='start'))
async def process_start_command(message: Message) -> None:
    await message.answer(text=LEXICON_RU['/start'], reply_markup=keyboard_back)

@router.message(Command(commands='help'))
async def process_help_command(message: Message) -> None:
    await message.answer(text=LEXICON_RU['/help'], reply_markup=keyboard_back)

@router.callback_query(F.data == 'menu_help')
async def process_help_callback(callback: CallbackQuery):
    await callback.message.edit_reply_markup()
    await callback.message.edit_text(text=LEXICON_RU['/help'], reply_markup=keyboard_back)

@router.message(Command(commands='menu'))
async def process_menu_command(message: Message) -> None:
    await message.answer(text=LEXICON_RU['/menu'])

@router.message(Command(commands='about'))
async def process_about_command(message: Message) -> None:
    await message.answer(text=LEXICON_RU['/about'], reply_markup=keyboard_back)

@router.callback_query(F.data == 'menu_about')
async def process_about_callback(callback: CallbackQuery) -> None:
    await callback.message.edit_reply_markup()
    await callback.message.edit_text(text=LEXICON_RU['/about'], reply_markup=keyboard_back)

@router.message(Command(commands='support'))
async def process_about_command(message: Message) -> None:
    await message.answer(text=LEXICON_RU['/support'], reply_markup=keyboard)

@router.callback_query(F.data == 'menu_support')
async def process_support_callback(callback: CallbackQuery) -> None:
    await callback.message.edit_reply_markup()
    await callback.message.answer(text=LEXICON_RU['/support'], reply_markup=keyboard)