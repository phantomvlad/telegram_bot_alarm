from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import default_state
from aiogram.types import Message, InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery
from aiogram import Router, F
from sqlalchemy.ext.asyncio import AsyncSession

from lexicon.lexicon import LEXICON_RU
from config.config import ConfigResult

router = Router()

config: ConfigResult = ConfigResult('./.env')

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

@router.callback_query(F.data == 'menu_help')
async def process_help_callback(callback: CallbackQuery):
    await callback.message.edit_reply_markup()
    await callback.message.answer(text=LEXICON_RU['/help'], reply_markup=None)

@router.message(Command(commands='menu'))
async def process_menu_command(message: Message) -> None:
    await message.answer(text=LEXICON_RU['/menu'])

@router.message(Command(commands='about'))
async def process_about_command(message: Message) -> None:
    await message.answer(text=LEXICON_RU['/about'])

@router.callback_query(F.data == 'menu_about')
async def process_about_callback(callback: CallbackQuery) -> None:
    await callback.message.edit_reply_markup()
    await callback.message.answer(text=LEXICON_RU['/about'], reply_markup=None)

@router.message(Command(commands='support'))
async def process_about_command(message: Message) -> None:
    await message.answer(text=LEXICON_RU['/support'], reply_markup=keyboard)

@router.callback_query(F.data == 'menu_support')
async def process_support_callback(callback: CallbackQuery) -> None:
    await callback.message.edit_reply_markup()
    await callback.message.answer(text=LEXICON_RU['/support'], reply_markup=keyboard)