# 并发场景使用指南

## 概述

V2.2.0 版本专门优化了训练和推理同时进行的场景，支持：
- ✅ 训练和推理任务并发执行
- ✅ 智能资源管理和调度
- ✅ 任务优先级队列
- ✅ 设备资源隔离
- ✅ 实时资源监控

## 核心特性

### 1. 资源管理

系统会自动管理GPU/CPU资源，确保任务不会相互干扰：

| 设备 | 最大训练并发 | 最大推理并发 | 说明 |
|------|-------------|-------------|------|
| GPU (CUDA) | 1 | 3 | 1个训练 + 3个推理可同时运行 |
| CPU | 2 | 4 | 2个训练 + 4个推理可同时运行 |

### 2. 任务队列

当资源不足时，任务会自动排队等待：
- **训练任务**: 默认优先级 5
- **推理任务**: 默认优先级 3（更高）
- 数字越小优先级越高（1-10）

### 3. 资源隔离

不同设备上的任务完全独立：
- GPU训练不会影响CPU推理
- 多个推理任务共享GPU资源
- 自动负载均衡

## 使用场景

### 场景1: 生产环境 - 训练时继续推理

**需求**: 在模型训练的同时，继续为用户提供推理服务

**配置**:
```python
# 训练任务 - 使用GPU，低优先级
train_config = {
    "model": "resnet50",
    "device": "cuda",
    "priority": 7,  # 低优先级
    # ... 其他参数
}

# 推理任务 - 使用GPU，高优先级
infer_config = {
    "device": "cuda",
    "priority": 2,  # 高优先级
    # ... 其他参数
}
```

### 场景2: 资源优化 - CPU训练 + GPU推理

**需求**: GPU专门用于快速推理，CPU用于后台训练

**配置**:
```python
# 训练任务 - 使用CPU
train_config = {
    "model": "mobilenet_v3_small",  # 轻量级模型
    "device": "cpu",
    "batch_size": 8,  # CPU时减小batch size
    # ... 其他参数
}

# 推理任务 - 使用GPU
infer_config = {
    "device": "cuda",
    "batch_size": 32,  # GPU可用大batch size
    # ... 其他参数
}
```

### 场景3: 批量推理 - 多任务并发

**需求**: 同时对多个数据集进行推理

**配置**:
```python
datasets = ["data1", "data2", "data3"]

for idx, dataset in enumerate(datasets):
    infer_config = {
        "source_path": dataset,
        "device": "cuda",
        "priority": 3,  # 相同优先级
        "task_id": f"infer_{idx}",
        # ... 其他参数
    }
    # 启动推理
```

## API使用

### 1. 启动训练任务

```python
import requests

config = {
    "model": "resnet18",
    "num_classes": 37,
    "train_path": "data/train",
    "val_path": "data/val",
    "device": "cuda",
    "priority": 5,  # 指定优先级
    # ... 其他参数
}

response = requests.post(
    "http://localhost:8000/api/v2/train",
    json=config
)
task_id = response.json()["task_id"]
```

### 2. 启动推理任务

```python
config = {
    "cfg_path": "configs/exp3.1_ResNet18.yaml",
    "weight_path": "models/best_model.pth",
    "source_path": "example/test_data/",
    "device": "cuda",
    "priority": 3,  # 推理优先级更高
}

response = requests.post(
    "http://localhost:8000/api/v2/inference",
    json=config
)
```

### 3. 查看资源状态

```python
response = requests.get("http://localhost:8000/api/v2/resources")
status = response.json()

print(f"GPU训练任务: {status['device_usage']['cuda']['training']}")
print(f"GPU推理任务: {status['device_usage']['cuda']['inference']}")
print(f"GPU显存信息: {status['gpu_memory_info']}")
```

### 4. 获取所有任务

```python
response = requests.get("http://localhost:8000/api/v2/tasks")
tasks = response.json()

print(f"训练任务数: {tasks['total_training']}")
print(f"推理任务数: {tasks['total_inference']}")
```

## 完整示例

### Python示例

```python
import requests
import time
import threading

API_BASE = "http://localhost:8000"

def start_training():
    """启动训练任务"""
    config = {
        "model": "resnet18",
        "num_classes": 37,
        "train_path": "data/train",
        "val_path": "data/val",
        "batch_size": 32,
        "num_epochs": 100,
        "device": "cuda",
        "save_path": "models/concurrent_train",
        "priority": 5
    }
    
    response = requests.post(f"{API_BASE}/api/v2/train", json=config)
    return response.json()["task_id"]

def start_inference():
    """启动推理任务"""
    config = {
        "cfg_path": "configs/exp3.1_ResNet18.yaml",
        "weight_path": "models/best_model.pth",
        "source_path": "example/test_data/",
        "device": "cuda",
        "priority": 3
    }
    
    response = requests.post(f"{API_BASE}/api/v2/inference", json=config)
    return response.json()["task_id"]

def monitor_resources():
    """监控资源使用"""
    while True:
        response = requests.get(f"{API_BASE}/api/v2/resources")
        status = response.json()
        
        print(f"\r资源状态 - 训练: {status['device_usage']['cuda']['training']}, "
              f"推理: {status['device_usage']['cuda']['inference']}", end="")
        
        time.sleep(2)

# 主流程
print("启动训练任务...")
train_id = start_training()
print(f"训练任务ID: {train_id}")

time.sleep(2)

print("启动推理任务...")
infer_id = start_inference()
print(f"推理任务ID: {infer_id}")

# 在后台监控资源
monitor_thread = threading.Thread(target=monitor_resources, daemon=True)
monitor_thread.start()

print("\n任务正在运行，按Ctrl+C停止...")
try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    print("\n停止监控")
```

### cURL示例

```bash
# 启动训练任务
curl -X POST "http://localhost:8000/api/v2/train" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "resnet18",
    "num_classes": 37,
    "train_path": "data/train",
    "val_path": "data/val",
    "device": "cuda",
    "priority": 5,
    "save_path": "models/test"
  }'

# 启动推理任务
curl -X POST "http://localhost:8000/api/v2/inference" \
  -H "Content-Type: application/json" \
  -d '{
    "cfg_path": "configs/exp3.1_ResNet18.yaml",
    "weight_path": "models/best_model.pth",
    "source_path": "example/test_data/",
    "device": "cuda",
    "priority": 3
  }'

# 查看资源状态
curl "http://localhost:8000/api/v2/resources"

# 查看所有任务
curl "http://localhost:8000/api/v2/tasks"
```

## 性能优化建议

### 1. GPU显存管理

```python
# 训练时减小batch size，为推理留出空间
train_config = {
    "batch_size": 16,  # 而不是32
    "device": "cuda"
}

# 推理时使用较小的batch size
infer_config = {
    "batch_size": 8,
    "device": "cuda"
}
```

### 2. 设备选择策略

```python
import torch

# 如果有多个GPU，可以指定不同GPU
if torch.cuda.device_count() > 1:
    train_config = {"device": "cuda:0"}
    infer_config = {"device": "cuda:1"}
else:
    # 单GPU时分时复用
    train_config = {"device": "cuda", "priority": 7}
    infer_config = {"device": "cuda", "priority": 3}
```

### 3. 优先级设置

```python
# 生产环境推理优先
real_time_infer = {"priority": 1}  # 最高
batch_infer = {"priority": 5}      # 中等
training = {"priority": 8}          # 最低

# 开发环境训练优先
training = {"priority": 2}
testing_infer = {"priority": 6}
```

### 4. 资源限制调整

```python
# 调整并发限制（通过API）
config = {
    "max_concurrent": {
        "cuda": {
            "training": 1,  # GPU上最多1个训练
            "inference": 5   # GPU上最多5个推理
        }
    }
}

requests.post(
    "http://localhost:8000/api/v2/resources/config",
    json=config
)
```

## 监控和调试

### 1. 实时监控资源

```python
def watch_resources():
    response = requests.get("http://localhost:8000/api/v2/resources")
    status = response.json()
    
    print("=== 资源状态 ===")
    print(f"GPU训练: {status['device_usage']['cuda']['training']}")
    print(f"GPU推理: {status['device_usage']['cuda']['inference']}")
    
    if status['gpu_memory_info']:
        for gpu, info in status['gpu_memory_info'].items():
            print(f"{gpu}: {info['allocated_gb']:.2f}GB / {info['total_gb']:.2f}GB")
```

### 2. 监控所有任务

```python
def list_all_tasks():
    response = requests.get("http://localhost:8000/api/v2/tasks")
    tasks = response.json()
    
    print("训练任务:")
    for task in tasks['training_tasks']:
        print(f"  {task['task_id'][:8]}: {task['status']}")
    
    print("推理任务:")
    for task in tasks['inference_tasks']:
        print(f"  {task['task_id'][:8]}: {task['status']}")
```

### 3. 实时日志流

```python
def stream_logs(task_id):
    response = requests.get(
        f"http://localhost:8000/api/v2/tasks/{task_id}/logs",
        stream=True
    )
    
    for line in response.iter_lines():
        if line:
            print(line.decode('utf-8'))
```

## 故障排除

### 问题1: 任务一直在排队

**原因**: 资源已满，等待其他任务完成

**解决**:
1. 检查资源状态: `GET /api/v2/resources`
2. 等待其他任务完成
3. 或者增加并发限制

### 问题2: GPU显存不足

**原因**: 训练和推理同时占用过多显存

**解决**:
```python
# 减小batch size
train_config = {"batch_size": 16}  # 从32降到16
infer_config = {"batch_size": 4}   # 从8降到4

# 或使用CPU
train_config = {"device": "cpu"}
```

### 问题3: 推理任务被阻塞

**原因**: 优先级设置不当

**解决**:
```python
# 提高推理优先级
infer_config = {"priority": 1}  # 最高优先级

# 降低训练优先级
train_config = {"priority": 9}  # 低优先级
```

## 最佳实践

1. **生产环境**: 推理优先级 > 训练优先级
2. **开发环境**: 灵活调整优先级
3. **显存管理**: 总batch size < 显存容量的70%
4. **监控**: 定期检查资源状态
5. **调优**: 根据实际情况调整并发限制

## 运行示例

```bash
# 1. 启动并发优化版服务
python app_concurrent.py

# 2. 运行并发示例
python concurrent_example.py

# 选择场景测试不同的并发模式
```

## API文档

完整API文档请访问: http://localhost:8000/docs

## 下一步

- 查看 `concurrent_example.py` 中的5个场景示例
- 阅读 `app_concurrent.py` 源码了解实现细节
- 根据实际需求调整资源配置

