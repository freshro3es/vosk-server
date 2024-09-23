import logging
from flask import request, current_app
from app.context import socketio
import numpy as np
import eventlet
import asyncio

@socketio.on('connect')
def handle_connect():
    logging.info(f"Client connected: {request.sid}")

@socketio.on('disconnect')
def handle_disconnect():
    logging.info(f"Client disconnected: {request.sid}")

@socketio.on('listen_task')
def handle_listen_task(data):
    task_id = data.get('task_id')
    logging.info(f'listen task request: task id is {task_id} and client sid is {request.sid}')

    if task_id:
        task_manager =  current_app.config['TASK_MANAGER']
        task = task_manager.find_task_by_id(task_id)
        if task:
            task.set_client(request.sid)
            logging.info(f"listen_task event: started work on WAV file {task.filename} with id {task_id}")
            socketio.start_background_task(
                target=task.transcribe_file,
            )
            send_message(request.sid, 'listening', {'message': f'Listening to task {task_id}'})
        else:
            send_message(request.sid, 'error', {'message': f'Task {task_id} not found'})
    else:
        send_message(request.sid, 'error', {'message': 'Invalid task_id'})
        
def send_message(client_sid, event, data=None):
    if client_sid:
        socketio.emit(event, data, room=client_sid)

# Обработчик WebSocket для начала передачи аудио данных
@socketio.on('start_recording')
def handle_start_recording(data):
    channel_count = data.get('channelCount')
    sample_rate = data.get('sampleRate')
    logging.info(f"Recording started, num channels is {channel_count} and sample rate is {sample_rate}")
    task_manager =  current_app.config['TASK_MANAGER']
    task = task_manager.add_voice_task(request.sid, sample_rate, channel_count, 2)
    logging.info(f"Client {task.client_sid} created a file. Audio file path: {task.audio_file_path}")

    # Запуск фоновой задачи для обработки аудио данных
    socketio.start_background_task(target=task.transcribe_audio_stream)
    
# Обработчик WebSocket для приема аудио данных
@socketio.on('audio_data')
def handle_audio_data(data):
    logging.info(f"Audio data recieved from {request.sid}")
    task_manager =  current_app.config['TASK_MANAGER']
    task = task_manager.find_task_by_client(request.sid)
    audio_data = data.get('audio_data')
    task.put_data(audio_data)

# Обработчик WebSocket для остановки передачи аудио данных
@socketio.on('stop_recording')
def handle_stop_recording():
    logging.info(f"Recording stopped")
    task_manager =  current_app.config['TASK_MANAGER']
    task = task_manager.find_task_by_client(request.sid)
    task.put_data(None)
    