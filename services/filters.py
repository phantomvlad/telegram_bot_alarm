from datetime import datetime
import re
from aiogram.filters import BaseFilter
from aiogram.types import Message

class DaysFilter(BaseFilter):
    async def __call__(self, message: Message) -> bool|dict[str, list[str]]:
        for char in message.text:
            if not (char.isdigit() or char.isspace() or char == '.'):
                return False
        array_dates = message.text.split()
        if len(array_dates) == 0 or array_dates is None:
            return False
        result_return = {'dates': []}
        for date in array_dates:
            try:
                datetime.strptime(date, "%d.%m.%Y")
                result_return['dates'].append(datetime.strptime(date, "%d.%m.%Y").strftime("%m/%d/%Y"))
            except ValueError:
                return False
        return result_return

class WeekFilter(BaseFilter):
    async def __call__(self, message: Message) -> bool|dict[str, list[int]]:
        words = ["пн", "вт", "ср", "чт", "пт", "сб", "вс"]
        if not message.text:
            return False
        result_return = {'dates': []}
        for char in message.text.lower().split():
            if char != " " and char not in words:
                return False
            if char == 'пн':
                result_return['dates'].append(1)
            if char == 'вт':
                result_return['dates'].append(2)
            if char == 'ср':
                result_return['dates'].append(3)
            if char == 'чт':
                result_return['dates'].append(4)
            if char == 'пт':
                result_return['dates'].append(5)
            if char == 'сб':
                result_return['dates'].append(6)
            if char == 'вс':
                result_return['dates'].append(7)
        input_list = message.text.lower().split()
        unique_words = set(input_list)
        if len(input_list) != len(unique_words):
            return False
        return result_return

class TimeFilter(BaseFilter):
    async def __call__(self, message: Message) -> bool | dict[str, str]:
        try:
            time_return = datetime.strptime(message.text, "%H:%M").strftime("%H:%M")
            return {'time': time_return}
        except ValueError:
            return False
