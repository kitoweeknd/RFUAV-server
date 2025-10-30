"""
FastAPI服务器：提供模型训练和推理接口（增强版）
支持参数解耦和实时日志流
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
from utils.build import check_cfg, build_from_cfg
import traceback
import asyncio
import json
from queue import Queue
import threading


# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# 创建FastAPI应用
app = FastAPI(
    title="RFUAV Model Service Enhanced",
    description="无人机信号识别模型训练和推理服务（增强版）",
    version="2.0.0"
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
log_queues: Dict[str, Queue] = {}


# ==================== 数据模型 ====================

class TrainingParameters(BaseModel):
    """训练参数模型 - 完全解耦的训练配置"""
    # 模型配置
    model: str = Field(..., description="模型名称", example="resnet18")
    num_classes: int = Field(..., description="分类类别数", example=37)
    
    # 数据集路径
    train_path: str = Field(..., description="训练集路径")
    val_path: str = Field(..., description="验证集路径")
    
    # 训练超参数
    batch_size: int = Field(default=8, description="批次大小", ge=1)
    num_epochs: int = Field(default=100, description="训练轮数", ge=1)
    learning_rate: float = Field(default=0.0001, description="学习率", gt=0)
    image_size: int = Field(default=224, description="图像尺寸", ge=32)
    
    # 其他配置
    device: str = Field(default="cuda", description="设备：cuda或cpu")
    save_path: str = Field(..., description="模型保存路径")
    weight_path: Optional[str] = Field(default="", description="预训练权重路径")
    shuffle: bool = Field(default=True, description="是否打乱数据")
    pretrained: bool = Field(default=True, description="是否使用预训练权重")
    
    # 任务信息
    task_id: Optional[str] = Field(None, description="任务ID")
    description: Optional[str] = Field(None, description="任务描述")


class TrainingConfigLegacy(BaseModel):
    """训练请求配置模型（兼容旧版本）"""
    task_id: Optional[str] = Field(None, description="任务ID，可选")
    cfg_path: str = Field(..., description="配置文件路径")
    description: Optional[str] = Field(None, description="任务描述")


class InferenceRequest(BaseModel):
    """推理请求模型"""
    cfg_path: str = Field(..., description="配置文件路径")
    weight_path: str = Field(..., description="模型权重路径")
    source_path: str = Field(..., description="待推理的数据路径")
    save_path: Optional[str] = Field(None, description="结果保存路径")
    device: Optional[str] = Field("cuda", description="推理设备：cuda或cpu")


class BenchmarkRequest(BaseModel):
    """基准测试请求模型"""
    cfg_path: str = Field(..., description="配置文件路径")
    weight_path: str = Field(..., description="模型权重路径")
    data_path: str = Field(..., description="测试数据路径")
    save_path: Optional[str] = Field(None, description="结果保存路径")
    device: Optional[str] = Field("cuda", description="测试设备：cuda或cpu")


class TaskStatusResponse(BaseModel):
    """任务状态响应模型"""
    task_id: str
    status: str
    message: Optional[str] = None
    progress: Optional[int] = None
    created_at: str
    updated_at: str
    logs: Optional[List[str]] = None


# ==================== 日志处理类 ====================

class LogHandler(logging.Handler):
    """自定义日志处理器，将日志推送到队列"""
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


# ==================== 辅助函数 ====================

def get_task_status_internal(task_id: str) -> Dict[str, Any]:
    """获取任务状态"""
    if task_id in training_tasks:
        return training_tasks[task_id]
    else:
        raise HTTPException(status_code=404, detail=f"任务 {task_id} 不存在")


def update_task_status(task_id: str, status: str, message: str = None, progress: int = None):
    """更新任务状态"""
    if task_id in training_tasks:
        training_tasks[task_id]['status'] = status
        training_tasks[task_id]['updated_at'] = datetime.now().isoformat()
        if message:
            training_tasks[task_id]['message'] = message
        if progress is not None:
            training_tasks[task_id]['progress'] = progress
    else:
        training_tasks[task_id] = {
            'task_id': task_id,
            'status': status,
            'message': message,
            'progress': progress,
            'created_at': datetime.now().isoformat(),
            'updated_at': datetime.now().isoformat()
        }


def train_model_with_params(task_id: str, params: TrainingParameters):
    """使用参数进行模型训练"""
    try:
        logger.info(f"开始训练任务 {task_id}")
        update_task_status(task_id, "running", "训练中...", 0)
        
        # 设置日志处理器
        task_logger = logging.getLogger(f'train_{task_id}')
        task_logger.setLevel(logging.INFO)
        log_handler = LogHandler(task_id)
        log_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
        task_logger.addHandler(log_handler)
        
        # 创建保存目录
        os.makedirs(params.save_path, exist_ok=True)
        
        # 验证路径
        if not os.path.exists(params.train_path):
            raise ValueError(f"训练集路径不存在: {params.train_path}")
        if not os.path.exists(params.val_path):
            raise ValueError(f"验证集路径不存在: {params.val_path}")
        
        task_logger.info(f"模型: {params.model}")
        task_logger.info(f"训练集: {params.train_path}")
        task_logger.info(f"验证集: {params.val_path}")
        task_logger.info(f"批次大小: {params.batch_size}")
        task_logger.info(f"训练轮数: {params.num_epochs}")
        task_logger.info(f"学习率: {params.learning_rate}")
        
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
        
        # 开始训练
        task_logger.info("开始训练...")
        trainer.train(num_epochs=params.num_epochs)
        
        update_task_status(task_id, "completed", "训练完成", 100)
        task_logger.info("训练完成！")
        logger.info(f"任务 {task_id} 训练完成")
        
    except Exception as e:
        error_msg = f"训练失败: {str(e)}\n{traceback.format_exc()}"
        logger.error(f"任务 {task_id} 失败: {error_msg}")
        update_task_status(task_id, "failed", error_msg, 0)
        
        if task_id in log_queues:
            log_queues[task_id].put({
                'timestamp': datetime.now().isoformat(),
                'level': 'ERROR',
                'message': error_msg
            })


async def log_stream_generator(task_id: str):
    """生成日志流"""
    if task_id not in log_queues:
        log_queues[task_id] = Queue()
    
    queue = log_queues[task_id]
    
    try:
        while True:
            # 检查任务状态
            if task_id in training_tasks:
                status = training_tasks[task_id]['status']
                
                # 如果有日志，发送日志
                while not queue.empty():
                    log_entry = queue.get()
                    yield f"data: {json.dumps(log_entry, ensure_ascii=False)}\n\n"
                
                # 如果任务完成或失败，发送完成信号并退出
                if status in ['completed', 'failed']:
                    yield f"data: {json.dumps({'status': status, 'message': '任务结束'}, ensure_ascii=False)}\n\n"
                    break
            
            await asyncio.sleep(0.5)
            
    finally:
        # 清理队列
        if task_id in log_queues:
            del log_queues[task_id]


# ==================== API路由 ====================

@app.get("/")
async def root():
    """根路径"""
    return {
        "message": "RFUAV模型服务（增强版）",
        "version": "2.0.0",
        "features": [
            "参数化训练配置",
            "实时日志流",
            "训练进度跟踪",
            "模型推理",
            "基准测试"
        ],
        "endpoints": {
            "训练（参数化）": "/api/v2/train",
            "训练（配置文件）": "/api/v1/train",
            "实时日志": "/api/v2/train/{task_id}/logs",
            "推理": "/api/v1/inference",
            "基准测试": "/api/v1/benchmark",
            "任务状态": "/api/v1/tasks/{task_id}"
        }
    }


@app.post("/api/v2/train", response_model=TaskStatusResponse)
async def start_training_v2(params: TrainingParameters, background_tasks: BackgroundTasks):
    """
    启动模型训练任务（V2 - 参数化版本）
    
    支持直接通过参数指定模型、数据集、超参数等，无需配置文件
    
    请求示例:
    {
        "model": "resnet18",
        "num_classes": 37,
        "train_path": "data/train",
        "val_path": "data/val",
        "batch_size": 32,
        "num_epochs": 100,
        "learning_rate": 0.0001,
        "image_size": 224,
        "device": "cuda",
        "save_path": "models/resnet18_experiment",
        "shuffle": true,
        "pretrained": true
    }
    """
    try:
        # 生成任务ID
        task_id = params.task_id or str(uuid.uuid4())
        
        # 验证模型名称
        valid_models = [
            "resnet18", "resnet34", "resnet50", "resnet101", "resnet152",
            "vit_b_16", "vit_b_32", "vit_l_16", "vit_l_32",
            "swin_v2_t", "swin_v2_s", "swin_v2_b",
            "mobilenet_v3_large", "mobilenet_v3_small"
        ]
        if params.model not in valid_models:
            raise HTTPException(
                status_code=400, 
                detail=f"不支持的模型: {params.model}。支持的模型: {', '.join(valid_models)}"
            )
        
        # 检查路径
        if not os.path.exists(params.train_path):
            raise HTTPException(status_code=400, detail=f"训练集路径不存在: {params.train_path}")
        if not os.path.exists(params.val_path):
            raise HTTPException(status_code=400, detail=f"验证集路径不存在: {params.val_path}")
        
        # 初始化任务状态
        update_task_status(task_id, "pending", "等待开始", 0)
        
        # 在后台启动训练任务
        background_tasks.add_task(train_model_with_params, task_id, params)
        
        return training_tasks[task_id]
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"启动训练任务失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"启动训练任务失败: {str(e)}")


@app.get("/api/v2/train/{task_id}/logs")
async def get_training_logs(task_id: str):
    """
    获取训练任务的实时日志流（Server-Sent Events）
    
    使用示例（JavaScript）:
    ```javascript
    const eventSource = new EventSource('/api/v2/train/{task_id}/logs');
    eventSource.onmessage = (event) => {
        const log = JSON.parse(event.data);
        console.log(log.timestamp, log.level, log.message);
    };
    ```
    
    使用示例（Python）:
    ```python
    import requests
    response = requests.get('http://localhost:8000/api/v2/train/{task_id}/logs', stream=True)
    for line in response.iter_lines():
        if line:
            print(line.decode('utf-8'))
    ```
    """
    if task_id not in training_tasks:
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


@app.post("/api/v1/train", response_model=TaskStatusResponse)
async def start_training_legacy(request: TrainingConfigLegacy, background_tasks: BackgroundTasks):
    """
    启动模型训练任务（V1 - 兼容旧版本，使用配置文件）
    """
    try:
        from utils.trainer import CustomTrainer
        
        task_id = request.task_id or str(uuid.uuid4())
        
        if not os.path.exists(request.cfg_path):
            raise HTTPException(status_code=400, detail=f"配置文件不存在: {request.cfg_path}")
        
        update_task_status(task_id, "pending", "等待开始", 0)
        
        def train_worker():
            try:
                update_task_status(task_id, "running", "训练中...", 0)
                if not check_cfg(request.cfg_path):
                    raise ValueError("配置文件验证失败")
                trainer = CustomTrainer(cfg=request.cfg_path)
                trainer.train()
                update_task_status(task_id, "completed", "训练完成", 100)
            except Exception as e:
                error_msg = f"训练失败: {str(e)}"
                update_task_status(task_id, "failed", error_msg, 0)
        
        background_tasks.add_task(train_worker)
        return training_tasks[task_id]
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"启动训练任务失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"启动训练任务失败: {str(e)}")


@app.get("/api/v1/tasks/{task_id}", response_model=TaskStatusResponse)
async def get_task_status(task_id: str):
    """获取训练任务状态"""
    return get_task_status_internal(task_id)


@app.post("/api/v1/inference")
async def model_inference(request: InferenceRequest):
    """
    模型推理接口
    
    请求示例:
    {
        "cfg_path": "configs/exp3.1_ResNet18.yaml",
        "weight_path": "models/best_model.pth",
        "source_path": "example/test_data/",
        "save_path": "results/inference/",
        "device": "cuda"
    }
    """
    try:
        logger.info(f"开始推理: {request.source_path}, 设备: {request.device}")
        
        if not os.path.exists(request.cfg_path):
            raise HTTPException(status_code=400, detail=f"配置文件不存在: {request.cfg_path}")
        if not os.path.exists(request.weight_path):
            raise HTTPException(status_code=400, detail=f"模型权重文件不存在: {request.weight_path}")
        if not os.path.exists(request.source_path):
            raise HTTPException(status_code=400, detail=f"数据路径不存在: {request.source_path}")
        
        # 加载配置并设置设备
        import yaml
        with open(request.cfg_path, 'r', encoding='utf-8') as f:
            cfg = yaml.safe_load(f)
        cfg['device'] = request.device  # 覆盖配置文件中的设备设置
        
        # 创建临时配置文件
        import tempfile
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False, encoding='utf-8') as tmp_cfg:
            yaml.dump(cfg, tmp_cfg, allow_unicode=True)
            tmp_cfg_path = tmp_cfg.name
        
        try:
            model = Classify_Model(cfg=tmp_cfg_path, weight_path=request.weight_path)
            model.inference(source=request.source_path, save_path=request.save_path or "./results/")
        finally:
            # 清理临时文件
            if os.path.exists(tmp_cfg_path):
                os.unlink(tmp_cfg_path)
        
        return {
            "status": "success",
            "message": "推理完成",
            "source_path": request.source_path,
            "save_path": request.save_path or "./results/",
            "device": request.device
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"推理失败: {str(e)}\n{traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=f"推理失败: {str(e)}")


@app.post("/api/v1/benchmark")
async def model_benchmark(request: BenchmarkRequest):
    """
    模型基准测试接口
    
    请求示例:
    {
        "cfg_path": "configs/exp3.1_ResNet18.yaml",
        "weight_path": "models/best_model.pth",
        "data_path": "data/benchmark/",
        "save_path": "results/benchmark/",
        "device": "cuda"
    }
    """
    try:
        logger.info(f"开始基准测试: {request.data_path}, 设备: {request.device}")
        
        if not os.path.exists(request.cfg_path):
            raise HTTPException(status_code=400, detail=f"配置文件不存在: {request.cfg_path}")
        if not os.path.exists(request.weight_path):
            raise HTTPException(status_code=400, detail=f"模型权重文件不存在: {request.weight_path}")
        if not os.path.exists(request.data_path):
            raise HTTPException(status_code=400, detail=f"数据路径不存在: {request.data_path}")
        
        # 加载配置并设置设备
        import yaml
        with open(request.cfg_path, 'r', encoding='utf-8') as f:
            cfg = yaml.safe_load(f)
        cfg['device'] = request.device  # 覆盖配置文件中的设备设置
        
        # 创建临时配置文件
        import tempfile
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False, encoding='utf-8') as tmp_cfg:
            yaml.dump(cfg, tmp_cfg, allow_unicode=True)
            tmp_cfg_path = tmp_cfg.name
        
        try:
            model = Classify_Model(cfg=tmp_cfg_path, weight_path=request.weight_path)
            model.benchmark(data_path=request.data_path, save_path=request.save_path)
        finally:
            # 清理临时文件
            if os.path.exists(tmp_cfg_path):
                os.unlink(tmp_cfg_path)
        
        return {
            "status": "success",
            "message": "基准测试完成",
            "data_path": request.data_path,
            "save_path": request.save_path or os.path.join(request.data_path, "benchmark result"),
            "device": request.device
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"基准测试失败: {str(e)}\n{traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=f"基准测试失败: {str(e)}")


@app.get("/api/v1/health")
async def health_check():
    """健康检查接口"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "training_tasks": len(training_tasks),
        "active_log_streams": len(log_queues)
    }


# ==================== 错误处理 ====================

@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    """HTTP异常处理"""
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
    """通用异常处理"""
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
    uvicorn.run("app_enhanced:app", host="0.0.0.0", port=8000, reload=True)

