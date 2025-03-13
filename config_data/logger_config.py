import logging
import os
import graypy
import colorlog
from dotenv import load_dotenv

# Загружаем переменные окружения из .env файла
load_dotenv()


def setup_logging():
    """Настройка логирования в Graylog программным способом"""

    # Получаем настройки из переменных окружения
    graylog_host = os.getenv('GRAYLOG_HOST', 'localhost')
    graylog_port = int(os.getenv('GRAYLOG_PORT', '12201'))
    log_level = os.getenv('LOG_LEVEL', 'INFO')
    app_name = os.getenv('APP_NAME', 'aiogram_bot')
    environment = os.getenv('ENVIRONMENT', 'development')

    # Получаем числовой уровень логирования
    numeric_level = getattr(logging, log_level.upper(), logging.INFO)

    # Создаем форматтер для логов
    formatter = logging.Formatter(
        fmt='[%(asctime)s] #%(levelname)-8s %(filename)s:%(lineno)d - %(name)s:%(funcName)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

    # Создаем цветной форматтер для консоли
    color_formatter = colorlog.ColoredFormatter(
        fmt='%(log_color)s[%(asctime)s] #%(levelname)-8s %(filename)s:%(lineno)d - %(name)s:%(funcName)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S',
        log_colors={
            'DEBUG': 'cyan',
            'INFO': 'green',
            'WARNING': 'yellow',
            'ERROR': 'red',
            'CRITICAL': 'red,bg_white',
        }
    )

    # Настраиваем корневой логгер
    root_logger = logging.getLogger()
    root_logger.setLevel(numeric_level)

    # Очищаем существующие обработчики (если нужно)
    if root_logger.handlers:
        root_logger.handlers.clear()

    # Создаем обработчик для консоли
    console_handler = logging.StreamHandler()
    console_handler.setLevel(numeric_level)
    console_handler.setFormatter(color_formatter)
    root_logger.addHandler(console_handler)

    # Создаем обработчик для Graylog
    graylog_handler = graypy.GELFUDPHandler(graylog_host, graylog_port, localname=app_name)
    graylog_handler.setFormatter(formatter)
    graylog_handler.setLevel(numeric_level)

    # Добавляем дополнительные поля
    graylog_handler._facility = app_name

    root_logger.addHandler(graylog_handler)

    # Настраиваем логгер для aiogram отдельно
    aiogram_logger = logging.getLogger('aiogram')
    aiogram_logger.setLevel(numeric_level)

    return root_logger


# Создаем глобальный логгер для использования в других модулях
logger = setup_logging()
