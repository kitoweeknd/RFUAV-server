from fastapi import APIRouter, HTTPException
import logging

from models.schemas import TaskListResponse, TaskResponse, TaskActionResponse
from services import get_task_service

logger = logging.getLogger(__name__)
router = APIRouter()
task_service = get_task_service()


@router.get("", response_model=TaskListResponse, summary="获取所有任务")
async def get_all_tasks(
    status: str = None,
    task_type: str = None,
    limit: int = 100
):
    """
    获取所有任务列表
    
    - **status**: 过滤状态 (pending, running, completed, failed)
    - **task_type**: 过滤类型 (training, inference)
    - **limit**: 返回数量限制
    
    返回训练和推理任务的完整列表及统计信息
    """
    try:
        return task_service.get_all_tasks(status, task_type, limit)
    except Exception as e:
        logger.error(f"获取任务列表失败: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{task_id}", response_model=TaskResponse, summary="获取任务详情")
async def get_task(task_id: str):
    """
    获取特定任务的详细信息
    
    包括状态、进度、设备、优先级等
    """
    task = task_service.get_task(task_id)
    if not task:
        raise HTTPException(status_code=404, detail=f"任务 {task_id} 不存在")
    return task


@router.get("/{task_id}/logs", summary="获取任务日志流")
async def get_task_logs(task_id: str):
    """
    获取任务的实时日志流
    
    支持训练和推理任务的日志流式传输
    """
    task = task_service.get_task(task_id)
    if not task:
        raise HTTPException(status_code=404, detail=f"任务 {task_id} 不存在")
    
    return task_service.stream_logs(task_id)


@router.post("/{task_id}/cancel", response_model=TaskActionResponse, summary="取消任务")
async def cancel_task(task_id: str):
    """
    取消正在运行或排队的任务
    
    已完成的任务无法取消
    """
    result = task_service.cancel_task(task_id)
    if not result:
        raise HTTPException(status_code=404, detail=f"任务 {task_id} 不存在或无法取消")
    
    return TaskActionResponse(
        status="success",
        message="任务已取消",
        task_id=task_id
    )


@router.delete("/{task_id}", response_model=TaskActionResponse, summary="删除任务记录")
async def delete_task(task_id: str):
    """
    删除任务记录
    
    只能删除已完成或已失败的任务
    """
    result = task_service.delete_task(task_id)
    if not result:
        raise HTTPException(status_code=404, detail=f"任务 {task_id} 不存在或无法删除")
    
    return TaskActionResponse(
        status="success",
        message="任务记录已删除",
        task_id=task_id
    )

