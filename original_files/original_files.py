# original_files = [
#     {
#         'path': 'original_files/sumimasen.ogg',
#         'translation': 'Извините'
#     },
#     {
#         'path': 'original_files/spath_to_file2.ogg',
#         'translation': 'Оригинальный файл 2'
#     },
#     {
#         'path': 'original_files/spath_to_file3.ogg',
#         'translation': 'Оригинальный файл 3'
#     }
# ]

import os
from mutagen import File

async def get_folders(dir_to_folders: str) -> list:
    # Получаем список элементов в директории
    items = os.listdir(dir_to_folders)
    # Фильтруем элементы, оставляя только папки
    folders = [item for item in items if os.path.isdir(os.path.join(dir_to_folders, item))]
    return folders


async def get_ogg_files(dir_to_files: str) -> list:
    # Получаем список элементов в директории
    files = os.listdir(dir_to_files)
    # Фильтруем файлы, оставляя только файлы с расширением .ogg
    ogg_files = [file for file in files if file.endswith('.ogg')]
    return ogg_files


async def get_tags(file: str):
    audio = File(file)
    tags = audio.tags
    return tags


BUTTONS: dict[str, str] = {
    'kawaisouni.ogg': 'かわいそうに - бедняга',
    'tasukaru.ogg': 'たすかる - спасибо за помощь',
    'utide_party.ogg': 'うちでパーティ - вечеринка у меня дома',
    'sashiire.ogg': 'さしいれ - угощение'}

BUTTONS_LIST = list(BUTTONS.keys())
