import eventlet
eventlet.monkey_patch()  # <-- Должно быть самым первым
from app import create_app
from app.context import socketio

app = create_app()

if __name__ == "__main__":
    socketio.run(app, debug=True, host='0.0.0.0', port=5000)