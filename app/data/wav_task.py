from app.data.task import Task
from app.data.task_status import TaskStatus
# from app.data.client import Client
 
class WAVTask(Task):
    # def __init__(self, task_id: str, client: Client, file_path: str, status: TaskStatus = TaskStatus.CREATED):
    #     super().__init__(task_id, client, status)
    #     self.file_path = file_path
    #     self.result = None  # Изначально результат пустой
    
    def __init__(self, file_path: str, filename: str):
        super().__init__()
        self.file_path = file_path
        self.filename = filename
        self.result = None  # Изначально результат пустой

    def set_result(self, result: str):
        self.result = result
        
    