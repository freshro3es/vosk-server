import json
import os

class Config:
    SECRET_KEY = 'secret!'
    RECORDS_DIR = 'records'
    UPLOADS_DIR = 'uploads'

    # Загрузка конфигурации из config.json
    with open("app/static/config.json") as config_file:
        config = json.load(config_file)

    SERVER_URI = config['serverUrl']
    VOSK_URI = os.getenv('VOSK_SERVER_URL', 'ws://localhost:2700')
    # VOSK_URI = config['voskUrl']
    os.makedirs(RECORDS_DIR, exist_ok=True)