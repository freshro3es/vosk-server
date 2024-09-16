import timer from './timer.js';

let context;
let source;
let processor;
let streamLocal;
// const sampleRate = 16000;
let channelCount;
let sampleRate;

function handleSuccess(socket, stream) {
    streamLocal = stream;
    // context = new AudioContext({ sampleRate: sampleRate });

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
            // const sample = event.data[0];  // берем первый сэмпл

            // // Печатаем минимальный и максимальный диапазон значений, чтобы предположить битовую глубину
            // console.log("Первый сэмпл:", sample);

            // // Выводим вероятную ширину семпла
            // // Если значения варьируются от -1 до 1, то это 32-bit float
            // const is32BitFloat = (sample >= -1 && sample <= 1);
            // const sampleWidth = is32BitFloat ? 32 : 16;  // предположительно 32-bit float или 16-bit int

            // console.log(`Предполагаемая ширина семпла: ${sampleWidth} бит`);

            // event.data содержит данные в формате Float32Array
            const float32Array = event.data;

            // Создаем новый буфер для хранения данных в формате int16
            const int16Array = new Int16Array(float32Array.length);

            // Преобразуем float32 данные в int16
            for (let i = 0; i < float32Array.length; i++) {
                const s = Math.max(-1, Math.min(1, float32Array[i])); // Ограничиваем значения между -1 и 1
                int16Array[i] = s < 0 ? s * 0x8000 : s * 0x7FFF;      // Преобразуем float32 в int16
            }

            // Преобразуем массив int16 в байты для отправки на сервер
            const byteArray = new Uint8Array(int16Array.buffer);

            // Отправляем преобразованные данные на сервер
            socket.sendAudioData({ audio_data: event.data });
        };

        processor.port.start();
        timer.start('recording-time');
        console.log('Recording started');
    }).catch(err => {
        console.error('Error adding audio worklet module:', err);
    });
};

const recordingHandler = {
    async startRecording(socket) {
        try {
            const stream = await navigator.mediaDevices.getUserMedia({
                audio: {
                    echoCancellation: true,
                    noiseSuppression: true,
                    channelCount: 1
                }
            });

            context = new AudioContext();

            channelCount = 1;
            sampleRate = context.sampleRate;
            socket.startRecording(channelCount, sampleRate);
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

// import timer from './timer.js';

// let mediaRecorder;
// let audioChunks = [];
// let streamLocal;

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

//             streamLocal = stream;
//             mediaRecorder = new MediaRecorder(stream);

//             timer.start('recording-time');

//             mediaRecorder.ondataavailable = (event) => {
//                 audioChunks.push(event.data);

//                 // Отправляем аудиоданные по WebSocket
//                 if (mediaRecorder.state === 'recording') {
//                     const blob = new Blob(audioChunks, { type: 'audio/webm' });
//                     audioChunks = []; // очищаем для следующего блока данных
//                     socket.sendAudioData(blob);
//                 }
//             };

//             mediaRecorder.start(1000); // Собираем данные каждые 1000 мс
//             console.log('Recording started');
//         } catch (err) {
//             console.error('Error accessing microphone:', err);
//         }
//     },

//     stopRecording(socket) {
//         if (mediaRecorder && mediaRecorder.state !== 'inactive') {
//             mediaRecorder.stop();
//             streamLocal.getTracks().forEach(track => track.stop());
//             console.log('Recording stopped by user');

//             timer.stop();

//             socket.stopRecording();
//         }
//     }
// };

// export default recordingHandler;
