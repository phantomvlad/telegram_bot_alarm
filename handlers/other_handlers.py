from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from aiogram import Router

from lexicon.lexicon import LEXICON_RU

router = Router()

@router.message()
async def random_message(message: Message, state: FSMContext) -> None:
    await state.clear()
    try:
        await message.answer(text=LEXICON_RU['random'])
    except TypeError:
        await message.answer(text='Не понял что ты прислал')
