from flask import Blueprint, session, request, jsonify, render_template, current_app
from werkzeug.utils import secure_filename
import logging
import os
import json
import wave
import asyncio
import websockets
import uuid
from app.extensions import socketio
from app.config import Config
from app.clients import Clients

from app.data.task_manager import TaskManager
from app.data.wav_task import WAVTask

wav_bp = Blueprint('wav_bp', __name__, template_folder="templates")

task_manager = TaskManager()

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

    task_id = str(uuid.uuid4())
    
    task = WAVTask(file_path, filename)
    task_manager.add_wav_task(task)

    # Отправляем task_id клиенту
    return jsonify({"task_id": task.task_id}), 200  
    

def transcribe_file(task):
    async def transcribe():
        uri = Config.VOSK_URI
        logging.info(f"def transcribe: Task ID in transcribe func is {task.task_id} and Client ID is {task.client_sid}")
        async with websockets.connect(uri) as websocket:
            wf = wave.open(task.file_path, "rb")
            await websocket.send('{ "config" : { "sample_rate" : %d } }' % (wf.getframerate()))
            buffer_size = int(wf.getframerate() * 1.2)

            while True:
                data = wf.readframes(buffer_size)
                if len(data) == 0:
                    break

                await websocket.send(data)
                result = await websocket.recv()
                #  send_message('message', json.loads(result))
                clients.send_message(task.client_sid, 'message', json.loads(result))
                # logging.info(f"Transcription result: {result}")
            
            await websocket.send('{"eof" : 1}')
            final_result = await websocket.recv()
            # send_message('message', json.loads(final_result))
            clients.send_message(task.client_sid, 'message', json.loads(final_result))
            # logging.info(f"Final transcription result: {final_result}")
            
            # send_message('transcription_finished')
            clients.send_message(task.client_sid, 'transcription_finished')
            logging.info("def transcribe: Transcription finished")
    
    asyncio.run(transcribe())
    os.remove(task.file_path)


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
    clients.remove_client(client_id)

  

@socketio.on('listen_task')
def handle_listen_task(data):
    logging.info(f'got information: {data}')
    task_id = data.get('task_id')
    client_sid = request.sid
    logging.info(f'listen task request: task id is {task_id} and client sid is {client_sid}')

    if task_id:        
        task = task_manager.find_task(task_id)
        task.set_client(client_sid) 
        if task:
            socketio.start_background_task(
                target=transcribe_file, 
                task=task
            )    
               
        logging.info(f"def upload: started work on WAV file {task.filename} with id {task_id}")

        send_message('listening', {'message': f'Listening to task {task_id}'}, room=client_sid)
    else:
        send_message('error', {'message': 'Invalid task_id'}, room=client_sid)
