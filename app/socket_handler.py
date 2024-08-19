import logging
from flask import request, current_app
from app.context import socketio

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
        task = task_manager.find_task(task_id)
        if task:
            task.set_client(request.sid)
            logging.info(f"listen_task event: started work on WAV file {task.filename} with id {task_id}")
            socketio.start_background_task(
                target=task.transcribe_file,
            )
            send_message(request.sid, 'listening', {'message': f'Listening to task {task_id}'})
        else:
            send_message(request.sid, 'error', {'message': 'Task not found'})
    else:
        send_message(request.sid, 'error', {'message': 'Invalid task_id'})
        
def send_message(client_sid, event, data=None):
    if client_sid:
        socketio.emit(event, data, room=client_sid)
