# from silero_vad import (load_silero_vad,
#                           read_audio,
#                           get_speech_timestamps,
#                           save_audio,
#                           VADIterator,
#                           collect_chunks)
# import numpy as np
# import logging
# import torch

# SAMPLING_RATE = 16000
# USE_ONNX = False # change this to True if you want to test onnx model

# model = load_silero_vad(onnx=USE_ONNX)
# vad_iterator = VADIterator(model, sampling_rate=SAMPLING_RATE)

# def voice_prob(data):
    
#     # Преобразование байтового потока в массив чисел (например, int16 для PCM 16-битного аудио)
#     audio_array = np.frombuffer(data, dtype=np.int16)
    
#     # Создание копии массива, чтобы он был доступен для записи
#     audio_array = np.copy(audio_array)
    
#     # Преобразование в тензор PyTorch и нормализация данных
#     audio_tensor = torch.from_numpy(audio_array).float()
    
#     speech_probs = []
#     window_size_samples = 512
#     for i in range(0, len(audio_tensor), window_size_samples):
#         chunk = audio_tensor[i: i+ window_size_samples]
#         if len(chunk) < window_size_samples:
#           break
#         speech_prob = model(chunk, SAMPLING_RATE).item()
#         speech_probs.append(speech_prob)
#     if (np.mean(speech_probs)<0.004):
#         logging.info(f"Total amount of speech probes: {len(speech_probs)}, average is {np.mean(speech_probs)}")
#     vad_iterator.reset_states() # reset model states after each audio
#     return np.mean(speech_probs)