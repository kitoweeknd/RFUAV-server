import logging
from typing import Optional

from services.base_service import BaseService
from services.training_service import TrainingService
from services.inference_service import InferenceService
from models.schemas import TaskListResponse, TaskResponse

logger = logging.getLogger(__name__)


class TaskService(BaseService):
    def __init__(self, training_service: TrainingService = None, inference_service: InferenceService = None):
        self.training_service = training_service if training_service is not None else TrainingService()
        self.inference_service = inference_service if inference_service is not None else InferenceService()
    
    def get_task(self, task_id: str) -> Optional[TaskResponse]:
        task = (
            self.training_service.get_task(task_id) or
            self.inference_service.get_task(task_id)
        )
        
        if task:
            return TaskResponse(**task)
        return None
    
    def get_all_tasks(
        self,
        status: str = None,
        task_type: str = None,
        limit: int = 100
    ) -> TaskListResponse:
        training_tasks = [
            TaskResponse(**task)
            for task in self.training_service.tasks.values()
        ]
        
        inference_tasks = [
            TaskResponse(**task)
            for task in self.inference_service.tasks.values()
        ]
        
        if status:
            training_tasks = [t for t in training_tasks if t.status == status]
            inference_tasks = [t for t in inference_tasks if t.status == status]
        
        if task_type == "training":
            inference_tasks = []
        elif task_type == "inference":
            training_tasks = []
        
        training_tasks = training_tasks[:limit]
        inference_tasks = inference_tasks[:limit]
        
        return TaskListResponse(
            training_tasks=training_tasks,
            inference_tasks=inference_tasks,
            total_training=len(training_tasks),
            total_inference=len(inference_tasks)
        )
    
    def stream_logs(self, task_id: str):
        if task_id in self.training_service.tasks:
            return self.training_service.stream_logs(task_id)
        elif task_id in self.inference_service.tasks:
            return self.inference_service.stream_logs(task_id)
        return None
    
    def cancel_task(self, task_id: str) -> bool:
        if task_id in self.training_service.tasks:
            return self.training_service.stop_task(task_id)
        if task_id in self.inference_service.tasks:
            task = self.inference_service.get_task(task_id)
            if task and task["status"] in ["pending", "queued", "running"]:
                self.inference_service.update_task_status(
                    task_id, "cancelled", "任务已取消", task.get("progress", 0)
                )
                return True
        
        return False
    
    def delete_task(self, task_id: str) -> bool:
        if task_id in self.training_service.tasks:
            task = self.training_service.tasks[task_id]
            if task["status"] in ["completed", "failed", "cancelled"]:
                del self.training_service.tasks[task_id]
                return True
        
        if task_id in self.inference_service.tasks:
            task = self.inference_service.tasks[task_id]
            if task["status"] in ["completed", "failed", "cancelled"]:
                del self.inference_service.tasks[task_id]
                return True
        
        return False
    
    @property
    def log_queues(self):
        queues = {}
        queues.update(self.training_service.log_queues)
        queues.update(self.inference_service.log_queues)
        return queues
    
    def get_all_log_queues(self):
        queues = {}
        queues.update(self.training_service.log_queues)
        queues.update(self.inference_service.log_queues)
        return queues