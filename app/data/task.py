import uuid
import logging
from app.data.task_status import TaskStatus
# from app.data.client import Client

class Task:
    def __init__(self):
        self.task_id = str(uuid.uuid4())  # Генерируем уникальный ID задачи
        self.status = TaskStatus.CREATED  # Статус задачи, по умолчанию "created"

    def set_status(self, status):
        """Обновление статуса задачи."""
        self.status = status
        logging.info(f"Task {self.task_id} status updated to {self.status}")

    def set_client(self, client_sid: str):
        self.client_sid = client_sid
        
    def get_task_id(self):
        return self.task_id