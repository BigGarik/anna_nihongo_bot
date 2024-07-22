# Бот для изучения языков

### Установка:
```bash
git clone git@github.com:BigGarik/anna_nihongo_bot.git
```
Установить зависимости
```bash
sudo apt install redis-server ffmpeg
```
```bash
sudo service redis-server start
```
```bash
sudo service redis-server  status
```


Создание виртуального окружения
```bash
python3 -m venv venv
```
```bash
source venv/bin/activate
```
```bash
pip install --upgrade pip
```
```bash
pip install -r requirements.txt
```

### Миграция

Инициализация Aerich:
```bash
aerich init -t db.config.TORTOISE_ORM
```
Создание первой миграции:
```bash
aerich init-db
```
Создание новой миграции:
```bash
aerich migrate
```
Применение миграций:
```bash
aerich upgrade
```
Откат последней миграции:
```bash
aerich downgrade
```
Просмотр статуса миграций:
```bash
aerich history
```
Просмотр текущего состояния базы данных:
```bash
aerich heads
```

#### Запуск бота
```bash
python3 -m bot
```
### Docker
```bash
docker build -t anna_nihongo_bot:latest .
```
```bash
docker compose up
```
```bash
docker compose down
```

#### Полезные команды
```
redis-cli
flushall

source venv/bin/activate
deactivate

python -m pip install --upgrade pip
pip install -r requirements.txt --force

sudo systemctl enable english_mrhatsu_bot.service
sudo systemctl start english_mrhatsu_bot.service
sudo systemctl status english_mrhatsu_bot.service
sudo systemctl stop english_mrhatsu_bot.service
sudo systemctl restart english_mrhatsu_bot.service
Для просмотра логов: sudo journalctl -u english_mrhatsu_bot.service
sudo journalctl --rotate --vacuum-time=1s -u english_mrhatsu_bot.service


sudo systemctl enable anna_nihongo_bot.service
sudo systemctl disable anna_nihongo_bot.service
sudo systemctl start anna_nihongo_bot.service
sudo systemctl status anna_nihongo_bot.service
sudo systemctl stop anna_nihongo_bot.service
sudo systemctl restart anna_nihongo_bot.service
Для просмотра логов: sudo journalctl -u anna_nihongo_bot.service
sudo journalctl --rotate --vacuum-time=1s -u anna_nihongo_bot.service


sudo systemctl restart english_mrhatsu_bot.service anna_nihongo_bot.service


```