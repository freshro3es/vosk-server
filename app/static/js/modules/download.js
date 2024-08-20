const download = {
    downloadText(elementId) {
        return function () {
            const textBlob = new Blob([document.getElementById(elementId).innerText], { type: 'text/plain' });
            const textURL = URL.createObjectURL(textBlob);
            const link = document.createElement('a');
            link.href = textURL;
            link.download = 'transcription.txt';
            link.click();
            URL.revokeObjectURL(textURL);
        }
    },
    // Under developing
    downloadWav(elementId) {
        return function() {
            console.log(`Download func is missing
                // TODO: Specify download func for WAV files`);
        }
    }
}

export default download