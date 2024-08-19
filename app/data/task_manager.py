import logging
from app.data.task import Task
from app.data.wav_task import WAVTask

class TaskManager:
    def __init__(self):
        self.tasks = []
        self.clients = []
    
    def add_task(self, task: Task):
        self.tasks.append(task)
     
    def add_wav_task(self, task: WAVTask):
        self.tasks.append(task)
        
    # def add_voice_task(self, task: Voic)
    
        
    def find_task(self, task_id):
        for task in self.tasks:
            if task.task_id == task_id:
                logging.info(f"TaskManager: Found task {task_id}")
                return task
        logging.info(f"TaskManager: There is no task with id {task_id}")
        return None
    
    