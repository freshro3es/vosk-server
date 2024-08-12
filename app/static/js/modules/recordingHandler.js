import timer from './timer.js';

let context;
let source;
let processor;
let streamLocal;
const sampleRate = 16000;

function handleSuccess(socket, stream) {
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
                    channelCount: 1,
                    sampleRate
                }
            });
            socket.startRecording();
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