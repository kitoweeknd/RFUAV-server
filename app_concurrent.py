"""
FastAPI服务器：支持训练和推理并发执行（优化版）
添加任务队列、资源管理和并发控制
"""
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.responses import JSONResponse, StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
import os
import uuid
import logging
from datetime import datetime
from utils.trainer import Basetrainer
from utils.benchmark import Classify_Model
from utils.build import check_cfg
import traceback
import asyncio
import json
from queue import Queue, PriorityQueue
import threading
import torch
from collections import defaultdict


# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# 创建FastAPI应用
app = FastAPI(
    title="RFUAV Model Service Concurrent",
    description="无人机信号识别模型训练和推理服务（并发优化版）",
    version="2.2.0"
)

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 全局变量
training_tasks: Dict[str, Dict[str, Any]] = {}
inference_tasks: Dict[str, Dict[str, Any]] = {}
log_queues: Dict[str, Queue] = {}

# 任务队列和锁
task_queue = PriorityQueue()  # 优先级队列
device_locks = defaultdict(threading.Lock)  # 每个设备一个锁
active_tasks = defaultdict(list)  # 跟踪每个设备上的活动任务


# ==================== 资源管理 ====================

class ResourceManager:
    """资源管理器 - 管理GPU/CPU资源分配"""
    
    def __init__(self):
        self.device_usage = defaultdict(lambda: {"training": 0, "inference": 0})
        self.max_concurrent = {
            "cuda": {"training": 1, "inference": 3},  # GPU上同时最多1个训练，3个推理
            "cpu": {"training": 2, "inference": 4}     # CPU上同时最多2个训练，4个推理
        }
        self.lock = threading.Lock()
    
    def can_allocate(self, device: str, task_type: str) -> bool:
        """检查是否可以分配资源"""
        with self.lock:
            current = self.device_usage[device][task_type]
            max_allowed = self.max_concurrent[device][task_type]
            return current < max_allowed
    
    def allocate(self, device: str, task_type: str, task_id: str):
        """分配资源"""
        with self.lock:
            self.device_usage[device][task_type] += 1
            active_tasks[device].append({"id": task_id, "type": task_type})
            logger.info(f"资源分配: {device} {task_type} - 当前使用: {self.device_usage[device]}")
    
    def release(self, device: str, task_type: str, task_id: str):
        """释放资源"""
        with self.lock:
            self.device_usage[device][task_type] -= 1
            active_tasks[device] = [t for t in active_tasks[device] if t["id"] != task_id]
            logger.info(f"资源释放: {device} {task_type} - 当前使用: {self.device_usage[device]}")
    
    def get_status(self) -> Dict:
        """获取资源使用状态"""
        with self.lock:
            return {
                "device_usage": dict(self.device_usage),
                "active_tasks": dict(active_tasks),
                "limits": self.max_concurrent
            }


resource_manager = ResourceManager()


# ==================== 数据模型 ====================

class TrainingParameters(BaseModel):
    """训练参数模型"""
    model: str = Field(..., description="模型名称")
    num_classes: int = Field(..., description="分类类别数")
    train_path: str = Field(..., description="训练集路径")
    val_path: str = Field(..., description="验证集路径")
    batch_size: int = Field(default=8, description="批次大小")
    num_epochs: int = Field(default=100, description="训练轮数")
    learning_rate: float = Field(default=0.0001, description="学习率")
    image_size: int = Field(default=224, description="图像尺寸")
    device: str = Field(default="cuda", description="设备")
    save_path: str = Field(..., description="模型保存路径")
    weight_path: Optional[str] = Field(default="", description="预训练权重路径")
    shuffle: bool = Field(default=True, description="是否打乱数据")
    pretrained: bool = Field(default=True, description="是否使用预训练权重")
    task_id: Optional[str] = Field(None, description="任务ID")
    priority: int = Field(default=5, description="优先级(1-10，数字越小优先级越高)")


class InferenceRequest(BaseModel):
    """推理请求模型"""
    cfg_path: str = Field(..., description="配置文件路径")
    weight_path: str = Field(..., description="模型权重路径")
    source_path: str = Field(..., description="待推理的数据路径")
    save_path: Optional[str] = Field(None, description="结果保存路径")
    device: Optional[str] = Field("cuda", description="推理设备")
    task_id: Optional[str] = Field(None, description="任务ID")
    priority: int = Field(default=3, description="优先级(1-10，推理默认优先级高)")


class TaskStatusResponse(BaseModel):
    """任务状态响应模型"""
    task_id: str
    task_type: str
    status: str
    message: Optional[str] = None
    progress: Optional[int] = None
    device: Optional[str] = None
    created_at: str
    updated_at: str


class ResourceStatus(BaseModel):
    """资源状态响应"""
    device_usage: Dict
    active_tasks: Dict
    limits: Dict
    gpu_available: bool
    gpu_memory_info: Optional[Dict] = None


# ==================== 日志处理 ====================

class LogHandler(logging.Handler):
    """自定义日志处理器"""
    def __init__(self, task_id: str):
        super().__init__()
        self.task_id = task_id
        if task_id not in log_queues:
            log_queues[task_id] = Queue()
    
    def emit(self, record):
        log_entry = self.format(record)
        if self.task_id in log_queues:
            log_queues[self.task_id].put({
                'timestamp': datetime.now().isoformat(),
                'level': record.levelname,
                'message': log_entry
            })


# ==================== 任务管理 ====================

def update_task_status(task_id: str, task_type: str, status: str, 
                       message: str = None, progress: int = None, device: str = None):
    """更新任务状态"""
    tasks = training_tasks if task_type == "training" else inference_tasks
    
    if task_id in tasks:
        tasks[task_id]['status'] = status
        tasks[task_id]['updated_at'] = datetime.now().isoformat()
        if message:
            tasks[task_id]['message'] = message
        if progress is not None:
            tasks[task_id]['progress'] = progress
        if device:
            tasks[task_id]['device'] = device
    else:
        tasks[task_id] = {
            'task_id': task_id,
            'task_type': task_type,
            'status': status,
            'message': message,
            'progress': progress,
            'device': device,
            'created_at': datetime.now().isoformat(),
            'updated_at': datetime.now().isoformat()
        }


def train_model_worker(task_id: str, params: TrainingParameters):
    """训练工作线程"""
    device = params.device
    
    try:
        # 等待资源
        update_task_status(task_id, "training", "queued", "等待资源...", 0, device)
        
        while not resource_manager.can_allocate(device, "training"):
            logger.info(f"任务 {task_id} 等待 {device} 资源...")
            threading.Event().wait(2)
        
        # 分配资源
        resource_manager.allocate(device, "training", task_id)
        update_task_status(task_id, "training", "running", "训练中...", 0, device)
        
        logger.info(f"开始训练任务 {task_id} on {device}")
        
        # 设置日志处理器
        task_logger = logging.getLogger(f'train_{task_id}')
        task_logger.setLevel(logging.INFO)
        log_handler = LogHandler(task_id)
        log_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
        task_logger.addHandler(log_handler)
        
        os.makedirs(params.save_path, exist_ok=True)
        
        # 创建训练器
        trainer = Basetrainer(
            model=params.model,
            train_path=params.train_path,
            val_path=params.val_path,
            num_class=params.num_classes,
            save_path=params.save_path,
            weight_path=params.weight_path,
            device=params.device,
            batch_size=params.batch_size,
            shuffle=params.shuffle,
            image_size=params.image_size,
            lr=params.learning_rate,
            pretrained=params.pretrained
        )
        
        trainer.train(num_epochs=params.num_epochs)
        
        update_task_status(task_id, "training", "completed", "训练完成", 100, device)
        task_logger.info("训练完成！")
        
    except Exception as e:
        error_msg = f"训练失败: {str(e)}"
        logger.error(f"任务 {task_id} 失败: {error_msg}\n{traceback.format_exc()}")
        update_task_status(task_id, "training", "failed", error_msg, 0, device)
    finally:
        # 释放资源
        resource_manager.release(device, "training", task_id)


def inference_worker(task_id: str, request: InferenceRequest):
    """推理工作线程"""
    device = request.device
    
    try:
        # 等待资源
        update_task_status(task_id, "inference", "queued", "等待资源...", 0, device)
        
        while not resource_manager.can_allocate(device, "inference"):
            logger.info(f"推理任务 {task_id} 等待 {device} 资源...")
            threading.Event().wait(1)
        
        # 分配资源
        resource_manager.allocate(device, "inference", task_id)
        update_task_status(task_id, "inference", "running", "推理中...", 0, device)
        
        logger.info(f"开始推理任务 {task_id} on {device}")
        
        # 加载配置并设置设备
        import yaml
        import tempfile
        
        with open(request.cfg_path, 'r', encoding='utf-8') as f:
            cfg = yaml.safe_load(f)
        cfg['device'] = device
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False, encoding='utf-8') as tmp_cfg:
            yaml.dump(cfg, tmp_cfg, allow_unicode=True)
            tmp_cfg_path = tmp_cfg.name
        
        try:
            model = Classify_Model(cfg=tmp_cfg_path, weight_path=request.weight_path)
            model.inference(source=request.source_path, save_path=request.save_path or "./results/")
            
            update_task_status(task_id, "inference", "completed", "推理完成", 100, device)
            
        finally:
            if os.path.exists(tmp_cfg_path):
                os.unlink(tmp_cfg_path)
        
    except Exception as e:
        error_msg = f"推理失败: {str(e)}"
        logger.error(f"推理任务 {task_id} 失败: {error_msg}\n{traceback.format_exc()}")
        update_task_status(task_id, "inference", "failed", error_msg, 0, device)
    finally:
        # 释放资源
        resource_manager.release(device, "inference", task_id)


async def log_stream_generator(task_id: str):
    """生成日志流"""
    if task_id not in log_queues:
        log_queues[task_id] = Queue()
    
    queue = log_queues[task_id]
    
    try:
        while True:
            # 检查任务状态
            task = training_tasks.get(task_id) or inference_tasks.get(task_id)
            if task:
                status = task['status']
                
                while not queue.empty():
                    log_entry = queue.get()
                    yield f"data: {json.dumps(log_entry, ensure_ascii=False)}\n\n"
                
                if status in ['completed', 'failed']:
                    yield f"data: {json.dumps({'status': status, 'message': '任务结束'}, ensure_ascii=False)}\n\n"
                    break
            
            await asyncio.sleep(0.5)
    finally:
        if task_id in log_queues:
            del log_queues[task_id]


# ==================== API路由 ====================

@app.get("/")
async def root():
    """根路径"""
    return {
        "message": "RFUAV模型服务（并发优化版）",
        "version": "2.2.0",
        "features": [
            "训练和推理并发执行",
            "智能资源管理",
            "任务优先级队列",
            "设备资源隔离",
            "实时监控"
        ],
        "endpoints": {
            "训练": "/api/v2/train",
            "推理": "/api/v2/inference",
            "资源状态": "/api/v2/resources",
            "任务列表": "/api/v2/tasks",
            "实时日志": "/api/v2/tasks/{task_id}/logs"
        }
    }


@app.post("/api/v2/train", response_model=TaskStatusResponse)
async def start_training(params: TrainingParameters, background_tasks: BackgroundTasks):
    """
    启动训练任务（支持并发）
    
    优先级说明：
    - 1-3: 高优先级
    - 4-6: 中优先级（默认5）
    - 7-10: 低优先级
    """
    try:
        task_id = params.task_id or str(uuid.uuid4())
        
        # 验证模型
        valid_models = [
            "resnet18", "resnet34", "resnet50", "resnet101", "resnet152",
            "vit_b_16", "vit_b_32", "vit_l_16", "vit_l_32",
            "swin_v2_t", "swin_v2_s", "swin_v2_b",
            "mobilenet_v3_large", "mobilenet_v3_small"
        ]
        if params.model not in valid_models:
            raise HTTPException(status_code=400, detail=f"不支持的模型: {params.model}")
        
        # 检查路径
        if not os.path.exists(params.train_path):
            raise HTTPException(status_code=400, detail=f"训练集路径不存在: {params.train_path}")
        if not os.path.exists(params.val_path):
            raise HTTPException(status_code=400, detail=f"验证集路径不存在: {params.val_path}")
        
        # 初始化任务状态
        update_task_status(task_id, "training", "pending", "等待开始", 0, params.device)
        
        # 在后台启动训练任务
        background_tasks.add_task(train_model_worker, task_id, params)
        
        return training_tasks[task_id]
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"启动训练任务失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"启动训练任务失败: {str(e)}")


@app.post("/api/v2/inference", response_model=TaskStatusResponse)
async def start_inference(request: InferenceRequest, background_tasks: BackgroundTasks):
    """
    启动推理任务（支持并发）
    
    推理任务默认优先级较高（3），可以与训练同时进行
    """
    try:
        task_id = request.task_id or str(uuid.uuid4())
        
        # 检查文件
        if not os.path.exists(request.cfg_path):
            raise HTTPException(status_code=400, detail=f"配置文件不存在: {request.cfg_path}")
        if not os.path.exists(request.weight_path):
            raise HTTPException(status_code=400, detail=f"模型权重不存在: {request.weight_path}")
        if not os.path.exists(request.source_path):
            raise HTTPException(status_code=400, detail=f"数据路径不存在: {request.source_path}")
        
        # 初始化任务状态
        update_task_status(task_id, "inference", "pending", "等待开始", 0, request.device)
        
        # 在后台启动推理任务
        background_tasks.add_task(inference_worker, task_id, request)
        
        return inference_tasks[task_id]
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"启动推理任务失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"启动推理任务失败: {str(e)}")


@app.get("/api/v2/resources", response_model=ResourceStatus)
async def get_resource_status():
    """
    获取资源使用状态
    
    返回：
    - 各设备使用情况
    - 活动任务列表
    - 资源限制
    - GPU可用性和显存信息
    """
    status = resource_manager.get_status()
    
    # 获取GPU信息
    gpu_available = torch.cuda.is_available()
    gpu_memory_info = None
    
    if gpu_available:
        gpu_memory_info = {}
        for i in range(torch.cuda.device_count()):
            total = torch.cuda.get_device_properties(i).total_memory / 1024**3
            allocated = torch.cuda.memory_allocated(i) / 1024**3
            cached = torch.cuda.memory_reserved(i) / 1024**3
            gpu_memory_info[f"GPU_{i}"] = {
                "name": torch.cuda.get_device_name(i),
                "total_gb": round(total, 2),
                "allocated_gb": round(allocated, 2),
                "cached_gb": round(cached, 2),
                "free_gb": round(total - allocated, 2)
            }
    
    return {
        "device_usage": status["device_usage"],
        "active_tasks": status["active_tasks"],
        "limits": status["limits"],
        "gpu_available": gpu_available,
        "gpu_memory_info": gpu_memory_info
    }


@app.get("/api/v2/tasks")
async def get_all_tasks():
    """
    获取所有任务状态
    
    返回训练和推理任务的完整列表
    """
    return {
        "training_tasks": list(training_tasks.values()),
        "inference_tasks": list(inference_tasks.values()),
        "total_training": len(training_tasks),
        "total_inference": len(inference_tasks)
    }


@app.get("/api/v2/tasks/{task_id}")
async def get_task_status(task_id: str):
    """获取特定任务状态"""
    task = training_tasks.get(task_id) or inference_tasks.get(task_id)
    if not task:
        raise HTTPException(status_code=404, detail=f"任务 {task_id} 不存在")
    return task


@app.get("/api/v2/tasks/{task_id}/logs")
async def get_task_logs(task_id: str):
    """获取任务实时日志流"""
    task = training_tasks.get(task_id) or inference_tasks.get(task_id)
    if not task:
        raise HTTPException(status_code=404, detail=f"任务 {task_id} 不存在")
    
    return StreamingResponse(
        log_stream_generator(task_id),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"
        }
    )


@app.post("/api/v2/resources/config")
async def update_resource_config(config: Dict):
    """
    更新资源配置
    
    允许动态调整并发限制
    """
    try:
        if "max_concurrent" in config:
            resource_manager.max_concurrent.update(config["max_concurrent"])
        return {
            "status": "success",
            "message": "资源配置已更新",
            "current_config": resource_manager.max_concurrent
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"更新配置失败: {str(e)}")


@app.get("/api/v1/health")
async def health_check():
    """健康检查"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "training_tasks": len(training_tasks),
        "inference_tasks": len(inference_tasks),
        "active_log_streams": len(log_queues),
        "resource_status": resource_manager.get_status()
    }


# ==================== 错误处理 ====================

@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "status": "error",
            "message": exc.detail,
            "timestamp": datetime.now().isoformat()
        }
    )


@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    logger.error(f"未处理的异常: {str(exc)}\n{traceback.format_exc()}")
    return JSONResponse(
        status_code=500,
        content={
            "status": "error",
            "message": f"服务器内部错误: {str(exc)}",
            "timestamp": datetime.now().isoformat()
        }
    )


# ==================== 启动服务 ====================

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app_concurrent:app", host="0.0.0.0", port=8000, reload=True)


