import eventlet
eventlet.monkey_patch()

from flask import Flask, request, jsonify, render_template, send_from_directory
from flask_socketio import SocketIO
from flask_cors import CORS
from werkzeug.utils import secure_filename
import os
import json
import wave
import asyncio
import websockets

eventlet.monkey_patch()

# Загрузка конфигурации из config.json
with open('config.json') as config_file:
    config = json.load(config_file)

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app, async_mode='eventlet', cors_allowed_origins="*")
CORS(app)

VOSK_URI = config['voskUrl']

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/wav-to-text')
def wav_to_text():
    return render_template('wav_to_text.html')

@app.route('/voice-to-text')
def voice_to_text():
    return render_template('voice_to_text.html')

@app.route('/data-conversion-processor.js')
def data_conversion_processor():
    return send_from_directory('templates', 'data-conversion-processor.js')

# Returns Uri configuration to frontend
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

    socketio.start_background_task(target=transcribe_file, file_path=file_path)

    return jsonify({"status": "Processing started"}), 200

# TODO: Add route for transcribing voice to text and logic also. Use WebSockets
@socketio.on('audio_data')
def handle_audio_data(audio_data):
    app.logger.info('Received audio data')
    async def transcribe():
        uri = VOSK_URI
        async with websockets.connect(uri) as websocket:
            await websocket.send('{ "config" : { "sample_rate" : 16000 } }')

            await websocket.send(audio_data)
            result = await websocket.recv()
            try:
                result_json = json.loads(result)
                socketio.emit('transcription_result', {'result': result_json.get('partial', '')})
                app.logger.info(f"Transcription result: {result_json}")
            except json.JSONDecodeError:
                app.logger.error(f"Failed to decode JSON: {result}")

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(transcribe())

@socketio.on('stop_recording')
def handle_stop_recording():
    app.logger.info('Received stop recording signal')
    # Here we can add logic to stop processing audio or other actions if necessary

@socketio.on('disconnect')
def handle_disconnect():
    app.logger.info('Client disconnected')
  


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
                socketio.emit('message', json.loads(result))
                # print('result: ', result)
                app.logger.info(f"Transcription result: {result}")  

            await websocket.send('{"eof" : 1}')
            final_result = await websocket.recv()
            socketio.emit('message', json.loads(final_result))
            # print('final_result: ', final_result)
            app.logger.info(f"Final transcription result: {final_result}")  # app.logger final transcription result
            
            # Emit a signal that the processing is finished
            socketio.emit('transcription_finished')
            app.logger.info("Transcription finished") 

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(transcribe())
    os.remove(file_path)

if __name__ == '__main__':
    os.makedirs("uploads", exist_ok=True)
    socketio.run(app, debug=True, host='0.0.0.0', port=5000)
