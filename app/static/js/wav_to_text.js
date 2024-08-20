import WebSocketHandler from './modules/webSocketHandler.js';
import voskHandler from './modules/voskMessageHandler.js';
import download from './modules/download.js';

document.addEventListener("DOMContentLoaded", async () => {
    await initialize();

    const wsUrl = window.serverUrl;
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
        const response = await fetch( wsUrl + '/upload', {
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
            wsHandler.sendEvent('listen_task', {task_id:task_id})
            
        } else {
            console.error('Failed to upload file');
        }
    };

    document.getElementById('fileInput').addEventListener('change', changeInputContent);
    document.getElementById('uploadForm').onsubmit = uploadRecord;
    document.getElementById('downloadBtn').addEventListener('click', download.downloadText('result'));

    wsHandler.socket.on('transcription_finished', () => {
        document.getElementById('downloadBtn').style.display = 'block';
    });


    wsHandler.socket.on('client_id', (messege) => {
        console.log(messege);
    });

    
});
