let text = '';

const voskHandler = {
    handleMessage : (msg) => {
        const resultElement = document.getElementById('result');
        if (msg.partial !== undefined) {
            resultElement.textContent = text + msg.partial + '\n';
            console.log(Date.now(), "partial", msg.partial);
        }
        if (msg.text !== undefined) {
            resultElement.textContent = text + " " + msg.text + '\n';
            text = resultElement.textContent;
            console.log(Date.now(), "text", msg.text);
        }
    },
    clearCache() {
        text = '';
    }
}

export default voskHandler;