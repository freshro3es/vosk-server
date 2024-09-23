from app.config import Config
from app.socket_handler import send_message
from app.data.task import Task
from app.data.task_status import TaskStatus
import eventlet
import logging
import wave
import websockets
import os
import asyncio
import json

# from app.libraries.vad import voice_prob

import numpy as np
from scipy.signal import resample


def log_wav_file_params(file_path):
    try:
        with wave.open(file_path, 'rb') as wf:
            params = wf.getparams()
            n_channels, sampwidth, framerate, n_frames = params[:4]

            # Длительность аудио в секундах
            duration = n_frames / float(framerate)

            # Логирование параметров
            logging.info(f"WAV File: {file_path}")
            logging.info(f"Number of Channels: {n_channels}")
            logging.info(f"Sample Width (bytes): {sampwidth}")
            logging.info(f"Frame Rate (samples per second): {framerate}")
            logging.info(f"Number of Frames: {n_frames}")
            logging.info(f"Duration (seconds): {duration:.2f}")

    except wave.Error as e:
        logging.error(f"Error processing WAV file: {e}")
 
class WAVTask(Task):
    def __init__(self, file_path: str, filename: str):
        super().__init__()
        self.file_path = file_path
        self.filename = filename
        self.result = None  # Изначально результат пустой

    def set_result(self, result: str):
        self.result = result
        
        
    def stereo_to_mono(self, data):
        # Преобразование стерео в моно усреднением
        mono_data = (data[0::2] + data[1::2]) // 2
        return mono_data

    def resample_audio(self, data, original_rate, target_rate):
        # Изменение частоты дискретизации
        num_samples = int(len(data) * float(target_rate) / original_rate)
        resampled_data = resample(data, num_samples)
        return resampled_data
        
        
    
    def transcribe_file(self):
        async def transcribe():
            uri = Config.VOSK_URI
            logging.info(f"def transcribe: Task ID in transcribe func is {self.task_id} and Client ID is {self.client_sid}")
            async with websockets.connect(uri) as websocket:
                wf = wave.open(self.file_path, "rb")
                
                target_samples = 512
                
                await websocket.send('{ "config" : { "sample_rate" : %d } }' % (16000))
                buffer_size = int(target_samples*40) # 40 packages about 512 samples

                while True:
                    data = wf.readframes(buffer_size)
                    if len(data) == 0:
                        break
                    
                    # Преобразование в массив numpy
                    audio_data = np.frombuffer(data, dtype=np.int16)

                    # Преобразование стерео в моно (если нужно)
                    if wf.getnchannels() == 2:
                        audio_data = self.stereo_to_mono(audio_data)

                    # Изменение частоты дискретизации (если нужно)
                    original_rate = wf.getframerate()
                    target_rate = 16000  # Частота дискретизации, которую требует модель
                    if original_rate != target_rate:
                        audio_data = self.resample_audio(audio_data, original_rate, target_rate)

                    # Преобразование обратно в байты
                    audio_data = audio_data.astype(np.int16).tobytes()
                    
                    # if (voice_prob(data)<0.004):
                    #     logging.info("Audio package is not sended")
                    #     send_message(self.client_sid, 'stopped')
                    #     continue

                    # # Запись обработанных данных в файл
                    # output_wav.writeframes(audio_data)
                        
                    send_message(self.client_sid, 'working')
                    await websocket.send(audio_data)    
                    result = await websocket.recv()
                    send_message(self.client_sid, 'message', json.loads(result))
                    # logging.info(f"Transcription result: {result}")
            
                await websocket.send('{"eof" : 1}')
                final_result = await websocket.recv()
                send_message(self.client_sid, 'message', json.loads(final_result))
                # logging.info(f"Final transcription result: {final_result}")
            
                send_message(self.client_sid, 'stopped')
                
                send_message(self.client_sid, 'transcription_finished')
                logging.info("def transcribe: Transcription finished")
                
                # # Закрываем файл
                # output_wav.close()
    
        log_wav_file_params(self.file_path)
        asyncio.run(transcribe())  
        
        # Используем eventlet для выполнения асинхронной задачи
        # eventlet.spawn(lambda: asyncio.run(transcribe()))   
        
        os.remove(self.file_path)
        # log_wav_file_params("output.wav")
        
        
    