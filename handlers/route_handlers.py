from datetime import datetime

from aiogram import F
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import default_state, State, StatesGroup
from aiogram.types import Message, ReplyKeyboardRemove, KeyboardButton, InlineKeyboardButton, InlineKeyboardMarkup, \
    CallbackQuery

from sqlalchemy.exc import SQLAlchemyError

from database.models.route import Route

from aiogram import Router
from sqlalchemy.ext.asyncio import AsyncSession

from services.filters import DaysFilter, WeekFilter, TimeFilter
from services.time import lat_lon_to_timezone
from services.api import request_to_get_time
from services.user import register_user
from services.routes import get_routes_user, get_route_id

router = Router()

class FSMCreateRouteForm(StatesGroup):
    title = State()
    start_g = State()
    stop_g = State()
    time_end = State()
    time_other = State()
    date_start = State()
    date_day = State()
    date_week = State()
    user_id = State()


WEEKS = {
    '1': 'понедельник',
    '2': 'вторник',
	'3': 'среда',
    '4': 'четверг',
    '5': 'пятница',
    '6': 'суббота',
    '7': 'воскресенье'
}

btn_date = InlineKeyboardButton(text='По датам', callback_data='days')
btn_week = InlineKeyboardButton(text='По дням недели', callback_data='week')
keyboard_days = InlineKeyboardMarkup(inline_keyboard=[[btn_date, btn_week]])

btn_routes_new = InlineKeyboardButton(text='Новый маршрут', callback_data='menu_routes_create')
btn_routes_back_menu = InlineKeyboardButton(text='Вернуться в меню', callback_data='menu_routes_back_menu')
btn_routes_start = InlineKeyboardButton(text='Назад', callback_data='menu_routes_start')

@router.message(Command(commands='routes'), StateFilter(default_state))
async def process_routes_all(message: Message, session: AsyncSession):
    keyboard_routes = [[btn_routes_new, btn_routes_back_menu]]
    if await register_user(message.from_user.id, session):
        routes = (await get_routes_user(message.from_user.id, session)).fetchall()
        if len(routes) != 0:
            for id, name, time_end in routes:
                keyboard_routes = [[InlineKeyboardButton(text=f'{name}, {time_end}',
                                                             callback_data=f'route_{id}')]] + keyboard_routes
        await message.answer(text='Все мои маршруты',
                                         reply_markup=InlineKeyboardMarkup(inline_keyboard=keyboard_routes))
    else:
        await message.answer(text='Необходимо зарегистрироваться\n/registration или /menu')

@router.callback_query(F.data == 'menu_routes_start', StateFilter(default_state))
async def process_routes_start(callback: CallbackQuery, session: AsyncSession):
    keyboard_routes = [[btn_routes_new, btn_routes_back_menu]]
    if await register_user(callback.message.chat.id, session):
        routes = (await get_routes_user(callback.message.chat.id, session)).fetchall()
        if len(routes) != 0:
            for id, title, time_end in routes:
                keyboard_routes = [[InlineKeyboardButton(text=f'{title}, {time_end}',
                                                         callback_data=f'route_{id}')]] + keyboard_routes
        await callback.message.edit_text(text='Все мои маршруты', reply_markup=InlineKeyboardMarkup(inline_keyboard=keyboard_routes))
    else:
        await callback.message.edit_reply_markup()
        await callback.message.answer(text='Необходимо зарегистрироваться\n/registration или /menu')

@router.message(Command(commands='cancel'), StateFilter(default_state))
async def process_cancel_create(message: Message):
    await message.answer(text='Вы не создаете маршрут')

@router.message(Command(commands='cancel'), ~StateFilter(default_state))
async def process_cancel_create(message: Message, state: FSMContext):
    await message.answer(text='Отмена создания маршрута', reply_markup=ReplyKeyboardRemove())
    await state.clear()

@router.message(Command(commands='route_create'), StateFilter(default_state))
async def process_start_create(message: Message, session: AsyncSession, state: FSMContext):
    if not await register_user(message.from_user.id, session):
        await message.answer(text='Для создания маршрута Вам нужно зарегистрироваться\n'
                                  '/registration')
        await state.set_state(default_state)
    else:
        await message.answer(text='Пожалуйста, сообщите геоданные о начальной точке.')
        await message.answer(text='Инструкция:\n'
                                  '1. Нажмите на значок скрепки (Поделиться)\n'
                                  '2. Нажмите "Геопозиция"\n'
                                  '3. Выберите необходимую точку начала маршрута\n'
                                  '4. Нажмите "Отправить выбранную геопозицию"', )
        await state.set_state(FSMCreateRouteForm.start_g)

@router.callback_query(F.data == 'menu_routes_create',StateFilter(default_state))
async def process_start_create_callback(callback: CallbackQuery, session: AsyncSession, state: FSMContext):
    keyboard_routes = [[btn_routes_new, btn_routes_back_menu]]
    if not await register_user(callback.message.chat.id, session):
        await callback.message.edit_reply_markup()
        await callback.message.edit_text(text='Для создания маршрута Вам нужно зарегистрироваться\n'
                                  '/registration')
        await state.set_state(default_state)
    else:
        await callback.message.edit_reply_markup()
        await callback.message.edit_text(text='Пожалуйста, сообщите геоданные о начальной точке.\n'
                                  'Инструкция:\n'
                                  '1. Нажмите на значок скрепки (Поделиться)\n'
                                  '2. Нажмите "Геопозиция"\n'
                                  '3. Выберите необходимую точку начала маршрута\n'
                                  '4. Нажмите "Отправить выбранную геопозицию"', )
        await state.set_state(FSMCreateRouteForm.start_g)

@router.message(StateFilter(FSMCreateRouteForm.start_g), lambda message: message.location is not None)
async def process_start_g_press(message: Message, state: FSMContext):
    await state.update_data(start=[message.location.latitude, message.location.longitude])
    await message.answer(text='Пожалуйста, сообщите геоданные о конечной точке.\n'
                              'Инструкция:\n'
                              '1. Нажмите на значок скрепки (Поделиться)\n'
                              '2. Нажмите "Геопозиция"\n'
                              '3. Выберите необходимую точку конца маршрута\n'
                              '4. Нажмите "Отправить выбранную геопозицию"')
    await state.set_state(FSMCreateRouteForm.stop_g)

@router.message(StateFilter(FSMCreateRouteForm.start_g))
async def process_start_g_error(message: Message):
    await message.answer(text='Вы прислали что-то не то')

@router.message(StateFilter(FSMCreateRouteForm.stop_g), lambda message: message.location is not None)
async def process_stop_g_press(message: Message, state: FSMContext):
    await state.update_data(stop = [message.location.latitude, message.location.longitude])
    await message.answer(text='Уведомления будут в конкретные даты или повторятся по дням недели?',reply_markup=keyboard_days)
    await state.set_state(FSMCreateRouteForm.date_start)

@router.message(StateFilter(FSMCreateRouteForm.stop_g))
async def process_start_g_error(message: Message, state: FSMContext):
    await message.answer(text='Вы прислали что-то не то')
    await state.set_state(FSMCreateRouteForm.stop_g)

@router.callback_query(StateFilter(FSMCreateRouteForm.date_start), F.data == 'days')
async def process_days_press(callback: CallbackQuery, state: FSMContext):
    await callback.message.edit_reply_markup()
    await callback.message.edit_text(text='Введите дату или даты через пробел в формате\n"ДД.ММ.ГГГГ ДД.ММ.ГГГГ\n'
                                          'Например: 22.02.2024 24.02.2023"')
    await state.set_state(FSMCreateRouteForm.date_day)

@router.callback_query(StateFilter(FSMCreateRouteForm.date_start), F.data == 'week')
async def process_week_press(callback: CallbackQuery, state: FSMContext):
    await callback.message.edit_reply_markup()
    await callback.message.edit_text(text='Введите день или дни недели в которые хотите повторения уведомлений в формате\n'
                              '"пн вт ср чт пт сб вс"\n'
                              'Например: пн ср чт')
    await state.set_state(FSMCreateRouteForm.date_week)

@router.message(StateFilter(FSMCreateRouteForm.date_day), DaysFilter())
async def process_days_finish(message: Message, state: FSMContext, dates: dict[str]):
    await message.answer(text=f'Даты уведомлений: {message.text}')
    await state.update_data(date_day=dates)
    await state.update_data(date_week=None)
    await message.answer(text=f'Введите время приезда на работу\n'
                              f'Формат: чч:мм\n'
                              f'Например: 23:15 или 08:05')
    await state.set_state(FSMCreateRouteForm.time_end)

@router.message(StateFilter(FSMCreateRouteForm.date_day))
async def process_days_finish(message: Message, state: FSMContext):
    await message.answer(text='Вы ввели что-то не то')
    await state.set_state(FSMCreateRouteForm.date_day)

@router.message(StateFilter(FSMCreateRouteForm.date_week), WeekFilter())
async def process_days_finish(message: Message, state: FSMContext, dates: dict[int]):
    await message.answer(text=f'Дни недели для уведомлений: {message.text}')
    await state.update_data(date_week=dates)
    await state.update_data(date_day=None)
    await message.answer(text=f'Введите время приезда на работу\n'
                              f'Формат: чч:мм\n'
                              f'Например: 23:15 или 08:05')
    await state.set_state(FSMCreateRouteForm.time_end)

@router.message(StateFilter(FSMCreateRouteForm.date_week))
async def process_days_finish(message: Message):
    await message.answer(text='Вы ввели что-то не то')

@router.message(StateFilter(FSMCreateRouteForm.time_end), TimeFilter())
async def process_time_end(message: Message, state: FSMContext, time: str):
    await state.update_data(time_end=time)
    await message.answer(text='Введите время, которое вы тратите на прогрев авто и другие траты\n'
                              'Формат: чч:мм\n'
                              'Например: 0:15 или 00:05 (15 или 5 минут)')
    await state.set_state(FSMCreateRouteForm.time_other)

@router.message(StateFilter(FSMCreateRouteForm.time_end))
async def process_time_end_error(message: Message):
    await message.answer(text='Вы ввели что-то не то')

@router.message(StateFilter(FSMCreateRouteForm.time_other), TimeFilter())
async def process_time_other_final(message: Message, state: FSMContext, time: str):
    await state.update_data(time_other=time)
    await message.answer(text='Как назовете маршрут?')
    await state.set_state(FSMCreateRouteForm.title)

@router.message(StateFilter(FSMCreateRouteForm.time_other))
async def process_time_other_error(message: Message):
    await message.answer(text='Вы ввели что-то не то')

@router.message(StateFilter(FSMCreateRouteForm.title), F.text, lambda message: len(message.text)<200)
async def process_title_end(message: Message, state: FSMContext, session: AsyncSession):
    await state.update_data(title=message.text.capitalize())
    data = await state.get_data()
    days_result = []
    if data['date_day'] is not None:
        days_result = [datetime.strptime(day, "%m/%d/%Y").date() for day in data['date_day']]
    time_average = await request_to_get_time(data['start'], data['stop'])
    if time_average is not None:
        route = Route(title=data['title'],
                      start=data['start'],
                      stop=data['stop'],
                      time_end=datetime.strptime(data['time_end'], "%H:%M").time(),
                      time_other=datetime.strptime(data['time_other'], "%H:%M").time(),
                      days_date=days_result,
                      days_week=data['date_week'],
                      timezone=lat_lon_to_timezone(data['start']),
                      user_id=message.from_user.id,
                      time_average=time_average)

        try:
            session.add(route)
            await session.commit()

            await message.answer(text='Вы удачно создали новый маршрут:\n'
                                      f'Название: {route.title}\n'
                                      f'Время прибытия: {route.time_end}\n'
                                      f'Время на расходы: {route.time_other}\n'
                                      f'Даты: {", ".join([str(day) for day in days_result]) if len(days_result) != 0 else ", ".join([WEEKS[str(day)] for day in data["date_week"]])}\n'
                                      f'Примерное время в пути (на данный момент): {route.time_average // 60} мин.\n'
                                      '/menu')
            await state.clear()
        except SQLAlchemyError as e:
            await message.answer(text=f'Ошибка при сохранении данных')
            await session.rollback()
    else:
        await message.answer(text='Что-то пошло не так, обратитесь в поддержку')
        await state.clear()

@router.callback_query(lambda c: 'route_' in c.data)
async def process_route_list(callback: CallbackQuery, session: AsyncSession):
    route = await get_route_id(int(callback.data.split('_')[1]), session)

    btn_route_delete = InlineKeyboardButton(text='Удалить маршрут', callback_data=f'route_delete_{route[0]}')
    btn_route_edit = InlineKeyboardButton(text='Изменить маршрут', callback_data=f'route_edit_{route[0]}')

    keyboard_route = InlineKeyboardMarkup(inline_keyboard=[[btn_route_edit, btn_route_delete], [btn_routes_start, btn_routes_back_menu]])
    await callback.message.edit_text(text=f'Название: {route[1]}\n'
                              f'Время прибытия: {route[4]}\n'
                              f'Время на расходы: {route[5]}\n'
                              f'Даты: {", ".join([str(day) for day in route[6]]) if len(route[6]) != 0 else ", ".join([WEEKS[str(day)] for day in route[7]])}\n'
                              f'Примерное время в пути: {int(route[9]) // 60} мин.', reply_markup=keyboard_route)
@router.message(StateFilter(FSMCreateRouteForm.title))
async def process_title_error(message: Message):
    await message.answer(text='Название должно быть менее 200 символов')






