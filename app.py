import eventlet
eventlet.monkey_patch()  # <-- Должно быть самым первым
from app import create_app
from app.context import socketio
from app.config import Config
import os

app = create_app()

# if __name__ == "__main__":
#     socketio.run(app, debug=True, host=Config.SERVER_URI, port=5000)
    
if __name__ == '__main__':
    app.run(app,  debug=True, host=os.getenv('HOST', '0.0.0.0'), port=int(os.getenv('PORT', 5000)))