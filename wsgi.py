from app import create_app
from app.context import socketio
import ssl
import logging

# Отключаем предупреждения о проблемах с SSL-сертификатами
logging.getLogger('gunicorn.error').setLevel(logging.ERROR)

# Также можете подавить конкретные SSL ошибки
ssl._create_default_https_context = ssl._create_unverified_context

application = app = create_app()