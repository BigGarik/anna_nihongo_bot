from mutagen import File


# Открываем аудиофайл
audio = File('original_files/kawaisouni.ogg')

# Проверяем, поддерживается ли формат аудиофайла
if audio is not None:
    # Получаем доступ к тегам аудиофайла
    tags = audio.tags

    # Печатаем информацию о тегах
    for key, value in tags.items():
        print(key, ":", value)
else:
    print("Неподдерживаемый формат аудиофайла")