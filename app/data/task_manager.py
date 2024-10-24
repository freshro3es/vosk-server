import logging
from app.data.task import Task
from app.data.wav_task import WAVTask
from app.data.voice_task import VoiceTask


class TaskManager:
    def __init__(self):
        self.tasks = []

    def add_task(self, task: Task):
        self.tasks.append(task)
        logging.info(f"Task Manager: Task {task.task_id} added")

    def add_wav_task(self, task: WAVTask):
        self.tasks.append(task)
        logging.info(f"Task Manager: WAVE Task {task.task_id} added")
        logging.info(f"{', '.join(task.task_id for task in self.tasks)}")

    def add_voice_task(
        self,
        client_sid: str,
        framerate: int = 16000,
        channels: int = 1,
        sampwidth: int = 2,
    ):
        task = VoiceTask(client_sid, framerate, channels, sampwidth)
        self.tasks.append(task)
        logging.info(f"Task Manager: Voice Task {task.task_id} added")
        return task

    def find_task_by_id(self, task_id):
        logging.info(f"Task Manager: Started searching for task {task_id}")
        for task in self.tasks:
            logging.info(f"Task Manager: Currently checking task {task.task_id}")
            if task.task_id == task_id:
                logging.info(f"TaskManager: Found task {task_id}")
                return task
        logging.info(f"TaskManager: There is no task with id {task_id}")
        return None

    def find_task_by_client(self, client_sid):
        for task in self.tasks:
            if task.client_sid == client_sid:
                logging.info(f"TaskManager: Found task {task.task_id}")
                return task
        logging.info(f"TaskManager: There is no task with sid {client_sid}")
        return None

    def find_current_task_by_client(self, client_sid):
        for task in self.tasks:
            if task.client_sid == client_sid and task.status == "processing":
                logging.info(f"TaskManager: Found task {task.task_id}")
                return task
        logging.info(f"TaskManager: There is no task with sid {client_sid}")
        return None
