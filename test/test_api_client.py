"""
RFUAV模型服务API测试客户端
演示如何使用参数化训练API和实时日志流
"""
import requests
import json
import time
import threading
from typing import Optional


class RFUAVClient:
    """RFUAV模型服务客户端"""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        
    def start_training(self, config: dict) -> dict:
        """
        启动训练任务
        
        Args:
            config: 训练配置字典
            
        Returns:
            任务信息
        """
        url = f"{self.base_url}/api/v2/train"
        response = requests.post(url, json=config)
        response.raise_for_status()
        return response.json()
    
    def get_task_status(self, task_id: str) -> dict:
        """
        获取任务状态
        
        Args:
            task_id: 任务ID
            
        Returns:
            任务状态信息
        """
        url = f"{self.base_url}/api/v1/tasks/{task_id}"
        response = requests.get(url)
        response.raise_for_status()
        return response.json()
    
    def stream_logs(self, task_id: str, callback=None):
        """
        流式获取训练日志
        
        Args:
            task_id: 任务ID
            callback: 日志回调函数，接收日志字典作为参数
        """
        url = f"{self.base_url}/api/v2/train/{task_id}/logs"
        response = requests.get(url, stream=True)
        
        for line in response.iter_lines():
            if line:
                line_str = line.decode('utf-8')
                if line_str.startswith('data: '):
                    try:
                        data = json.loads(line_str[6:])
                        if callback:
                            callback(data)
                        else:
                            self._default_log_handler(data)
                        
                        # 检查是否结束
                        if 'status' in data and data['status'] in ['completed', 'failed']:
                            break
                    except json.JSONDecodeError as e:
                        print(f"解析日志失败: {e}")
    
    def _default_log_handler(self, log_data: dict):
        """默认日志处理"""
        if 'message' in log_data:
            level = log_data.get('level', 'INFO')
            timestamp = log_data.get('timestamp', '')
            message = log_data['message']
            print(f"[{timestamp}] [{level}] {message}")
    
    def inference(self, cfg_path: str, weight_path: str, source_path: str, 
                  save_path: Optional[str] = None, device: str = "cuda") -> dict:
        """
        模型推理
        
        Args:
            cfg_path: 配置文件路径
            weight_path: 模型权重路径
            source_path: 数据路径
            save_path: 结果保存路径
            device: 推理设备，cuda或cpu
            
        Returns:
            推理结果
        """
        url = f"{self.base_url}/api/v1/inference"
        data = {
            "cfg_path": cfg_path,
            "weight_path": weight_path,
            "source_path": source_path,
            "device": device
        }
        if save_path:
            data["save_path"] = save_path
        
        response = requests.post(url, json=data)
        response.raise_for_status()
        return response.json()
    
    def health_check(self) -> dict:
        """健康检查"""
        url = f"{self.base_url}/api/v1/health"
        response = requests.get(url)
        response.raise_for_status()
        return response.json()


def example_1_basic_training():
    """示例1：基础训练"""
    print("=" * 60)
    print("示例1：基础训练")
    print("=" * 60)
    
    client = RFUAVClient()
    
    # 训练配置
    config = {
        "model": "resnet18",
        "num_classes": 37,
        "train_path": "data/train",
        "val_path": "data/val",
        "batch_size": 32,
        "num_epochs": 100,
        "learning_rate": 0.0001,
        "image_size": 224,
        "device": "cuda",
        "save_path": "models/resnet18_test",
        "shuffle": True,
        "pretrained": True,
        "description": "测试ResNet18训练"
    }
    
    # 启动训练
    print("正在启动训练任务...")
    task_info = client.start_training(config)
    task_id = task_info['task_id']
    print(f"训练任务已启动")
    print(f"任务ID: {task_id}")
    print(f"状态: {task_info['status']}")
    print(f"创建时间: {task_info['created_at']}")
    print()
    
    # 在后台线程中流式获取日志
    print("开始监听训练日志...")
    print("-" * 60)
    log_thread = threading.Thread(target=client.stream_logs, args=(task_id,))
    log_thread.start()
    
    # 定期查询任务状态
    while True:
        time.sleep(10)
        status = client.get_task_status(task_id)
        
        if status['status'] in ['completed', 'failed']:
            print("-" * 60)
            print(f"任务结束: {status['status']}")
            print(f"消息: {status.get('message', '')}")
            break
    
    log_thread.join()


def example_2_monitoring_only():
    """示例2：仅监控已存在的任务"""
    print("=" * 60)
    print("示例2：监控已存在的任务")
    print("=" * 60)
    
    client = RFUAVClient()
    
    # 输入任务ID
    task_id = input("请输入任务ID: ").strip()
    
    try:
        # 检查任务状态
        status = client.get_task_status(task_id)
        print(f"任务状态: {status['status']}")
        print(f"进度: {status.get('progress', 0)}%")
        print()
        
        # 流式获取日志
        print("开始监听训练日志...")
        print("-" * 60)
        client.stream_logs(task_id)
        
    except requests.exceptions.HTTPError as e:
        print(f"错误: {e}")


def example_3_custom_log_handler():
    """示例3：自定义日志处理"""
    print("=" * 60)
    print("示例3：自定义日志处理")
    print("=" * 60)
    
    client = RFUAVClient()
    
    # 自定义日志处理函数
    log_history = []
    
    def custom_log_handler(log_data):
        """自定义日志处理 - 只显示重要信息"""
        if 'message' in log_data:
            message = log_data['message']
            log_history.append(message)
            
            # 只打印包含关键信息的日志
            keywords = ['Epoch', 'Loss', 'Accuracy', '完成', '失败', '开始']
            if any(keyword in message for keyword in keywords):
                level = log_data.get('level', 'INFO')
                print(f"[{level}] {message}")
    
    # 配置
    config = {
        "model": "mobilenet_v3_small",
        "num_classes": 37,
        "train_path": "data/train",
        "val_path": "data/val",
        "batch_size": 64,
        "num_epochs": 10,
        "learning_rate": 0.001,
        "image_size": 224,
        "device": "cuda",
        "save_path": "models/mobilenet_test",
        "shuffle": True,
        "pretrained": True
    }
    
    # 启动训练
    task_info = client.start_training(config)
    task_id = task_info['task_id']
    print(f"任务ID: {task_id}")
    print()
    
    # 使用自定义日志处理器
    print("开始监听训练日志（只显示关键信息）...")
    print("-" * 60)
    client.stream_logs(task_id, callback=custom_log_handler)
    
    print("-" * 60)
    print(f"共收集到 {len(log_history)} 条日志")


def example_4_inference():
    """示例4：模型推理"""
    print("=" * 60)
    print("示例4：模型推理")
    print("=" * 60)
    
    client = RFUAVClient()
    
    # 推理配置
    cfg_path = input("配置文件路径 [configs/exp3.1_ResNet18.yaml]: ").strip() or "configs/exp3.1_ResNet18.yaml"
    weight_path = input("模型权重路径 [models/best_model.pth]: ").strip() or "models/best_model.pth"
    source_path = input("数据路径 [example/test_data/]: ").strip() or "example/test_data/"
    device = input("推理设备 [cuda]: ").strip() or "cuda"
    
    try:
        print(f"正在进行推理（设备: {device}）...")
        result = client.inference(cfg_path, weight_path, source_path, device=device)
        
        print("推理完成！")
        print(f"状态: {result['status']}")
        print(f"消息: {result['message']}")
        print(f"使用设备: {result.get('device', 'N/A')}")
        print(f"结果保存路径: {result['save_path']}")
        
    except requests.exceptions.HTTPError as e:
        print(f"推理失败: {e}")


def main():
    """主函数"""
    print("RFUAV模型服务API测试客户端")
    print()
    
    # 健康检查
    client = RFUAVClient()
    try:
        health = client.health_check()
        print(f"服务状态: {health['status']}")
        print(f"当前训练任务数: {health['training_tasks']}")
        print(f"活跃日志流: {health['active_log_streams']}")
        print()
    except requests.exceptions.ConnectionError:
        print("错误: 无法连接到服务器，请确保服务已启动")
        print("运行: python app_enhanced.py")
        return
    
    # 选择示例
    while True:
        print("\n请选择示例:")
        print("1. 基础训练（启动新任务并监控）")
        print("2. 监控已存在的任务")
        print("3. 自定义日志处理")
        print("4. 模型推理")
        print("0. 退出")
        
        choice = input("\n请输入选项: ").strip()
        
        if choice == "1":
            example_1_basic_training()
        elif choice == "2":
            example_2_monitoring_only()
        elif choice == "3":
            example_3_custom_log_handler()
        elif choice == "4":
            example_4_inference()
        elif choice == "0":
            print("退出程序")
            break
        else:
            print("无效选项，请重新输入")


if __name__ == "__main__":
    main()

