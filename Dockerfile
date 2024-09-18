# Используем легковесный базовый образ Python
FROM python:3.10-slim

# Устанавливаем рабочую директорию
WORKDIR /app
# COPY requirements.txt .
COPY . .
RUN pip install --no-cache-dir -r requirements.txt

# Определяем переменные окружения для адресов Flask и Vosk
ENV FLASK_APP=app
ENV HOST=0.0.0.0
ENV PORT=5000
ENV VOSK=ws://host.docker.internal:2700

EXPOSE 5000

# Команда для запуска сервера Flask
CMD ["flask", "run", "--host=0.0.0.0", "--port=5000"]

