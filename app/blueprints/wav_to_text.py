from flask import Blueprint, render_template, request, jsonify, current_app
from werkzeug.utils import secure_filename
import logging
import os
from app.data.wav_task import WAVTask

wav_bp = Blueprint('wav_bp', __name__, template_folder="templates")

@wav_bp.route('/wav-to-text')
def wav_to_text():
    return render_template('wav_to_text.html')

@wav_bp.route('/upload', methods=['POST'])
def upload():
    if 'file' not in request.files:
        return jsonify({"error": "No file provided"}), 400

    file = request.files['file']

    logging.info(f"Received file: {file.filename}")
    logging.info(f"File content type: {file.content_type}")

    if not file.filename.endswith('.wav'):
        return jsonify({"error": "File format not supported, please upload a WAV file"}), 400

    filename = secure_filename(file.filename)
    file_path = os.path.join("uploads", filename)
    file.save(file_path)

    if not os.path.exists(file_path):
        current_app.logger.error(f"Failed to save file: {file_path}")
        return jsonify({"error": "Failed to save file"}), 500
    
    task = WAVTask(file_path, filename)
    task_manager =  current_app.config['TASK_MANAGER']
    task_manager.add_wav_task(task)

    # Отправляем task_id клиенту
    return jsonify({"task_id": task.task_id}), 200
