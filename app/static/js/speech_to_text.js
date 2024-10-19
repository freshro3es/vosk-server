import WebSocketHandler from './modules/webSocketHandler.js';
import voskHandler from './modules/voskMessageHandler.js';
import recordingHandler from './modules/recordingHandler.js';
import timer from './modules/timer.js';
import download from './modules/download.js';

document.addEventListener("DOMContentLoaded", async () => {

    let isRecording = false;

    const wsUrl = window.location.origin;
    const wsHandler = new WebSocketHandler(wsUrl, voskHandler.handleMessage);

    document.getElementById('record').addEventListener('click', handleRecording);
    document.getElementById('downloadBtn').addEventListener('click', download.downloadText('result'));

    async function handleRecording() {
        // console.log(`Went into ${handleRecording.name}`);
        // console.log(`isRecording variable now is "${isRecording}"`);
        if (!isRecording) {
            isRecording = true;
            document.getElementById('record').textContent = 'Остановить запись';
            document.getElementById('downloadBtn').style.display = 'none';
            document.getElementById('result').textContent = '';
            document.getElementById('resultForm').classList.add('show');
            voskHandler.clearCache();
            await recordingHandler.startRecording(wsHandler);
        } else {
            isRecording = false;
            document.getElementById('record').textContent = 'Записать заново';
            recordingHandler.stopRecording(wsHandler);
            document.getElementById('downloadBtn').style.display = 'block';
        }
    }

    wsHandler.socket.on('disconnect', () => {
        timer.stop();
        console.log("Timer stopped");
        document.getElementById('circle').style.background = "white";
        console.log("VAD status cleared");
        if (document.getElementById('result').textContent != '') {
            document.getElementById('downloadBtn').style.display = 'block';
        }
        document.getElementById('errorForm').style.display = 'block';
        document.getElementById('errorForm').innerHTML = `<b>Соединение было разорвано...</b>`
    });

    wsHandler.socket.on('connect', () => {
        if (document.getElementById('errorForm').innerHTML) {
            document.getElementById('errorForm').innerHTML = `<b>Соединение было восстановлено</b> <br> Запустите задачу снова`
            setTimeout(() => {
                document.getElementById('errorForm').innerHTML = '';
                document.getElementById('errorForm').style.display = 'none';
            }, 10000)
        } 
    });

    wsHandler.socket.on('working', () => {
        document.getElementById('circle').style.background = "yellow";
    })

    wsHandler.socket.on('stopped', () => {
        document.getElementById('circle').style.background = "white";
    })
});