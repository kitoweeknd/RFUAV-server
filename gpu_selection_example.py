"""
GPU设备选择示例
演示如何在训练和推理时选择不同的GPU设备
"""
import requests
import time
from test_refactored_api import RFUAVClient


def print_separator(title):
    """打印分隔符"""
    print("\n" + "="*70)
    print(f"  {title}")
    print("="*70)


def show_gpu_info(client):
    """显示GPU信息"""
    print_separator("🔍 查看GPU信息")
    
    gpu_info = client.get_gpu_info()
    
    print(f"\nGPU可用: {gpu_info['available']}")
    if not gpu_info['available']:
        print("❌ 未检测到GPU")
        return False
    
    print(f"CUDA版本: {gpu_info['cuda_version']}")
    print(f"PyTorch版本: {gpu_info['pytorch_version']}")
    print(f"GPU数量: {gpu_info['count']}\n")
    
    for device in gpu_info['devices']:
        print(f"GPU {device['id']} ({device['device_name']})")
        print(f"  型号: {device['name']}")
        print(f"  总显存: {device['total_memory_gb']:.2f} GB")
        print(f"  空闲显存: {device['free_memory_gb']:.2f} GB")
        print(f"  使用率: {device['utilization']:.1f}%")
        print(f"  当前任务: 训练={device['current_tasks']['training']}, 推理={device['current_tasks']['inference']}")
        print()
    
    return True


def example_auto_selection(client):
    """示例1: 自动选择GPU"""
    print_separator("📝 示例1: 自动选择GPU（推荐）")
    
    print("\n使用 device='cuda' 会自动选择负载最小的GPU")
    print("适合大多数场景，系统自动优化资源分配\n")
    
    # 启动训练任务，自动选择GPU
    print("启动训练任务（自动选择GPU）...")
    result = client.start_training(
        model="resnet18",
        num_classes=37,
        train_path="data/train",
        val_path="data/val",
        save_path="models/auto_gpu",
        batch_size=8,
        num_epochs=5,
        device="cuda"  # 自动选择
    )
    
    task_id = result['task_id']
    print(f"✅ 任务已创建: {task_id}")
    print(f"   实际使用设备: {result.get('device', 'cuda')}")
    
    return task_id


def example_specific_gpu(client):
    """示例2: 指定特定GPU"""
    print_separator("📝 示例2: 指定特定GPU")
    
    print("\n使用 device='cuda:0' 或 'cuda:1' 指定具体GPU")
    print("适合需要精确控制资源的场景\n")
    
    # 在GPU 0上训练
    print("在GPU 0上启动训练...")
    result1 = client.start_training(
        model="resnet18",
        num_classes=37,
        train_path="data/train",
        val_path="data/val",
        save_path="models/gpu0",
        batch_size=8,
        num_epochs=5,
        device="cuda:0"  # 指定GPU 0
    )
    
    print(f"✅ 任务已创建 (GPU 0): {result1['task_id']}")
    
    # 在GPU 1上推理（如果有多个GPU）
    gpu_info = client.get_gpu_info()
    if gpu_info['count'] > 1:
        print("\n在GPU 1上启动推理...")
        result2 = client.start_inference(
            cfg_path="configs/model.yaml",
            weight_path="models/best.pth",
            source_path="data/test",
            device="cuda:1"  # 指定GPU 1
        )
        print(f"✅ 任务已创建 (GPU 1): {result2['task_id']}")
        return [result1['task_id'], result2['task_id']]
    else:
        print("\n⚠️ 只有一个GPU，跳过GPU 1示例")
        return [result1['task_id']]


def example_multi_tasks(client):
    """示例3: 多任务并行"""
    print_separator("📝 示例3: 多任务并行")
    
    print("\n同时启动多个任务，系统自动分配到不同GPU")
    print("实现负载均衡\n")
    
    tasks = []
    
    # 启动3个训练任务
    for i in range(3):
        print(f"启动训练任务 {i+1}...")
        result = client.start_training(
            model="resnet18",
            num_classes=37,
            train_path="data/train",
            val_path="data/val",
            save_path=f"models/parallel_{i}",
            batch_size=8,
            num_epochs=3,
            device="cuda",  # 自动选择
            task_id=f"parallel_train_{i}"
        )
        tasks.append(result['task_id'])
        print(f"   任务 {i+1}: {result['task_id'][:8]}... -> {result.get('device', 'cuda')}")
        time.sleep(0.5)  # 避免过快创建
    
    return tasks


def example_train_and_infer(client):
    """示例4: 训练和推理同时进行"""
    print_separator("📝 示例4: 训练和推理同时进行")
    
    print("\n在不同GPU上同时运行训练和推理")
    print("充分利用多GPU资源\n")
    
    gpu_info = client.get_gpu_info()
    
    if gpu_info['count'] < 2:
        print("⚠️ 需要至少2个GPU才能演示此示例")
        return []
    
    tasks = []
    
    # 在GPU 0上训练
    print("在GPU 0上启动训练...")
    train_result = client.start_training(
        model="resnet18",
        num_classes=37,
        train_path="data/train",
        val_path="data/val",
        save_path="models/train_gpu0",
        device="cuda:0"
    )
    tasks.append(train_result['task_id'])
    print(f"✅ 训练任务: {train_result['task_id'][:8]}...")
    
    # 在GPU 1上推理
    print("\n在GPU 1上启动推理...")
    infer_result = client.start_inference(
        cfg_path="configs/model.yaml",
        weight_path="models/best.pth",
        source_path="data/test",
        device="cuda:1"
    )
    tasks.append(infer_result['task_id'])
    print(f"✅ 推理任务: {infer_result['task_id'][:8]}...")
    
    return tasks


def show_resource_status(client):
    """显示资源使用状态"""
    print_separator("📊 资源使用状态")
    
    resources = client.get_resources()
    
    print("\n设备使用情况:")
    for device, usage in resources['device_usage'].items():
        print(f"  {device}:")
        print(f"    训练任务: {usage['training']}")
        print(f"    推理任务: {usage['inference']}")
    
    print("\n资源限制:")
    for device, limits in resources['limits'].items():
        print(f"  {device}:")
        print(f"    最大训练任务: {limits['training']}")
        print(f"    最大推理任务: {limits['inference']}")
    
    print("\n活动任务:")
    for device, tasks in resources['active_tasks'].items():
        if tasks:
            print(f"  {device}: {len(tasks)} 个任务")
            for task in tasks:
                print(f"    - {task['id'][:8]}... ({task['type']})")


def main():
    """主函数"""
    print("\n" + "="*70)
    print("  🎮 GPU设备选择示例")
    print("  RFUAV Model Service V2.3")
    print("="*70)
    
    # 创建客户端
    client = RFUAVClient("http://localhost:8000")
    
    # 检查服务是否可用
    try:
        health = client.health_check()
        print(f"\n✅ 服务状态: {health['status']}")
        print(f"   版本: {health['version']}")
    except Exception as e:
        print(f"\n❌ 无法连接到服务: {e}")
        print("   请确保服务已启动: python app_refactored.py")
        return
    
    # 1. 显示GPU信息
    has_gpu = show_gpu_info(client)
    
    if not has_gpu:
        print("\n⚠️ 没有可用的GPU，示例将使用CPU")
    
    input("\n按Enter继续示例1...")
    
    # 2. 示例1: 自动选择
    # example_auto_selection(client)
    # show_resource_status(client)
    
    # input("\n按Enter继续示例2...")
    
    # 3. 示例2: 指定GPU
    # example_specific_gpu(client)
    # show_resource_status(client)
    
    # input("\n按Enter继续示例3...")
    
    # 4. 示例3: 多任务
    # example_multi_tasks(client)
    # show_resource_status(client)
    
    # input("\n按Enter继续示例4...")
    
    # 5. 示例4: 训练+推理
    # example_train_and_infer(client)
    # show_resource_status(client)
    
    print_separator("✅ 示例完成")
    
    print("\n💡 提示:")
    print("1. 使用 'cuda' 自动选择最优GPU（推荐）")
    print("2. 使用 'cuda:0', 'cuda:1' 指定具体GPU")
    print("3. 多GPU环境下系统自动负载均衡")
    print("4. 随时通过 /api/v2/resources 查看资源状态")
    print("\n详细文档: GPU_SELECTION_GUIDE.md")
    
    print("\n" + "="*70)


if __name__ == "__main__":
    main()


