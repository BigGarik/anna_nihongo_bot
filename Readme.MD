# Бот для изучения языков

### Установка:

`git clone git@github.com:BigGarik/anna_nihongo_bot.git`

Установить зависимости

`sudo apt install redis-server ffmpeg`

`sudo service redis-server start`

`sudo service redis-server  status`

Создание виртуального окружения

`python3 -m venv venv`

`source venv/bin/activate`

`pip install --upgrade pip`

`pip install -r requirements.txt`

Запуск

`python3 -m bot`

### Docker

`docker build -t anna_nihongo_bot:latest .`

`docker compose up`

`docker compose down`
