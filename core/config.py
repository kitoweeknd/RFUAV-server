"""
核心配置
"""
from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    """应用配置"""
    
    # 应用信息
    APP_NAME: str = "RFUAV Model Service"
    VERSION: str = "2.3.0"
    DESCRIPTION: str = "无人机信号识别模型训练和推理服务（重构版）"
    ENVIRONMENT: str = "development"
    
    # 服务器配置
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    DEBUG: bool = True
    
    # CORS配置
    CORS_ORIGINS: List[str] = ["*"]
    
    # 资源限制
    MAX_TRAINING_CONCURRENT_GPU: int = 1
    MAX_INFERENCE_CONCURRENT_GPU: int = 3
    MAX_TRAINING_CONCURRENT_CPU: int = 2
    MAX_INFERENCE_CONCURRENT_CPU: int = 4
    
    # 任务配置
    DEFAULT_TRAIN_PRIORITY: int = 5
    DEFAULT_INFERENCE_PRIORITY: int = 3
    TASK_QUEUE_SIZE: int = 100
    
    # 日志配置
    LOG_LEVEL: str = "INFO"
    LOG_FILE: str = "logs/app.log"
    
    # 模型配置
    SUPPORTED_MODELS: List[str] = [
        "resnet18", "resnet34", "resnet50", "resnet101", "resnet152",
        "vit_b_16", "vit_b_32", "vit_l_16", "vit_l_32",
        "swin_v2_t", "swin_v2_s", "swin_v2_b",
        "mobilenet_v3_large", "mobilenet_v3_small"
    ]
    
    # GPU配置
    ENABLE_GPU_SELECTION: bool = True  # 是否启用GPU设备选择
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()

