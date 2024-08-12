from flask import Flask
from flask_cors import CORS
from app.config import Config
from app.extensions import socketio
from app.blueprints.home import home_bp
from app.blueprints.wav_to_text import wav_bp
from app.blueprints.voice_to_text import voice_bp
import logging

logging.basicConfig(level=logging.INFO)

def create_app() -> Flask:
    """
    Creates a Flask app instance with registered blueprints and extensions.
    """
    try:
        app = Flask(__name__)
        app.config.from_object(Config)
        
        # Initialize SocketIO
        socketio.init_app(app)

        # Initialize CORS
        CORS(app)

        # Register blueprints
        app.register_blueprint(home_bp)
        app.register_blueprint(wav_bp)
        app.register_blueprint(voice_bp)

        return app
    except Exception as e:
        logging.error(f"Error creating app: {e}")
        raise