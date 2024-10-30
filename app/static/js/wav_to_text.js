import WebSocketHandler from './modules/webSocketHandler.js';
import voskHandler from './modules/voskMessageHandler.js';
import download from './modules/download.js';
import timer from './modules/timer.js';

const TIMER_ID = 'recording-time';
const VAD_INDICATOR = 'circle';
const RESULT_ID = 'result';
const DOWNLOAD_RESULT_BTN_ID = 'downloadBtn';
const ERROR_FORM_ID = 'errorForm';

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
        document.getElementById(DOWNLOAD_RESULT_BTN_ID).style.display = 'none';
        document.getElementById(RESULT_ID).textContent = '';
        voskHandler.clearCache();
        timer.reset(TIMER_ID);

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

    const terminal_op_handler = {
        stop_transcribition() {
            timer.stop();
            console.log("Timer stopped");
            document.getElementById(VAD_INDICATOR).style.background = "white";
            console.log("VAD status cleared");
            if (document.getElementById(RESULT_ID).textContent != '') {
                document.getElementById(DOWNLOAD_RESULT_BTN_ID).style.display = 'block';
            }
        },
        show_error_form(msg) {
            document.getElementById(ERROR_FORM_ID).style.display = 'block';
            document.getElementById(ERROR_FORM_ID).innerHTML = msg
        },
        hide_error_form(time=0) {
            setTimeout(() => {
                document.getElementById(ERROR_FORM_ID).innerHTML = '';
                document.getElementById(ERROR_FORM_ID).style.display = 'none';
            }, time)
        }
    }

    wsHandler.socket.on('failed', () => {
        terminal_op_handler.stop_transcribition();
        terminal_op_handler.show_error_form(`<b>Обработка файла на сервере провалена</b> <br> Запустите задачу снова`);
        terminal_op_handler.hide_error_form(5000);
    });

    wsHandler.socket.on('disconnect', () => {
        terminal_op_handler.stop_transcribition();
        terminal_op_handler.show_error_form(`<b>Соединение было разорвано...</b>`);
    });

    wsHandler.socket.on('connect', () => {
        if (document.getElementById('errorForm').innerHTML) {
            terminal_op_handler.show_error_form(`<b>Соединение было восстановлено</b> <br> Запустите задачу снова`);
            terminal_op_handler.hide_error_form(5000);
        }
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
