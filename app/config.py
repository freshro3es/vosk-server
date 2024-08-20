import json
import os

class Config:
    SECRET_KEY = 'secret!'
    RECORDS_DIR = 'records'
    UPLOADS_DIR = 'uploads'

    # Загрузка конфигурации из config.json
    with open("app/static/config.json") as config_file:
        config = json.load(config_file)

    SERVER_URI = config['NICServerUrl']
    VOSK_URI = config['NICVoskUrl']
    os.makedirs(RECORDS_DIR, exist_ok=True)
    os.makedirs(UPLOADS_DIR, exist_ok=True)