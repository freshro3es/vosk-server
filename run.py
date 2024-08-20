import eventlet
eventlet.monkey_patch()
from eventlet.queue import Queue
import wave
import time
import os
import json
import wave
import asyncio
import websockets
from flask import Flask, request, jsonify, render_template, send_from_directory
from flask_socketio import SocketIO, emit, disconnect
from flask_cors import CORS
from werkzeug.utils import secure_filename
from werkzeug.utils import secure_filename
from threading import Lock

# Загрузка конфигурации из config.json
with open('config.json') as config_file:
    config = json.load(config_file)

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app, async_mode='eventlet', cors_allowed_origins="*")
CORS(app)

VOSK_URI = config['voskUrl']
RECORDS_DIR = 'records'

os.makedirs(RECORDS_DIR, exist_ok=True)

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


# Очередь для хранения аудио данных
audio_queues = {}
# Для файлов
audio_files = {}
audio_files_lock = Lock()

# Обработчик WebSocket для начала передачи аудио данных
@socketio.on('start_recording')
def handle_start_recording():
    app.logger.info(f"Recording started")
    client_id = request.sid
    audio_queue = Queue()
    audio_queues[client_id] = audio_queue

    # Создаем файл для записи аудио данных в формате WAV
    timestamp = int(time.time())
    audio_file_path = os.path.join(RECORDS_DIR, f"{client_id}_{timestamp}.wav")
    audio_file = wave.open(audio_file_path, 'wb')
    audio_file.setnchannels(1)  # Mono
    audio_file.setsampwidth(2)  # 16bit
    audio_file.setframerate(16000)  # 16kHz
    
    with audio_files_lock:
        audio_files[client_id] = audio_file
        app.logger.info(f"Client {client_id} created a file. Audio file path: {audio_file_path}")

    # Запуск фоновой задачи для обработки аудио данных
    socketio.start_background_task(target=transcribe_audio_stream, client_id=client_id, audio_queue=audio_queue)

# Обработчик WebSocket для приема аудио данных
@socketio.on('audio_data')
def handle_audio_data(data):
    #app.logger.info(f"Audio data recieved from {request.sid}")
    client_id = request.sid
    if client_id in audio_queues:
        audio_data = data.get('audio_data')
        if audio_data:
            audio_queues[client_id].put_nowait(audio_data)

# Обработчик WebSocket для остановки передачи аудио данных
@socketio.on('stop_recording')
def handle_stop_recording():
    app.logger.info(f"Recording stopped")
    client_id = request.sid
    if client_id in audio_queues:
        audio_queues[client_id].put_nowait(None)  # Используем None как сигнал окончания записи


# Функция для обработки аудио потока
def transcribe_audio_stream(client_id, audio_queue):
    async def transcribe():
        app.logger.info(f"Audio stream started for client {client_id}")
        uri = VOSK_URI
        async with websockets.connect(uri) as websocket:
            app.logger.info(f"Connected to websocket of vosk")
            await websocket.send('{ "config" : { "sample_rate" : 16000 } }')
            app.logger.info(f"client_id is {client_id}")

            with audio_files_lock:
                if client_id not in audio_files:
                    app.logger.error(f"Audio file for client {client_id} not found.")
                    app.logger.error(f"Dict {audio_files}")
                    return
            audio_file = audio_files[client_id]
                
            while True:
                data = audio_queue.get()
                app.logger.info(f"Got data from audio queue")
                if data is None and audio_queue.empty(): # Наверное, если добавить И на очередь, то ок?
                    break  # Завершаем цикл, если получили сигнал окончания записи
                
                if data:
                    audio_file.writeframes(data)
                    await websocket.send(data)
                
                result = await websocket.recv()
                
                try:
                    result_json = json.loads(result)
                    send_message('message', result_json, room=client_id)
                    app.logger.info(f"Transcription result: {result_json}")
                except json.JSONDecodeError:
                    app.logger.error(f"Failed to decode JSON: {result}")

            await websocket.send('{"eof" : 1}')
            audio_file.close()
            with audio_files_lock:
                del audio_files[client_id]

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(transcribe())
    asyncio.run(transcribe())
    


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

# Если пустые файлы 
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
                # TODO: добавить room
                send_message('message', json.loads(result))
                app.logger.info(f"Transcription result: {result}")

            await websocket.send('{"eof" : 1}')
            final_result = await websocket.recv()
            # TODO: добавить room
            send_message('message', json.loads(final_result))
            app.logger.info(f"Final transcription result: {final_result}")

            # Сигнал о завершении транскрипции
            send_message('transcription_finished')
            app.logger.info("Transcription finished")

    # loop = asyncio.new_event_loop()
    # asyncio.set_event_loop(loop)
    # loop.run_until_complete(transcribe())
    asyncio.run(transcribe())
    os.remove(file_path)

if __name__ == '__main__':
    os.makedirs("uploads", exist_ok=True)
    socketio.run(app, debug=True, host='0.0.0.0', port=5000)
