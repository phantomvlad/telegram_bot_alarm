from datetime import datetime

from aiogram import F, types
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import default_state, State, StatesGroup
from aiogram.types import Message, ReplyKeyboardRemove, WebAppInfo, CallbackQuery, KeyboardButton

from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

from database.models.user import User
from database.models.route import Route


from aiogram import Router
from sqlalchemy.ext.asyncio import AsyncSession
from services.filters import DaysFilter, WeekFilter, TimeFilter
from sqlalchemy.ext.asyncio import AsyncSession

router = Router()

class FSMCreateRouteForm(StatesGroup):
    title = State()
    start_g = State()
    stop_g = State()
    time_end = State()
    time_other = State()
    type_auto = State()
    date_start = State()
    date_day = State()
    date_week = State()
    user_id = State()


button_days = KeyboardButton(
    text = 'По датам',
    callback_data='days_date'
)

button_week = KeyboardButton(
    text = 'По дням недели',
    callback_data='days_week'
)

button_auto = KeyboardButton(
    text = 'Личное авто',
    callback_data='auto'
)

button_taxi = KeyboardButton(
    text = 'Такси',
    callback_data='taxi'
)

keyboard_dict = {'Такси': 'taxi', 'Личное авто': 'auto'}

keyboard_days = types.ReplyKeyboardMarkup(keyboard=[[button_days, button_week]], resize_keyboard=True, remove_keyboard=True)
keyboard_type = types.ReplyKeyboardMarkup(keyboard=[[button_auto, button_taxi]], resize_keyboard=True, remove_keyboard=True)

@router.message(Command(commands='cancel'), StateFilter(default_state))
async def process_cancel_create(message: Message):
    await message.answer(text='Вы не создаете маршрут')

@router.message(Command(commands='cancel'), ~StateFilter(default_state))
async def process_cancel_create(message: Message, state: FSMContext):
    await message.answer(text='Отмена создания маршрута', reply_markup=ReplyKeyboardRemove())
    await state.clear()

@router.message(Command(commands='route_create'), StateFilter(default_state))
async def process_start_create(message: Message, session: AsyncSession, state: FSMContext):
    users = await session.execute(text(f"SELECT * FROM users WHERE user_id={message.from_user.id}"))

    if users.fetchone() is None:
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

@router.message(StateFilter(FSMCreateRouteForm.start_g), lambda message: message.location is not None)
async def process_start_g_press(message: Message, state: FSMContext):
    await state.update_data(start=[message.location.latitude, message.location.longitude])
    await message.answer(text='Пожалуйста, сообщите геоданные о конечной точке.')
    await message.answer(text='Инструкция:\n'
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
    await message.answer(text='Уведомления будут в конкретные даты или повторятся по дням недели?',)
    await message.answer(text='Выберите снизу', reply_markup=keyboard_days)
    await state.set_state(FSMCreateRouteForm.date_start)

@router.message(StateFilter(FSMCreateRouteForm.stop_g))
async def process_start_g_error(message: Message, state: FSMContext):
    await message.answer(text='Вы прислали что-то не то')
    await state.set_state(FSMCreateRouteForm.stop_g)

@router.message(StateFilter(FSMCreateRouteForm.date_start), F.text == 'По датам')
async def process_days_press(message: Message, state: FSMContext):
    await message.answer(text='Введите дату или даты через пробел в формате\n"ДД.ММ.ГГГГ ДД.ММ.ГГГГ\n'
                              'Например: 22.02.2024 24.02.23"', reply_markup=ReplyKeyboardRemove())
    await state.set_state(FSMCreateRouteForm.date_day)


@router.message(StateFilter(FSMCreateRouteForm.date_start), F.text == 'По дням недели')
async def process_week_press(message: Message, state: FSMContext):
    await message.answer(text='Введите день или дни недели в которые хотите повторения уведомлений в формате\n'
                              '"пн вт ср чт пт сб вс"\n'
                              'Например: пн ср чт', reply_markup=ReplyKeyboardRemove())
    await state.set_state(FSMCreateRouteForm.date_week)

@router.message(StateFilter(FSMCreateRouteForm.date_day), DaysFilter())
async def process_days_finish(message: Message, state: FSMContext, dates: dict[str]):
    await message.answer(text=f'Даты уведомлений: {message.text}')
    await state.update_data(date_day=[datetime.strptime(day,"%d.%m.%Y").date() for day in dates])
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
async def process_days_finish(message: Message, state: FSMContext):
    await message.answer(text='Вы ввели что-то не то')
    await state.set_state(FSMCreateRouteForm.date_week)

@router.message(StateFilter(FSMCreateRouteForm.time_end), TimeFilter())
async def process_time_end(message: Message, state: FSMContext, time: str):
    await state.update_data(time_end=time)
    await message.answer(text='Введите время, которое вы тратите на прогрев авто и другие траты\n'
                              'Формат: чч:мм\n'
                              'Например: 0:15 или 00:05 (15 или 5 минут)')
    await state.set_state(FSMCreateRouteForm.time_other)

@router.message(StateFilter(FSMCreateRouteForm.time_end))
async def process_time_end_error(message: Message, state: FSMContext):
    await message.answer(text='Вы ввели что-то не то')
    await state.set_state(FSMCreateRouteForm.time_end)

@router.message(StateFilter(FSMCreateRouteForm.time_other), TimeFilter())
async def process_time_end_final(message: Message, state: FSMContext, time: str):
    await state.update_data(time_other=time)
    await message.answer(text='Выберите тип транспорта', reply_markup=keyboard_type)
    await state.set_state(FSMCreateRouteForm.type_auto)

@router.message(StateFilter(FSMCreateRouteForm.type_auto), F.text == 'Личное авто')
@router.message(StateFilter(FSMCreateRouteForm.type_auto), F.text =='Такси')
async def process_type_car(message: Message, state: FSMContext):
    await state.update_data(type_auto=keyboard_dict[message.text])
    await message.answer(text='Как назовете маршрут?', reply_markup=ReplyKeyboardRemove())
    await state.set_state(FSMCreateRouteForm.title)

@router.message(StateFilter(FSMCreateRouteForm.type_auto))
async def process_type_car_error(message: Message):
    await message.answer(text='Вы ввели что-то не то')

@router.message(StateFilter(FSMCreateRouteForm.title), lambda message: len(message.text)<200)
async def process_type_car_end(message: Message, state: FSMContext, session: AsyncSession):
    await state.update_data(title=message.text.capitalize())
    data = await state.get_data()
    route = Route(title=data['title'],
                  start=data['start'],
                  stop=data['stop'],
                  time_end=datetime.strptime(data['time_end'], "%H:%M").time(),
                  time_other=datetime.strptime(data['time_other'], "%H:%M").time(),
                  type_auto=data['type_auto'],
                  days_date=data['date_day'],
                  days_week=data['date_week'],
                  user_id=message.from_user.id)

    try:
        session.add(route)
        await session.commit()
        await message.answer(text='Вы удачно создали новый маршрут')
        await state.clear()
    except SQLAlchemyError as e:
        await message.answer(text=f'Ошибка при сохранении данных {e}')
        await session.rollback()

@router.message(StateFilter(FSMCreateRouteForm.title))
async def process_type_car(message: Message):
    await message.answer(text='Название должно быть менее 200 символов')






