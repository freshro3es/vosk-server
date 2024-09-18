class AudioProcessor extends AudioWorkletProcessor {
    constructor() {
        super();
        this.buffer = new Int16Array(12288); // Буфер для накопления 12288 семплов
        this.bufferIndex = 0; // Текущая позиция в буфере
    }

    process(inputs) {
        const input = inputs[0];
        const channelData = input[0];

        // Преобразуем float32 данные в int16 и добавляем в буфер
        for (let i = 0; i < channelData.length; i++) {
            const s = Math.max(-1, Math.min(1, channelData[i]));
            this.buffer[this.bufferIndex++] = s < 0 ? s * 0x8000 : s * 0x7FFF;

            // Если буфер заполнен, отправляем данные в главный поток
            if (this.bufferIndex === this.buffer.length) {
                this.port.postMessage(this.buffer);
                this.bufferIndex = 0; // Сбрасываем индекс для новой порции данных
            }
        }

        return true; // Возвращаем true, чтобы продолжать обработку
    }
}

registerProcessor('audio-processor', AudioProcessor);
