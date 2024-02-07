from aiogram.filters import Command, StateFilter
from aiogram.fsm.state import default_state
from aiogram.types import Message, InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery
from aiogram import Router, F
from sqlalchemy.ext.asyncio import AsyncSession

from services.user import register_user, get_routes_user

router = Router()

btn_routes_start = InlineKeyboardButton(text='Мои маршруты', callback_data='menu_routes_start')
btn_registrate = InlineKeyboardButton(text='Регистрация', callback_data='menu_registrate')
btn_help = InlineKeyboardButton(text='Помощь', callback_data='menu_help')
btn_support = InlineKeyboardButton(text='Написать разработчику', callback_data='menu_support')
btn_about = InlineKeyboardButton(text='О нас', callback_data='menu_about')

btn_routes_new = InlineKeyboardButton(text='Новый маршрут', callback_data='menu_routes_create')
btn_routes_back_menu = InlineKeyboardButton(text='Вернуться в меню', callback_data='menu_routes_back_menu')

@router.message(Command(commands='menu'))
async def process_start_menu(message: Message, session: AsyncSession):
    if await register_user(message.from_user.id, session) is False:
        keyboard_menu = InlineKeyboardMarkup(inline_keyboard=[[btn_registrate], [btn_help, btn_support], [btn_about]])
    else:
        keyboard_menu = InlineKeyboardMarkup(inline_keyboard=[[btn_routes_start], [btn_help, btn_support], [btn_about]])
    await message.answer(text='Меню', reply_markup=keyboard_menu)

@router.callback_query(F.data == 'menu_routes_start', StateFilter(default_state))
async def process_routes_start(callback: CallbackQuery, session: AsyncSession):
    keyboard_routes = [[btn_routes_new, btn_routes_back_menu]]
    if await register_user(callback.message.chat.id, session):
        routes = (await get_routes_user(callback.message.chat.id, session)).fetchall()
        if len(routes) != 0:
            for id, name, time_end in routes:
                keyboard_routes = [[InlineKeyboardButton(text=f'{name}, {time_end}', callback_data=f'route_{id}')]] + keyboard_routes
        await callback.message.edit_text(text='Все мои маршруты', reply_markup=InlineKeyboardMarkup(inline_keyboard=keyboard_routes))
    else:
        await callback.message.edit_reply_markup()
        await callback.message.answer(text='Необходимо зарегистрироваться\n/registration или /menu')
