from flask import Blueprint, session, request, jsonify, render_template, current_app
from werkzeug.utils import secure_filename
import logging
import os
import json
import wave
import asyncio
import websockets
from app.extensions import socketio
from app.config import Config
from app.clients import Clients

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

    # Запуск асинхронной задачи для транскрибации файла
    client_id = session.get('client_id')  # Извлекаем client_id из сессии
    if (client_id is None):
        logging.warning(f"Client ID is {client_id}, something went wrong")
        return jsonify({"error": "Failed to identify the client"}), 500
    logging.info(f"started work on WAV file {filename} of client {client_id}")
    
    socketio.start_background_task(target=transcribe_file, file_path=file_path, client_id=client_id)
    
    return jsonify({"status": "Processing started"}), 200

# def transcribe_file(file_path):
#     async def transcribe():
#         uri = Config.VOSK_URI
#         async with websockets.connect(uri) as websocket:
#             wf = wave.open(file_path, "rb")
#             await websocket.send('{ "config" : { "sample_rate" : %d } }' % (wf.getframerate()))
#             buffer_size = int(wf.getframerate() * 1.2)

#             while True:
#                 data = wf.readframes(buffer_size)
#                 if len(data) == 0:
#                     break

#                 await websocket.send(data)
#                 result = await websocket.recv()
#                 send_message('message', json.loads(result))
#                 logging.info(f"Transcription result: {result}")
            
#             await websocket.send('{"eof" : 1}')
#             final_result = await websocket.recv()
#             send_message('message', json.loads(final_result))
#             logging.info(f"Final transcription result: {final_result}")
            
#             send_message('transcription_finished')
#             logging.info("Transcription finished")
    
#     asyncio.run(transcribe())
#     # loop.run_until_complete(transcribe())
#     os.remove(file_path)

def transcribe_file(file_path, client_id):
    async def transcribe():
        uri = Config.VOSK_URI
        async with websockets.connect(uri) as websocket:
            wf = wave.open(file_path, "rb")
            await websocket.send('{ "config" : { "sample_rate" : %d } }' % (wf.getframerate()))
            buffer_size = int(wf.getframerate() * 1.2)

            while True:
                data = wf.readframes(buffer_size)
                if len(data) == 0:
                    break

                await websocket.send(data)
                result = await websocket.recv()
                clients.send_message('message', json.loads(result))
                logging.info(f"Transcription result: {result}")
            
            await websocket.send('{"eof" : 1}')
            final_result = await websocket.recv()
            clients.send_message('message', json.loads(final_result))
            logging.info(f"Final transcription result: {final_result}")
            
            clients.send_message('transcription_finished')
            logging.info("Transcription finished")
    
    asyncio.run(transcribe())
    # loop.run_until_complete(transcribe())
    os.remove(file_path)

def send_message(event, data=None, room=None):
    if room:
        socketio.emit(event, data, room=room)
    else:
        socketio.emit(event, data)
        
        
        
# Инициализация клиента в приложении Flask
clients = Clients()

# Примеры использования внутри маршрутов Flask или обработчиков событий SocketIO
@socketio.on('connect')
def handle_connect():
    client_id = request.sid
    clients.add_client(client_id)
    clients.send_message(client_id, 'client_id', client_id)

@socketio.on('disconnect')
def handle_disconnect():
    client_id = request.sid
    session['client_id'] = client_id  # Сохраняем client_id в сессии
    clients.remove_client(client_id)
