"""
测试训练任务详细指标功能

演示如何使用增强后的训练接口获取详细的训练指标
"""
import requests
import json
import time
from typing import Dict, Any


BASE_URL = "http://localhost:8000"


def start_training() -> str:
    """启动训练任务"""
    print("=" * 60)
    print("1. 启动训练任务")
    print("=" * 60)
    
    url = f"{BASE_URL}/api/v2/training/start"
    
    # 训练请求（请根据实际情况修改路径）
    training_request = {
        "model": "resnet18",
        "num_classes": 37,
        "train_path": "D:/ML_Project/RFUAV-server/data/train",
        "val_path": "D:/ML_Project/RFUAV-server/data/val",
        "save_path": "D:/ML_Project/RFUAV-server/checkpoints",
        "batch_size": 8,
        "num_epochs": 5,
        "learning_rate": 0.0001,
        "device": "cuda:0",
        "priority": 5,
        "pretrained": True
    }
    
    response = requests.post(url, json=training_request)
    
    if response.status_code == 200:
        result = response.json()
        task_id = result["task_id"]
        print(f"✓ 训练任务已启动")
        print(f"  任务ID: {task_id}")
        print(f"  状态: {result['status']}")
        print(f"  设备: {result.get('device', 'N/A')}")
        print(f"  总轮次: {result.get('total_epochs', 'N/A')}")
        return task_id
    else:
        print(f"✗ 启动失败: {response.text}")
        return None


def get_training_status(task_id: str):
    """获取训练任务详细状态"""
    print("\n" + "=" * 60)
    print("2. 获取训练状态（含详细指标）")
    print("=" * 60)
    
    url = f"{BASE_URL}/api/v2/training/{task_id}"
    response = requests.get(url)
    
    if response.status_code == 200:
        result = response.json()
        print(f"✓ 任务状态获取成功")
        print(f"  任务ID: {result['task_id']}")
        print(f"  状态: {result['status']}")
        print(f"  进度: {result.get('progress', 0)}%")
        print(f"  设备: {result.get('device', 'N/A')}")
        
        # 显示详细的训练指标
        if result.get('current_epoch'):
            print(f"  当前轮次: {result['current_epoch']}/{result.get('total_epochs', 'N/A')}")
        
        if result.get('latest_metrics'):
            metrics = result['latest_metrics']
            print("\n  最新训练指标:")
            
            if metrics.get('train_loss') is not None:
                print(f"    训练损失: {metrics['train_loss']:.4f}")
            if metrics.get('train_acc') is not None:
                print(f"    训练准确率: {metrics['train_acc']:.2f}%")
            
            if metrics.get('val_loss') is not None:
                print(f"    验证损失: {metrics['val_loss']:.4f}")
            if metrics.get('val_acc') is not None:
                print(f"    验证准确率: {metrics['val_acc']:.2f}%")
            
            if metrics.get('macro_f1') is not None:
                print(f"    Macro F1: {metrics['macro_f1']:.4f}")
            if metrics.get('micro_f1') is not None:
                print(f"    Micro F1: {metrics['micro_f1']:.4f}")
            
            if metrics.get('mAP') is not None:
                print(f"    mAP: {metrics['mAP']:.4f}")
            
            if metrics.get('top1_acc') is not None:
                print(f"    Top-1准确率: {metrics['top1_acc']:.2f}%")
            if metrics.get('top3_acc') is not None:
                print(f"    Top-3准确率: {metrics['top3_acc']:.2f}%")
            if metrics.get('top5_acc') is not None:
                print(f"    Top-5准确率: {metrics['top5_acc']:.2f}%")
            
            if metrics.get('best_acc') is not None:
                print(f"    最佳准确率: {metrics['best_acc']:.2f}%")
            
            if metrics.get('learning_rate') is not None:
                print(f"    学习率: {metrics['learning_rate']:.6f}")
        
        return result
    else:
        print(f"✗ 获取失败: {response.text}")
        return None


def monitor_training_logs(task_id: str, duration: int = 30):
    """
    监控训练日志流
    
    Args:
        task_id: 任务ID
        duration: 监控持续时间（秒）
    """
    print("\n" + "=" * 60)
    print("3. 监控训练日志流（含详细指标）")
    print("=" * 60)
    print(f"监控时长: {duration}秒\n")
    
    url = f"{BASE_URL}/api/v2/training/{task_id}/logs"
    
    try:
        response = requests.get(url, stream=True, timeout=duration+5)
        
        start_time = time.time()
        for line in response.iter_lines():
            if time.time() - start_time > duration:
                print("\n⏱ 监控时间到，停止监控")
                break
            
            if line:
                line_str = line.decode('utf-8')
                if line_str.startswith('data: '):
                    data_str = line_str[6:]  # 移除 "data: " 前缀
                    try:
                        log_entry = json.loads(data_str)
                        
                        # 格式化显示日志
                        timestamp = log_entry.get('timestamp', '')
                        level = log_entry.get('level', 'INFO')
                        message = log_entry.get('message', '')
                        
                        # 显示基本日志
                        print(f"[{timestamp}] [{level}] {message}")
                        
                        # 如果有训练指标，详细显示
                        if log_entry.get('metrics'):
                            metrics = log_entry['metrics']
                            stage = log_entry.get('stage', '')
                            print(f"  └─ 阶段: {stage}")
                            print(f"  └─ 指标: {json.dumps(metrics, indent=4, ensure_ascii=False)}")
                        
                    except json.JSONDecodeError:
                        print(f"无法解析: {data_str}")
    
    except requests.exceptions.Timeout:
        print("\n⏱ 监控超时")
    except Exception as e:
        print(f"\n✗ 监控出错: {e}")


def main():
    """主测试流程"""
    print("\n" + "=" * 60)
    print("训练任务详细指标测试")
    print("=" * 60)
    
    # 1. 启动训练任务
    task_id = start_training()
    if not task_id:
        print("\n✗ 无法启动训练任务，测试终止")
        return
    
    # 2. 等待一段时间
    print("\n⏱ 等待5秒后获取状态...")
    time.sleep(5)
    
    # 3. 获取训练状态
    get_training_status(task_id)
    
    # 4. 监控训练日志（持续30秒）
    monitor_training_logs(task_id, duration=30)
    
    # 5. 再次获取最新状态
    print("\n⏱ 等待5秒后再次获取状态...")
    time.sleep(5)
    get_training_status(task_id)
    
    print("\n" + "=" * 60)
    print("测试完成！")
    print("=" * 60)
    print(f"\n可以通过以下方式继续监控训练进度：")
    print(f"  - 获取状态: GET {BASE_URL}/api/v2/training/{task_id}")
    print(f"  - 日志流: GET {BASE_URL}/api/v2/training/{task_id}/logs")
    print(f"  - Swagger文档: {BASE_URL}/docs")


if __name__ == "__main__":
    main()

