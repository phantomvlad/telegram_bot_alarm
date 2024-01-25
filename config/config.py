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
    token: str            # Токен для доступа к телеграм-боту

@dataclass
class Config:
    tg_bot: TgBot
    db: DatabaseConfig

def load_config(path: str | None = None) -> Config:
    load_dotenv(dotenv_path = path)

    return Config(
        tg_bot = TgBot(
            token = os.getenv('API_TOKEN'),
        ),
        db = DatabaseConfig(
            database = os.getenv('POSTGRES_DB'),
            db_host = os.getenv('POSTGRES_HOST'),
            db_port = os.getenv('POSTGRES_PORT'),
            db_user = os.getenv('POSTGRES_USER'),
            db_password = os.getenv('POSTGRES_PASSWORD')
        )
    )

