from app.config import Config
from app.socket_handler import send_message
from app.data.task import Task
import logging
import wave
from wave import Wave_read
import websockets
import os
import asyncio
import json
import traceback

from app.libraries.vad import voice_prob, load_model

import numpy as np


class WAVTask(Task):
    def __init__(self, file_path: str, filename: str):
        super().__init__()
        self.file_path: str = file_path
        self.filename: str = filename
        self.audiofile: Wave_read
        self.result: str = ''# Изначально результат пустой

    def add_result(self, result: str):
        if self.result:
            self.result += result
        else:
            self.result = result

    def stereo_to_mono(self, data:bytes):
        # Преобразование в массив numpy
        audio_data = np.frombuffer(data, dtype=np.int16)
        # Преобразование стерео в моно усреднением
        mono_data = (audio_data[0::2] + audio_data[1::2]) // 2
        return mono_data.astype(np.int16).tobytes()

    def transcribe_file(self):
        async def transcribe():
            uri = Config.VOSK_URI
            logging.info(
                f"def transcribe: Task ID in transcribe func is {self.task_id} and Client ID is {self.client_sid}"
            )
            vad_model = load_model()
            vad_target_samples = 512
            async with websockets.connect(uri) as websocket:
                self.audiofile = wave.open(self.file_path, "rb")
                original_rate = self.audiofile.getframerate()
                buffer_size = int(
                    vad_target_samples * (original_rate // 512)
                )  # dynamic buffer, takes about 1 second from file
                await websocket.send(
                    '{ "config" : { "sample_rate" : %d } }' % (original_rate)
                )

                active_sentence = False
                start_time_in_seconds = 0
                while True:
                    if not active_sentence:
                        active_sentence = True
                        # Вычисляем тайм-код в секундах
                        start_time_in_seconds = self.audiofile.tell() / self.audiofile.getframerate()

                    # Считываем массив байтов длинной `buffer_size` из аудиофайла
                    data = self.audiofile.readframes(buffer_size)
                    if len(data) == 0:
                        break

                    # Преобразование стерео в моно (если нужно)
                    if self.audiofile.getnchannels() == 2:
                        data = self.stereo_to_mono(data)

                    # Скармливаем данные VAD детектору
                    if voice_prob(vad_model, data, original_rate) < 0.1:
                        logging.info(
                            f"Buffer size is {buffer_size}, it's {buffer_size/512} packages. Audio package is not sended"
                        )
                        send_message(self.client_sid, "stopped")
                        continue

                    send_message(self.client_sid, "working")
                    await websocket.send(data)
                    result = await websocket.recv()

                    if '"result"' in result:
                        result = self.process_result(
                            result, start_time_in_seconds, self.audiofile.tell() / self.audiofile.getframerate()
                        )
                        active_sentence = False

                    logging.debug(result)
                    if result:
                        send_message(self.client_sid, "message", json.loads(result))

                await websocket.send('{"eof" : 1}')
                final_result = await websocket.recv()
                final_result = self.process_result(
                    final_result, start_time_in_seconds, self.audiofile.tell() / self.audiofile.getframerate()
                )
                if final_result:
                    send_message(self.client_sid, "message", json.loads(final_result))

                send_message(self.client_sid, "stopped")
                send_message(self.client_sid, "transcription_finished")
                logging.info("def transcribe: Transcription finished")
                del vad_model

        self.log_file_params(self.file_path)
        self.set_status("processing")
        try:
            asyncio.run(transcribe())
            self.set_status("completed")
        except Exception:
            self.set_status("failed")
            send_message(self.client_sid, "failed")
            logging.info(traceback.format_exc())
        finally:
            os.remove(self.file_path)

    def process_result(self, data: str, start: float, end: float) -> str:
        """
        Эта функция появилась как ответ на бесполезность временных меток VOSK в поле "result" из-за использования VAD.
        
        Модифицирует JSON-строку с промежуточным результатом и текстом из VOSK модели, удаляя поле "result" и добавляя временные метки "start" и "end".

        Аргументы:
            data (str): Строка с данными в формате JSON.
            start (float): Время начала, которое будет добавлено в JSON-объект.
            end (float): Время окончания, которое будет добавлено в JSON-объект.

        Возвращает:
            str: Обновлённая строка в формате JSON с добавленными полями "start" и "end" и без поля "result".
            
        """
        # Преобразуем строку в словарь
        parsed_data = json.loads(data)

        if not parsed_data["text"]:
            return None

        # Удаляем ключ "result"
        if "result" in parsed_data:
            del parsed_data["result"]

        self.add_result(parsed_data["text"])
        
        # Добавляем start и end в словарь
        parsed_data["start"] = start
        parsed_data["end"] = end

        # Преобразуем словарь обратно в строку JSON
        json_string = json.dumps(parsed_data, ensure_ascii=False)

        # Выводим результат
        return json_string

