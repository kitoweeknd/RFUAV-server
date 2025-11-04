import logging
import os
import traceback
import shutil
import random
from fastapi import BackgroundTasks
from typing import List, Optional
import albumentations as A
import cv2

from services.base_service import BaseService
from models.schemas import (
    DatasetSplitRequest,
    DataAugmentationRequest,
    ImageCropRequest
)

logger = logging.getLogger(__name__)


class PreprocessingService(BaseService):
    
    def __init__(self):
        super().__init__()
    
    async def split_dataset(
        self,
        request: DatasetSplitRequest,
        background_tasks: BackgroundTasks
    ) -> str:
        task_id = self.generate_task_id(request.task_id)
        
        if not os.path.exists(request.input_path):
            raise FileNotFoundError(f"输入路径不存在: {request.input_path}")
        
        self.update_task_status(
            task_id,
            "pending",
            "等待开始",
            0,
            task_type="dataset_split",
            input_path=request.input_path,
            output_path=request.output_path,
            train_ratio=request.train_ratio,
            val_ratio=request.val_ratio
        )
        
        # 在后台执行分割
        background_tasks.add_task(self._split_worker, task_id, request)
        
        logger.info(f"数据集分割任务已创建: {task_id}")
        return task_id
    
    def _split_worker(self, task_id: str, request: DatasetSplitRequest):
        try:
            # 创建日志队列
            self.create_log_queue(task_id)
            
            self.update_task_status(task_id, "running", "正在分割数据集...", 0)
            self.add_log(task_id, "INFO", f"开始分割数据集: {request.input_path}")
            
            if not os.path.exists(request.output_path):
                os.makedirs(request.output_path)
                self.add_log(task_id, "INFO", f"创建输出目录: {request.output_path}")

            stats = {
                "total_images": 0,
                "train_images": 0,
                "val_images": 0,
                "test_images": 0,
                "classes": []
            }
            
            classes = [d for d in os.listdir(request.input_path) 
                      if os.path.isdir(os.path.join(request.input_path, d))]
            stats["classes"] = classes
            
            self.add_log(task_id, "INFO", f"检测到 {len(classes)} 个类别")
            
            for idx, drone_type in enumerate(classes):
                train_path = os.path.join(os.path.join(request.output_path, 'train'), drone_type)
                val_path = os.path.join(os.path.join(request.output_path, 'valid'), drone_type)
                
                os.makedirs(train_path, exist_ok=True)
                os.makedirs(val_path, exist_ok=True)
                
                # 如果需要test集，这个接口不用但先保留
                if request.val_ratio:
                    test_path = os.path.join(os.path.join(request.output_path, 'test'), drone_type)
                    os.makedirs(test_path, exist_ok=True)
                
                # 获取图像文件
                class_path = os.path.join(request.input_path, drone_type)
                image_files = [f for f in os.listdir(class_path) 
                             if f.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp'))]
                
                # 打乱
                random.shuffle(image_files)
                
                # 计算分割点
                total = len(image_files)
                stats["total_images"] += total
                
                # 不用，但先保留
                if request.val_ratio:
                    num_train = int(total * request.train_ratio)
                    num_val = int(total * request.val_ratio)
                    
                    train_files = image_files[:num_train]
                    val_files = image_files[num_train:num_train+num_val]
                    test_files = image_files[num_train+num_val:]
                    
                    stats["train_images"] += len(train_files)
                    stats["val_images"] += len(val_files)
                    stats["test_images"] += len(test_files)
                    
                    # 复制文件
                    for img in train_files:
                        shutil.copy(
                            os.path.join(class_path, img),
                            os.path.join(train_path, img)
                        )
                    
                    for img in val_files:
                        shutil.copy(
                            os.path.join(class_path, img),
                            os.path.join(val_path, img)
                        )
                    
                    for img in test_files:
                        shutil.copy(
                            os.path.join(class_path, img),
                            os.path.join(test_path, img)
                        )
                    
                    self.add_log(
                        task_id, "INFO",
                        f"{drone_type}: {len(train_files)} train, {len(val_files)} val, {len(test_files)} test"
                    )
                else:
                    num_train = int(total * request.train_ratio)
                    
                    train_files = image_files[:num_train]
                    val_files = image_files[num_train:]
                    
                    stats["train_images"] += len(train_files)
                    stats["val_images"] += len(val_files)
                    
                    for img in train_files:
                        shutil.copy(
                            os.path.join(class_path, img),
                            os.path.join(train_path, img)
                        )
                    
                    for img in val_files:
                        shutil.copy(
                            os.path.join(class_path, img),
                            os.path.join(val_path, img)
                        )
                    
                    self.add_log(
                        task_id, "INFO",
                        f"{drone_type}: {len(train_files)} train, {len(val_files)} val"
                    )
                
                progress = int(((idx + 1) / len(classes)) * 100)
                self.update_task_status(task_id, "running", f"处理中 ({idx+1}/{len(classes)})", progress)
            
            self.update_task_status(task_id, "completed", "数据集分割完成", 100, stats=stats)
            self.add_log(task_id, "INFO", f"分割完成！总计 {stats['total_images']} 张图像")
            self.add_log(task_id, "INFO", f"训练集: {stats['train_images']}, 验证集: {stats['val_images']}")
            if stats["test_images"] > 0:
                self.add_log(task_id, "INFO", f"测试集: {stats['test_images']}")
            
            logger.info(f"任务 {task_id} 数据集分割完成")
            
        except Exception as e:
            error_msg = f"分割失败: {str(e)}"
            logger.error(f"任务 {task_id} 失败: {error_msg}\n{traceback.format_exc()}")
            self.update_task_status(task_id, "failed", error_msg, 0)
            self.add_log(task_id, "ERROR", error_msg)
    
    async def augment_dataset(
        self,
        request: DataAugmentationRequest,
        background_tasks: BackgroundTasks
    ) -> str:
        task_id = self.generate_task_id(request.task_id)
        
        if not os.path.exists(request.dataset_path):
            raise FileNotFoundError(f"数据集路径不存在: {request.dataset_path}")
        
        self.update_task_status(
            task_id,
            "pending",
            "等待开始",
            0,
            task_type="data_augmentation",
            input_path=request.dataset_path,
            output_path=request.output_path,
            methods=request.methods
        )
        
        background_tasks.add_task(self._augment_worker, task_id, request)
        
        logger.info(f"数据增强任务已创建: {task_id}")
        return task_id
    
    def _augment_worker(self, task_id: str, request: DataAugmentationRequest):
        try:
            # 创建日志队列
            self.create_log_queue(task_id)
            
            self.update_task_status(task_id, "running", "正在进行数据增强...", 0)
            self.add_log(task_id, "INFO", f"开始数据增强: {request.dataset_path}")
            
            # 确定输出路径
            if not request.output_path:
                prefix = os.path.dirname(os.path.dirname(request.dataset_path))
                output_path = os.path.join(prefix, 'dataset_aug')
            else:
                output_path = request.output_path
            
            if not os.path.exists(output_path):
                os.makedirs(output_path)
                self.add_log(task_id, "INFO", f"创建输出目录: {output_path}")
            
            # 准备增强方法
            if request.methods is None or len(request.methods) == 0:
                # 使用默认方法
                methods = self._get_default_augmentation_methods()
                self.add_log(task_id, "INFO", "使用默认增强方法（6种）")
            else:
                methods = self._get_augmentation_methods(request.methods)
                self.add_log(task_id, "INFO", f"使用指定增强方法: {', '.join(request.methods)}")
            
            # 统计信息
            stats = {
                "original_images": 0,
                "augmented_images": 0,
                "methods_used": len(methods),
                "classes": []
            }
            
            # 处理train和valid文件夹
            total_paths = []
            for subset in ['train', 'valid']:
                subset_path = os.path.join(request.dataset_path, subset)
                if os.path.exists(subset_path):
                    total_paths.append(subset_path)
            
            if len(total_paths) == 0:
                raise FileNotFoundError("未找到train或valid文件夹")
            
            self.add_log(task_id, "INFO", f"找到 {len(total_paths)} 个数据子集")
            
            total_progress = 0
            for path_idx, path in enumerate(total_paths):
                # 创建输出子目录
                subset_name = os.path.basename(path)
                output_subset = os.path.join(output_path, subset_name)
                if not os.path.exists(output_subset):
                    os.makedirs(output_subset)
                
                # 获取所有类别
                classes = [d for d in os.listdir(path) 
                          if os.path.isdir(os.path.join(path, d))]
                
                if path_idx == 0:
                    stats["classes"] = classes
                
                self.add_log(task_id, "INFO", f"{subset_name}: {len(classes)} 个类别")
                
                for class_idx, _class in enumerate(classes):
                    # 创建类别输出目录
                    _save_path = os.path.join(output_subset, _class)
                    if not os.path.exists(_save_path):
                        os.makedirs(_save_path)
                    
                    # 获取图像
                    class_path = os.path.join(path, _class)
                    images = [f for f in os.listdir(class_path) 
                             if f.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp'))]
                    
                    stats["original_images"] += len(images)
                    
                    # 对每种方法进行增强
                    for method_idx, method in enumerate(methods):
                        for img_name in images:
                            try:
                                # 读取原图
                                img_path = os.path.join(class_path, img_name)
                                original_image = cv2.imread(img_path)
                                
                                if original_image is None:
                                    self.add_log(task_id, "WARNING", f"无法读取图像: {img_name}")
                                    continue
                                
                                # 应用增强
                                transform = A.Compose([method])
                                augmented = transform(image=original_image)
                                
                                # 保存增强后的图像
                                base_name = os.path.splitext(img_name)[0]
                                ext = os.path.splitext(img_name)[1]
                                aug_name = f"{base_name}_AugM{method_idx}{ext}"
                                cv2.imwrite(os.path.join(_save_path, aug_name), augmented['image'])
                                
                                # 同时保存原图
                                orig_name = f"{base_name}_origin{ext}"
                                cv2.imwrite(os.path.join(_save_path, orig_name), original_image)
                                
                                stats["augmented_images"] += 1
                                
                            except Exception as e:
                                self.add_log(task_id, "ERROR", f"增强失败 {img_name}: {str(e)}")
                    
                    self.add_log(task_id, "INFO", f"完成增强: {_class} ({len(images)} 张)")
                    
                    # 更新进度
                    total_classes = sum(len([d for d in os.listdir(p) 
                                           if os.path.isdir(os.path.join(p, d))]) 
                                       for p in total_paths)
                    total_progress += 1
                    progress = int((total_progress / total_classes) * 100)
                    self.update_task_status(
                        task_id, "running",
                        f"处理中 ({total_progress}/{total_classes})",
                        progress
                    )
            
            # 完成
            self.update_task_status(task_id, "completed", "数据增强完成", 100, stats=stats)
            self.add_log(task_id, "INFO", f"增强完成！")
            self.add_log(task_id, "INFO", f"原始图像: {stats['original_images']}")
            self.add_log(task_id, "INFO", f"增强图像: {stats['augmented_images']}")
            self.add_log(task_id, "INFO", f"输出路径: {output_path}")
            
            logger.info(f"任务 {task_id} 数据增强完成")
            
        except Exception as e:
            error_msg = f"增强失败: {str(e)}"
            logger.error(f"任务 {task_id} 失败: {error_msg}\n{traceback.format_exc()}")
            self.update_task_status(task_id, "failed", error_msg, 0)
            self.add_log(task_id, "ERROR", error_msg)
    
    async def crop_images(
        self,
        request: ImageCropRequest,
        background_tasks: BackgroundTasks
    ) -> str:
        task_id = self.generate_task_id(request.task_id)
        
        if not os.path.exists(request.input_path):
            raise FileNotFoundError(f"输入路径不存在: {request.input_path}")
        
        self.update_task_status(
            task_id,
            "pending",
            "等待开始",
            0,
            task_type="image_crop",
            input_path=request.input_path,
            output_path=request.output_path,
            crop_params={"x": request.x, "y": request.y, "width": request.width, "height": request.height}
        )
        
        background_tasks.add_task(self._crop_worker, task_id, request)
        
        logger.info(f"图像裁剪任务已创建: {task_id}")
        return task_id
    
    def _crop_worker(self, task_id: str, request: ImageCropRequest):
        try:
            self.create_log_queue(task_id)
            
            self.update_task_status(task_id, "running", "正在裁剪图像...", 0)
            self.add_log(task_id, "INFO", f"开始裁剪: {request.input_path}")
            self.add_log(task_id, "INFO", f"裁剪区域: ({request.x}, {request.y}, {request.width}, {request.height})")
            
            if not os.path.exists(request.output_path):
                os.makedirs(request.output_path)
            
            stats = {"total_images": 0, "success": 0, "failed": 0}
            
            if os.path.isfile(request.input_path):
                try:
                    img = cv2.imread(request.input_path)
                    if img is None:
                        raise ValueError("无法读取图像")
                    
                    cropped = img[request.y:request.y+request.height, 
                                 request.x:request.x+request.width]
                    
                    output_file = os.path.join(request.output_path, os.path.basename(request.input_path))
                    cv2.imwrite(output_file, cropped)
                    
                    stats["total_images"] = 1
                    stats["success"] = 1
                    self.add_log(task_id, "INFO", f"裁剪完成: {os.path.basename(request.input_path)}")
                except Exception as e:
                    stats["failed"] = 1
                    self.add_log(task_id, "ERROR", f"裁剪失败: {str(e)}")
            
            else:
                for root, dirs, files in os.walk(request.input_path):
                    for file in files:
                        if file.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp')):
                            try:
                                input_file = os.path.join(root, file)
                                
                                rel_path = os.path.relpath(root, request.input_path)
                                output_dir = os.path.join(request.output_path, rel_path)
                                if not os.path.exists(output_dir):
                                    os.makedirs(output_dir)
                                
                                img = cv2.imread(input_file)
                                if img is None:
                                    stats["failed"] += 1
                                    continue
                                
                                cropped = img[request.y:request.y+request.height, 
                                            request.x:request.x+request.width]
                                
                                output_file = os.path.join(output_dir, file)
                                cv2.imwrite(output_file, cropped)
                                
                                stats["total_images"] += 1
                                stats["success"] += 1
                                
                                if stats["total_images"] % 10 == 0:
                                    self.add_log(task_id, "INFO", f"已处理 {stats['total_images']} 张图像")
                                
                            except Exception as e:
                                stats["failed"] += 1
                                self.add_log(task_id, "ERROR", f"处理失败 {file}: {str(e)}")
            
            # 完成
            self.update_task_status(task_id, "completed", "裁剪完成", 100, stats=stats)
            self.add_log(task_id, "INFO", f"裁剪完成！")
            self.add_log(task_id, "INFO", f"总计: {stats['total_images']}, 成功: {stats['success']}, 失败: {stats['failed']}")
            
            logger.info(f"任务 {task_id} 图像裁剪完成")
            
        except Exception as e:
            error_msg = f"裁剪失败: {str(e)}"
            logger.error(f"任务 {task_id} 失败: {error_msg}\n{traceback.format_exc()}")
            self.update_task_status(task_id, "failed", error_msg, 0)
            self.add_log(task_id, "ERROR", error_msg)
    
    def _get_default_augmentation_methods(self) -> List:
        return [
            A.AdvancedBlur(
                blur_limit=(7, 13),
                sigma_x_limit=(7, 13),
                sigma_y_limit=(7, 13),
                rotate_limit=(-90, 90),
                beta_limit=(0.5, 8),
                noise_limit=(2, 10),
                p=1),
            A.CLAHE(
                clip_limit=3,
                tile_grid_size=(13, 13),
                p=1),
            A.ColorJitter(
                brightness=(0.5, 1.5),
                contrast=(1, 1),
                saturation=(1, 1),
                hue=(-0, 0),
                p=1),
            A.GaussNoise(
                var_limit=(100, 500),
                mean=0,
                p=1),
            A.ISONoise(
                intensity=(0.2, 0.5),
                color_shift=(0.01, 0.05),
                p=1),
            A.Sharpen(
                alpha=(0.2, 0.5),
                lightness=(0.5, 1),
                p=1)
        ]
    
    def _get_augmentation_methods(self, method_names: List[str]) -> List:
        methods = []
        method_map = {
            "AdvancedBlur": A.AdvancedBlur(
                blur_limit=(7, 13), sigma_x_limit=(7, 13), sigma_y_limit=(7, 13),
                rotate_limit=(-90, 90), beta_limit=(0.5, 8), noise_limit=(2, 10), p=1),
            "CLAHE": A.CLAHE(clip_limit=3, tile_grid_size=(13, 13), p=1),
            "ColorJitter": A.ColorJitter(brightness=(0.5, 1.5), contrast=(1, 1), 
                                        saturation=(1, 1), hue=(-0, 0), p=1),
            "GaussNoise": A.GaussNoise(var_limit=(100, 500), mean=0, p=1),
            "ISONoise": A.ISONoise(intensity=(0.2, 0.5), color_shift=(0.01, 0.05), p=1),
            "Sharpen": A.Sharpen(alpha=(0.2, 0.5), lightness=(0.5, 1), p=1)
        }
        
        for name in method_names:
            if name in method_map:
                methods.append(method_map[name])
            else:
                logger.warning(f"未知的增强方法: {name}")
        
        return methods if methods else self._get_default_augmentation_methods()

