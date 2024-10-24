from silero_vad import load_silero_vad, VADIterator
import numpy as np
import logging
import torch
import torchaudio
import traceback

SAMPLING_RATE = 16000
USE_ONNX = False  # change this to True if you want to test onnx model

# def create_vad_instance():
#     model = load_silero_vad(onnx=USE_ONNX)
#     return VADIterator(model, sampling_rate=SAMPLING_RATE)

try:
    model = load_silero_vad(onnx=USE_ONNX)
    vad_iterator = VADIterator(model, sampling_rate=SAMPLING_RATE)
except Exception:
    logging.info(traceback.format_exc())


def voice_prob(data: bytes, original_sample_rate: int):
    # # Преобразование байтового потока в тензор PyTorch напрямую без копирования
    # audio_tensor = torch.frombuffer(data, dtype=torch.int16).float()

    audio_tensor = resample_audio(data, original_sample_rate)

    speech_probs = []
    window_size_samples = 512
    for i in range(0, len(audio_tensor), window_size_samples):
        chunk = audio_tensor[i : i + window_size_samples]
        if len(chunk) < window_size_samples:
            break
        speech_prob = model(chunk, SAMPLING_RATE).item()
        # speech_prob = vad_iterator(chunk)
        speech_probs.append(speech_prob)
    if np.mean(speech_probs) < 0.004:
        logging.info(
            f"Total amount of speech probes: {len(speech_probs)}, average is {np.mean(speech_probs)}"
        )
    vad_iterator.reset_states()  # reset model states after each audio
    return np.mean(speech_probs)


def resample_audio(
    data: bytes, original_sample_rate: int, target_sample_rate: int = SAMPLING_RATE
):
    # Преобразование байтового потока в массив NumPy и создание копии для доступности записи
    audio_array = np.frombuffer(data, dtype=np.int16).copy()

    # Преобразование массива в тензор PyTorch
    audio_tensor = torch.from_numpy(audio_array).float()

    # Применение ресемплинга
    resampler = torchaudio.transforms.Resample(
        orig_freq=original_sample_rate, new_freq=target_sample_rate
    )
    resampled_audio = resampler(audio_tensor)

    return resampled_audio
