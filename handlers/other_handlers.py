from aiogram.types import Message
from aiogram import Router

from lexicon.lexicon import LEXICON_RU

router = Router()

@router.message()
async def random_message(message: Message) -> None:
    try:
        await message.answer(text=LEXICON_RU['random'])
    except TypeError:
        await message.answer(text='Не понял что ты прислал')
