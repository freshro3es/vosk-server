from eventlet.queue import Queue
from app.config import Config
from app.socket_handler import send_message
from app.data.task import Task
from app.data.task_status import TaskStatus
import logging
import wave
import websockets
import os
import asyncio
import json
import time
 
class VoiceTask(Task):
    def __init__(self, client_sid: str, framerate:int=16000, channels:int=1, sampwidth:int=2):
        super().__init__()
        self.audio_queue = Queue()
        self.framerate = framerate
        self.channels = channels
        self.sampwidth = sampwidth
        
        # Создаем файл для записи аудио данных в формате WAV
        self.timestamp = int(time.time())
        self.audio_file_path = os.path.join(Config.RECORDS_DIR, f"{client_sid}_{self.timestamp}.wav")
        self.audio_file = wave.open(self.audio_file_path, 'wb')
        self.audio_file.setnchannels(channels)  # Mono
        self.audio_file.setsampwidth(sampwidth)  # 16bit
        self.audio_file.setframerate(framerate)  # 16kHz
        
        # Заглушка, не используется
        self.result = None  # Изначально результат пустой

    # Заглушка, не используется
    def set_result(self, result: str):
        self.result = result
    
    def put_data(self, audio_data):
        self.audio_queue.put_nowait(audio_data)
    
    # Функция для обработки аудио потока
    def transcribe_audio_stream(self):
        async def transcribe():
            logging.info(f"Audio stream started for client {self.client_sid}")
            uri = Config.VOSK_URI
            async with websockets.connect(uri) as websocket:
                logging.info(f"Connected to websocket of vosk")
                await websocket.send('{ "config" : { "sample_rate" : 16000 } }')
                logging.info(f"client_id is {self.client_sid}")
                
                while True:
                    data = self.audio_queue.get()
                    logging.info(f"Got data from audio queue")
                    if data is None and self.audio_queue.empty(): # Наверное, если добавить И на очередь, то ок?
                        break  # Завершаем цикл, если получили сигнал окончания записи
                
                    if data:
                        self.audio_file.writeframes(data)
                        await websocket.send(data)

                    result = await websocket.recv()
                
                    try:
                        result_json = json.loads(result)
                        send_message(self.client_sid, 'message', result_json)
                        logging.info(f"Transcription result: {result_json}")
                    except json.JSONDecodeError:
                        logging.error(f"Failed to decode JSON: {result}")

                await websocket.send('{"eof" : 1}')
                self.audio_file.close()
        asyncio.run(transcribe())
