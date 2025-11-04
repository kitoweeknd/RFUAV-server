from fastapi import APIRouter, HTTPException, BackgroundTasks
import logging

from models.schemas import TrainingRequest, TaskResponse, TaskActionResponse
from services import get_training_service

logger = logging.getLogger(__name__)
router = APIRouter()
training_service = get_training_service()

@router.post("/start", response_model=TaskResponse, summary="启动训练任务")
async def start_training(
    request: TrainingRequest,
    background_tasks: BackgroundTasks
):
    """
    启动模型训练任务
    
    - **model**: 模型名称 (resnet18, resnet50, vit_b_16, etc.)
    - **num_classes**: 分类类别数
    - **train_path**: 训练集路径
    - **val_path**: 验证集路径  
    - **device**: 设备选择 (cuda/cpu)
    - **priority**: 优先级 (1-10, 数字越小优先级越高)
    
    返回任务信息，可通过task_id查询状态和日志
    """
    try:
        task_id = await training_service.start_training(request, background_tasks)
        return training_service.get_task(task_id)
    except Exception as e:
        logger.error(f"启动训练任务失败: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{task_id}", response_model=TaskResponse, summary="获取训练任务状态（含详细指标）")
async def get_training_status(task_id: str):
    """
    获取训练任务状态（包含详细的训练指标）
    
    返回任务的当前状态、进度、设备、以及最新的训练指标，包括：
    - current_epoch: 当前训练轮次
    - total_epochs: 总训练轮次
    - latest_metrics: 最新的训练指标
      - epoch: 当前epoch
      - train_loss: 训练损失
      - train_acc: 训练准确率
      - val_loss: 验证损失
      - val_acc: 验证准确率
      - macro_f1: Macro F1分数
      - micro_f1: Micro F1分数
      - macro_precision: Macro精确度
      - macro_recall: Macro召回率
      - micro_precision: Micro精确度
      - micro_recall: Micro召回率
      - mAP: 平均精度
      - top1_acc, top3_acc, top5_acc: Top-k准确率
      - learning_rate: 当前学习率
      - best_acc: 最佳准确率
    """
    task = training_service.get_task(task_id)
    if not task:
        raise HTTPException(status_code=404, detail=f"任务 {task_id} 不存在")
    return task


@router.get("/{task_id}/logs", summary="获取训练日志流（含详细指标）")
async def get_training_logs(task_id: str):
    """
    获取训练任务的实时日志流 (Server-Sent Events)
    
    使用EventSource连接此端点以接收实时日志，每条日志包含：
    - timestamp: 时间戳
    - level: 日志级别
    - message: 日志消息
    - metrics: 训练指标（如果有）
    - step: 训练步数（如果有）
    - stage: 训练阶段（epoch_start/training/validation/epoch_end/completed）
    
    使用示例：
    ```javascript
    const eventSource = new EventSource('/api/v2/training/{task_id}/logs');
    eventSource.onmessage = (event) => {
        const logEntry = JSON.parse(event.data);
        console.log(logEntry);
        if (logEntry.metrics) {
            console.log('训练指标:', logEntry.metrics);
        }
    };
    ```
    """
    task = training_service.get_task(task_id)
    if not task:
        raise HTTPException(status_code=404, detail=f"任务 {task_id} 不存在")
    
    return training_service.stream_logs(task_id)


@router.post("/{task_id}/stop", response_model=TaskActionResponse, summary="停止训练任务")
async def stop_training(task_id: str):
    """
    停止正在运行的训练任务
    
    将任务标记为已取消
    """
    result = training_service.stop_task(task_id)
    if not result:
        raise HTTPException(status_code=404, detail=f"任务 {task_id} 不存在")
    
    return TaskActionResponse(
        status="success",
        message="训练任务已停止",
        task_id=task_id
    )

