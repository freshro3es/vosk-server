import json
import os

class Config:
    SECRET_KEY = 'secret!'
    RECORDS_DIR = 'records'
    UPLOADS_DIR = 'uploads'

    # Загрузка конфигурации из config.json
    with open("app/static/config.json") as config_file:
        config = json.load(config_file)

    # SERVER_URI = config['serverUrl']
    SERVER_URI = "http://" + "127.0.0.1" + ":" + str(os.getenv('PORT', 5000))
    VOSK_URI = os.getenv('VOSK', 'ws://localhost:2700')
    # VOSK_URI = config['voskUrl']
    os.makedirs(RECORDS_DIR, exist_ok=True)