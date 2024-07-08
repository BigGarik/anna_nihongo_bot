import logging
import os

from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger(__name__)


async def get_languages(**kwargs):
    locales = os.getenv('LOCALES').split(',')
    items = [(locale, locale) for locale in locales]
    return {'languages': items}
