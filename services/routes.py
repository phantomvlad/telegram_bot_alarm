from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text

async def get_routes_user(user_id: int, session: AsyncSession):
    routes = await session.execute(text(f"SELECT id, title, time_end FROM routes WHERE user_id={user_id} ORDER BY id ASC"))
    return routes
