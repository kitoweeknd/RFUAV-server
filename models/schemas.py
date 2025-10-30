"""
数据模型定义
"""
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime


# ==================== 请求模型 ====================

class TrainingRequest(BaseModel):
    """训练请求"""
    # 模型配置
    model: str = Field(..., description="模型名称", example="resnet18")
    num_classes: int = Field(..., description="分类类别数", example=37)
    
    # 数据路径
    train_path: str = Field(..., description="训练集路径")
    val_path: str = Field(..., description="验证集路径")
    save_path: str = Field(..., description="模型保存路径")
    
    # 训练参数
    batch_size: int = Field(default=8, description="批次大小", ge=1)
    num_epochs: int = Field(default=100, description="训练轮数", ge=1)
    learning_rate: float = Field(default=0.0001, description="学习率", gt=0)
    image_size: int = Field(default=224, description="图像尺寸", ge=32)
    
    # 设备和权重
    device: str = Field(
        default="cuda", 
        description="设备 (cpu/cuda/cuda:0/cuda:1/...)",
        example="cuda:0"
    )
    weight_path: Optional[str] = Field(default="", description="预训练权重路径")
    pretrained: bool = Field(default=True, description="是否使用预训练")
    shuffle: bool = Field(default=True, description="是否打乱数据")
    
    # 任务配置
    task_id: Optional[str] = Field(None, description="任务ID")
    priority: int = Field(default=5, description="优先级", ge=1, le=10)
    description: Optional[str] = Field(None, description="任务描述")


class InferenceRequest(BaseModel):
    """推理请求"""
    cfg_path: str = Field(..., description="配置文件路径")
    weight_path: str = Field(..., description="模型权重路径")
    source_path: str = Field(..., description="数据路径")
    save_path: Optional[str] = Field(None, description="结果保存路径")
    device: str = Field(
        default="cuda", 
        description="推理设备 (cpu/cuda/cuda:0/cuda:1/...)",
        example="cuda:0"
    )
    task_id: Optional[str] = Field(None, description="任务ID")
    priority: int = Field(default=3, description="优先级", ge=1, le=10)


class BatchInferenceRequest(BaseModel):
    """批量推理请求"""
    cfg_path: str = Field(..., description="配置文件路径")
    weight_path: str = Field(..., description="模型权重路径")
    source_paths: List[str] = Field(..., description="数据路径列表")
    save_base_path: Optional[str] = Field(None, description="结果保存基础路径")
    device: str = Field(default="cuda", description="推理设备")
    priority: int = Field(default=3, description="优先级")


class ResourceConfigUpdate(BaseModel):
    """资源配置更新"""
    max_concurrent: Optional[Dict[str, Dict[str, int]]] = None


# ==================== 响应模型 ====================

class TaskResponse(BaseModel):
    """任务响应"""
    task_id: str
    task_type: str
    status: str
    message: Optional[str] = None
    progress: Optional[int] = None
    device: Optional[str] = None
    priority: Optional[int] = None
    created_at: str
    updated_at: str
    
    # 训练详细指标（仅训练任务使用）
    current_epoch: Optional[int] = None
    total_epochs: Optional[int] = None
    latest_metrics: Optional[TrainingMetrics] = None


class TaskListResponse(BaseModel):
    """任务列表响应"""
    training_tasks: List[TaskResponse]
    inference_tasks: List[TaskResponse]
    total_training: int
    total_inference: int


class ResourceStatusResponse(BaseModel):
    """资源状态响应"""
    device_usage: Dict[str, Dict[str, int]]
    active_tasks: Dict[str, List[Dict]]
    limits: Dict[str, Dict[str, int]]
    gpu_info: Dict[str, Any]


class HealthResponse(BaseModel):
    """健康检查响应"""
    status: str
    timestamp: str
    version: str
    training_tasks: int
    inference_tasks: int
    active_log_streams: int
    resource_status: Dict


class InfoResponse(BaseModel):
    """系统信息响应"""
    app_name: str
    version: str
    environment: str
    supported_models: List[str]
    resource_limits: Dict
    gpu_available: bool


class ErrorResponse(BaseModel):
    """错误响应"""
    status: str = "error"
    message: str
    timestamp: str
    detail: Optional[str] = None


class SuccessResponse(BaseModel):
    """成功响应"""
    status: str = "success"
    message: str
    data: Optional[Dict[str, Any]] = None


class TaskActionResponse(BaseModel):
    """任务操作响应"""
    status: str
    message: str
    task_id: str


class BatchInferenceResponse(BaseModel):
    """批量推理响应"""
    status: str
    message: str
    task_ids: List[str]
    total: int


class ConfigUpdateResponse(BaseModel):
    """配置更新响应"""
    status: str
    message: str
    current_config: Dict[str, Any]


# ==================== 训练指标模型 ====================

class TrainingMetrics(BaseModel):
    """训练指标"""
    epoch: Optional[int] = Field(None, description="当前epoch")
    total_epochs: Optional[int] = Field(None, description="总epoch数")
    
    # 训练指标
    train_loss: Optional[float] = Field(None, description="训练损失")
    train_acc: Optional[float] = Field(None, description="训练准确率(%)")
    
    # 验证指标
    val_loss: Optional[float] = Field(None, description="验证损失")
    val_acc: Optional[float] = Field(None, description="验证准确率(%)")
    
    # F1分数
    macro_f1: Optional[float] = Field(None, description="Macro F1分数")
    micro_f1: Optional[float] = Field(None, description="Micro F1分数")
    
    # mAP和Top-k
    mAP: Optional[float] = Field(None, description="平均精度")
    top1_acc: Optional[float] = Field(None, description="Top-1准确率")
    top3_acc: Optional[float] = Field(None, description="Top-3准确率")
    top5_acc: Optional[float] = Field(None, description="Top-5准确率")
    
    # 精确度和召回率
    precision: Optional[float] = Field(None, description="精确度")
    recall: Optional[float] = Field(None, description="召回率")
    
    # 其他信息
    learning_rate: Optional[float] = Field(None, description="当前学习率")
    best_acc: Optional[float] = Field(None, description="最佳准确率")


class DetailedLogEntry(BaseModel):
    """详细日志条目"""
    timestamp: str = Field(..., description="时间戳")
    level: str = Field(..., description="日志级别")
    message: str = Field(..., description="日志消息")
    metrics: Optional[TrainingMetrics] = Field(None, description="训练指标")
    step: Optional[int] = Field(None, description="训练步数")
    stage: Optional[str] = Field(None, description="训练阶段 (epoch_start/training/validation/epoch_end/completed)")


class TrainingStatusResponse(BaseModel):
    """训练状态详细响应"""
    task_id: str
    status: str
    progress: int
    current_epoch: Optional[int] = None
    total_epochs: Optional[int] = None
    latest_metrics: Optional[TrainingMetrics] = None
    device: Optional[str] = None
    created_at: str
    updated_at: str


# ==================== 数据预处理模型 ====================

class DatasetSplitRequest(BaseModel):
    """数据集分割请求"""
    input_path: str = Field(..., description="输入数据集路径")
    output_path: str = Field(..., description="输出数据集路径")
    train_ratio: float = Field(default=0.8, description="训练集比例", ge=0.1, le=0.9)
    val_ratio: Optional[float] = Field(None, description="验证集比例（可选，用于三分割）", ge=0.05, le=0.5)
    task_id: Optional[str] = Field(None, description="任务ID")
    description: Optional[str] = Field(None, description="任务描述")


class DataAugmentationRequest(BaseModel):
    """数据增强请求"""
    dataset_path: str = Field(..., description="数据集路径（应包含train和valid文件夹）")
    output_path: Optional[str] = Field(None, description="输出路径（默认为dataset_aug）")
    methods: Optional[List[str]] = Field(
        default=None,
        description="增强方法列表（可选）：AdvancedBlur, CLAHE, ColorJitter, GaussNoise, ISONoise, Sharpen"
    )
    task_id: Optional[str] = Field(None, description="任务ID")
    description: Optional[str] = Field(None, description="任务描述")


class ImageCropRequest(BaseModel):
    """图像裁剪请求"""
    input_path: str = Field(..., description="输入图像路径")
    output_path: str = Field(..., description="输出路径")
    x: int = Field(..., description="裁剪区域左上角X坐标", ge=0)
    y: int = Field(..., description="裁剪区域左上角Y坐标", ge=0)
    width: int = Field(..., description="裁剪宽度", gt=0)
    height: int = Field(..., description="裁剪高度", gt=0)
    task_id: Optional[str] = Field(None, description="任务ID")
    description: Optional[str] = Field(None, description="任务描述")


class PreprocessingResponse(BaseModel):
    """预处理响应"""
    task_id: str
    task_type: str  # split/augment/crop
    status: str
    message: Optional[str] = None
    progress: int = 0
    input_path: Optional[str] = None
    output_path: Optional[str] = None
    stats: Optional[Dict[str, Any]] = None  # 统计信息
    created_at: str
    updated_at: str

