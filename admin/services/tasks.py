from schemas import tasks_add
from utils.repository import AbstractRepository

class TasksServise:
    def __init__(self, tasks_repo: AbstractRepository):
        self.tasks_repo = tasks_repo()
    
    async def add_task(self, task: tasks_add):
        tasks_dict = task.model_dump()
        task_id = await self.tasks_repo.add_one(tasks_dict)
        return task_id
