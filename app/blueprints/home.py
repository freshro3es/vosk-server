from flask import Blueprint, request, jsonify, render_template
from app.context import socketio
from app.config import Config

home_bp = Blueprint('home_bp', __name__, template_folder="templates")

@home_bp.route('/')
def index():
    return render_template('home.html')

@home_bp.route('/config')
def get_config():
    return jsonify(Config.config)