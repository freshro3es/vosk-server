import os

# Количество воркеров
workers = 1

# Используемый worker class
worker_class = 'eventlet'

# Адрес и порт для запуска
bind = str(os.getenv('HOST', '0.0.0.0')) + ":" + str(os.getenv('PORT', 5000))

# Файлы сертификатов для SSL
certfile = 'certificates/certificate.crt'
keyfile = 'certificates/private.key'

# Режим отладки
debug = os.getenv('DEBUG', 'false').lower() == 'true'

