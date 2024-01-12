from mutagen import File
import asyncio

from services.services import create_kb_file


def read_ogg_tags(file_path):
    audio = File(file_path)
    if audio.tags:
        tags = {}
        for key, value in audio.tags.items():
            tags[key] = str(value)
        return tags
    else:
        return None


# Открываем аудиофайл
# audio = File('original_files/kawaisouni.ogg')
async def main() -> None:
    # kb_names = await create_kb_names('original_files')
    # print(kb_names)

    file_path = "original_files/kawaisouni.ogg"
    tags_dict = read_ogg_tags(file_path)
    if tags_dict:
        print("Теги файла:")
        for key, value in tags_dict.items():
            value = value.replace('\'', '')
            value = value.replace('[', '')
            value = value.replace(']', '')
            print(f"{key}: {value}")
    else:
        print("Файл не содержит тегов.")


if __name__ == "__main__":
    asyncio.run(main())
