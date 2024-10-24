function formatTime(seconds) {
    const date = new Date(0);
    date.setSeconds(seconds);

    const hours = date.getUTCHours();
    const minutes = date.getUTCMinutes();
    const secs = date.getUTCSeconds();

    // Формируем строку времени
    let timeString = '';
    if (hours > 0) {
        timeString += `${hours}:`;
    }
    timeString += `${minutes.toString().padStart(2, '0')}:`;
    timeString += secs.toString().padStart(2, '0');

    return timeString;
}

let text = '';

const voskHandler = {
    handleMessage: (msg) => {
        const resultElement = document.getElementById('result');
        if (msg.partial !== undefined) {
            resultElement.innerHTML = text + msg.partial + '<br>';
            console.log(Date.now(), "partial", msg.partial);
        }
        // if (msg.result !== undefined) {
        //     // Извлекаем время начала и конца для каждого слова в result
        //     const startTimes = msg.result.map(word => word.start);
        //     const endTimes = msg.result.map(word => word.end);

        //     const startTime = Math.min(...startTimes);
        //     const endTime = Math.max(...endTimes);

        //     // Форматируем время в hh:mm:ss
        //     const formattedStartTime = formatTime(startTime);
        //     const formattedEndTime = formatTime(endTime);

        //     if (msg.text !== undefined) {
        //         resultElement.innerHTML = `${text} <b>${formattedStartTime}-${formattedEndTime}</b>    ${msg.text} <br>`;
        //         text = resultElement.innerHTML;
        //         console.log(Date.now(), "text", msg.text);
        //     }
        // }
        if (msg.text !== undefined) {
            // Извлекаем время начала и конца реплики
            const startTime = msg.start;
            const endTime = msg.end;

            // Форматируем время в hh:mm:ss
            const formattedStartTime = formatTime(startTime);
            const formattedEndTime = formatTime(endTime);

            resultElement.innerHTML = `${text} <b>${formattedStartTime}-${formattedEndTime}</b>    ${msg.text} <br>`;
            text = resultElement.innerHTML;
            console.log(Date.now(), "text", msg.text);


        }
    },
    clearCache() {
        text = '';
    }
}

export default voskHandler;
