# Используем легковесный базовый образ Python
FROM python:3.10-slim

# Устанавливаем рабочую директорию
WORKDIR /app
COPY requirements.txt .
# COPY . .
RUN apt-get update && apt-get install -y ffmpeg
RUN pip install --no-cache-dir -r requirements.txt

# Создаем необходимые директории
RUN mkdir -p /app/uploads /app/records

# Копируем файл .env в контейнер
COPY .env .env

EXPOSE 5000

# Команда для запуска сервера Flask
CMD ["flask", "run", "--host=0.0.0.0", "--port=5000"]

