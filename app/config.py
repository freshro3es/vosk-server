import json
import os

class Config:
    SECRET_KEY = 'secret!'
    RECORDS_DIR = str(os.getenv('RECORDS_DIR', "records"))
    UPLOADS_DIR = str(os.getenv('RECORDS_DIR', "uploads"))
    SERVER_URI = "https://" + str(os.getenv('HOST', "127.0.0.1")) + ":" + str(os.getenv('PORT', 5000))
    VOSK_URI = os.getenv('VOSK', 'ws://localhost:2700')
    
    os.makedirs(RECORDS_DIR, exist_ok=True)
    os.makedirs(UPLOADS_DIR, exist_ok=True)

    def __init__(self):
        # Загрузка конфигурации из config.json
        config_path = "app/static/config.json"
        try:
            with open(config_path, "r") as config_file:
                self.config = json.load(config_file)
        except FileNotFoundError:
            self.config = {}
        except json.JSONDecodeError as e:
            print(f"Error decoding JSON: {e}")
            self.config = {}

        # Обновление данных в конфигурации
        self.config['recordsDir'] = self.RECORDS_DIR
        self.config['uploadsDir'] = self.UPLOADS_DIR
        self.config['serverUrl'] = self.SERVER_URI
        self.config['voskUrl'] = self.VOSK_URI

        # Запись обновленных данных обратно в config.json
        with open(config_path, "w") as config_file:
            json.dump(self.config, config_file, indent=4)