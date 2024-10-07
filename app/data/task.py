import uuid
import logging
from app.data.task_status import TaskStatus
import wave


# from app.data.client import Client

class Task:
    def __init__(self):
        self.task_id = str(uuid.uuid4())  # Генерируем уникальный ID задачи
        self.status = TaskStatus.CREATED  # Статус задачи, по умолчанию "created"

    def set_status(self, status):
        """Обновление статуса задачи."""
        self.status = status
        logging.info(f"Task {self.task_id} status updated to {self.status}")

    def set_client(self, client_sid: str):
        self.client_sid = client_sid
        
    def get_task_id(self):
        return self.task_id
    
    def log_file_params(self, file_path):
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
