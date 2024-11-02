from werkzeug.utils import secure_filename
import logging
import traceback

from datetime import datetime

import soundfile as sf
import os

import subprocess
import json

class Converter:
    def convert_file(file) -> tuple[str, str]:
        extension = file.filename.split(".")[-1]
        if extension == "mp3":
            new_filename, new_filepath = mp3_to_wav(file, 25 * 1024 * 8)
            return new_filename, new_filepath
        if extension == "mp4": # Может быть расширено до .mov, .avi, .mkv, .flv, .wmv, .webm, .3gp и других
            filename = secure_filename(file.filename)
            filepath = os.path.join(
                os.getenv("UPLOADS_DIR", "uploads"),
                filename,
            )
            file.save(filepath)
            new_filename = f"{filename[:-4]}_{datetime.now().strftime('%d-%m-%Y')}.wav"
            new_filepath = os.path.join(
                os.getenv("UPLOADS_DIR", "uploads"),
                new_filename,
            )
            extract_audio(filepath, new_filepath)
            os.remove(filepath)
            return new_filename, new_filepath
            
        # Other formats
        return None

def get_sample_rate(input_file):
    # Команда ffprobe для получения информации о частоте дискретизации
    command = [
        "ffprobe",
        "-v", "error",
        "-select_streams", "a:0",
        "-show_entries", "stream=sample_rate",
        "-of", "json",
        input_file
    ]
    # Запуск команды и получение информации о частоте дискретизации
    result = subprocess.run(command, capture_output=True, text=True)
    info = json.loads(result.stdout)
    # Извлечение частоты дискретизации
    sample_rate = int(info['streams'][0]['sample_rate'])
    return sample_rate

def extract_audio(input_file, output_file):
    # Получаем частоту дискретизации из входного файла
    sample_rate = get_sample_rate(input_file)
    
    # Команда ffmpeg для извлечения аудио в формате wav
    command = [
        "ffmpeg",
        "-i", input_file,         # Входной файл (видео)
        "-vn",                     # Отключение видео
        "-acodec", "pcm_s16le",    # Кодек для WAV
        "-ar", str(sample_rate),   # Динамическая частота дискретизации
        "-ac", "1",                # Один аудиоканал (моно)
        output_file                # Выходной файл (wav)
    ]
    subprocess.run(command, check=True)



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
            logging.debug(
                f"pos is {pos} and framerate is {input_file.samplerate}, type is {input_file.format}, size is {input_file.frames}, raw data type is {data.dtype}"
            )
            
        logging.debug("New file params: \n" 
                      f"Framerate {output_file.samplerate} \n"  
                      f"Filename: {new_filename} \n" 
                      f"Filepath: {new_filepath} \n"
                      )
        input_file.close()
        output_file.close()
        return new_filename, new_filepath
    except Exception:
        logging.info("something went wrong")
        logging.info(traceback.format_exc())
        return None



