import WebSocketHandler from './modules/webSocketHandler.js';
import voskHandler from './modules/voskMessageHandler.js';
import download from './modules/download.js';
import timer from './modules/timer.js';

document.addEventListener("DOMContentLoaded", async () => {

    const wsUrl = window.location.origin;
    console.log(`current url is ${window.location.origin}`);
    
    const wsHandler = new WebSocketHandler(wsUrl, voskHandler.handleMessage);

    let task_id;

    const changeInputContent = (event) => {
        const fileName = event.target.files[0]?.name || 'No file chosen';
        document.getElementById('fileName').textContent = fileName;
    }

    const uploadRecord = async (event) => {
        event.preventDefault();

        // Clear result form
        document.getElementById('downloadBtn').style.display = 'none';
        document.getElementById('result').textContent = '';
        voskHandler.clearCache();

        // Form data to send it
        const fileInput = document.getElementById('fileInput');
        const formData = new FormData();
        formData.append('file', fileInput.files[0]);

        // Send the data
        const response = await fetch(wsUrl + '/upload', {
            method: 'POST',
            body: formData
        });

        // With the good response show result form
        if (response.ok) {
            document.getElementById('resultForm').classList.add('show');
            console.log('File uploaded successfully');

            // Working with response
            const data = await response.json();
            task_id = data.task_id;
            console.log(task_id);

            // Интервал для отправки запроса на сервер каждые 2 секунды
            const intervalId = setInterval(() => {
                console.log('Отправляю запрос listen_task');
                wsHandler.sendEvent('listen_task', { task_id: task_id });
            }, 2000); // Отправляем запрос каждые 2 секунды

            // Обработчик события для успешного подписывания на таску
            wsHandler.socket.on('listening', (data) => {
                if (data.message.includes(task_id)) {
                    console.log(`Таска ${task_id} найдена и прослушивается`);
                    timer.start('recording-time'); // Запускаем таймер обработки файла
                    clearInterval(intervalId); // Останавливаем интервал, если таска найдена
                }
            });

        } else {
            console.error('Failed to upload file');
        }
    };

    document.getElementById('fileInput').addEventListener('change', changeInputContent);
    document.getElementById('uploadForm').onsubmit = uploadRecord;
    document.getElementById('downloadBtn').addEventListener('click', download.downloadText('result'));

    wsHandler.socket.on('transcription_finished', () => {
        document.getElementById('downloadBtn').style.display = 'block';

        timer.stop();
    });


    wsHandler.socket.on('client_id', (message) => {
        console.log(message);
    });

    wsHandler.socket.on('working', () => {
        document.getElementById('circle').style.background = "yellow";
    })

    wsHandler.socket.on('stopped', () => {
        document.getElementById('circle').style.background = "white";
    })


});
