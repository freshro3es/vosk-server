import eventlet
eventlet.monkey_patch()

from flask import Flask, request, jsonify, render_template
from flask_socketio import SocketIO
from flask_cors import CORS
from werkzeug.utils import secure_filename
import os
import json
import wave
import asyncio
import websockets

eventlet.monkey_patch()

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app, async_mode='eventlet', cors_allowed_origins="*")
CORS(app)

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/wav-to-text')
def wav_to_text():
    return render_template('wav_to_text.html')

@app.route('/voice-to-text')
def voice_to_text():
    return render_template('voice_to_text.html')

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
# Paste code here

def transcribe_file(file_path):
    async def transcribe():
        uri = "ws://localhost:2700"
        async with websockets.connect(uri) as websocket:
            wf = wave.open(file_path, "rb")
            await websocket.send('{ "config" : { "sample_rate" : %d } }' % (wf.getframerate()))
            buffer_size = int(wf.getframerate() * 0.2)  # 0.2 seconds of audio

            while True:
                data = wf.readframes(buffer_size)
                if len(data) == 0:
                    break

                await websocket.send(data)
                result = await websocket.recv()
                socketio.emit('transcription_result', json.loads(result))
                print(result)

            await websocket.send('{"eof" : 1}')
            final_result = await websocket.recv()
            socketio.emit('transcription_result', json.loads(final_result))
            print(final_result)
            
            # Emit a signal that the processing is finished
            socketio.emit('transcription_finished')

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(transcribe())
    os.remove(file_path)

if __name__ == '__main__':
    os.makedirs("uploads", exist_ok=True)
    socketio.run(app, debug=True, host='0.0.0.0', port=5000)
