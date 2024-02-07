from dataclasses import dataclass
import os
from dotenv import load_dotenv

@dataclass
class DatabaseConfig:
    database: str         # Название базы данных
    db_host: str          # URL-адрес базы данных
    db_port: str
    db_user: str          # Username пользователя базы данных
    db_password: str      # Пароль к базе данных

@dataclass
class TgBot:
    token: str           # Токен для доступа к телеграм-боту
    creator: str

@dataclass
class Celery:
    broker_url: str
    imports: tuple
    result_backend: str

@dataclass
class Api:
    token: str
    url: str

@dataclass
class Config:
    tg_bot: TgBot
    db: DatabaseConfig
    celery: Celery
    api: Api

load_dotenv(dotenv_path = './.env')

class ConfigResult:
    def __init__(self, path):
        load_dotenv(dotenv_path=path)
        self.tg_bot = TgBot(
            token=os.getenv('TG_TOKEN'),
            creator=os.getenv('CREATOR_ID')
        )
        self.db = DatabaseConfig(
            database=os.getenv('POSTGRES_DB'),
            db_host=os.getenv('POSTGRES_HOST'),
            db_port=os.getenv('POSTGRES_PORT'),
            db_user=os.getenv('POSTGRES_USER'),
            db_password=os.getenv('POSTGRES_PASSWORD')
        )
        self.celery = Celery(
            broker_url=os.getenv('CELERY_BROKER_URL'),
            imports=(os.getenv('CELERY_IMPORTS'),),
            result_backend=os.getenv("CELERY_RESULT_BACKEND")
        )
        self.api = Api(
            token=os.getenv('API_TOKEN'),
            url=os.getenv('API_URL'),
        )
