from werkzeug.utils import secure_filename
import logging
import traceback

import soundfile as sf
import os


class Converter:
    def convert_file(file):
        extension = file.filename.split(".")[-1]
        if extension == "mp3":
            new_filename = mp3_to_wav(file, 25 * 1024 * 8)
            return new_filename

        # Other formats
        return None


def mp3_to_wav(file, buffer: int) -> tuple[str, str] | None:
    try:
        input_file = sf.SoundFile(file, "r")
        new_filename = secure_filename(file.filename.replace(".mp3", ".wav"))
        new_filepath = os.path.join(os.getenv("UPLOADS_DIR", "uploads"), new_filename)
        output_file = sf.SoundFile(
            new_filepath,
            "w",
            samplerate=input_file.samplerate,
            channels=input_file.channels,
        )

        while input_file.tell() < input_file.frames:
            pos = input_file.tell()
            if pos + buffer < input_file.frames:
                data = input_file.read(buffer)
                output_file.write(data)
            else:
                data = input_file.read(input_file.frames - pos)
                output_file.write(data)
                logging.info(f"ended on {input_file.tell()}, all is good")
                break

            pos += buffer
            input_file.seek(pos)
            output_file.seek(pos)
            logging.info(
                f"pos is {pos} and framerate is {input_file.samplerate}, type is {input_file.format}, size is {input_file.frames}, raw data type is {data.dtype}"
            )

        return new_filename, new_filepath
    except Exception:
        logging.info("something went wrong")
        logging.info(traceback.format_exc())
        return None


# class Converter:
#     def convert_file(file):
#         extension = file.filename.split('.')[-1]
#         if extension == 'mp3':
#             wav_io = mp3_to_wav(file)

#             # Создаем новый FileStorage объект для конвертированного файла
#             filename = secure_filename(file.filename.replace(extension, 'wav'))
#             file = FileStorage(
#                 stream=wav_io,
#                 filename=filename,
#                 content_type='audio/wav'
#             )

#             return file

#         # Other formats
#         return None

# def mp3_to_wav(file):
#         # Чтение файла mp3
#         sound = AudioSegment.from_mp3(file)

#         # Преобразование в массив numpy
#         samples = np.array(sound.get_array_of_samples())

#         # Если аудио стерео, то преобразование в моно
#         if sound.channels == 2:
#             samples = samples.reshape((-1, 2))
#             samples = np.mean(samples, axis=1)

#         # Нормализация аудиоданных
#         samples = samples / np.max(np.abs(samples))
#         samples = (samples * 32767).astype(np.int16)

#         return write_wav(sound, samples)


# def write_wav(sound, samples):
#     # Создание WAV файла в памяти с использованием BytesIO
#         wav_io = BytesIO()
#         with wave.open(wav_io, "w") as wav_file:
#             wav_file.setnchannels(1)  # моно
#             wav_file.setsampwidth(2)  # 16 бит
#             wav_file.setframerate(sound.frame_rate)
#             wav_file.writeframes(samples.tobytes())

#         # Перематываем файл на начало
#         wav_io.seek(0)
#         return wav_io
