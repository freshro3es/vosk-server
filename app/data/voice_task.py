from queue import Queue
from app.config import Config
from app.socket_handler import send_message
from app.data.task import Task
import logging
import wave
import websockets
import os
import asyncio
import json
import time
from datetime import datetime
import traceback

from app.libraries.vad import voice_prob


class VoiceTask(Task):
    def __init__(
        self,
        client_sid: str,
        framerate: int = 16000,
        channels: int = 1,
        sampwidth: int = 2,
    ):
        super().__init__()
        self.set_client(client_sid)
        self.audio_queue: Queue = Queue()
        self.framerate = framerate
        self.channels = channels
        self.sampwidth = sampwidth

        # Создаем файл для записи аудио данных в формате WAV
        self.timestamp = int(time.time())
        # Получаем текущее время в формате hh-mm-ss_dd-mm-yy
        current_time = datetime.now().strftime("%d-%m-%yT%H:%M:%SZ")
        self.audio_file_path = os.path.join(
            Config.RECORDS_DIR, f"{client_sid}_{current_time}.wav"
        )
        self.audio_file = wave.open(self.audio_file_path, "wb")
        self.audio_file.setnchannels(channels)  # Mono
        self.audio_file.setsampwidth(sampwidth)  # 16bit
        self.audio_file.setframerate(framerate)  # 16kHz

        # Заглушка, не используется
        self.result: str  # Изначально результат пустой

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
                logging.info("Connected to websocket of vosk")
                await websocket.send(
                    '{ "config" : { "sample_rate" : ' + str(self.framerate) + " } }"
                )
                logging.info(f"client_id is {self.client_sid}")

                active_sentence = False
                start_time_in_seconds = 0
                while True:
                    if self.audio_queue.empty():
                        await asyncio.sleep(1)
                        continue

                    if not active_sentence:
                        active_sentence = True
                        # Вычисляем тайм-код в секундах
                        start_time_in_seconds = (
                            self.audio_file.tell() / self.audio_file.getframerate()
                        )

                    data = self.audio_queue.get()
                    logging.info("Got data from audio queue")

                    if data is None:
                        break  # Завершаем цикл, если получили сигнал окончания записи

                    self.audio_file.writeframes(data)

                    # Скармливаем данные VAD детектору
                    if voice_prob(data, self.framerate) < 0.1:
                        logging.info(
                            f"Buffer size is {len(data)}, it's {len(data)/512} packages. Audio package is not sended"
                        )
                        send_message(self.client_sid, "stopped")
                        continue

                    send_message(self.client_sid, "working")
                    await websocket.send(data)

                    result = await websocket.recv()

                    if '"result"' in result:
                        result = process_result(
                            result,
                            start_time_in_seconds,
                            self.audio_file.tell() / self.audio_file.getframerate(),
                        )
                        active_sentence = False

                    try:
                        result_json = json.loads(result)
                        send_message(self.client_sid, "message", result_json)
                        logging.info(f"Transcription result: {result_json}")
                    except json.JSONDecodeError:
                        logging.error(f"Failed to decode JSON: {result}")

                send_message(self.client_sid, "stopped")
                await websocket.send('{"eof" : 1}')
                self.audio_file.close()
                self.log_file_params(self.audio_file_path)
                # self.client_sid += self.audio_file_path

        self.set_status("processing")
        try:
            asyncio.run(transcribe())
            self.set_status("completed")
        except Exception:
            self.set_status("failed")
            logging.info(traceback.format_exc())


def process_result(data, start, end):
    # Преобразуем одинарные кавычки в двойные для корректного парсинга
    data = data.replace("'", '"')

    # Преобразуем строку в словарь
    parsed_data = json.loads(data)

    # Удаляем ключ "result"
    if "result" in parsed_data:
        del parsed_data["result"]

    # Добавляем start и end в словарь
    parsed_data["start"] = start
    parsed_data["end"] = end

    # Преобразуем словарь обратно в строку JSON
    json_string = json.dumps(parsed_data, ensure_ascii=False)

    # Выводим результат
    return json_string
