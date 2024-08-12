import WebSocketHandler from './modules/webSocketHandler.js';
import voskHandler from './modules/voskMessageHandler.js';
import recordingHandler from './modules/recordingHandler.js';
import timer from './modules/timer.js';
import download from './modules/download.js';

document.addEventListener("DOMContentLoaded", async () => {
    // Ждём пока загрузится конфигурация
    await initialize();

// TODO: Необходимо затестить единую кнопку с записью.
// Если работает, то снести старый код
// ---------- Под снос ----------
    let context;
    let source;
    let processor;
    let streamLocal;
    const sampleRate = 16000;
// ------------------------------

    let isRecording = false;

    const wsUrl = window.serverUrl;
    const socket = new WebSocketHandler(wsUrl, voskHandler.handleMessage);

// ---------- Под снос ----------
    document.getElementById('start').addEventListener('click', startRecording);
    document.getElementById('stop').addEventListener('click', stopRecording);
// ------------------------------   
    document.getElementById('record').addEventListener('click', handleRecording);
    document.getElementById('downloadBtn').addEventListener('click', download.downloadText('result'));

    async function handleRecording() {
        if (!isRecording) {
            isRecording = true;
            document.getElementById('record').textContent = 'Остановить запись';
            await recordingHandler.startRecording(socket);
        } else {
            isRecording = false;
            document.getElementById('record').textContent = 'Записать заново';
            recordingHandler.stopRecording(socket);
        }
    }

// ---------- Под снос ----------
    async function startRecording() {
        try {
            const stream = await navigator.mediaDevices.getUserMedia({audio: {
                echoCancellation: true,
                noiseSuppression: true,
                channelCount: 1,
                sampleRate
            }});
            socket.startRecording();
            handleSuccess(stream);
        } catch (err) {
            console.error('Error accessing microphone:', err);
        }
    }

    function handleSuccess(stream) {
        streamLocal = stream;
        context = new AudioContext({ sampleRate: sampleRate });

        context.audioWorklet.addModule('/static/js/modules/dataConversionProcessor.js').then(() => {
            processor = new AudioWorkletNode(context, 'data-conversion-processor', {
                channelCount: 1,
                numberOfInputs: 1,
                numberOfOutputs: 1
            });

            source = context.createMediaStreamSource(stream);
            source.connect(processor);
            processor.connect(context.destination);

            processor.port.onmessage = event => {
                // console.log('Audio data received from processor:', event.data);
                socket.sendAudioData({ audio_data: event.data});
            };
            
            processor.port.start();
            timer.start('recording-time');
            console.log('Recording started');
        }).catch(err => {
            console.error('Error adding audio worklet module:', err);
        });
    }

    function stopRecording() {
        if (processor && context) {
            processor.disconnect();
            context.close();
            if (streamLocal && streamLocal.active) {
                streamLocal.getTracks()[0].stop();
            }
            timer.stop();
            socket.stopRecording();
            console.log('Recording stopped by user');
        }
    }
// ------------------------------
});