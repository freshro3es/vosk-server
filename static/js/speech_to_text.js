// static/js/speech_to_text.js

// important TODO: rewrite functionality of voice to text page here and use websocket_handler.js
// after TODO: after frontend will work fine and so we will need to make more handlers for basic reusable operations like downloading transcribition via button

import WebSocketHandler from './websocket_handler.js';

document.addEventListener("DOMContentLoaded", () => {
    const wsUrl = "ws://localhost:5000/speech_to_text";
    const messageHandler = (event) => {
        console.log("Speech to Text: ", event.data);
        // Обработка сообщения и обновление DOM
    };

    const wsHandler = new WebSocketHandler(wsUrl, messageHandler);
    
    // Пример отправки сообщения
    const sendButton = document.getElementById("sendButton");
    sendButton.addEventListener("click", () => {
        const message = document.getElementById("messageInput").value;
        wsHandler.send(message);
    });
});
