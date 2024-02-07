import aiohttp
from datetime import datetime

from aiohttp import ContentTypeError

from config.config import ConfigResult

HEADERS = {'Content-Type': 'application/json'}

async def request_to_get_time(coords_start: list[float, float],
                              coords_stop: list[float, float]) -> datetime|None:
    config: ConfigResult = ConfigResult('./.env')
    lon1: float = coords_start[1]
    lat1: float = coords_start[0]
    lon2: float = coords_stop[1]
    lat2: float = coords_stop[0]
    payload: dict = {"points": [
        {
            "lon1": lon1,
            "lat1": lat1,
            "lon2": lon2,
            "lat2": lat2,
        }
    ],
        "type": "jam",
        "output": "simple"
    }

    async with aiohttp.ClientSession() as session:
        async with session.post(f"{config.api.url}car?key={config.api.token}", headers=HEADERS, json=payload) as resp:
            response = await resp.json(content_type=None)

        try:
            result_time = response[0]['duration']
            return result_time
        except (ContentTypeError, IndexError, KeyError):
            return None