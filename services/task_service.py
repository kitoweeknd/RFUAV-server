"""
任务管理服务
"""
import logging
from typing import Optional

from services.base_service import BaseService
from services.training_service import TrainingService
from services.inference_service import InferenceService
from models.schemas import TaskListResponse, TaskResponse

logger = logging.getLogger(__name__)


class TaskService(BaseService):
    """任务管理服务 - 统一管理所有任务"""
    
    def __init__(self):
        super().__init__()
        self.training_service = TrainingService()
        self.inference_service = InferenceService()
    
    def get_task(self, task_id: str) -> Optional[TaskResponse]:
        """获取任务（从训练或推理服务）"""
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
        """获取所有任务列表"""
        # 获取所有训练任务
        training_tasks = [
            TaskResponse(**task)
            for task in self.training_service.tasks.values()
        ]
        
        # 获取所有推理任务
        inference_tasks = [
            TaskResponse(**task)
            for task in self.inference_service.tasks.values()
        ]
        
        # 过滤
        if status:
            training_tasks = [t for t in training_tasks if t.status == status]
            inference_tasks = [t for t in inference_tasks if t.status == status]
        
        if task_type == "training":
            inference_tasks = []
        elif task_type == "inference":
            training_tasks = []
        
        # 限制数量
        training_tasks = training_tasks[:limit]
        inference_tasks = inference_tasks[:limit]
        
        return TaskListResponse(
            training_tasks=training_tasks,
            inference_tasks=inference_tasks,
            total_training=len(training_tasks),
            total_inference=len(inference_tasks)
        )
    
    def stream_logs(self, task_id: str):
        """获取任务日志流"""
        # 检查任务来源
        if task_id in self.training_service.tasks:
            return self.training_service.stream_logs(task_id)
        elif task_id in self.inference_service.tasks:
            return self.inference_service.stream_logs(task_id)
        return None
    
    def cancel_task(self, task_id: str) -> bool:
        """取消任务"""
        # 尝试从训练服务取消
        if task_id in self.training_service.tasks:
            return self.training_service.stop_task(task_id)
        
        # 尝试从推理服务取消
        if task_id in self.inference_service.tasks:
            task = self.inference_service.get_task(task_id)
            if task and task["status"] in ["pending", "queued", "running"]:
                self.inference_service.update_task_status(
                    task_id, "cancelled", "任务已取消", task.get("progress", 0)
                )
                return True
        
        return False
    
    def delete_task(self, task_id: str) -> bool:
        """删除任务记录"""
        # 从训练服务删除
        if task_id in self.training_service.tasks:
            task = self.training_service.tasks[task_id]
            if task["status"] in ["completed", "failed", "cancelled"]:
                del self.training_service.tasks[task_id]
                return True
        
        # 从推理服务删除
        if task_id in self.inference_service.tasks:
            task = self.inference_service.tasks[task_id]
            if task["status"] in ["completed", "failed", "cancelled"]:
                del self.inference_service.tasks[task_id]
                return True
        
        return False
    
    @property
    def log_queues(self):
        """获取所有日志队列"""
        queues = {}
        queues.update(self.training_service.log_queues)
        queues.update(self.inference_service.log_queues)
        return queues


