from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text

async def register_user(user_id: int, session: AsyncSession) -> bool:
    users = await session.execute(text(f"SELECT * FROM users WHERE user_id={user_id}"))
    return True if users.fetchone() is not None else False
