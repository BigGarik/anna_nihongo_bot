import os
import random

from dotenv import load_dotenv
from mutagen import File

load_dotenv()
location = os.getenv('LOCATION')


def get_folders(dir_to_folders: str) -> dict[str, str]:
    # Получаем список элементов в директории
    items = os.listdir(dir_to_folders)
    kb_folders = {}
    # Фильтруем элементы, оставляя только папки
    folders = [item for item in items if os.path.isdir(os.path.join(dir_to_folders, item))]
    for folder in folders:
        kb_folders[folder] = f'{dir_to_folders}/{folder}'
    return kb_folders


def get_ogg_files(dir_to_files: str) -> list:
    # Получаем список элементов в директории
    files = os.listdir(dir_to_files)
    # Фильтруем файлы, оставляя только файлы с расширением .ogg
    ogg_files = [file for file in files if file.endswith('.ogg')]
    return ogg_files


def get_all_ogg_files(start_dir: str) -> list:
    all_ogg_files = []
    for root, dirs, files in os.walk(start_dir):
        for file in files:
            if file.endswith(".ogg"):
                all_ogg_files.append(file)
    return all_ogg_files


def get_all_tags(path_to_file: str):
    audio = File(path_to_file)
    tags = audio.tags
    return tags


def get_tag(path_to_file: str, tag: str):
    tag = str(get_all_tags(path_to_file)[tag])
    tag = tag.replace('\'', '')
    tag = tag.replace('[', '')
    tag = tag.replace(']', '')
    return tag


def create_kb_file(dir_to_files: str) -> dict[str, str]:
    files = get_ogg_files(dir_to_files)
    kb_name = {}
    for file in files:
        tags = get_all_tags(f'{dir_to_files}/{file}')
        title = str(tags['title'])
        title = title.replace('\'', '')
        title = title.replace('[', '')
        title = title.replace(']', '')
        kb_name[title] = file

    return kb_name


def replace_random_words(phrase):
    words = phrase.split()
    # Убедимся, что в фразе есть более двух слов для замены
    if len(words) < 3:
        return phrase

    # Выбираем два разных случайных индекса слов, которые не находятся рядом
    first_index = random.randint(0, len(words) - 3)
    second_index = random.randint(first_index + 2, len(words) - 1)

    # Заменяем выбранные слова на три звездочки
    words[first_index] = '___'
    words[second_index] = '___'

    # Возвращаем измененную фразу
    if location == 'ja-JP':
        return ''.join(words)
    else:
        return ' '.join(words)


BUTTONS: dict[str, str] = {
    #     'kawaisouni.ogg': 'かわいそうに - бедняга',
    #     'tasukaru.ogg': 'たすかる - спасибо за помощь',
    #     'utide_party.ogg': 'うちでパーティ - вечеринка у меня дома',
    #     'sashiire.ogg': 'さしいれ - угощение'
}
#
# BUTTONS_LIST = list(BUTTONS.keys())


if __name__ == "__main__":
    # print(get_all_ogg_files('../original_files'))
    # print(list(get_folders('../original_files')))
    # print(get_folders('../original_files'))
    # print(create_kb_file('../original_files/Spy Family'))
    print(get_all_tags('../original_files/Spy Family/kawaisouni.ogg'))
    # print(get_tag('../original_files/Spy Family/kawaisouni.ogg', 'translation'))
