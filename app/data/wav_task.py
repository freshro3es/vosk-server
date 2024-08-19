from app.config import Config
from app.socket_handler import send_message
from app.data.task import Task
from app.data.task_status import TaskStatus
import logging
import wave
import websockets
import os
import asyncio
import json
 
class WAVTask(Task):
    def __init__(self, file_path: str, filename: str):
        super().__init__()
        self.file_path = file_path
        self.filename = filename
        self.result = None  # Изначально результат пустой

    def set_result(self, result: str):
        self.result = result
        
    def transcribe_file(self):
        async def transcribe():
            uri = Config.VOSK_URI
            logging.info(f"def transcribe: Task ID in transcribe func is {self.task_id} and Client ID is {self.client_sid}")
            async with websockets.connect(uri) as websocket:
                wf = wave.open(self.file_path, "rb")
                await websocket.send('{ "config" : { "sample_rate" : %d } }' % (wf.getframerate()))
                buffer_size = int(wf.getframerate() * 1.2)

                while True:
                    data = wf.readframes(buffer_size)
                    if len(data) == 0:
                        break

                    await websocket.send(data)
                    result = await websocket.recv()
                    send_message(self.client_sid, 'message', json.loads(result))
                    # logging.info(f"Transcription result: {result}")
            
                await websocket.send('{"eof" : 1}')
                final_result = await websocket.recv()
                send_message(self.client_sid, 'message', json.loads(final_result))
                # logging.info(f"Final transcription result: {final_result}")
            
                send_message(self.client_sid, 'transcription_finished')
                logging.info("def transcribe: Transcription finished")
    
        asyncio.run(transcribe())
        os.remove(self.file_path)
        
        
    