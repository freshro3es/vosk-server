# Используем легковесный базовый образ Python
FROM python:3.10-slim

# Устанавливаем рабочую директорию
WORKDIR /app

# Копируем файл зависимостей в контейнер
COPY requirements.txt .

# Устанавливаем зависимости
RUN pip install --no-cache-dir -r requirements.txt

# Копируем все файлы приложения в контейнер
COPY . .

# Определяем переменные окружения для адресов Flask и Vosk
ENV FLASK_APP=app.py
ENV FLASK_RUN_HOST=0.0.0.0
ENV FLASK_RUN_PORT=5000
ENV VOSK_SERVER_URL=http://localhost:2700

# Команда для запуска сервера Flask
CMD ["flask", "run"]
