from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text

from aiogram.types import Message

from database.models import Route


async def register_user(user_id: int, session: AsyncSession) -> bool:
    users = await session.execute(text(f"SELECT * FROM users WHERE user_id={user_id}"))
    return True if users.fetchone() is not None else False

async def get_routes_user(user_id: int, session: AsyncSession):
    routes = await session.execute(text(f"SELECT id, title, time_end FROM routes WHERE user_id={user_id} ORDER BY id DESC"))
    return routes