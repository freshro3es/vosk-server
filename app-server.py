from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import json
import wave
import asyncio
import websockets
from websockets.exceptions import WebSocketException
from werkzeug.utils import secure_filename

app = Flask(__name__)
CORS(app)  # Это разрешит все CORS-запросы

# Укажите URL сервера Vosk
vosk_server_url = "ws://127.0.0.1:2700"

async def transcribe_audio(file_path):
    try:
        async with websockets.connect(vosk_server_url) as websocket:
            wf = wave.open(file_path, "rb")
            await websocket.send('{ "config" : { "sample_rate" : %d } }' % (wf.getframerate()))
            buffer_size = int(wf.getframerate() * 0.2)  # 0.2 seconds of audio
            transcription_result = []

            while True:
                data = wf.readframes(buffer_size)
                if len(data) == 0:
                    break
                await websocket.send(data)
                response = await websocket.recv()
                transcription_result.append(json.loads(response))

            await websocket.send('{"eof" : 1}')
            response = await websocket.recv()
            transcription_result.append(json.loads(response))

            # Combine all partial results into a single result
            combined_result = {
                "text": " ".join([res.get("text", "") for res in transcription_result])
            }
            return combined_result
    except WebSocketException as e:
        raise Exception(f"WebSocket error: {e}")
    except Exception as e:
        raise Exception(f"Error during transcription: {e}")

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

    filename = secure_filename(file.filename)
    file_path = os.path.join("uploads", filename)
    file.save(file_path)

    # Проверка, что файл сохранен
    if not os.path.exists(file_path):
        app.logger.error(f"Failed to save file: {file_path}")
        return jsonify({"error": "Failed to save file"}), 500

    try:
        # Выполнение транскрибирования с использованием asyncio
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        transcription_result = loop.run_until_complete(transcribe_audio(file_path))
    except Exception as e:
        app.logger.error(f"Error transcribing file: {e}")
        return jsonify({"error": str(e)}), 500
    finally:
        # Удаляем файл после обработки
        os.remove(file_path)

    app.logger.info(f"Transcription result: {transcription_result}")

    return jsonify(transcription_result)

if __name__ == '__main__':
    os.makedirs("uploads", exist_ok=True)
    app.run(debug=True)
