from aiogram import Bot, Dispatcher, F, types
from aiogram.filters import Command, CommandStart, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import default_state, State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import (CallbackQuery, InlineKeyboardButton,
                           InlineKeyboardMarkup, Message, PhotoSize)
from aiogram.methods import SendContact
from sqlalchemy.orm import session
from sqlalchemy import text

from database.models.user import User
from aiogram import Router
from sqlalchemy.ext.asyncio import AsyncSession

router = Router()

class FSMRegistrationForm(StatesGroup):
    user_name = State()
    user_phone = State()

button_phone = types.KeyboardButton(
    text = 'Отправить номер телефона',
    request_contact=True,
)

keyboard = types.ReplyKeyboardMarkup(keyboard=[[button_phone]], resize_keyboard=True)

@router.message(Command(commands='registration'), StateFilter(default_state))
async def process_start_registration(message: Message, session: AsyncSession, state: FSMContext):
    users = await session.execute(text(f"SELECT * FROM users WHERE user_id={message.from_user.id}"))

    if users.fetchone() is not None:
        await message.answer(text='Вы уже зарегистрированы')
    else:
        await message.answer(text='Пожалуйста, введите ваше имя')
        await state.set_state(FSMRegistrationForm.user_name)

@router.message(StateFilter(FSMRegistrationForm.user_name), F.text.isalpha())
async def process_name_sent(message: Message, state: FSMContext):
    await state.update_data(user_name = message.text)
    await message.answer(text='Отправьте номер телефона', reply_markup=keyboard)
    await state.set_state(FSMRegistrationForm.user_phone)

@router.message(StateFilter(FSMRegistrationForm.user_phone))
async def process_number_sent(message: Message, state: FSMContext, session: AsyncSession ):
    user_phone = message.contact.phone_number
    await state.update_data(user_phone = user_phone)
    data = await state.get_data()
    user = User(user_id=message.from_user.id, name=data['user_name'], phone = data['user_phone'])
    session.add(user)
    await session.commit()
    await message.answer(text='Вы зарегистрированы')
    await state.clear()
