FROM python:3.12-slim

WORKDIR /app

# Копируем исходный код и файл зависимостей
COPY src/ ./src/

# Установка git и обновление pip
RUN apt-get update && apt-get install -y git && pip install --upgrade pip

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY entrypoint.sh .
RUN chmod +x entrypoint.sh
ENTRYPOINT ["./entrypoint.sh"]

