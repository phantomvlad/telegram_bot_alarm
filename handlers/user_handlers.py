from aiogram.filters import Command, CommandStart
from aiogram.types import Message, KeyboardButton, ReplyKeyboardRemove
from aiogram.utils.keyboard import ReplyKeyboardBuilder
from aiogram import Router
from lexicon.lexicon import LEXICON_RU

router = Router()

builder_bt = ReplyKeyboardBuilder()
buttons: list[KeyboardButton] = []

button_help = KeyboardButton(text='Помощь 💬')

buttons.append(button_help)
builder_bt.add(*buttons)
builder_bt.adjust(2)

@router.message(CommandStart())
async def process_start_command(message: Message) -> None:
    await message.answer(text=LEXICON_RU['/start'])

@router.message(Command(commands='help'))
async def process_help_command(message: Message) -> None:
    await message.answer(text=LEXICON_RU['/help'], reply_markup=ReplyKeyboardRemove())

@router.message(Command(commands='menu'))
async def process_start_command(message: Message) -> None:
    await message.answer(text='Меню', reply_markup=builder_bt.as_markup(resize_keyboard=True))
