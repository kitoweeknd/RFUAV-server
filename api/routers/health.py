"""
健康检查和系统信息路由
"""
from fastapi import APIRouter
from datetime import datetime
import logging

from models.schemas import HealthResponse, InfoResponse
from core.config import settings
from core.resource_manager import resource_manager
from services.task_service import TaskService

logger = logging.getLogger(__name__)
router = APIRouter()
task_service = TaskService()


@router.get("/health", response_model=HealthResponse, summary="健康检查")
async def health_check():
    """
    健康检查端点
    
    返回:
    - 服务状态
    - 当前时间
    - 版本信息
    - 任务统计
    - 资源状态
    
    用于监控服务是否正常运行
    """
    try:
        tasks = task_service.get_all_tasks()
        resource_status = resource_manager.get_status()
        
        return HealthResponse(
            status="healthy",
            timestamp=datetime.now().isoformat(),
            version=settings.VERSION,
            training_tasks=tasks.total_training,
            inference_tasks=tasks.total_inference,
            active_log_streams=len(task_service.log_queues),
            resource_status=resource_status
        )
    except Exception as e:
        logger.error(f"健康检查失败: {str(e)}")
        return HealthResponse(
            status="unhealthy",
            timestamp=datetime.now().isoformat(),
            version=settings.VERSION,
            training_tasks=0,
            inference_tasks=0,
            active_log_streams=0,
            resource_status={}
        )


@router.get("/info", response_model=InfoResponse, summary="系统信息")
async def get_system_info():
    """
    获取系统信息
    
    返回:
    - 应用名称和版本
    - 运行环境
    - 支持的模型列表
    - 资源限制配置
    - GPU可用性
    """
    gpu_info = resource_manager.get_gpu_info()
    
    return InfoResponse(
        app_name=settings.APP_NAME,
        version=settings.VERSION,
        environment=settings.ENVIRONMENT,
        supported_models=settings.SUPPORTED_MODELS,
        resource_limits=resource_manager.max_concurrent,
        gpu_available=gpu_info["available"]
    )


