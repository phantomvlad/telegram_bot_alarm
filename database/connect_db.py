from sqlalchemy import create_engine

from config.config import Config

async def connect_db(config: Config):
    engine = create_engine(f"postgresql+psycopg2://{config.db.db_user}:{config.db.db_password}@localhost/{config.db.database}")
    engine.connect()
    print('test', engine)