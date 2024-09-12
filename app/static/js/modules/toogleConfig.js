// Функция для отображения/скрытия опций VAD в зависимости от состояния чекбокса
function toggleVADOptions() {
    var useVad = document.getElementById('useVadCheckbox').checked;
    var vadOptions = document.getElementById('vadOptions');
    
    if (useVad) {
        vadOptions.style.display = 'block';
    } else {
        vadOptions.style.display = 'none';
        document.getElementById('bufferSizeContainer').style.display = 'none'; // скрыть буфер при отключении VAD
    }
}

// Функция для отображения/скрытия опции "размер буфера"
function toggleBufferSize() {
    var vadMode = document.querySelector('input[name="vadMode"]:checked').value;
    var bufferSizeContainer = document.getElementById('bufferSizeContainer');
    
    if (vadMode === 'streaming') {
        bufferSizeContainer.style.display = 'block';
    } else {
        bufferSizeContainer.style.display = 'none';
    }
}

// Функция для обновления отображаемого значения ползунка размера буфера
function updateBufferSizeValue() {
    var bufferSize = document.getElementById('bufferSize').value;
    document.getElementById('bufferSizeValue').innerText = bufferSize;
}


export default {toggleVADOptions, toggleBufferSize, updateBufferSizeValue};