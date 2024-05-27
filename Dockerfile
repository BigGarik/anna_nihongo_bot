# Отдельный "сборочный" образ
FROM python:3.12-slim-bullseye as compile-image
WORKDIR /app
ENV PYTHONDONTWRITEBYTECODE 1 PYTHONUNBUFFERED 1
COPY requirements.txt .
# Установка зависимостей в одном слое и очистка кэша pip
RUN python -m pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Образ, который будет непосредственно превращаться в контейнер
FROM python:3.12-slim-bullseye as run-image
WORKDIR /app

# Установка ffmpeg и очистка кэша apt в одном слое
RUN apt-get update && \
    apt-get install -y --no-install-recommends ffmpeg && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Копирование установленных зависимостей из сборочного образа
COPY --from=compile-image /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages

# Копирование исходного кода приложения
COPY . .
CMD ["python", "-m", "bot"]
