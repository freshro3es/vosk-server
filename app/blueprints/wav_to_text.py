from flask import Blueprint, render_template, request, jsonify, current_app
from werkzeug.utils import secure_filename
import logging
import os
from datetime import datetime
from app.data.wav_task import WAVTask
from app.libraries.converter import Converter

wav_bp = Blueprint("wav_bp", __name__, template_folder="templates")


@wav_bp.route("/wav-to-text")
def wav_to_text():
    return render_template("wav_to_text.html")


@wav_bp.route("/upload", methods=["POST"])
def upload():
    if "file" not in request.files:
        return jsonify({"error": "No file provided"}), 400

    file = request.files["file"]

    logging.info(f"Received file: {file.filename}")
    logging.info(f"File content type: {file.content_type}")

    if file.filename.endswith(".wav"):
        filename = secure_filename(file.filename)
        file_path = os.path.join(
            os.path.join(
                os.getenv("UPLOADS_DIR", "uploads"),
                f"{filename[:-4]}_{datetime.now().strftime('%d-%m-%Y')}.wav",
            )
        )
        file.save(file_path)
    else:
        filename, file_path = Converter.convert_file(file)
        if filename is None:
            return (
                jsonify(
                    {"error": "File format not supported, please upload a WAV file"}
                ),
                400,
            )

    if not os.path.exists(file_path):
        current_app.logger.error(f"Failed to save file: {file_path}")
        return jsonify({"error": "Failed to save file"}), 500

    task = WAVTask(file_path, filename)
    task_manager = current_app.config["TASK_MANAGER"]
    task_manager.add_wav_task(task)
    logging.info(f"Generated task with id: {task.task_id}")

    # Отправляем task_id клиенту
    return jsonify({"task_id": task.task_id}), 200
