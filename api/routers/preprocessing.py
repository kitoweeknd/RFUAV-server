"""
数据预处理路由
"""
from fastapi import APIRouter, HTTPException, BackgroundTasks
import logging

from models.schemas import (
    DatasetSplitRequest,
    DataAugmentationRequest,
    ImageCropRequest,
    PreprocessingResponse,
    TaskActionResponse
)
from services.preprocessing_service import PreprocessingService

logger = logging.getLogger(__name__)
router = APIRouter()
preprocessing_service = PreprocessingService()


@router.post("/split", response_model=PreprocessingResponse, summary="数据集分割")
async def split_dataset(
    request: DatasetSplitRequest,
    background_tasks: BackgroundTasks
):
    """
    将数据集按比例分割为训练集、验证集（和测试集）
    
    - **input_path**: 输入数据集路径（应包含按类别组织的图像）
    - **output_path**: 输出路径
    - **train_ratio**: 训练集比例（0.1-0.9）
    - **val_ratio**: 验证集比例（可选，用于三分割）
    
    数据集结构示例：
    ```
    input_path/
        ├── class1/
        │   ├── img1.jpg
        │   └── img2.jpg
        └── class2/
            ├── img1.jpg
            └── img2.jpg
    ```
    
    输出结构：
    ```
    output_path/
        ├── train/
        │   ├── class1/
        │   └── class2/
        └── valid/
            ├── class1/
            └── class2/
    ```
    """
    try:
        task_id = await preprocessing_service.split_dataset(request, background_tasks)
        task = preprocessing_service.get_task(task_id)
        return PreprocessingResponse(**task)
    except Exception as e:
        logger.error(f"启动数据集分割任务失败: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/augment", response_model=PreprocessingResponse, summary="数据增强")
async def augment_dataset(
    request: DataAugmentationRequest,
    background_tasks: BackgroundTasks
):
    """
    对数据集进行数据增强
    
    - **dataset_path**: 数据集路径（应包含train和valid文件夹）
    - **output_path**: 输出路径（默认为dataset_aug）
    - **methods**: 增强方法列表（可选）
    
    支持的增强方法：
    - **AdvancedBlur**: 高级模糊
    - **CLAHE**: 对比度受限自适应直方图均衡化
    - **ColorJitter**: 颜色抖动
    - **GaussNoise**: 高斯噪声
    - **ISONoise**: ISO噪声
    - **Sharpen**: 锐化
    
    如果不指定methods，将使用所有默认方法。
    
    数据集结构示例：
    ```
    dataset_path/
        ├── train/
        │   ├── class1/
        │   └── class2/
        └── valid/
            ├── class1/
            └── class2/
    ```
    """
    try:
        task_id = await preprocessing_service.augment_dataset(request, background_tasks)
        task = preprocessing_service.get_task(task_id)
        return PreprocessingResponse(**task)
    except Exception as e:
        logger.error(f"启动数据增强任务失败: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/crop", response_model=PreprocessingResponse, summary="图像裁剪")
async def crop_images(
    request: ImageCropRequest,
    background_tasks: BackgroundTasks
):
    """
    裁剪图像的指定区域
    
    - **input_path**: 输入路径（文件或目录）
    - **output_path**: 输出路径
    - **x**: 裁剪区域左上角X坐标
    - **y**: 裁剪区域左上角Y坐标
    - **width**: 裁剪宽度
    - **height**: 裁剪高度
    
    如果input_path是目录，将递归处理所有图像并保持目录结构。
    """
    try:
        task_id = await preprocessing_service.crop_images(request, background_tasks)
        task = preprocessing_service.get_task(task_id)
        return PreprocessingResponse(**task)
    except Exception as e:
        logger.error(f"启动图像裁剪任务失败: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{task_id}", response_model=PreprocessingResponse, summary="获取预处理任务状态")
async def get_preprocessing_status(task_id: str):
    """
    获取预处理任务的状态和统计信息
    
    返回任务的当前状态、进度、统计信息等
    """
    task = preprocessing_service.get_task(task_id)
    if not task:
        raise HTTPException(status_code=404, detail=f"任务 {task_id} 不存在")
    return PreprocessingResponse(**task)


@router.get("/{task_id}/logs", summary="获取预处理任务日志流")
async def get_preprocessing_logs(task_id: str):
    """
    获取预处理任务的实时日志流 (Server-Sent Events)
    
    使用EventSource连接此端点以接收实时日志
    """
    task = preprocessing_service.get_task(task_id)
    if not task:
        raise HTTPException(status_code=404, detail=f"任务 {task_id} 不存在")
    
    return preprocessing_service.stream_logs(task_id)


@router.post("/{task_id}/cancel", response_model=TaskActionResponse, summary="取消预处理任务")
async def cancel_preprocessing(task_id: str):
    """
    取消正在运行的预处理任务
    
    注意：由于预处理任务在后台线程中运行，取消操作只会标记任务为已取消，
    实际的处理可能需要等待当前操作完成。
    """
    task = preprocessing_service.get_task(task_id)
    if not task:
        raise HTTPException(status_code=404, detail=f"任务 {task_id} 不存在")
    
    if task["status"] in ["pending", "queued", "running"]:
        preprocessing_service.update_task_status(task_id, "cancelled", "任务已取消", task.get("progress", 0))
        preprocessing_service.add_log(task_id, "WARNING", "任务已被用户取消")
        return TaskActionResponse(
            status="success",
            message="预处理任务已取消",
            task_id=task_id
        )
    else:
        raise HTTPException(status_code=400, detail=f"任务状态为 {task['status']}，无法取消")

