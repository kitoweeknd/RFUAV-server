"""
设备选择示例 - 演示如何在训练、推理和基准测试中指定设备
"""
import requests
import torch

API_BASE = "http://localhost:8000"


def check_cuda_available():
    """检查CUDA是否可用"""
    cuda_available = torch.cuda.is_available()
    print("=" * 60)
    print("设备检查")
    print("=" * 60)
    print(f"CUDA可用: {cuda_available}")
    if cuda_available:
        print(f"CUDA版本: {torch.version.cuda}")
        print(f"GPU数量: {torch.cuda.device_count()}")
        for i in range(torch.cuda.device_count()):
            print(f"GPU {i}: {torch.cuda.get_device_name(i)}")
    print()
    return cuda_available


def example_train_with_device(device="cuda"):
    """示例1：使用指定设备训练"""
    print("=" * 60)
    print(f"示例1：使用 {device.upper()} 训练模型")
    print("=" * 60)
    
    config = {
        "model": "resnet18",
        "num_classes": 37,
        "train_path": "data/train",
        "val_path": "data/val",
        "batch_size": 32 if device == "cuda" else 8,  # CPU时减小batch size
        "num_epochs": 10,
        "learning_rate": 0.0001,
        "image_size": 224,
        "device": device,  # 指定设备
        "save_path": f"models/resnet18_{device}",
        "shuffle": True,
        "pretrained": True,
        "description": f"使用{device.upper()}训练ResNet18"
    }
    
    print(f"配置信息:")
    print(f"  模型: {config['model']}")
    print(f"  设备: {config['device']}")
    print(f"  批次大小: {config['batch_size']}")
    print(f"  训练轮数: {config['num_epochs']}")
    print()
    
    try:
        response = requests.post(f"{API_BASE}/api/v2/train", json=config)
        response.raise_for_status()
        result = response.json()
        
        print(f"✓ 训练任务已启动")
        print(f"  任务ID: {result['task_id']}")
        print(f"  状态: {result['status']}")
        print(f"  创建时间: {result['created_at']}")
        print()
        return result['task_id']
        
    except requests.exceptions.RequestException as e:
        print(f"✗ 启动失败: {e}")
        return None


def example_inference_with_device(device="cuda"):
    """示例2：使用指定设备推理"""
    print("=" * 60)
    print(f"示例2：使用 {device.upper()} 进行推理")
    print("=" * 60)
    
    config = {
        "cfg_path": "configs/exp3.1_ResNet18.yaml",
        "weight_path": "models/best_model.pth",
        "source_path": "example/test_data/",
        "save_path": f"results/inference_{device}/",
        "device": device  # 指定设备
    }
    
    print(f"配置信息:")
    print(f"  配置文件: {config['cfg_path']}")
    print(f"  权重文件: {config['weight_path']}")
    print(f"  数据路径: {config['source_path']}")
    print(f"  推理设备: {config['device']}")
    print()
    
    try:
        response = requests.post(f"{API_BASE}/api/v1/inference", json=config)
        response.raise_for_status()
        result = response.json()
        
        print(f"✓ 推理完成")
        print(f"  状态: {result['status']}")
        print(f"  消息: {result['message']}")
        print(f"  使用设备: {result['device']}")
        print(f"  结果保存路径: {result['save_path']}")
        print()
        
    except requests.exceptions.RequestException as e:
        print(f"✗ 推理失败: {e}")


def example_benchmark_with_device(device="cuda"):
    """示例3：使用指定设备进行基准测试"""
    print("=" * 60)
    print(f"示例3：使用 {device.upper()} 进行基准测试")
    print("=" * 60)
    
    config = {
        "cfg_path": "configs/exp3.1_ResNet18.yaml",
        "weight_path": "models/best_model.pth",
        "data_path": "data/benchmark/",
        "save_path": f"results/benchmark_{device}/",
        "device": device  # 指定设备
    }
    
    print(f"配置信息:")
    print(f"  配置文件: {config['cfg_path']}")
    print(f"  权重文件: {config['weight_path']}")
    print(f"  测试数据: {config['data_path']}")
    print(f"  测试设备: {config['device']}")
    print()
    
    try:
        response = requests.post(f"{API_BASE}/api/v1/benchmark", json=config)
        response.raise_for_status()
        result = response.json()
        
        print(f"✓ 基准测试完成")
        print(f"  状态: {result['status']}")
        print(f"  消息: {result['message']}")
        print(f"  使用设备: {result['device']}")
        print(f"  结果保存路径: {result['save_path']}")
        print()
        
    except requests.exceptions.RequestException as e:
        print(f"✗ 基准测试失败: {e}")


def example_auto_device_selection():
    """示例4：自动选择可用设备"""
    print("=" * 60)
    print("示例4：自动选择可用设备")
    print("=" * 60)
    
    # 自动检测并选择设备
    device = "cuda" if torch.cuda.is_available() else "cpu"
    print(f"自动选择设备: {device.upper()}")
    print()
    
    # 使用自动选择的设备进行训练
    config = {
        "model": "mobilenet_v3_small",
        "num_classes": 37,
        "train_path": "data/train",
        "val_path": "data/val",
        "batch_size": 64 if device == "cuda" else 16,
        "num_epochs": 10,
        "learning_rate": 0.001,
        "save_path": f"models/mobilenet_{device}_auto",
        "device": device,  # 自动选择的设备
        "description": f"自动选择{device.upper()}训练MobileNet"
    }
    
    print(f"使用配置:")
    print(f"  模型: {config['model']}")
    print(f"  设备: {config['device']} (自动)")
    print(f"  批次大小: {config['batch_size']} (根据设备调整)")
    print()
    
    try:
        response = requests.post(f"{API_BASE}/api/v2/train", json=config)
        response.raise_for_status()
        result = response.json()
        
        print(f"✓ 训练任务已启动")
        print(f"  任务ID: {result['task_id']}")
        print()
        
    except requests.exceptions.RequestException as e:
        print(f"✗ 启动失败: {e}")


def example_compare_devices():
    """示例5：对比不同设备的性能"""
    print("=" * 60)
    print("示例5：对比GPU和CPU推理性能")
    print("=" * 60)
    
    import time
    
    base_config = {
        "cfg_path": "configs/exp3.1_ResNet18.yaml",
        "weight_path": "models/best_model.pth",
        "source_path": "example/test_data/",
    }
    
    results = {}
    
    # 测试GPU
    if torch.cuda.is_available():
        print("测试GPU推理速度...")
        gpu_config = {**base_config, "device": "cuda", "save_path": "results/gpu_test/"}
        start_time = time.time()
        try:
            response = requests.post(f"{API_BASE}/api/v1/inference", json=gpu_config)
            response.raise_for_status()
            gpu_time = time.time() - start_time
            results['GPU'] = gpu_time
            print(f"  GPU推理时间: {gpu_time:.2f}秒")
        except Exception as e:
            print(f"  GPU测试失败: {e}")
    
    # 测试CPU
    print("测试CPU推理速度...")
    cpu_config = {**base_config, "device": "cpu", "save_path": "results/cpu_test/"}
    start_time = time.time()
    try:
        response = requests.post(f"{API_BASE}/api/v1/inference", json=cpu_config)
        response.raise_for_status()
        cpu_time = time.time() - start_time
        results['CPU'] = cpu_time
        print(f"  CPU推理时间: {cpu_time:.2f}秒")
    except Exception as e:
        print(f"  CPU测试失败: {e}")
    
    # 对比结果
    if len(results) == 2:
        speedup = results['CPU'] / results['GPU']
        print()
        print("性能对比:")
        print(f"  GPU加速倍数: {speedup:.2f}x")
        print(f"  GPU相对速度: {100:.0f}%")
        print(f"  CPU相对速度: {(100/speedup):.0f}%")
    print()


def main():
    """主函数"""
    print("\n" + "=" * 60)
    print("RFUAV设备选择示例")
    print("=" * 60)
    print()
    
    # 检查服务状态
    try:
        response = requests.get(f"{API_BASE}/api/v1/health")
        health = response.json()
        print(f"✓ 服务状态: {health['status']}")
        print()
    except requests.exceptions.ConnectionError:
        print("✗ 无法连接到服务器")
        print("  请先启动服务: python app_enhanced.py")
        return
    
    # 检查CUDA可用性
    cuda_available = check_cuda_available()
    
    # 菜单
    while True:
        print("\n请选择示例:")
        print("1. 使用GPU训练 (需要CUDA)")
        print("2. 使用CPU训练")
        print("3. 使用GPU推理 (需要CUDA)")
        print("4. 使用CPU推理")
        print("5. 使用GPU基准测试 (需要CUDA)")
        print("6. 使用CPU基准测试")
        print("7. 自动选择设备训练")
        print("8. 对比GPU和CPU性能 (需要CUDA)")
        print("0. 退出")
        
        choice = input("\n请输入选项: ").strip()
        print()
        
        if choice == "1":
            if cuda_available:
                example_train_with_device("cuda")
            else:
                print("CUDA不可用，请安装CUDA或选择CPU训练")
        elif choice == "2":
            example_train_with_device("cpu")
        elif choice == "3":
            if cuda_available:
                example_inference_with_device("cuda")
            else:
                print("CUDA不可用，请安装CUDA或选择CPU推理")
        elif choice == "4":
            example_inference_with_device("cpu")
        elif choice == "5":
            if cuda_available:
                example_benchmark_with_device("cuda")
            else:
                print("CUDA不可用，请安装CUDA或选择CPU测试")
        elif choice == "6":
            example_benchmark_with_device("cpu")
        elif choice == "7":
            example_auto_device_selection()
        elif choice == "8":
            if cuda_available:
                example_compare_devices()
            else:
                print("CUDA不可用，无法进行性能对比")
        elif choice == "0":
            print("退出程序")
            break
        else:
            print("无效选项，请重新输入")


if __name__ == "__main__":
    main()


