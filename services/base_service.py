"""
基础服务类
"""
import logging
import uuid
from datetime import datetime
from queue import Queue
from typing import Dict, Optional
from fastapi.responses import StreamingResponse
import asyncio
import json

logger = logging.getLogger(__name__)


class BaseService:
    """基础服务类 - 提供通用功能"""
    
    def __init__(self):
        self.tasks: Dict = {}
        self.log_queues: Dict[str, Queue] = {}
        self.log_history: Dict[str, list] = {}  # 存储所有日志历史
    
    def generate_task_id(self, custom_id: Optional[str] = None) -> str:
        """生成任务ID"""
        return custom_id if custom_id else str(uuid.uuid4())
    
    def update_task_status(
        self,
        task_id: str,
        status: str,
        message: str = None,
        progress: int = None,
        **kwargs
    ):
        """更新任务状态"""
        if task_id in self.tasks:
            self.tasks[task_id]["status"] = status
            self.tasks[task_id]["updated_at"] = datetime.now().isoformat()
            
            if message:
                self.tasks[task_id]["message"] = message
            if progress is not None:
                self.tasks[task_id]["progress"] = progress
                
            # 更新其他字段
            for key, value in kwargs.items():
                self.tasks[task_id][key] = value
        else:
            self.tasks[task_id] = {
                "task_id": task_id,
                "status": status,
                "message": message,
                "progress": progress,
                "created_at": datetime.now().isoformat(),
                "updated_at": datetime.now().isoformat(),
                **kwargs
            }
        
        logger.debug(f"任务状态更新: {task_id} -> {status}")
    
    def get_task(self, task_id: str) -> Optional[Dict]:
        """获取任务信息"""
        return self.tasks.get(task_id)
    
    def create_log_queue(self, task_id: str):
        """创建日志队列"""
        if task_id not in self.log_queues:
            self.log_queues[task_id] = Queue()
        if task_id not in self.log_history:
            self.log_history[task_id] = []
    
    def add_log(self, task_id: str, level: str, message: str, metrics=None, step=None, stage=None):
        """添加日志（支持训练指标）"""
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "level": level,
            "message": message
        }
        
        # 添加可选的训练指标信息
        if metrics is not None:
            log_entry["metrics"] = metrics
        if step is not None:
            log_entry["step"] = step
        if stage is not None:
            log_entry["stage"] = stage
        
        # 添加到日志队列（用于SSE流）
        if task_id in self.log_queues:
            self.log_queues[task_id].put(log_entry)
        
        # 添加到日志历史（用于查询）
        if task_id not in self.log_history:
            self.log_history[task_id] = []
        self.log_history[task_id].append(log_entry)
    
    async def log_generator(self, task_id: str):
        """日志生成器"""
        if task_id not in self.log_queues:
            self.create_log_queue(task_id)
        
        queue = self.log_queues[task_id]
        
        try:
            while True:
                task = self.get_task(task_id)
                if not task:
                    break
                
                status = task.get("status")
                
                # 发送队列中的日志
                while not queue.empty():
                    log_entry = queue.get()
                    yield f"data: {json.dumps(log_entry, ensure_ascii=False)}\n\n"
                
                # 如果任务结束，发送完成信号
                if status in ["completed", "failed", "cancelled"]:
                    yield f"data: {json.dumps({'status': status, 'message': '任务结束'}, ensure_ascii=False)}\n\n"
                    break
                
                await asyncio.sleep(0.5)
        finally:
            # 清理日志队列
            if task_id in self.log_queues:
                del self.log_queues[task_id]
    
    def stream_logs(self, task_id: str):
        """返回日志流响应"""
        return StreamingResponse(
            self.log_generator(task_id),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "X-Accel-Buffering": "no"
            }
        )
    
    def get_logs(self, task_id: str) -> list:
        """获取任务的所有日志历史"""
        return self.log_history.get(task_id, [])


