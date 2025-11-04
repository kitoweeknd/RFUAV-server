import logging
import os
import traceback
import yaml
import tempfile
from fastapi import BackgroundTasks
from typing import List

from services.base_service import BaseService
from models.schemas import InferenceRequest, BatchInferenceRequest
from core.resource_manager import resource_manager
from utils.benchmark import Classify_Model

logger = logging.getLogger(__name__)


class InferenceService(BaseService):
    def __init__(self):
        super().__init__()
    
    async def start_inference(
        self,
        request: InferenceRequest,
        background_tasks: BackgroundTasks
    ) -> str:        # 生成任务ID
        task_id = self.generate_task_id(request.task_id)
        
        # 检查文件
        if not os.path.exists(request.cfg_path):
            raise FileNotFoundError(f"配置文件不存在: {request.cfg_path}")
        if not os.path.exists(request.weight_path):
            raise FileNotFoundError(f"模型权重不存在: {request.weight_path}")
        if not os.path.exists(request.source_path):
            raise FileNotFoundError(f"数据路径不存在: {request.source_path}")
        
        self.update_task_status(
            task_id,
            "pending",
            "等待开始",
            0,
            task_type="inference",
            device=request.device,
            priority=request.priority
        )
        
        background_tasks.add_task(self._inference_worker, task_id, request)
        
        logger.info(f"推理任务已创建: {task_id}")
        return task_id
    
    async def start_batch_inference(
        self,
        request: BatchInferenceRequest,
        background_tasks: BackgroundTasks
    ) -> List[str]:
        task_ids = []
        
        for idx, source_path in enumerate(request.source_paths):
            infer_request = InferenceRequest(
                cfg_path=request.cfg_path,
                weight_path=request.weight_path,
                source_path=source_path,
                save_path=f"{request.save_base_path}/{idx}" if request.save_base_path else None,
                device=request.device,
                priority=request.priority,
                task_id=None  # 自动生成
            )
            
            task_id = await self.start_inference(infer_request, background_tasks)
            task_ids.append(task_id)
        
        logger.info(f"批量推理已创建 {len(task_ids)} 个任务")
        return task_ids
    
    def _inference_worker(self, task_id: str, request: InferenceRequest):
        device = request.device
        
        try:
            self.create_log_queue(task_id)
            
            self.update_task_status(task_id, "queued", "等待资源...", 0)
            self.add_log(task_id, "INFO", f"等待{device.upper()}资源...")
            
            import threading
            while not resource_manager.can_allocate(device, "inference"):
                logger.info(f"推理任务 {task_id} 等待 {device} 资源...")
                threading.Event().wait(1)
            
            actual_device = resource_manager.allocate(device, "inference", task_id)
            self.update_task_status(task_id, "running", "推理中...", 0, device=actual_device)
            self.add_log(task_id, "INFO", f"资源已分配，使用设备: {actual_device}")
            self.add_log(task_id, "INFO", "开始推理...")
            
            with open(request.cfg_path, 'r', encoding='utf-8') as f:
                cfg = yaml.safe_load(f)
            cfg['device'] = actual_device  # 使用实际分配的设备
            
            with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False, encoding='utf-8') as tmp_cfg:
                yaml.dump(cfg, tmp_cfg, allow_unicode=True)
                tmp_cfg_path = tmp_cfg.name
            
            try:
                self.add_log(task_id, "INFO", f"加载模型: {request.weight_path}")
                model = Classify_Model(cfg=tmp_cfg_path, weight_path=request.weight_path)
                
                self.add_log(task_id, "INFO", f"推理数据: {request.source_path}")
                model.inference(
                    source=request.source_path,
                    save_path=request.save_path or "./results/"
                )
                
                self.update_task_status(task_id, "completed", "推理完成", 100)
                self.add_log(task_id, "INFO", "推理完成！")
                logger.info(f"推理任务 {task_id} 完成")
                
            finally:
                if os.path.exists(tmp_cfg_path):
                    os.unlink(tmp_cfg_path)
            
        except Exception as e:
            error_msg = f"推理失败: {str(e)}"
            logger.error(f"推理任务 {task_id} 失败: {error_msg}\n{traceback.format_exc()}")
            self.update_task_status(task_id, "failed", error_msg, 0)
            self.add_log(task_id, "ERROR", error_msg)
        finally:
            actual_device = self.get_task(task_id).get("device", device)
            resource_manager.release(actual_device, "inference", task_id)

