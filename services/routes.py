from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text

async def get_routes_user(user_id: int, session: AsyncSession):
    routes = await session.execute(text(f"SELECT id, title, time_end FROM routes WHERE user_id={user_id} ORDER BY id ASC"))
    return routes

async def get_route_id(route_id: int, session: AsyncSession):
    route = (await session.execute(text(f"SELECT id, "
                                        f"title, "
                                        f"start,"
                                        f" stop, "
                                        f"time_end, "
                                        f"time_other, "
                                        f"days_date, "
                                        f"days_week, "
                                        f"timezone, "
                                        f"time_average FROM routes WHERE id={route_id}"))).fetchone()

    return route