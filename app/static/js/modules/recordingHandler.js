// import timer from './timer.js';

// let context;
// let source;
// let processor;
// let streamLocal;
// // const sampleRate = 16000;
// let channelCount;
// let sampleRate;

// function handleSuccess(socket, stream) {
//     streamLocal = stream;
//     // context = new AudioContext({ sampleRate: sampleRate });

//     context.audioWorklet.addModule('/static/js/modules/dataConversionProcessor.js').then(() => {
//         processor = new AudioWorkletNode(context, 'data-conversion-processor', {
//             channelCount: 1,
//             numberOfInputs: 1,
//             numberOfOutputs: 1
//         });

//         source = context.createMediaStreamSource(stream);
//         source.connect(processor);
//         processor.connect(context.destination);

//         processor.port.onmessage = event => {
//             console.log('Audio data received from processor:', event.data);

//             // Преобразуем массив int16 в байты для отправки на сервер
//             const byteArray = new Uint8Array(event.data.buffer);

//             console.log('Raw PCM audio data sending to server:', byteArray);

//             // Отправляем преобразованные данные на сервер
//             socket.sendAudioData({ audio_data: event.data });
//         };

//         processor.port.start();
//         timer.start('recording-time');
//         console.log('Recording started');
//     }).catch(err => {
//         console.error('Error adding audio worklet module:', err);
//     });
// };

// const recordingHandler = {
//     async startRecording(socket) {
//         try {
//             const stream = await navigator.mediaDevices.getUserMedia({
//                 audio: {
//                     echoCancellation: true,
//                     noiseSuppression: true,
//                     channelCount: 1
//                 }
//             });

//             context = new AudioContext();

//             channelCount = 1;
//             sampleRate = context.sampleRate;
//             socket.startRecording(channelCount, sampleRate);
//             handleSuccess(socket, stream);
//         } catch (err) {
//             console.error('Error accessing microphone:', err);
//         }
//     },
//     stopRecording(socket) {
//         if (processor && context) {
//             processor.disconnect();
//             context.close();
//             if (streamLocal && streamLocal.active) {
//                 streamLocal.getTracks()[0].stop();
//             }
//             timer.stop();
//             socket.stopRecording();
//             console.log('Recording stopped by user');
//         }
//     }
// }

// export default recordingHandler;

import timer from './timer.js';

let context;
let source;
let processor;
let streamLocal;
let sampleRate;

async function handleSuccess(socket, stream) {
    streamLocal = stream;
    context = new AudioContext();

    try {
        await context.audioWorklet.addModule('/static/js/modules/processor.js');

        processor = new AudioWorkletNode(context, 'audio-processor');
        processor.port.onmessage = event => {
            // Получаем данные и отправляем их на сервер
            socket.sendAudioData({ audio_data: event.data });
        };

        source = context.createMediaStreamSource(stream);

        // Если подключаем фильтры, то это закомментировать
        source.connect(processor);
        processor.connect(context.destination);

        // // Фильтр высоких частот
        // const highpassFilter = context.createBiquadFilter();
        // highpassFilter.type = 'highpass';
        // highpassFilter.frequency.value = 85;  // Обрезаем все ниже 85 Гц

        // // Фильтр низких частот
        // const lowpassFilter = context.createBiquadFilter();
        // lowpassFilter.type = 'lowpass';
        // lowpassFilter.frequency.value = 255; // Обрезаем все выше 255 Гц

        // // Подключаем фильтры
        // source.connect(highpassFilter);
        // highpassFilter.connect(lowpassFilter);

        // // Подключаем обработчик для передачи данных
        // lowpassFilter.connect(processor);
        // processor.connect(context.destination);

        timer.start('recording-time');
        console.log('Recording started');
    } catch (err) {
        console.error('Error adding audio worklet module:', err);
    }
}

const recordingHandler = {
    async startRecording(socket) {
        try {
            const stream = await navigator.mediaDevices.getUserMedia({
                audio: {
                    echoCancellation: true,     // Подавление эха
                    noiseSuppression: true,     // Подавление шума
                    autoGainControl: true,      // Автоматическая регулировка усиления
                    channelCount: 1
                }
            });

            context = new AudioContext();
            sampleRate = context.sampleRate;
            socket.startRecording(1, sampleRate);
            handleSuccess(socket, stream);
        } catch (err) {
            console.error('Error accessing microphone:', err);
        }
    },
    stopRecording(socket) {
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
}

export default recordingHandler;

