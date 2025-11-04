from fastapi import APIRouter, HTTPException
import logging
import psutil

from models.schemas import ResourceStatusResponse, ResourceConfigUpdate, ConfigUpdateResponse
from core.resource_manager import resource_manager

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("", response_model=ResourceStatusResponse, summary="获取资源状态")
async def get_resource_status():
    """
    获取当前资源使用状态
    
    返回:
    - 各设备使用情况 (训练/推理任务数)
    - 活动任务列表
    - 资源限制配置
    - GPU详细信息 (显存使用等)
    
    用于监控资源使用和判断是否有资源执行新任务
    """
    try:
        status = resource_manager.get_status()
        gpu_info = resource_manager.get_gpu_info()
        
        return ResourceStatusResponse(
            device_usage=status["device_usage"],
            active_tasks=status["active_tasks"],
            limits=status["limits"],
            gpu_info=gpu_info
        )
    except Exception as e:
        logger.error(f"获取资源状态失败: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/gpu", summary="获取GPU信息")
async def get_gpu_info():
    """
    获取详细的GPU信息
    
    返回:
    - GPU可用性
    - GPU数量
    - 每个GPU的名称、显存等信息
    """
    try:
        return resource_manager.get_gpu_info()
    except Exception as e:
        logger.error(f"获取GPU信息失败: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/config", response_model=ConfigUpdateResponse, summary="更新资源配置")
async def update_resource_config(config: ResourceConfigUpdate):
    """
    动态更新资源配置
    
    可以调整各设备的最大并发任务数，无需重启服务
    
    示例:
    ```json
    {
        "max_concurrent": {
            "cuda": {
                "training": 1,
                "inference": 5
            }
        }
    }
    ```
    """
    try:
        resource_manager.update_limits(config.dict(exclude_none=True))
        return ConfigUpdateResponse(
            status="success",
            message="资源配置已更新",
            current_config=resource_manager.max_concurrent
        )
    except Exception as e:
        logger.error(f"更新资源配置失败: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/cpu", summary="获取CPU使用信息")
async def get_cpu_info():
    """
    获取CPU关键指标:
    - percent: CPU总体使用率%
    - per_cpu_percent: 各核使用率%
    - cores: 逻辑核数
    - physical_cores: 物理核数
    - freq_mhz: 当前频率MHz
    - load_avg: 1/5/15分钟平均负载（若平台支持）
    - memory_percent: 内存使用率%
    """
    try:
        percent = psutil.cpu_percent(interval=0.1)
        per_cpu_percent = psutil.cpu_percent(interval=0.0, percpu=True)
        freq = psutil.cpu_freq()
        cores = psutil.cpu_count(logical=True) or 0
        physical_cores = psutil.cpu_count(logical=False) or cores
        mem = psutil.virtual_memory()

        load_avg = None
        try:
            load1, load5, load15 = psutil.getloadavg()
            load_avg = {"1": load1, "5": load5, "15": load15}
        except (AttributeError, OSError):
            load_avg = None

        return {
            "percent": percent,
            "per_cpu_percent": per_cpu_percent,
            "cores": cores,
            "physical_cores": physical_cores,
            "freq_mhz": freq.current if freq else None,
            "load_avg": load_avg,
            "memory_percent": mem.percent,
        }
    except Exception as e:
        logger.error(f"获取CPU信息失败: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
