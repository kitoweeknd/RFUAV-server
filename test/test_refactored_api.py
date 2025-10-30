"""
重构版API测试客户端
"""
import requests
import time
import json
from typing import Dict, Optional


class RFUAVClient:
    """RFUAV服务客户端"""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
    
    # ==================== 训练接口 ====================
    
    def start_training(
        self,
        model: str,
        num_classes: int,
        train_path: str,
        val_path: str,
        save_path: str,
        batch_size: int = 16,
        num_epochs: int = 50,
        learning_rate: float = 0.0001,
        device: str = "cuda",
        priority: int = 5,
        **kwargs
    ) -> Dict:
        """启动训练任务"""
        url = f"{self.base_url}/api/v2/training/start"
        data = {
            "model": model,
            "num_classes": num_classes,
            "train_path": train_path,
            "val_path": val_path,
            "save_path": save_path,
            "batch_size": batch_size,
            "num_epochs": num_epochs,
            "learning_rate": learning_rate,
            "device": device,
            "priority": priority,
            **kwargs
        }
        response = requests.post(url, json=data)
        response.raise_for_status()
        return response.json()
    
    def get_training_status(self, task_id: str) -> Dict:
        """获取训练任务状态"""
        url = f"{self.base_url}/api/v2/training/{task_id}"
        response = requests.get(url)
        response.raise_for_status()
        return response.json()
    
    def stop_training(self, task_id: str) -> Dict:
        """停止训练任务"""
        url = f"{self.base_url}/api/v2/training/{task_id}/stop"
        response = requests.post(url)
        response.raise_for_status()
        return response.json()
    
    def stream_training_logs(self, task_id: str):
        """流式获取训练日志"""
        url = f"{self.base_url}/api/v2/training/{task_id}/logs"
        with requests.get(url, stream=True) as response:
            response.raise_for_status()
            for line in response.iter_lines():
                if line:
                    if line.startswith(b'data: '):
                        data = line[6:]
                        yield json.loads(data.decode('utf-8'))
    
    # ==================== 推理接口 ====================
    
    def start_inference(
        self,
        cfg_path: str,
        weight_path: str,
        source_path: str,
        save_path: Optional[str] = None,
        device: str = "cuda",
        priority: int = 3
    ) -> Dict:
        """启动推理任务"""
        url = f"{self.base_url}/api/v2/inference/start"
        data = {
            "cfg_path": cfg_path,
            "weight_path": weight_path,
            "source_path": source_path,
            "device": device,
            "priority": priority
        }
        if save_path:
            data["save_path"] = save_path
        
        response = requests.post(url, json=data)
        response.raise_for_status()
        return response.json()
    
    def start_batch_inference(
        self,
        cfg_path: str,
        weight_path: str,
        source_paths: list,
        save_base_path: Optional[str] = None,
        device: str = "cuda"
    ) -> Dict:
        """批量推理"""
        url = f"{self.base_url}/api/v2/inference/batch"
        data = {
            "cfg_path": cfg_path,
            "weight_path": weight_path,
            "source_paths": source_paths,
            "device": device
        }
        if save_base_path:
            data["save_base_path"] = save_base_path
        
        response = requests.post(url, json=data)
        response.raise_for_status()
        return response.json()
    
    def get_inference_status(self, task_id: str) -> Dict:
        """获取推理任务状态"""
        url = f"{self.base_url}/api/v2/inference/{task_id}"
        response = requests.get(url)
        response.raise_for_status()
        return response.json()
    
    # ==================== 任务管理 ====================
    
    def get_all_tasks(
        self,
        status: Optional[str] = None,
        task_type: Optional[str] = None,
        limit: int = 100
    ) -> Dict:
        """获取所有任务"""
        url = f"{self.base_url}/api/v2/tasks"
        params = {"limit": limit}
        if status:
            params["status"] = status
        if task_type:
            params["task_type"] = task_type
        
        response = requests.get(url, params=params)
        response.raise_for_status()
        return response.json()
    
    def get_task(self, task_id: str) -> Dict:
        """获取任务详情"""
        url = f"{self.base_url}/api/v2/tasks/{task_id}"
        response = requests.get(url)
        response.raise_for_status()
        return response.json()
    
    def cancel_task(self, task_id: str) -> Dict:
        """取消任务"""
        url = f"{self.base_url}/api/v2/tasks/{task_id}/cancel"
        response = requests.post(url)
        response.raise_for_status()
        return response.json()
    
    def delete_task(self, task_id: str) -> Dict:
        """删除任务"""
        url = f"{self.base_url}/api/v2/tasks/{task_id}"
        response = requests.delete(url)
        response.raise_for_status()
        return response.json()
    
    # ==================== 资源管理 ====================
    
    def get_resources(self) -> Dict:
        """获取资源状态"""
        url = f"{self.base_url}/api/v2/resources"
        response = requests.get(url)
        response.raise_for_status()
        return response.json()
    
    def get_gpu_info(self) -> Dict:
        """获取GPU信息"""
        url = f"{self.base_url}/api/v2/resources/gpu"
        response = requests.get(url)
        response.raise_for_status()
        return response.json()
    
    def update_resource_config(self, config: Dict) -> Dict:
        """更新资源配置"""
        url = f"{self.base_url}/api/v2/resources/config"
        response = requests.post(url, json=config)
        response.raise_for_status()
        return response.json()
    
    # ==================== 系统状态 ====================
    
    def health_check(self) -> Dict:
        """健康检查"""
        url = f"{self.base_url}/api/v1/health"
        response = requests.get(url)
        response.raise_for_status()
        return response.json()
    
    def get_system_info(self) -> Dict:
        """获取系统信息"""
        url = f"{self.base_url}/api/v1/info"
        response = requests.get(url)
        response.raise_for_status()
        return response.json()
    
    # ==================== 工具方法 ====================
    
    def wait_for_task(self, task_id: str, interval: int = 5, timeout: int = 3600):
        """等待任务完成"""
        start_time = time.time()
        
        while True:
            if time.time() - start_time > timeout:
                raise TimeoutError(f"任务 {task_id} 超时")
            
            task = self.get_task(task_id)
            status = task["status"]
            
            print(f"[{task_id[:8]}] 状态: {status}, 进度: {task.get('progress', 0)}%")
            
            if status in ["completed", "failed", "cancelled"]:
                return task
            
            time.sleep(interval)


# ==================== 使用示例 ====================

def example_training():
    """训练示例"""
    client = RFUAVClient()
    
    print("=== 启动训练任务 ===")
    result = client.start_training(
        model="resnet18",
        num_classes=37,
        train_path="data/train",
        val_path="data/val",
        save_path="models/output",
        batch_size=16,
        num_epochs=50,
        device="cuda"
    )
    task_id = result["task_id"]
    print(f"任务ID: {task_id}")
    
    # 等待完成
    final_task = client.wait_for_task(task_id)
    print(f"训练完成: {final_task}")


def example_inference():
    """推理示例"""
    client = RFUAVClient()
    
    print("=== 启动推理任务 ===")
    result = client.start_inference(
        cfg_path="configs/model.yaml",
        weight_path="models/best.pth",
        source_path="data/test",
        save_path="results/",
        device="cuda"
    )
    task_id = result["task_id"]
    print(f"任务ID: {task_id}")
    
    # 等待完成
    final_task = client.wait_for_task(task_id)
    print(f"推理完成: {final_task}")


def example_batch_inference():
    """批量推理示例"""
    client = RFUAVClient()
    
    print("=== 启动批量推理 ===")
    result = client.start_batch_inference(
        cfg_path="configs/model.yaml",
        weight_path="models/best.pth",
        source_paths=[
            "data/test1",
            "data/test2",
            "data/test3"
        ],
        device="cuda"
    )
    print(f"启动了 {len(result['task_ids'])} 个任务")
    
    # 等待所有任务完成
    for task_id in result["task_ids"]:
        client.wait_for_task(task_id)


def example_monitoring():
    """监控示例"""
    client = RFUAVClient()
    
    print("=== 系统信息 ===")
    info = client.get_system_info()
    print(f"版本: {info['version']}")
    print(f"GPU可用: {info['gpu_available']}")
    
    print("\n=== 资源状态 ===")
    resources = client.get_resources()
    print(f"GPU使用: {resources['device_usage']}")
    print(f"GPU限制: {resources['limits']}")
    
    print("\n=== 所有任务 ===")
    tasks = client.get_all_tasks()
    print(f"训练任务: {tasks['total_training']}")
    print(f"推理任务: {tasks['total_inference']}")


def example_logs():
    """日志流示例"""
    client = RFUAVClient()
    
    # 启动训练
    result = client.start_training(
        model="resnet18",
        num_classes=37,
        train_path="data/train",
        val_path="data/val",
        save_path="models/output",
        num_epochs=10,
        device="cuda"
    )
    task_id = result["task_id"]
    
    print(f"=== 实时日志流: {task_id} ===")
    for log in client.stream_training_logs(task_id):
        timestamp = log.get("timestamp", "")
        level = log.get("level", "INFO")
        message = log.get("message", "")
        print(f"[{timestamp}] {level}: {message}")


if __name__ == "__main__":
    # 选择要运行的示例
    print("RFUAV API测试客户端")
    print("=" * 50)
    
    # 示例1: 监控
    example_monitoring()
    
    # 示例2: 推理
    # example_inference()
    
    # 示例3: 训练
    # example_training()
    
    # 示例4: 批量推理
    # example_batch_inference()
    
    # 示例5: 实时日志
    # example_logs()


