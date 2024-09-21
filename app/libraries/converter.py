from pydub import AudioSegment
import wave
import numpy as np
from io import BytesIO
from werkzeug.utils import secure_filename
from werkzeug.datastructures import FileStorage

class Converter:
    def convert_file(file):
        extension = file.filename.split('.')[-1]
        if extension == 'mp3':
            wav_io = mp3_to_wav(file)
            
            # Создаем новый FileStorage объект для конвертированного файла
            filename = secure_filename(file.filename.replace(extension, 'wav'))
            file = FileStorage(
                stream=wav_io,
                filename=filename,
                content_type='audio/wav'
            )
            
            return file
            
        # Other formats
        return None

def mp3_to_wav(file):
        # Чтение файла mp3
        sound = AudioSegment.from_mp3(file)

        # Преобразование в массив numpy
        samples = np.array(sound.get_array_of_samples())

        # Если аудио стерео, то преобразование в моно
        if sound.channels == 2:
            samples = samples.reshape((-1, 2))
            samples = np.mean(samples, axis=1)

        # Нормализация аудиоданных
        samples = samples / np.max(np.abs(samples))
        samples = (samples * 32767).astype(np.int16)

        return write_wav(sound, samples)
        
    
def write_wav(sound, samples):
    # Создание WAV файла в памяти с использованием BytesIO
        wav_io = BytesIO()
        with wave.open(wav_io, "w") as wav_file:
            wav_file.setnchannels(1)  # моно
            wav_file.setsampwidth(2)  # 16 бит
            wav_file.setframerate(sound.frame_rate)
            wav_file.writeframes(samples.tobytes())

        # Перематываем файл на начало
        wav_io.seek(0)
        return wav_io 