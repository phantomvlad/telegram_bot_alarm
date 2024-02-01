from aiogram import F, types
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import default_state, State, StatesGroup
from aiogram.types import Message, ReplyKeyboardRemove

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

keyboard = types.ReplyKeyboardMarkup(keyboard=[[button_phone]], resize_keyboard=True, remove_keyboard=True)

@router.message(Command(commands='cancel'), StateFilter(default_state))
async def process_cancel_registration(message: Message):
    await message.answer(text='Вы не заполяете никакую анкету')

@router.message(Command(commands='cancel'), ~StateFilter(default_state))
async def process_cancel_registration(message: Message, state: FSMContext):
    await message.answer(text='Отмена заполнения анкеты', reply_markup=ReplyKeyboardRemove())
    await state.clear()

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
    await message.answer(text='Отправьте номер телефона нажатием на кнопку\n'
                              'Если хотите отменить регистрацию - введите команду /cancel',
                         reply_markup=keyboard,
                         input_field_placeholder='Нажмите кнопку ниже',
                         )
    await state.set_state(FSMRegistrationForm.user_phone)

@router.message(StateFilter(FSMRegistrationForm.user_name))
async def process_name_sent(message: Message):
    await message.answer(text='Вы ввели странное имя, должны быть только буквы\n'
                              'Если хотите отменить регистрацию - введите команду /cancel')

@router.message(StateFilter(FSMRegistrationForm.user_phone))
async def process_number_sent(message: Message, state: FSMContext, session: AsyncSession):
    if message.contact is None:
        await message.answer(text='Вам просто нужно нажать кнопку внизу',
                             reply_markup=keyboard,
                             input_field_placeholder='Нажмите кнопку ниже',)
        return

    user_phone = message.contact.phone_number
    await state.update_data(user_phone = user_phone)
    data = await state.get_data()
    user = User(user_id=message.from_user.id, name=data['user_name'], phone = data['user_phone'])
    session.add(user)
    await session.commit()
    await message.answer(text='Вы зарегистрированы\n'
                              'Приятного использования!',
                         reply_markup=ReplyKeyboardRemove())
    await state.clear()



