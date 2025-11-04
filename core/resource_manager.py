import threading
import torch
from collections import defaultdict
from typing import Dict, List, Optional
import logging

from core.config import settings

logger = logging.getLogger(__name__)


class ResourceManager:
    """资源管理器 - 管理GPU/CPU资源分配"""
    
    _instance = None
    _lock = threading.Lock()
    
    def __new__(cls):
        """单例模式"""
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        """初始化资源管理器"""
        if hasattr(self, '_initialized'):
            return
            
        # 检测GPU信息
        self.gpu_available = torch.cuda.is_available()
        self.gpu_count = torch.cuda.device_count() if self.gpu_available else 0
        
        # 为每个GPU设备创建资源追踪
        self.device_usage = defaultdict(lambda: {"training": 0, "inference": 0})
        self.active_tasks = defaultdict(list)
        self.lock = threading.Lock()
        
        # 基础配置
        self.max_concurrent = {
            "cuda": {
                "training": settings.MAX_TRAINING_CONCURRENT_GPU,
                "inference": settings.MAX_INFERENCE_CONCURRENT_GPU
            },
            "cpu": {
                "training": settings.MAX_TRAINING_CONCURRENT_CPU,
                "inference": settings.MAX_INFERENCE_CONCURRENT_CPU
            }
        }
        
        # 为每个GPU设备设置独立的限制
        if self.gpu_count > 1:
            for i in range(self.gpu_count):
                device_name = f"cuda:{i}"
                self.max_concurrent[device_name] = {
                    "training": settings.MAX_TRAINING_CONCURRENT_GPU,
                    "inference": settings.MAX_INFERENCE_CONCURRENT_GPU
                }
        
        self._initialized = True
        logger.info(f"资源管理器初始化完成 - GPU可用: {self.gpu_available}, GPU数量: {self.gpu_count}")
    
    def can_allocate(self, device: str, task_type: str) -> bool:
        """检查是否可以分配资源"""
        with self.lock:
            # 处理通用cuda设备（自动选择）
            if device == "cuda":
                # 如果只有一个GPU，使用cuda:0
                if self.gpu_count == 1:
                    device = "cuda:0"
                # 如果有多个GPU，检查是否有任何一个GPU可用
                elif self.gpu_count > 1:
                    for i in range(self.gpu_count):
                        gpu_device = f"cuda:{i}"
                        current = self.device_usage[gpu_device][task_type]
                        max_allowed = self.max_concurrent.get(gpu_device, self.max_concurrent["cuda"])[task_type]
                        if current < max_allowed:
                            return True
                    return False
            
            # 检查具体设备
            current = self.device_usage[device][task_type]
            if device.startswith("cuda:"):
                # 具体GPU设备
                max_allowed = self.max_concurrent.get(device, self.max_concurrent["cuda"])[task_type]
            else:
                # CPU或通用cuda
                max_allowed = self.max_concurrent[device][task_type]
            return current < max_allowed
    
    def _select_best_gpu(self, task_type: str) -> Optional[str]:
        """自动选择最合适的GPU设备"""
        if not self.gpu_available or self.gpu_count == 0:
            return None
        
        if self.gpu_count == 1:
            return "cuda:0"
        
        # 选择负载最小的GPU
        best_gpu = None
        min_load = float('inf')
        
        for i in range(self.gpu_count):
            gpu_device = f"cuda:{i}"
            current_load = self.device_usage[gpu_device][task_type]
            if current_load < min_load:
                min_load = current_load
                best_gpu = gpu_device
        
        return best_gpu
    
    def allocate(self, device: str, task_type: str, task_id: str) -> str:
        """
        分配资源
        返回实际分配的设备名称（如果是cuda会自动选择具体GPU）
        """
        with self.lock:
            # 如果是通用cuda，自动选择最合适的GPU
            actual_device = device
            if device == "cuda" and self.gpu_count > 0:
                actual_device = self._select_best_gpu(task_type)
                if actual_device is None:
                    actual_device = "cuda:0"  # 回退到第一个GPU
            
            self.device_usage[actual_device][task_type] += 1
            self.active_tasks[actual_device].append({
                "id": task_id,
                "type": task_type
            })
            
            # 获取限制信息
            if actual_device.startswith("cuda:"):
                max_allowed = self.max_concurrent.get(actual_device, self.max_concurrent["cuda"])[task_type]
            else:
                max_allowed = self.max_concurrent[actual_device][task_type]
            
            logger.info(
                f"资源分配: {actual_device} {task_type} (任务: {task_id[:8]}) - "
                f"当前: {self.device_usage[actual_device][task_type]}/{max_allowed}"
            )
            
            return actual_device
    
    def release(self, device: str, task_type: str, task_id: str):
        """释放资源"""
        with self.lock:
            self.device_usage[device][task_type] = max(0, self.device_usage[device][task_type] - 1)
            self.active_tasks[device] = [
                t for t in self.active_tasks[device] if t["id"] != task_id
            ]
            
            # 获取限制信息
            if device.startswith("cuda:"):
                max_allowed = self.max_concurrent.get(device, self.max_concurrent["cuda"])[task_type]
            else:
                max_allowed = self.max_concurrent[device][task_type]
            
            logger.info(
                f"资源释放: {device} {task_type} (任务: {task_id[:8]}) - "
                f"当前: {self.device_usage[device][task_type]}/{max_allowed}"
            )
    
    def get_status(self) -> Dict:
        """获取资源使用状态"""
        with self.lock:
            return {
                "device_usage": dict(self.device_usage),
                "active_tasks": dict(self.active_tasks),
                "limits": self.max_concurrent
            }
    
    def get_gpu_info(self) -> Dict:
        """获取GPU信息"""
        gpu_info = {
            "available": torch.cuda.is_available(),
            "count": 0,
            "devices": [],
            "cuda_version": torch.version.cuda if torch.cuda.is_available() else None,
            "pytorch_version": torch.__version__
        }
        
        if torch.cuda.is_available():
            gpu_info["count"] = torch.cuda.device_count()
            
            for i in range(gpu_info["count"]):
                props = torch.cuda.get_device_properties(i)
                total_memory = props.total_memory / 1024**3
                allocated_memory = torch.cuda.memory_allocated(i) / 1024**3
                cached_memory = torch.cuda.memory_reserved(i) / 1024**3
                
                device_name = f"cuda:{i}"
                
                gpu_info["devices"].append({
                    "id": i,
                    "device_name": device_name,
                    "name": torch.cuda.get_device_name(i),
                    "compute_capability": f"{props.major}.{props.minor}",
                    "total_memory_gb": round(total_memory, 2),
                    "allocated_memory_gb": round(allocated_memory, 2),
                    "cached_memory_gb": round(cached_memory, 2),
                    "free_memory_gb": round(total_memory - allocated_memory, 2),
                    "utilization": round((allocated_memory / total_memory * 100) if total_memory > 0 else 0, 1),
                    "current_tasks": {
                        "training": self.device_usage[device_name]["training"],
                        "inference": self.device_usage[device_name]["inference"]
                    }
                })
        
        return gpu_info
    
    def print_gpu_info(self):
        """打印GPU信息到控制台"""
        gpu_info = self.get_gpu_info()
        
        print("\n" + "="*70)
        print("🚀 GPU硬件信息")
        print("="*70)
        
        if not gpu_info["available"]:
            print("❌ GPU不可用，将使用CPU进行计算")
            return
        
        print(f"✅ GPU可用")
        print(f"📦 CUDA版本: {gpu_info['cuda_version']}")
        print(f"🔧 PyTorch版本: {gpu_info['pytorch_version']}")
        print(f"🎯 检测到 {gpu_info['count']} 个GPU设备:")
        print()
        
        for device in gpu_info["devices"]:
            print(f"  GPU {device['id']} ({device['device_name']})")
            print(f"  ├─ 型号: {device['name']}")
            print(f"  ├─ Compute Capability: {device['compute_capability']}")
            print(f"  ├─ 总显存: {device['total_memory_gb']:.2f} GB")
            print(f"  ├─ 已用显存: {device['allocated_memory_gb']:.2f} GB ({device['utilization']:.1f}%)")
            print(f"  ├─ 空闲显存: {device['free_memory_gb']:.2f} GB")
            print(f"  └─ 当前任务: 训练={device['current_tasks']['training']}, 推理={device['current_tasks']['inference']}")
            print()
        
        print("="*70)
        print()
    
    def update_limits(self, config: Dict):
        """更新资源限制"""
        with self.lock:
            if "max_concurrent" in config:
                self.max_concurrent.update(config["max_concurrent"])
            logger.info(f"资源限制已更新: {self.max_concurrent}")


# 全局资源管理器实例
resource_manager = ResourceManager()

