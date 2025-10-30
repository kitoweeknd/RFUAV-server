"""
测试数据预处理API接口

演示如何使用数据集分割、数据增强和图像裁剪功能
"""
import requests
import json
import time
from typing import Dict, Any


BASE_URL = "http://localhost:8000"


def print_section(title: str):
    """打印分节标题"""
    print("\n" + "=" * 60)
    print(f"  {title}")
    print("=" * 60)


def print_task_info(task: Dict[str, Any]):
    """打印任务信息"""
    print(f"✓ 任务ID: {task['task_id']}")
    print(f"  类型: {task['task_type']}")
    print(f"  状态: {task['status']}")
    print(f"  进度: {task.get('progress', 0)}%")
    if task.get('message'):
        print(f"  消息: {task['message']}")
    if task.get('input_path'):
        print(f"  输入: {task['input_path']}")
    if task.get('output_path'):
        print(f"  输出: {task['output_path']}")
    if task.get('stats'):
        print(f"  统计信息: {json.dumps(task['stats'], indent=2, ensure_ascii=False)}")


def test_dataset_split():
    """测试数据集分割"""
    print_section("1. 数据集分割测试")
    
    # 准备请求数据（请根据实际情况修改路径）
    request_data = {
        "input_path": "D:/ML_Project/RFUAV-server/data/raw_dataset",
        "output_path": "D:/ML_Project/RFUAV-server/data/split_dataset",
        "train_ratio": 0.7,
        "val_ratio": 0.2,  # 剩余0.1作为测试集
        "description": "分割数据集为train/val/test"
    }
    
    print("\n发送请求...")
    print(f"输入路径: {request_data['input_path']}")
    print(f"输出路径: {request_data['output_path']}")
    print(f"分割比例: train={request_data['train_ratio']}, val={request_data['val_ratio']}, test=0.1")
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/v2/preprocessing/split",
            json=request_data
        )
        
        if response.status_code == 200:
            task = response.json()
            print("\n✓ 任务已创建")
            print_task_info(task)
            
            # 监控任务进度
            task_id = task['task_id']
            print("\n监控任务进度...")
            monitor_task(task_id, "/api/v2/preprocessing")
            
        else:
            print(f"\n✗ 请求失败: {response.status_code}")
            print(f"  错误: {response.text}")
    
    except Exception as e:
        print(f"\n✗ 发生错误: {str(e)}")


def test_data_augmentation():
    """测试数据增强"""
    print_section("2. 数据增强测试")
    
    # 准备请求数据
    request_data = {
        "dataset_path": "D:/ML_Project/RFUAV-server/data/split_dataset",
        "output_path": "D:/ML_Project/RFUAV-server/data/augmented_dataset",
        "methods": ["CLAHE", "ColorJitter", "GaussNoise"],  # 指定使用的增强方法
        "description": "对数据集进行增强"
    }
    
    print("\n发送请求...")
    print(f"数据集路径: {request_data['dataset_path']}")
    print(f"输出路径: {request_data['output_path']}")
    print(f"增强方法: {', '.join(request_data['methods'])}")
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/v2/preprocessing/augment",
            json=request_data
        )
        
        if response.status_code == 200:
            task = response.json()
            print("\n✓ 任务已创建")
            print_task_info(task)
            
            # 监控任务进度
            task_id = task['task_id']
            print("\n监控任务进度...")
            monitor_task(task_id, "/api/v2/preprocessing")
            
        else:
            print(f"\n✗ 请求失败: {response.status_code}")
            print(f"  错误: {response.text}")
    
    except Exception as e:
        print(f"\n✗ 发生错误: {str(e)}")


def test_image_crop():
    """测试图像裁剪"""
    print_section("3. 图像裁剪测试")
    
    # 准备请求数据
    request_data = {
        "input_path": "D:/ML_Project/RFUAV-server/data/test_images",
        "output_path": "D:/ML_Project/RFUAV-server/data/cropped_images",
        "x": 100,
        "y": 100,
        "width": 500,
        "height": 500,
        "description": "裁剪图像中心区域"
    }
    
    print("\n发送请求...")
    print(f"输入路径: {request_data['input_path']}")
    print(f"输出路径: {request_data['output_path']}")
    print(f"裁剪区域: ({request_data['x']}, {request_data['y']}, {request_data['width']}, {request_data['height']})")
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/v2/preprocessing/crop",
            json=request_data
        )
        
        if response.status_code == 200:
            task = response.json()
            print("\n✓ 任务已创建")
            print_task_info(task)
            
            # 监控任务进度
            task_id = task['task_id']
            print("\n监控任务进度...")
            monitor_task(task_id, "/api/v2/preprocessing")
            
        else:
            print(f"\n✗ 请求失败: {response.status_code}")
            print(f"  错误: {response.text}")
    
    except Exception as e:
        print(f"\n✗ 发生错误: {str(e)}")


def monitor_task(task_id: str, endpoint_prefix: str, check_interval: int = 2):
    """监控任务进度"""
    while True:
        try:
            response = requests.get(f"{BASE_URL}{endpoint_prefix}/{task_id}")
            if response.status_code == 200:
                task = response.json()
                status = task['status']
                progress = task.get('progress', 0)
                message = task.get('message', '')
                
                print(f"  [{status}] {progress}% - {message}")
                
                if status in ['completed', 'failed', 'cancelled']:
                    print("\n最终状态:")
                    print_task_info(task)
                    break
            else:
                print(f"  查询失败: {response.status_code}")
                break
            
            time.sleep(check_interval)
            
        except KeyboardInterrupt:
            print("\n\n用户中断监控")
            break
        except Exception as e:
            print(f"  监控错误: {str(e)}")
            break


def test_api_docs():
    """测试API文档访问"""
    print_section("API文档")
    
    print("\n可以通过以下地址访问API文档:")
    print(f"  Swagger UI: {BASE_URL}/docs")
    print(f"  ReDoc: {BASE_URL}/redoc")
    print("\n在浏览器中打开上述地址可以查看完整的API文档和测试接口")


def main():
    """主测试函数"""
    print("\n" + "=" * 60)
    print("  数据预处理API测试")
    print("=" * 60)
    print("\n注意：请先修改测试脚本中的路径为您实际的数据路径")
    print("      然后确保服务已启动（python app_refactored.py）")
    
    # 显示API文档信息
    test_api_docs()
    
    # 提示用户
    print("\n" + "=" * 60)
    print("可用的测试选项:")
    print("  1. 测试数据集分割")
    print("  2. 测试数据增强")
    print("  3. 测试图像裁剪")
    print("  4. 运行所有测试")
    print("=" * 60)
    
    choice = input("\n请选择测试选项 (1/2/3/4) 或按Enter退出: ")
    
    if choice == "1":
        test_dataset_split()
    elif choice == "2":
        test_data_augmentation()
    elif choice == "3":
        test_image_crop()
    elif choice == "4":
        test_dataset_split()
        time.sleep(2)
        test_data_augmentation()
        time.sleep(2)
        test_image_crop()
    else:
        print("\n退出测试")
    
    print("\n" + "=" * 60)
    print("  测试完成")
    print("=" * 60)


# 使用示例函数
def example_usage():
    """
    使用示例 - 可以直接复制这些代码到您的项目中
    """
    
    # ========== 1. 数据集分割 ==========
    # 将原始数据集按比例分割为训练集、验证集和测试集
    split_request = {
        "input_path": "path/to/raw_dataset",
        "output_path": "path/to/split_dataset",
        "train_ratio": 0.7,  # 70% 训练集
        "val_ratio": 0.2,    # 20% 验证集，剩余10%作为测试集
    }
    response = requests.post(f"{BASE_URL}/api/v2/preprocessing/split", json=split_request)
    task = response.json()
    
    # ========== 2. 数据增强 ==========
    # 对已分割的数据集进行数据增强
    augment_request = {
        "dataset_path": "path/to/split_dataset",
        "output_path": "path/to/augmented_dataset",
        "methods": ["CLAHE", "ColorJitter", "GaussNoise"],  # 可选，不指定则使用全部6种方法
    }
    response = requests.post(f"{BASE_URL}/api/v2/preprocessing/augment", json=augment_request)
    task = response.json()
    
    # ========== 3. 图像裁剪 ==========
    # 裁剪图像的指定区域
    crop_request = {
        "input_path": "path/to/images",
        "output_path": "path/to/cropped_images",
        "x": 100,
        "y": 100,
        "width": 500,
        "height": 500,
    }
    response = requests.post(f"{BASE_URL}/api/v2/preprocessing/crop", json=crop_request)
    task = response.json()
    
    # ========== 4. 查询任务状态 ==========
    task_id = task['task_id']
    response = requests.get(f"{BASE_URL}/api/v2/preprocessing/{task_id}")
    task_status = response.json()
    
    # ========== 5. 实时获取日志 ==========
    # 使用Server-Sent Events获取实时日志
    response = requests.get(f"{BASE_URL}/api/v2/preprocessing/{task_id}/logs", stream=True)
    for line in response.iter_lines():
        if line:
            log_entry = json.loads(line.decode('utf-8')[6:])  # 移除 "data: " 前缀
            print(f"[{log_entry['level']}] {log_entry['message']}")


if __name__ == "__main__":
    main()

