import asyncio
import os
from mutagen import File


def get_folders(dir_to_folders: str) -> list:
    # Получаем список элементов в директории
    items = os.listdir(dir_to_folders)
    # Фильтруем элементы, оставляя только папки
    folders = [item for item in items if os.path.isdir(os.path.join(dir_to_folders, item))]
    return folders


def get_ogg_files(dir_to_files: str) -> list:
    # Получаем список элементов в директории
    files = os.listdir(dir_to_files)
    # Фильтруем файлы, оставляя только файлы с расширением .ogg
    ogg_files = [file for file in files if file.endswith('.ogg')]
    return ogg_files


def get_tags(path_to_file: str):
    audio = File(path_to_file)
    tags = audio.tags
    return tags


def create_kb_name(dir_to_files: str) -> dict[str, str]:
    files = get_ogg_files(dir_to_files)
    kb_name = {}
    for file in files:
        tags = get_tags(f'{dir_to_files}/{file}')
        title = str(tags['title'])
        title = title.replace('\'', '')
        title = title.replace('[', '')
        title = title.replace(']', '')
        kb_name[file] = title

    return kb_name


BUTTONS: dict[str, str] = {
#     'kawaisouni.ogg': 'かわいそうに - бедняга',
#     'tasukaru.ogg': 'たすかる - спасибо за помощь',
#     'utide_party.ogg': 'うちでパーティ - вечеринка у меня дома',
#     'sashiire.ogg': 'さしいれ - угощение'
}
#
# BUTTONS_LIST = list(BUTTONS.keys())


if __name__ == "__main__":
    create_kb_name('../original_files')
