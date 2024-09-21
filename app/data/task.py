import uuid
import logging
from app.data.task_status import TaskStatus
import numpy as np
import scipy.fftpack


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
    
    def is_speech(self, audio_data, sample_rate):
        # Преобразование аудиоданных в массив NumPy
        # audio_array = np.frombuffer(audio_data.get_raw_data(), dtype=np.int16)
        audio_array = np.frombuffer(audio_data, dtype=np.int16)
    
        # Применение быстрого преобразования Фурье (FFT)
        fft_spectrum = np.abs(scipy.fftpack.fft(audio_array))
    
        # Частотная шкала
        freqs = scipy.fftpack.fftfreq(len(fft_spectrum), 1/sample_rate)
    
        # Удаление отрицательных частот
        positive_freqs = freqs[freqs >= 0]
        positive_spectrum = fft_spectrum[freqs >= 0]
    
        # Ограничение диапазона частот для речи (примерно от 300 Гц до 3000 Гц)
        speech_freqs = positive_spectrum[(positive_freqs >= 300) & (positive_freqs <= 3000)]
    
        # Анализ энергии сигнала в этом диапазоне
        speech_energy = np.sum(speech_freqs ** 2)
    
        # Пороговое значение для определения речи
        energy_threshold = 500000  # Настройка порога в зависимости от условий
    
        return speech_energy > energy_threshold
