import WebSocketHandler from './modules/webSocketHandler.js';
import voskHandler from './modules/voskMessageHandler.js';
import recordingHandler from './modules/recordingHandler.js';
import timer from './modules/timer.js';
import download from './modules/download.js';

document.addEventListener("DOMContentLoaded", async () => {

    let isRecording = false;

    const wsUrl = window.location.origin;
    const socket = new WebSocketHandler(wsUrl, voskHandler.handleMessage);

    document.getElementById('record').addEventListener('click', handleRecording);
    document.getElementById('downloadBtn').addEventListener('click', download.downloadText('result'));

    async function handleRecording() {
        if (!isRecording) {
            isRecording = true;
            document.getElementById('record').textContent = 'Остановить запись';
            document.getElementById('downloadBtn').style.display = 'none';
            document.getElementById('result').textContent = '';
            document.getElementById('resultForm').classList.add('show');
            voskHandler.clearCache();
            await recordingHandler.startRecording(socket);
        } else {
            isRecording = false;
            document.getElementById('record').textContent = 'Записать заново';
            recordingHandler.stopRecording(socket);
            document.getElementById('downloadBtn').style.display = 'block';
        }
    }
});