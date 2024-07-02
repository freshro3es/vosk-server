import eventlet
eventlet.monkey_patch()

import os
import json
import wave
import asyncio
import websockets
from flask import Flask, request, jsonify, render_template, send_from_directory
from flask_socketio import SocketIO, emit, disconnect
from flask_cors import CORS
from werkzeug.utils import secure_filename

eventlet.monkey_patch()

# Загрузка конфигурации из config.json
with open('config.json') as config_file:
    config = json.load(config_file)

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app, async_mode='eventlet', cors_allowed_origins="*")
CORS(app)

VOSK_URI = config['voskUrl']

# Хранение соответствия соединений WebSocket и идентификаторов клиентов
client_connections = {}

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/wav-to-text')
def wav_to_text():
    return render_template('wav_to_text.html')

@app.route('/voice-to-text')
def voice_to_text():
    return render_template('voice_to_text.html')

# Возвращает конфигурацию URI на frontend
@app.route('/config')
def get_config():
    return config

@app.route('/upload', methods=['POST'])
def upload():
    if 'file' not in request.files:
        return jsonify({"error": "No file provided"}), 400

    file = request.files['file']

    app.logger.info(f"Received file: {file.filename}")
    app.logger.info(f"File content type: {file.content_type}")

    if not file.filename.endswith('.wav'):
        return jsonify({"error": "File format not supported, please upload a WAV file"}), 400

    filename = secure_filename(file.filename)
    file_path = os.path.join("uploads", filename)
    file.save(file_path)

    if not os.path.exists(file_path):
        app.logger.error(f"Failed to save file: {file_path}")
        return jsonify({"error": "Failed to save file"}), 500

    # Запуск асинхронной задачи для транскрибации файла
    socketio.start_background_task(target=transcribe_file, file_path=file_path)

    return jsonify({"status": "Processing started"}), 200

# Обработчик WebSocket для приема аудио данных
@socketio.on('audio_data')
def handle_audio_data(message):
    client_id = message.get('client_id')
    if client_id in client_connections:
        async def transcribe():
            uri = VOSK_URI
            async with websockets.connect(uri) as websocket:
                await websocket.send('{ "config" : { "sample_rate" : 16000 } }')
                await websocket.send(message['audio_data'])
                result = await websocket.recv()
                try:
                    result_json = json.loads(result)
                    send_message('transcription_result', {'result': result_json.get('partial', '')}, room=client_connections[client_id])
                    app.logger.info(f"Transcription result: {result_json}")
                except json.JSONDecodeError:
                    app.logger.error(f"Failed to decode JSON: {result}")

        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(transcribe())

@socketio.on('stop_recording')
def handle_stop_recording():
    # Добавьте здесь логику остановки записи или другие действия при необходимости
    app.logger.info('Received stop recording signal')

@socketio.on('connect')
def handle_connect():
    client_id = request.sid
    client_connections[client_id] = request.sid
    app.logger.info(f"Client connected: {client_id}")

@socketio.on('disconnect')
def handle_disconnect():
    client_id = request.sid
    if client_id in client_connections:
        del client_connections[client_id]
        app.logger.info(f"Client disconnected: {client_id}")
    disconnect()
    
    
# Функция отправки сообщения по сокету
def send_message(event, data=None, room=None):
    if room:
        socketio.emit(event, data, room=room)
    else:
        socketio.emit(event, data)

def transcribe_file(file_path):
    async def transcribe():
        uri = VOSK_URI
        async with websockets.connect(uri) as websocket:
            wf = wave.open(file_path, "rb")
            await websocket.send('{ "config" : { "sample_rate" : %d } }' % (wf.getframerate()))
            buffer_size = int(wf.getframerate() * 1.2)  # 1.2 seconds of audio

            while True:
                data = wf.readframes(buffer_size)
                if len(data) == 0:
                    break

                await websocket.send(data)
                result = await websocket.recv()
                send_message('message', json.loads(result))
                app.logger.info(f"Transcription result: {result}")

            await websocket.send('{"eof" : 1}')
            final_result = await websocket.recv()
            send_message('message', json.loads(final_result))
            app.logger.info(f"Final transcription result: {final_result}")

            # Сигнал о завершении транскрипции
            send_message('transcription_finished')
            app.logger.info("Transcription finished")

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(transcribe())
    os.remove(file_path)

if __name__ == '__main__':
    os.makedirs("uploads", exist_ok=True)
    socketio.run(app, debug=True, host='0.0.0.0', port=5000)
