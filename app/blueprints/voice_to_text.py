from flask import Blueprint, request, jsonify, render_template
from werkzeug.utils import secure_filename
import os
import json
import wave
import time
import asyncio
import websockets
from app.context import socketio
from app.config import Config
from threading import Lock
import logging

voice_bp = Blueprint('voice_bp', __name__, template_folder="templates")

@voice_bp.route('/voice-to-text')
def voice_to_text():
    return render_template('voice_to_text.html')


# # Очередь для хранения аудио данных
# audio_queues = {}
# # Для файлов
# audio_files = {}
# audio_files_lock = Lock()

# @socketio.on('start_recording')
# def handle_start_recording():
#     logging.info(f"Recording started")
    
#     client_id = request.sid
#     audio_queue = asyncio.Queue()
#     audio_queues[client_id] = audio_queue

#     timestamp = int(time.time())
#     audio_file_path = os.path.join(Config.RECORDS_DIR, f"{client_id}_{timestamp}.wav")
#     audio_file = wave.open(audio_file_path, 'wb')
#     audio_file.setnchannels(1)  # Mono
#     audio_file.setsampwidth(2)  # 16bit
#     audio_file.setframerate(16000)  # 16kHz
    
#     with audio_files_lock:
#         audio_files[client_id] = audio_file
#         logging.info(f"Client {client_id} created a file. Audio file path: {audio_file_path}")

#     socketio.start_background_task(target=transcribe_audio_stream, client_id=client_id, audio_queue=audio_queue)

# @socketio.on('audio_data')
# def handle_audio_data(data):
#     client_id = request.sid
#     if client_id in audio_queues:
#         audio_queues[client_id].put_nowait(data)

# @socketio.on('stop_recording')
# def handle_stop_recording():
#     client_id = request.sid
#     if client_id in audio_queues:
#         audio_queues[client_id].put_nowait(None)

# def transcribe_audio_stream(client_id, audio_queue):
#     async def transcribe():
#         uri = Config.VOSK_URI
#         async with websockets.connect(uri) as websocket:
#             await websocket.send('{ "config" : { "sample_rate" : 16000 } }')

#             with audio_files_lock:
#                 audio_file = audio_files[client_id]
                
#             while True:
#                 data = await audio_queue.get()
#                 if data is None and audio_queue.empty():
#                     break
                
#                 if data:
#                     audio_file.writeframes(data)
#                     await websocket.send(data)
                
#                 result = await websocket.recv()
#                 try:
#                     result_json = json.loads(result)
#                     send_message('message', result_json, room=client_id)
#                 except json.JSONDecodeError:
#                     pass

#             await websocket.send('{"eof" : 1}')
#             audio_file.close()
#             with audio_files_lock:
#                 del audio_files[client_id]

#     asyncio.run(transcribe())

# def send_message(event, data=None, room=None):
#     if room:
#         socketio.emit(event, data, room=room)
#     else:
#         socketio.emit(event, data)

