// static/js/wav_to_text.js
import WebSocketHandler from './websocket_handler.js';

document.addEventListener("DOMContentLoaded", async () => {
    
    await initialize();

    const wsUrl = window.serverUrl;
    let text = '';

    const messageHandler = (msg) => {
        const resultElement = document.getElementById('result');
        if (msg.partial !== undefined) {
            resultElement.textContent = text + msg.partial + '\n';
            console.log(Date.now(), "partial", msg.partial);
        }
        if (msg.text !== undefined) {
            text += " " + msg.text;
            resultElement.textContent = text + '\n';
            console.log(Date.now(), "text", msg.text);
        }
    };

    const wsHandler = new WebSocketHandler(wsUrl, messageHandler);

    document.getElementById('fileInput').addEventListener('change', (event) => {
        const fileName = event.target.files[0]?.name || 'No file chosen';
        document.getElementById('fileName').textContent = fileName;
    });

    document.getElementById('uploadForm').onsubmit = async (event) => {
        event.preventDefault();

        document.getElementById('downloadBtn').style.display = 'none';
        document.getElementById('result').textContent = '';
        text = '';

        const fileInput = document.getElementById('fileInput');
        const formData = new FormData();
        formData.append('file', fileInput.files[0]);

        const response = await fetch( wsUrl + '/upload', {
            method: 'POST',
            body: formData
        });

        if (response.ok) {
            document.getElementById('resultForm').classList.add('show');
            console.log('File uploaded successfully');
        } else {
            console.error('Failed to upload file');
        }
    };

    document.getElementById('downloadBtn').addEventListener('click', () => {
        const textBlob = new Blob([text], { type: 'text/plain' });
        const textURL = URL.createObjectURL(textBlob);
        const link = document.createElement('a');
        link.href = textURL;
        link.download = 'transcription.txt';
        link.click();
        URL.revokeObjectURL(textURL);
    });

    wsHandler.socket.on('transcription_finished', () => {
        document.getElementById('downloadBtn').style.display = 'block';
    });
});
