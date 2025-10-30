"""
并发场景示例 - 演示训练和推理同时进行
"""
import requests
import threading
import time
from typing import List
import json

API_BASE = "http://localhost:8000"


def monitor_task(task_id: str, task_name: str):
    """监控单个任务"""
    print(f"[{task_name}] 开始监控任务 {task_id[:8]}")
    
    try:
        # 连接日志流
        response = requests.get(f"{API_BASE}/api/v2/tasks/{task_id}/logs", stream=True)
        
        for line in response.iter_lines():
            if line:
                line_str = line.decode('utf-8')
                if line_str.startswith('data: '):
                    try:
                        data = json.loads(line_str[6:])
                        if 'message' in data:
                            print(f"[{task_name}] {data['message']}")
                        if 'status' in data and data['status'] in ['completed', 'failed']:
                            print(f"[{task_name}] 任务结束: {data['status']}")
                            break
                    except json.JSONDecodeError:
                        pass
    except Exception as e:
        print(f"[{task_name}] 监控失败: {e}")


def start_training(name: str, device: str = "cuda", priority: int = 5):
    """启动训练任务"""
    config = {
        "model": "resnet18",
        "num_classes": 37,
        "train_path": "data/train",
        "val_path": "data/val",
        "batch_size": 32 if device == "cuda" else 8,
        "num_epochs": 10,
        "learning_rate": 0.0001,
        "save_path": f"models/concurrent_{name}",
        "device": device,
        "priority": priority,
        "description": f"并发训练-{name}"
    }
    
    response = requests.post(f"{API_BASE}/api/v2/train", json=config)
    result = response.json()
    print(f"✓ 训练任务 '{name}' 已启动")
    print(f"  任务ID: {result['task_id']}")
    print(f"  设备: {device}")
    print(f"  优先级: {priority}")
    return result['task_id']


def start_inference(name: str, device: str = "cuda", priority: int = 3):
    """启动推理任务"""
    config = {
        "cfg_path": "configs/exp3.1_ResNet18.yaml",
        "weight_path": "models/best_model.pth",
        "source_path": "example/test_data/",
        "save_path": f"results/concurrent_{name}/",
        "device": device,
        "priority": priority
    }
    
    response = requests.post(f"{API_BASE}/api/v2/inference", json=config)
    result = response.json()
    print(f"✓ 推理任务 '{name}' 已启动")
    print(f"  任务ID: {result['task_id']}")
    print(f"  设备: {device}")
    print(f"  优先级: {priority}")
    return result['task_id']


def show_resource_status():
    """显示资源状态"""
    response = requests.get(f"{API_BASE}/api/v2/resources")
    status = response.json()
    
    print("\n" + "=" * 60)
    print("资源状态")
    print("=" * 60)
    
    # 设备使用情况
    print("\n设备使用情况:")
    for device, usage in status['device_usage'].items():
        print(f"  {device.upper()}:")
        print(f"    训练任务: {usage['training']}")
        print(f"    推理任务: {usage['inference']}")
    
    # 资源限制
    print("\n资源限制:")
    for device, limits in status['limits'].items():
        print(f"  {device.upper()}:")
        print(f"    最大训练并发: {limits['training']}")
        print(f"    最大推理并发: {limits['inference']}")
    
    # GPU信息
    if status.get('gpu_memory_info'):
        print("\nGPU显存信息:")
        for gpu_name, info in status['gpu_memory_info'].items():
            print(f"  {info['name']}:")
            print(f"    总容量: {info['total_gb']} GB")
            print(f"    已使用: {info['allocated_gb']} GB")
            print(f"    可用: {info['free_gb']} GB")
    
    # 活动任务
    print("\n活动任务:")
    for device, tasks in status['active_tasks'].items():
        if tasks:
            print(f"  {device.upper()}: {len(tasks)} 个任务")
            for task in tasks:
                print(f"    - {task['type']}: {task['id'][:8]}")
    
    print("=" * 60 + "\n")


def scenario_1_single_gpu_mixed():
    """场景1: 单GPU上同时训练和推理"""
    print("\n" + "=" * 60)
    print("场景1: 单GPU上同时训练和推理")
    print("=" * 60)
    print("说明: 在同一个GPU上启动1个训练和2个推理任务")
    print()
    
    # 显示初始资源状态
    show_resource_status()
    
    # 启动1个训练任务
    train_id = start_training("gpu_train", device="cuda", priority=5)
    
    # 稍等片刻
    time.sleep(2)
    
    # 启动2个推理任务
    infer_id1 = start_inference("gpu_infer1", device="cuda", priority=3)
    time.sleep(1)
    infer_id2 = start_inference("gpu_infer2", device="cuda", priority=3)
    
    print()
    
    # 显示资源状态
    time.sleep(2)
    show_resource_status()
    
    # 监控所有任务
    threads = []
    for task_id, name in [(train_id, "训练"), (infer_id1, "推理1"), (infer_id2, "推理2")]:
        t = threading.Thread(target=monitor_task, args=(task_id, name))
        t.start()
        threads.append(t)
    
    # 等待所有任务完成
    for t in threads:
        t.join()
    
    print("\n所有任务已完成")
    show_resource_status()


def scenario_2_cpu_gpu_separate():
    """场景2: CPU训练 + GPU推理"""
    print("\n" + "=" * 60)
    print("场景2: CPU训练 + GPU推理")
    print("=" * 60)
    print("说明: CPU上训练，GPU上推理，资源完全隔离")
    print()
    
    show_resource_status()
    
    # CPU训练
    train_id = start_training("cpu_train", device="cpu", priority=5)
    
    # GPU推理
    time.sleep(1)
    infer_id = start_inference("gpu_infer", device="cuda", priority=3)
    
    print()
    time.sleep(2)
    show_resource_status()
    
    # 监控任务
    threads = []
    for task_id, name in [(train_id, "CPU训练"), (infer_id, "GPU推理")]:
        t = threading.Thread(target=monitor_task, args=(task_id, name))
        t.start()
        threads.append(t)
    
    for t in threads:
        t.join()
    
    print("\n所有任务已完成")
    show_resource_status()


def scenario_3_multiple_inference():
    """场景3: 多个推理任务并发"""
    print("\n" + "=" * 60)
    print("场景3: 多个推理任务并发")
    print("=" * 60)
    print("说明: 同时启动3个推理任务，测试并发能力")
    print()
    
    show_resource_status()
    
    # 启动3个推理任务
    task_ids = []
    for i in range(3):
        task_id = start_inference(f"infer_{i+1}", device="cuda", priority=3)
        task_ids.append((task_id, f"推理{i+1}"))
        time.sleep(0.5)
    
    print()
    time.sleep(2)
    show_resource_status()
    
    # 监控所有任务
    threads = []
    for task_id, name in task_ids:
        t = threading.Thread(target=monitor_task, args=(task_id, name))
        t.start()
        threads.append(t)
    
    for t in threads:
        t.join()
    
    print("\n所有任务已完成")
    show_resource_status()


def scenario_4_priority_test():
    """场景4: 优先级测试"""
    print("\n" + "=" * 60)
    print("场景4: 优先级测试")
    print("=" * 60)
    print("说明: 测试不同优先级任务的执行顺序")
    print()
    
    show_resource_status()
    
    # 启动不同优先级的任务
    print("启动任务（优先级从低到高）:")
    low_id = start_inference("low_priority", device="cuda", priority=8)
    time.sleep(0.5)
    high_id = start_inference("high_priority", device="cuda", priority=1)
    time.sleep(0.5)
    med_id = start_inference("medium_priority", device="cuda", priority=5)
    
    print("\n观察执行顺序（高优先级应该先执行）")
    
    print()
    time.sleep(2)
    show_resource_status()
    
    # 监控任务
    threads = []
    for task_id, name in [(low_id, "低优先级"), (high_id, "高优先级"), (med_id, "中优先级")]:
        t = threading.Thread(target=monitor_task, args=(task_id, name))
        t.start()
        threads.append(t)
    
    for t in threads:
        t.join()
    
    print("\n所有任务已完成")
    show_resource_status()


def scenario_5_resource_limit_test():
    """场景5: 资源限制测试"""
    print("\n" + "=" * 60)
    print("场景5: 资源限制测试")
    print("=" * 60)
    print("说明: 超过资源限制时，任务会排队等待")
    print()
    
    show_resource_status()
    
    # 启动超过限制的任务数量
    print("启动5个推理任务（超过GPU限制3个）:")
    task_ids = []
    for i in range(5):
        task_id = start_inference(f"infer_{i+1}", device="cuda", priority=3)
        task_ids.append((task_id, f"推理{i+1}"))
        time.sleep(0.3)
    
    print("\n资源状态（部分任务应该在排队）:")
    time.sleep(2)
    show_resource_status()
    
    print("等待任务完成...")
    
    # 监控所有任务
    threads = []
    for task_id, name in task_ids:
        t = threading.Thread(target=monitor_task, args=(task_id, name))
        t.start()
        threads.append(t)
    
    for t in threads:
        t.join()
    
    print("\n所有任务已完成")
    show_resource_status()


def main():
    """主函数"""
    print("=" * 60)
    print("RFUAV并发场景示例")
    print("=" * 60)
    
    # 检查服务状态
    try:
        response = requests.get(f"{API_BASE}/api/v1/health")
        health = response.json()
        print(f"✓ 服务状态: {health['status']}")
        print()
    except requests.exceptions.ConnectionError:
        print("✗ 无法连接到服务器")
        print("  请先启动服务: python app_concurrent.py")
        return
    
    while True:
        print("\n请选择场景:")
        print("1. 单GPU上同时训练和推理")
        print("2. CPU训练 + GPU推理（资源隔离）")
        print("3. 多个推理任务并发")
        print("4. 优先级测试")
        print("5. 资源限制测试")
        print("6. 显示当前资源状态")
        print("0. 退出")
        
        choice = input("\n请输入选项: ").strip()
        
        if choice == "1":
            scenario_1_single_gpu_mixed()
        elif choice == "2":
            scenario_2_cpu_gpu_separate()
        elif choice == "3":
            scenario_3_multiple_inference()
        elif choice == "4":
            scenario_4_priority_test()
        elif choice == "5":
            scenario_5_resource_limit_test()
        elif choice == "6":
            show_resource_status()
        elif choice == "0":
            print("退出程序")
            break
        else:
            print("无效选项")


if __name__ == "__main__":
    main()


