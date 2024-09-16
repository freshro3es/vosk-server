class AudioProcessor extends AudioWorkletProcessor {
    process(inputs) {
        const input = inputs[0];
        const channelData = input[0];

        // Преобразуем float32 данные в int16
        const int16Array = new Int16Array(channelData.length);
        for (let i = 0; i < channelData.length; i++) {
            const s = Math.max(-1, Math.min(1, channelData[i]));
            int16Array[i] = s < 0 ? s * 0x8000 : s * 0x7FFF;
        }

        // Отправляем данные в главный поток
        this.port.postMessage(int16Array);
        return true; // Возвращаем true, чтобы продолжать обработку
    }
}

registerProcessor('audio-processor', AudioProcessor);
