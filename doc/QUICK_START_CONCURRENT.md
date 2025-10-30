# 并发版本快速开始

## 30秒快速体验

```bash
# 1. 启动服务
python app_concurrent.py

# 2. 运行示例（新终端）
python concurrent_example.py

# 3. 选择场景1
```

## 5分钟完整演示

### 步骤1: 启动服务 (1分钟)

```bash
# 安装依赖
pip install -r requirements_enhanced.txt

# 启动并发优化版服务
python app_concurrent.py
```

看到以下输出表示成功：
```
INFO: Application startup complete.
INFO: Uvicorn running on http://0.0.0.0:8000
```

### 步骤2: 测试基础功能 (2分钟)

打开新终端，运行：

```python
import requests

# 检查服务
response = requests.get("http://localhost:8000")
print(response.json())

# 查看资源状态
response = requests.get("http://localhost:8000/api/v2/resources")
print(response.json())
```

### 步骤3: 启动并发任务 (2分钟)

```python
import requests

API_BASE = "http://localhost:8000"

# 启动训练任务
train_config = {
    "model": "resnet18",
    "num_classes": 37,
    "train_path": "data/train",
    "val_path": "data/val",
    "batch_size": 32,
    "num_epochs": 10,
    "device": "cuda",
    "save_path": "models/test",
    "priority": 5
}

train_response = requests.post(f"{API_BASE}/api/v2/train", json=train_config)
train_id = train_response.json()["task_id"]
print(f"训练任务ID: {train_id}")

# 启动推理任务（与训练同时进行）
infer_config = {
    "cfg_path": "configs/exp3.1_ResNet18.yaml",
    "weight_path": "models/best_model.pth",
    "source_path": "example/test_data/",
    "device": "cuda",
    "priority": 3  # 优先级高于训练
}

infer_response = requests.post(f"{API_BASE}/api/v2/inference", json=infer_config)
infer_id = infer_response.json()["task_id"]
print(f"推理任务ID: {infer_id}")

# 查看资源使用
response = requests.get(f"{API_BASE}/api/v2/resources")
status = response.json()
print(f"\nGPU训练任务: {status['device_usage']['cuda']['training']}")
print(f"GPU推理任务: {status['device_usage']['cuda']['inference']}")
```

## 常用场景

### 场景A: 生产环境（推荐配置）

```python
# GPU专用于推理，CPU用于训练
train_config = {
    "model": "mobilenet_v3_small",  # 轻量级模型
    "device": "cpu",                # CPU训练
    "batch_size": 8,
    "priority": 7,                  # 低优先级
    # ... 其他参数
}

infer_config = {
    "device": "cuda",               # GPU推理
    "priority": 2,                  # 高优先级
    # ... 其他参数
}
```

### 场景B: 批量推理

```python
# 同时处理多个数据集
datasets = [
    "data/dataset1/",
    "data/dataset2/",
    "data/dataset3/"
]

for dataset in datasets:
    config = {
        "cfg_path": "configs/exp3.1_ResNet18.yaml",
        "weight_path": "models/best_model.pth",
        "source_path": dataset,
        "device": "cuda",
        "priority": 3
    }
    
    response = requests.post(f"{API_BASE}/api/v2/inference", json=config)
    print(f"推理任务已启动: {dataset}")

# 系统会自动调度，最多3个同时运行
```

### 场景C: 开发测试

```python
# 训练新模型时，测试旧模型
train_config = {
    "model": "resnet50",
    "device": "cuda",
    "priority": 6,  # 中等优先级
    # ... 其他参数
}

test_infer_config = {
    "device": "cuda",
    "priority": 4,  # 略高优先级
    # ... 其他参数
}
```

## 监控命令

### 实时监控资源

```python
import requests
import time

while True:
    response = requests.get("http://localhost:8000/api/v2/resources")
    status = response.json()
    
    print(f"\r训练: {status['device_usage']['cuda']['training']}, "
          f"推理: {status['device_usage']['cuda']['inference']}", end="")
    
    time.sleep(2)
```

### 查看所有任务

```python
response = requests.get("http://localhost:8000/api/v2/tasks")
tasks = response.json()

print(f"训练任务: {tasks['total_training']}")
print(f"推理任务: {tasks['total_inference']}")

for task in tasks['training_tasks']:
    print(f"  {task['task_id'][:8]}: {task['status']}")
```

### 查看任务日志

```python
response = requests.get(
    f"http://localhost:8000/api/v2/tasks/{task_id}/logs",
    stream=True
)

for line in response.iter_lines():
    if line:
        print(line.decode('utf-8'))
```

## 配置调优

### 增加推理并发数

```python
# 如果GPU显存充足，可以增加并发数
config = {
    "max_concurrent": {
        "cuda": {
            "training": 1,
            "inference": 5  # 从默认3增加到5
        }
    }
}

requests.post(
    "http://localhost:8000/api/v2/resources/config",
    json=config
)
```

### 优先级设置建议

```python
# 生产环境
实时推理 = 1-2    # 最高
批量推理 = 3-5    # 中高
后台训练 = 7-9    # 最低

# 开发环境
快速实验 = 2-3
正常训练 = 4-6
测试任务 = 7-9
```

## 常见问题

### Q: 任务一直在排队？
**A**: 资源已满，等待其他任务完成。查看资源状态：
```python
requests.get("http://localhost:8000/api/v2/resources")
```

### Q: GPU显存不足？
**A**: 减小batch_size或使用CPU：
```python
config = {
    "batch_size": 8,  # 从32降到8
    # 或
    "device": "cpu"
}
```

### Q: 推理被训练阻塞？
**A**: 提高推理优先级：
```python
infer_config = {"priority": 1}  # 最高优先级
train_config = {"priority": 9}  # 最低优先级
```

## 完整示例脚本

### 示例1: 简单并发

```python
#!/usr/bin/env python3
"""简单并发示例"""
import requests
import time

API_BASE = "http://localhost:8000"

def main():
    # 启动训练
    print("启动训练...")
    train_config = {
        "model": "resnet18",
        "num_classes": 37,
        "train_path": "data/train",
        "val_path": "data/val",
        "device": "cuda",
        "save_path": "models/test",
        "priority": 5
    }
    
    response = requests.post(f"{API_BASE}/api/v2/train", json=train_config)
    train_id = response.json()["task_id"]
    print(f"训练ID: {train_id[:8]}")
    
    # 等待2秒
    time.sleep(2)
    
    # 启动推理
    print("启动推理...")
    infer_config = {
        "cfg_path": "configs/exp3.1_ResNet18.yaml",
        "weight_path": "models/best_model.pth",
        "source_path": "example/test_data/",
        "device": "cuda",
        "priority": 3
    }
    
    response = requests.post(f"{API_BASE}/api/v2/inference", json=infer_config)
    infer_id = response.json()["task_id"]
    print(f"推理ID: {infer_id[:8]}")
    
    # 监控资源
    print("\n监控中...")
    for _ in range(10):
        response = requests.get(f"{API_BASE}/api/v2/resources")
        status = response.json()
        print(f"训练: {status['device_usage']['cuda']['training']}, "
              f"推理: {status['device_usage']['cuda']['inference']}")
        time.sleep(3)

if __name__ == "__main__":
    main()
```

### 示例2: 使用预设示例

```bash
# 最简单的方式
python concurrent_example.py

# 按提示选择场景
```

## 下一步

1. ✅ 运行 `concurrent_example.py` 体验5个场景
2. 📖 阅读 `CONCURRENT_USAGE.md` 了解详细用法
3. 📊 阅读 `VERSION_COMPARISON.md` 了解版本差异
4. 🔧 根据需求调整资源配置

## 文档链接

- [并发使用指南](CONCURRENT_USAGE.md)
- [版本对比](VERSION_COMPARISON.md)
- [完整总结](SUMMARY.md)
- [API文档](http://localhost:8000/docs)

## 技术支持

- 示例代码: `concurrent_example.py`
- 源码: `app_concurrent.py`
- 在线文档: http://localhost:8000/docs

