"""
训练服务
"""
import logging
import os
import traceback
import re
from datetime import datetime
from typing import Dict, Any, Optional
from fastapi import BackgroundTasks

from services.base_service import BaseService
from models.schemas import TrainingRequest, TrainingMetrics
from core.resource_manager import resource_manager
from core.config import settings
from utils.trainer import Basetrainer

logger = logging.getLogger(__name__)


class TrainingLogHandler(logging.Handler):
    """自定义日志处理器，用于捕获训练指标"""
    def __init__(self, task_id: str, service_instance: Any):
        super().__init__()
        self.task_id = task_id
        self.service = service_instance
        self.metrics_buffer: Dict[str, Any] = {}
        self.current_epoch: Optional[int] = None
        self.total_epochs: Optional[int] = None

    def emit(self, record: logging.LogRecord):
        """处理日志记录并提取指标"""
        log_entry = {
            "timestamp": datetime.fromtimestamp(record.created).isoformat(),
            "level": record.levelname,
            "message": record.getMessage(),
            "metrics": None,
            "step": None,
            "stage": None
        }
        
        message = record.getMessage()
        metrics = {}
        stage = None
        
        # 解析日志消息中的训练指标
        if "Epoch [" in message and "started" in message:
            match = re.search(r"Epoch \[(\d+)/(\d+)\] started", message)
            if match:
                self.current_epoch = int(match.group(1))
                self.total_epochs = int(match.group(2))
                metrics["epoch"] = self.current_epoch
                metrics["total_epochs"] = self.total_epochs
                stage = "epoch_start"
        
        elif "Train Loss:" in message and "Train Accuracy:" in message:
            match = re.search(r"Train Loss: ([\d.]+), Train Accuracy: ([\d.]+)%", message)
            if match:
                metrics["train_loss"] = float(match.group(1))
                metrics["train_acc"] = float(match.group(2))
                stage = "training"
        
        elif "Validation Loss:" in message and "Validation Accuracy:" in message:
            match = re.search(r"Validation Loss: ([\d.]+), Validation Accuracy: ([\d.]+)%", message)
            if match:
                metrics["val_loss"] = float(match.group(1))
                metrics["val_acc"] = float(match.group(2))
                stage = "validation"
        
        elif "Validation macro_F1:" in message:
            match = re.search(r"Validation macro_F1: ([\d.]+)", message)
            if match:
                metrics["macro_f1"] = float(match.group(1))
                stage = "validation"
        
        elif "Validation micro_F1:" in message:
            match = re.search(r"Validation micro_F1: ([\d.]+)", message)
            if match:
                metrics["micro_f1"] = float(match.group(1))
                stage = "validation"
        
        elif "Validation mAP:" in message:
            match = re.search(r"Validation mAP: ([\d.]+)", message)
            if match:
                metrics["mAP"] = float(match.group(1))
                stage = "validation"
        
        elif "Validation Top-k Accuracy:" in message:
            match = re.search(r"Validation Top-k Accuracy: \{'top1': ([\d.]+), 'top3': ([\d.]+), 'top5': ([\d.]+)\}", message)
            if match:
                metrics["top1_acc"] = float(match.group(1))
                metrics["top3_acc"] = float(match.group(2))
                metrics["top5_acc"] = float(match.group(3))
                stage = "validation"
        
        elif "New best model saved with Accuracy:" in message:
            match = re.search(r"Accuracy: ([\d.]+)%", message)
            if match:
                metrics["best_acc"] = float(match.group(1))
                stage = "epoch_end"
        
        elif "训练完成！" in message or "Training completed" in message:
            stage = "completed"

        if metrics:
            # 合并当前epoch和total_epochs到metrics
            if self.current_epoch is not None:
                metrics["epoch"] = self.current_epoch
            if self.total_epochs is not None:
                metrics["total_epochs"] = self.total_epochs
            
            # 更新任务的最新指标
            self.service.update_task_metrics(self.task_id, TrainingMetrics(**metrics))
            log_entry["metrics"] = metrics
            log_entry["stage"] = stage
            
            # 更新任务进度
            if self.current_epoch is not None and self.total_epochs is not None and self.total_epochs > 0:
                progress = int((self.current_epoch / self.total_epochs) * 100)
                self.service.update_task_status(self.task_id, progress=progress)

        # 添加日志到队列（包含指标信息）
        self.service.add_log(
            self.task_id, 
            record.levelname, 
            message, 
            metrics=log_entry["metrics"], 
            step=log_entry["step"], 
            stage=log_entry["stage"]
        )


class TrainingService(BaseService):
    """训练服务"""
    
    def __init__(self):
        super().__init__()
        self.latest_metrics: Dict[str, TrainingMetrics] = {}  # 存储每个任务的最新指标
    
    async def start_training(
        self,
        request: TrainingRequest,
        background_tasks: BackgroundTasks
    ) -> str:
        """启动训练任务"""
        # 生成任务ID
        task_id = self.generate_task_id(request.task_id)
        
        # 验证模型
        if request.model not in settings.SUPPORTED_MODELS:
            raise ValueError(f"不支持的模型: {request.model}")
        
        # 检查路径
        if not os.path.exists(request.train_path):
            raise FileNotFoundError(f"训练集路径不存在: {request.train_path}")
        if not os.path.exists(request.val_path):
            raise FileNotFoundError(f"验证集路径不存在: {request.val_path}")
        
        # 初始化任务状态
        self.update_task_status(
            task_id,
            "pending",
            "等待开始",
            0,
            task_type="training",
            device=request.device,
            priority=request.priority,
            model=request.model,
            total_epochs=request.num_epochs
        )
        
        # 初始化指标
        self.latest_metrics[task_id] = TrainingMetrics(total_epochs=request.num_epochs)
        
        # 在后台执行训练
        background_tasks.add_task(self._train_worker, task_id, request)
        
        logger.info(f"训练任务已创建: {task_id}")
        return task_id
    
    def _train_worker(self, task_id: str, request: TrainingRequest):
        """训练工作线程"""
        device = request.device
        
        # 获取训练器logger并添加自定义处理器
        trainer_logger = logging.getLogger('Train')
        
        # 移除可能存在的旧handler，避免重复日志
        for handler in list(trainer_logger.handlers):
            if isinstance(handler, TrainingLogHandler) and handler.task_id == task_id:
                trainer_logger.removeHandler(handler)
        
        # 添加自定义日志处理器
        log_handler = TrainingLogHandler(task_id, self)
        trainer_logger.addHandler(log_handler)
        trainer_logger.setLevel(logging.INFO)
        
        try:
            # 创建日志队列
            self.create_log_queue(task_id)
            
            # 等待资源
            self.update_task_status(task_id, "queued", "等待资源...", 0)
            self.add_log(task_id, "INFO", f"等待{device.upper()}资源...")
            
            import threading
            while not resource_manager.can_allocate(device, "training"):
                logger.info(f"任务 {task_id} 等待 {device} 资源...")
                threading.Event().wait(2)
            
            # 分配资源（可能会自动选择具体GPU）
            actual_device = resource_manager.allocate(device, "training", task_id)
            self.update_task_status(task_id, "running", "训练中...", 0, device=actual_device)
            self.add_log(task_id, "INFO", f"资源已分配，使用设备: {actual_device}")
            self.add_log(task_id, "INFO", "开始训练...")
            
            # 创建保存目录
            os.makedirs(request.save_path, exist_ok=True)
            
            self.add_log(task_id, "INFO", f"模型: {request.model}")
            self.add_log(task_id, "INFO", f"设备: {actual_device}")
            self.add_log(task_id, "INFO", f"批次大小: {request.batch_size}")
            self.add_log(task_id, "INFO", f"训练轮数: {request.num_epochs}")
            
            # 创建训练器（使用实际分配的设备）
            trainer = Basetrainer(
                model=request.model,
                train_path=request.train_path,
                val_path=request.val_path,
                num_class=request.num_classes,
                save_path=request.save_path,
                weight_path=request.weight_path,
                device=actual_device,  # 使用实际分配的设备
                batch_size=request.batch_size,
                shuffle=request.shuffle,
                image_size=request.image_size,
                lr=request.learning_rate,
                pretrained=request.pretrained
            )
            
            # 开始训练
            trainer.train(num_epochs=request.num_epochs)
            
            self.update_task_status(task_id, "completed", "训练完成", 100)
            self.add_log(task_id, "INFO", "训练完成！")
            logger.info(f"任务 {task_id} 训练完成")
            
        except Exception as e:
            error_msg = f"训练失败: {str(e)}"
            logger.error(f"任务 {task_id} 失败: {error_msg}\n{traceback.format_exc()}")
            self.update_task_status(task_id, "failed", error_msg, 0)
            self.add_log(task_id, "ERROR", error_msg)
        finally:
            # 释放资源（使用实际分配的设备）
            actual_device = self.get_task(task_id).get("device", device)
            resource_manager.release(actual_device, "training", task_id)
            # 移除自定义日志处理器
            trainer_logger.removeHandler(log_handler)
    
    def stop_task(self, task_id: str) -> bool:
        """停止训练任务"""
        task = self.get_task(task_id)
        if not task:
            return False
        
        if task["status"] in ["pending", "queued", "running"]:
            self.update_task_status(task_id, "cancelled", "任务已取消", task.get("progress", 0))
            self.add_log(task_id, "WARNING", "任务已被用户取消")
            return True
        
        return False
    
    def update_task_metrics(self, task_id: str, metrics: TrainingMetrics):
        """更新任务的最新指标"""
        if task_id in self.latest_metrics:
            # 合并新旧指标
            existing_metrics = self.latest_metrics[task_id].model_dump(exclude_none=True)
            new_metrics = metrics.model_dump(exclude_none=True)
            updated_metrics_dict = {**existing_metrics, **new_metrics}
            self.latest_metrics[task_id] = TrainingMetrics(**updated_metrics_dict)
        else:
            self.latest_metrics[task_id] = metrics
        
        # 更新任务状态中的latest_metrics和current_epoch
        task = self.get_task(task_id)
        if task:
            task["latest_metrics"] = self.latest_metrics[task_id].model_dump(exclude_none=True)
            task["current_epoch"] = self.latest_metrics[task_id].epoch
            self.tasks[task_id] = task  # 确保更新到内存中的任务字典

