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

from app.libraries.vad import voice_prob

import numpy as np
from scipy.signal import resample
 
class WAVTask(Task):
    def __init__(self, file_path: str, filename: str):
        super().__init__()
        self.file_path = file_path
        self.filename = filename
        self.result = None  # Изначально результат пустой

    def set_result(self, result: str):
        self.result = result
        
    def stereo_to_mono(self, data):
        # Преобразование в массив numpy
        audio_data = np.frombuffer(data, dtype=np.int16)
        # Преобразование стерео в моно усреднением
        mono_data = (audio_data[0::2] + audio_data[1::2]) // 2
        return mono_data.astype(np.int16).tobytes()
        
    def transcribe_file(self):
        async def transcribe():
            uri = Config.VOSK_URI
            logging.info(f"def transcribe: Task ID in transcribe func is {self.task_id} and Client ID is {self.client_sid}")
            async with websockets.connect(uri) as websocket:
                wf = wave.open(self.file_path, "rb")
                target_samples = 512
                original_rate = wf.getframerate()
                buffer_size = int(target_samples*(original_rate//512)) # dynamic buffer, takes about 1 second from file
                await websocket.send('{ "config" : { "sample_rate" : %d } }' % (original_rate))
        
                while True:
                    data = wf.readframes(buffer_size)
                    if len(data) == 0:
                        break

                    # Преобразование стерео в моно (если нужно)
                    if wf.getnchannels() == 2:
                        data = self.stereo_to_mono(data)
                    
                    # Скармливаем данные VAD детектору
                    if (voice_prob(data, original_rate)<0.1):
                        logging.info(f"Buffer size is {buffer_size}, it's {buffer_size/512} packages. Audio package is not sended")
                        send_message(self.client_sid, 'stopped')
                        continue
                        
                    send_message(self.client_sid, 'working')
                    await websocket.send(data)    
                    result = await websocket.recv()
                    logging.info(result)
                    send_message(self.client_sid, 'message', json.loads(result))
            
                await websocket.send('{"eof" : 1}')
                final_result = await websocket.recv()
                send_message(self.client_sid, 'message', json.loads(final_result))
            
                send_message(self.client_sid, 'stopped')
                send_message(self.client_sid, 'transcription_finished')
                logging.info("def transcribe: Transcription finished")
    
        self.log_file_params(self.file_path)
        self.set_status("processing")         
        try:
            asyncio.run(transcribe())     
            self.set_status("completed")
        except:
            self.set_status("failed")
        finally:
            os.remove(self.file_path)
        
        
    