from dataclasses import dataclass

from environs import Env


@dataclass
class WebConfig:
    web_server_host: str    # Port for incoming request from reverse proxy. Should be any available port
    web_server_port: int
    webhook_path: str   # Path to webhook route, on which Telegram will send requests
    webhook_secret: str     # Secret key to validate requests from Telegram (optional)
    # Base URL for webhook will be used to generate webhook URL for Telegram,
    # it is used public DNS with HTTPS support
    base_webhook_url: str


@dataclass
class DatabaseConfig:
    database: str         # Название базы данных
    db_host: str          # URL-адрес базы данных
    db_port: str          # Порт базы
    db_user: str          # Username пользователя базы данных
    db_password: str      # Пароль к базе данных


@dataclass
class TgBot:
    token: str            # Токен для доступа к телеграм-боту
    admin_ids: list[int]  # Список id администраторов бота


@dataclass
class OpenAI:
    token: str            # Токен для доступа к OpenAI api


@dataclass
class Redis:
    redis_dsn: str


@dataclass
class Config:
    tg_bot: TgBot
    db: DatabaseConfig
    webhook: WebConfig
    openai: OpenAI
    redis: Redis


def load_config(path: str | None = None) -> Config:

    env: Env = Env()
    env.read_env(path)

    return Config(
        tg_bot=TgBot(
            token=env('BOT_TOKEN'),
            admin_ids=list(map(int, env.list('ADMIN_IDS')))
        ),
        db=DatabaseConfig(
            database=env('DATABASE'),
            db_host=env('DB_HOST'),
            db_port=env('DB_PORT'),
            db_user=env('DB_USER'),
            db_password=env('DB_PASSWORD')
        ),
        webhook=WebConfig(
            web_server_host=env('WEB_SERVER_HOST'),
            web_server_port=env('WEB_SERVER_PORT'),
            webhook_path=env('WEBHOOK_PATH'),
            webhook_secret=env('WEBHOOK_SECRET'),
            base_webhook_url=env('BASE_WEBHOOK_URL')
        ),
        openai=OpenAI(
            token=env('OPENAI_API_KEY')
        ),
        redis=Redis(
            redis_dsn=env('REDIS_DSN')
        )
    )
