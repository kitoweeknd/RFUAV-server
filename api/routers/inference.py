from fastapi import APIRouter, HTTPException, BackgroundTasks
import logging

from models.schemas import (
    InferenceRequest, 
    BatchInferenceRequest, 
    TaskResponse,
    BatchInferenceResponse
)
from services import get_inference_service

logger = logging.getLogger(__name__)
router = APIRouter()
inference_service = get_inference_service()


@router.post("/start", response_model=TaskResponse, summary="启动推理任务")
async def start_inference(
    request: InferenceRequest,
    background_tasks: BackgroundTasks
):
    """
    启动模型推理任务
    
    - **cfg_path**: 配置文件路径
    - **weight_path**: 模型权重路径
    - **source_path**: 待推理数据路径
    - **device**: 推理设备 (cuda/cpu)
    - **priority**: 优先级 (推理默认3，高于训练)
    
    推理任务通常比训练任务优先级更高，执行更快
    """
    try:
        task_id = await inference_service.start_inference(request, background_tasks)
        return inference_service.get_task(task_id)
    except Exception as e:
        logger.error(f"启动推理任务失败: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/batch", response_model=BatchInferenceResponse, summary="批量推理")
async def batch_inference(
    request: BatchInferenceRequest,
    background_tasks: BackgroundTasks
):
    """
    批量推理任务
    
    同时对多个数据集进行推理，系统会自动调度和排队
    
    返回所有启动的任务ID列表
    """
    try:
        task_ids = await inference_service.start_batch_inference(request, background_tasks)
        return BatchInferenceResponse(
            status="success",
            message=f"已启动 {len(task_ids)} 个推理任务",
            task_ids=task_ids,
            total=len(task_ids)
        )
    except Exception as e:
        logger.error(f"启动批量推理失败: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{task_id}", response_model=TaskResponse, summary="获取推理任务状态")
async def get_inference_status(task_id: str):
    """
    获取推理任务状态
    """
    task = inference_service.get_task(task_id)
    if not task:
        raise HTTPException(status_code=404, detail=f"任务 {task_id} 不存在")
    return task

