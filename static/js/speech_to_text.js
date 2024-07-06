// static/js/speech_to_text.js

// important TODO: rewrite functionality of voice to text page here and use websocket_handler.js
// after TODO: after frontend will work fine and so we will need to make more handlers for basic reusable operations like downloading transcribition via button

import WebSocketHandler from './websocket_handler.js';
// import DataConversionAudioProcessor from './data-conversion-processor.js';

document.addEventListener("DOMContentLoaded", async () => {
    // Ждём пока загрузится конфигурация
    await initialize();

    const wsUrl = window.serverUrl;
    let context;
    let source;
    let processor;
    let streamLocal;
    let recordingTimer;
    let startTime;
    const sampleRate = 16000;

    // function handleMessage(msg) {
    //     if (msg.result) {
    //         // TODO: fix result display
    //         // Вот тут не получается отображать в блоке результаты
    //         requestAnimationFrame(() => {
    //             document.getElementById('result').innerHTML += msg.result + ' ';
    //         });
    //     } else if (msg.transcription_finished) {
    //         requestAnimationFrame(() => {
    //             document.getElementById('result').innerHTML += "<br><b>Transcription finished.</b><br>";
    //         });
    //     } else if (msg.recording_time) {
    //         document.getElementById('recording-time').innerText = msg.recording_time;
    //     }
    // }  
    
    let text = '';
    
    const handleMessage = (msg) => {
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

    const socket = new WebSocketHandler(wsUrl, handleMessage);

    document.getElementById('start').addEventListener('click', startRecording);
    document.getElementById('stop').addEventListener('click', stopRecording);
    document.getElementById('downloadBtn').addEventListener('click', downloadText);

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

        context.audioWorklet.addModule('/static/js/data-conversion-processor.js').then(() => {
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
            startTime = Date.now();
            startTimer();
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
            clearInterval(recordingTimer);
            socket.stopRecording();
            console.log('Recording stopped by user');
        }
    }

    function startTimer() {
        recordingTimer = setInterval(() => {
            const elapsedTime = Date.now() - startTime;
            const formattedTime = formatTime(elapsedTime);
            document.getElementById('recording-time').innerText = formattedTime;
        }, 1000);
    }

    function formatTime(milliseconds) {
        const totalSeconds = Math.floor(milliseconds / 1000);
        const minutes = Math.floor(totalSeconds / 60);
        const seconds = totalSeconds % 60;
        return minutes.toString().padStart(2, '0') + ':' + seconds.toString().padStart(2, '0');
    }

    function downloadText() {
        const textBlob = new Blob([document.getElementById('result').innerText], { type: 'text/plain' });
        const textURL = URL.createObjectURL(textBlob);
        const link = document.createElement('a');
        link.href = textURL;
        link.download = 'transcription.txt';
        link.click();
        URL.revokeObjectURL(textURL);
    }
});