// static/js/websocket_handler.js
class WebSocketHandler {
    constructor(url, messageHandler, openHandler, closeHandler, errorHandler) {
        this.url = url;
        this.messageHandler = messageHandler || this.defaultMessageHandler;
        this.openHandler = openHandler || this.defaultOpenHandler;
        this.closeHandler = closeHandler || this.defaultCloseHandler;
        this.errorHandler = errorHandler || this.defaultErrorHandler;
        this.connect();
    }

    connect() {
        console.log("Connecting to WebSocket at", this.url);
        this.socket = io(this.url);

        this.socket.on('connect', () => {
            console.log("WebSocket connected");
            if (this.openHandler) this.openHandler();
        });

        this.socket.on('message', (msg) => {
            console.log("Message received:", msg);
            if (this.messageHandler) this.messageHandler(msg);
        });

        this.socket.on('disconnect', () => {
            console.log("WebSocket disconnected");
            if (this.closeHandler) this.closeHandler();
        });

        this.socket.on('error', (err) => {
            console.error("WebSocket error:", err);
            if (this.errorHandler) this.errorHandler(err);
        });
    }

    send(message) {
        if (this.socket.connected) {
            this.socket.emit('message', message);
        } else {
            console.error("WebSocket is not open.");
        }
    }

    sendEvent(event, data) {
        if (this.socket.connected) {
            this.socket.emit(event, data);
        } else {
            console.error("WebSocket is not open.");
        }
    }

    startRecording(channelCount, sampleRate) {
        if (this.socket.connected) {
            console.log('channelcount is ', channelCount, 'and sample rate is ', sampleRate);
            this.socket.emit('start_recording', {channelCount, sampleRate});
        } else {
            console.error("WebSocket is not open.");
        }
    }


    stopRecording() {
        if (this.socket.connected) {
            this.socket.emit('stop_recording');
        } else {
            console.error("WebSocket is not open.");
        }
    }


    sendAudioData(message) {
        if (this.socket.connected) {
            this.socket.emit('audio_data', message);
        } else {
            console.error("WebSocket is not open.");
        }
    }

    close() {
        this.socket.disconnect();
    }
}

export default WebSocketHandler;
//window.WebSocketHandler = WebSocketHandler;
