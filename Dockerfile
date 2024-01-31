# Отдельный "сборочный" образ
FROM python:3.11-slim-bullseye as compile-image
WORKDIR /app
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
COPY requirements.txt .
RUN apt update && apt install -y ffmpeg && \
	# apt install redis-server && \
	python -m pip install --upgrade pip && \
	pip install --no-cache -r /app/requirements.txt && \
    pip wheel --no-cache-dir --wheel-dir /opt/pip_wheels -r /app/requirements.txt

# Образ, который будет непосредственно превращаться в контейнер
FROM python:3.11-slim-bullseye as run-image
WORKDIR /app
COPY --from=compile-image /opt/pip_wheels /opt/pip_wheels
RUN pip install --no-cache /opt/pip_wheels/* && rm -rf /opt/pip_wheels
COPY . .
CMD ["python", "-m", "bot"]