/**
 * @module Timer
 * @description
 * Модуль для управления таймером записи. Предоставляет методы для запуска и остановки таймера,
 * а также для форматирования времени в формате MM:SS.
 */

let recordingTimer;
let startTime;

/**
 * Модуль для управления таймером записи. Предоставляет методы для запуска и остановки таймера,
 * а также для форматирования времени в формате MM:SS.
 * @namespace timer
 */
const timer = {
    /**
     * Останавливает таймер записи.
     * @function
     */
    stop() {
        if (recordingTimer) {
            clearInterval(recordingTimer);
        }
    },

    reset(elementId) {
        document.getElementById(elementId).innerText = this.formatTime(0);
    },
    
    /**
     * Запускает таймер записи, обновляя элемент с переданным id каждую секунду.
     * @function
     */
    start(elementId) {
        startTime = Date.now();
        recordingTimer = setInterval(() => {
            const elapsedTime = Date.now() - startTime;
            const formattedTime = this.formatTime(elapsedTime);
            document.getElementById(elementId).innerText = formattedTime;
        }, 1000);
    },
    
    /**
     * Форматирует время в миллисекундах в строку формата MM:SS.
     * @param {number} milliseconds - Время в миллисекундах.
     * @returns {string} Форматированное время в виде строки MM:SS.
     * @function
     */
    formatTime(milliseconds) {
        const totalSeconds = Math.floor(milliseconds / 1000);
        const minutes = Math.floor(totalSeconds / 60);
        const seconds = totalSeconds % 60;
        return minutes.toString().padStart(2, '0') + ':' + seconds.toString().padStart(2, '0');
    }
};

export default timer;
