from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import default_state
from aiogram.types import Message, InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery
from aiogram import Router, F
from sqlalchemy.ext.asyncio import AsyncSession

from services.user import register_user

router = Router()

btn_routes_start = InlineKeyboardButton(text='Мои маршруты', callback_data='menu_routes_start')
btn_registrate = InlineKeyboardButton(text='Регистрация', callback_data='menu_registrate')
btn_help = InlineKeyboardButton(text='Помощь', callback_data='menu_help')
btn_support = InlineKeyboardButton(text='Написать разработчику', callback_data='menu_support')
btn_about = InlineKeyboardButton(text='О нас', callback_data='menu_about')

btn_routes_new = InlineKeyboardButton(text='Новый маршрут', callback_data='menu_routes_create')
btn_routes_back_menu = InlineKeyboardButton(text='Вернуться в меню', callback_data='menu_routes_back_menu')

@router.message(Command(commands='menu'))
async def process_start_menu(message: Message, session: AsyncSession, state: FSMContext):
    await state.clear()
    if await register_user(message.from_user.id, session) is False:
        keyboard_menu = InlineKeyboardMarkup(inline_keyboard=[[btn_registrate], [btn_help, btn_support], [btn_about]])
    else:
        keyboard_menu = InlineKeyboardMarkup(inline_keyboard=[[btn_routes_start], [btn_help, btn_support], [btn_about]])
    await message.answer(text='Меню', reply_markup=keyboard_menu)

@router.callback_query(F.data == 'menu_routes_back_menu', StateFilter(default_state))
async def process_start_menu_callback(callback: CallbackQuery, session: AsyncSession):
    if await register_user(callback.message.chat.id, session) is False:
        keyboard_menu = InlineKeyboardMarkup(inline_keyboard=[[btn_registrate], [btn_help, btn_support], [btn_about]])
    else:
        keyboard_menu = InlineKeyboardMarkup(inline_keyboard=[[btn_routes_start], [btn_help, btn_support], [btn_about]])
    await callback.message.edit_text(text='Меню', reply_markup=keyboard_menu)
