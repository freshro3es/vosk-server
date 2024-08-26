import eventlet
eventlet.monkey_patch()  # <-- Должно быть самым первым
from app import create_app
from app.context import socketio
from app.config import Config

app = create_app()

if __name__ == "__main__":
    socketio.run(app, debug=True, host=Config.SERVER_URI, port=5000)