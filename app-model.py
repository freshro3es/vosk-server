from flask import Flask, request, jsonify
from flask_cors import CORS
import wave
import os
import json
from vosk import Model, KaldiRecognizer

app = Flask(__name__)
CORS(app)  # Это разрешит все CORS-запросы

# Укажите путь к вашей модели Vosk
model_path = "/home/freshro3es/vosk/vosk-model-small-ru-0.22"  # замените на ваш путь
model = Model(model_path)

@app.route('/transcribe', methods=['POST'])
def transcribe():
    if 'file' not in request.files:
        return jsonify({"error": "No file provided"}), 400

    file = request.files['file']
    
    # Логирование информации о загруженном файле
    app.logger.info(f"Received file: {file.filename}")
    app.logger.info(f"File content type: {file.content_type}")

    # Проверка на допустимый формат файла
    if not file.filename.endswith('.wav'):
        return jsonify({"error": "File format not supported, please upload a WAV file"}), 400

    filename = os.path.join("uploads", file.filename)
    file.save(filename)
    
    # Проверка, что файл сохранен
    if not os.path.exists(filename):
        app.logger.error(f"Failed to save file: {filename}")
        return jsonify({"error": "Failed to save file"}), 500

    try:
        wf = wave.open(filename, "rb")
    except wave.Error as e:
        app.logger.error(f"Error opening WAV file: {e}")
        return jsonify({"error": "Failed to process WAV file"}), 500

    rec = KaldiRecognizer(model, wf.getframerate())
    result = ""

    while True:
        data = wf.readframes(4000)
        if len(data) == 0:
            break
        if rec.AcceptWaveform(data):
            res = rec.Result()
            res_json = json.loads(res)
            result += res_json.get("text", "") + " "

    final_res = rec.FinalResult()
    final_res_json = json.loads(final_res)
    result += final_res_json.get("text", "")

    app.logger.info(f"Transcription result: {result.strip()}")

    # Для отладки не удаляем файл
    os.remove(filename)

    return jsonify({"text": result.strip()})


if __name__ == '__main__':
    app.run(debug=True)
