# GPU设备选择指南

## 🎯 功能概述

RFUAV Model Service V2.3 支持灵活的GPU设备选择：
- ✅ 自动检测并显示所有可用GPU
- ✅ 支持指定具体GPU设备（cuda:0, cuda:1等）
- ✅ 支持自动选择最优GPU
- ✅ 多GPU环境下智能负载均衡
- ✅ 实时追踪每个GPU的任务情况

## 🚀 启动时GPU信息

启动服务时会自动输出GPU硬件信息：

```bash
python app_refactored.py
```

输出示例：
```
======================================================================
🚀 GPU硬件信息
======================================================================
✅ GPU可用
📦 CUDA版本: 11.8
🔧 PyTorch版本: 2.0.1
🎯 检测到 2 个GPU设备:

  GPU 0 (cuda:0)
  ├─ 型号: NVIDIA GeForce RTX 3090
  ├─ Compute Capability: 8.6
  ├─ 总显存: 24.00 GB
  ├─ 已用显存: 0.50 GB (2.1%)
  ├─ 空闲显存: 23.50 GB
  └─ 当前任务: 训练=0, 推理=0

  GPU 1 (cuda:1)
  ├─ 型号: NVIDIA GeForce RTX 3080
  ├─ Compute Capability: 8.6
  ├─ 总显存: 10.00 GB
  ├─ 已用显存: 0.30 GB (3.0%)
  ├─ 空闲显存: 9.70 GB
  └─ 当前任务: 训练=0, 推理=0

======================================================================
```

## 📋 设备选择方式

### 1. 自动选择（推荐）

使用 `cuda` 会自动选择最优GPU：

```json
{
  "device": "cuda"
}
```

**优势**：
- 系统自动选择负载最小的GPU
- 适合不关心具体GPU的场景
- 自动负载均衡

### 2. 指定具体GPU

```json
{
  "device": "cuda:0"  // 使用第一块GPU
}
```

```json
{
  "device": "cuda:1"  // 使用第二块GPU
}
```

**适用场景**：
- 需要固定使用某块GPU
- 特定模型适合特定GPU
- 手动负载均衡

### 3. 使用CPU

```json
{
  "device": "cpu"
}
```

**适用场景**：
- 没有GPU
- 测试小模型
- GPU资源紧张

## 🎓 训练时选择GPU

### Python客户端

```python
from test_refactored_api import RFUAVClient

client = RFUAVClient("http://localhost:8000")

# 方式1: 自动选择GPU
result = client.start_training(
    model="resnet18",
    num_classes=37,
    train_path="data/train",
    val_path="data/val",
    save_path="models/output",
    device="cuda"  # 自动选择
)

# 方式2: 指定GPU 0
result = client.start_training(
    model="resnet50",
    num_classes=37,
    train_path="data/train",
    val_path="data/val",
    save_path="models/output_gpu0",
    device="cuda:0"  # 指定GPU 0
)

# 方式3: 指定GPU 1
result = client.start_training(
    model="vit_b_16",
    num_classes=37,
    train_path="data/train",
    val_path="data/val",
    save_path="models/output_gpu1",
    device="cuda:1"  # 指定GPU 1
)
```

### cURL

```bash
# 自动选择
curl -X POST "http://localhost:8000/api/v2/training/start" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "resnet18",
    "num_classes": 37,
    "train_path": "data/train",
    "val_path": "data/val",
    "save_path": "models/output",
    "device": "cuda"
  }'

# 指定GPU 0
curl -X POST "http://localhost:8000/api/v2/training/start" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "resnet18",
    "num_classes": 37,
    "train_path": "data/train",
    "val_path": "data/val",
    "save_path": "models/output",
    "device": "cuda:0"
  }'
```

## 🔍 推理时选择GPU

### Python客户端

```python
# 自动选择
result = client.start_inference(
    cfg_path="configs/model.yaml",
    weight_path="models/best.pth",
    source_path="data/test",
    device="cuda"
)

# 指定GPU 1
result = client.start_inference(
    cfg_path="configs/model.yaml",
    weight_path="models/best.pth",
    source_path="data/test",
    device="cuda:1"
)
```

### cURL

```bash
# 指定GPU 0
curl -X POST "http://localhost:8000/api/v2/inference/start" \
  -H "Content-Type: application/json" \
  -d '{
    "cfg_path": "configs/model.yaml",
    "weight_path": "models/best.pth",
    "source_path": "data/test",
    "device": "cuda:0"
  }'
```

## 📊 查看GPU使用情况

### 查看资源状态

```bash
curl http://localhost:8000/api/v2/resources
```

响应示例：
```json
{
  "device_usage": {
    "cuda:0": {
      "training": 1,
      "inference": 2
    },
    "cuda:1": {
      "training": 0,
      "inference": 1
    }
  },
  "active_tasks": {
    "cuda:0": [
      {"id": "task1", "type": "training"},
      {"id": "task2", "type": "inference"}
    ]
  },
  "limits": {
    "cuda:0": {
      "training": 1,
      "inference": 3
    }
  }
}
```

### 查看GPU详细信息

```bash
curl http://localhost:8000/api/v2/resources/gpu
```

响应示例：
```json
{
  "available": true,
  "count": 2,
  "cuda_version": "11.8",
  "pytorch_version": "2.0.1",
  "devices": [
    {
      "id": 0,
      "device_name": "cuda:0",
      "name": "NVIDIA GeForce RTX 3090",
      "compute_capability": "8.6",
      "total_memory_gb": 24.0,
      "allocated_memory_gb": 8.5,
      "cached_memory_gb": 10.2,
      "free_memory_gb": 15.5,
      "utilization": 35.4,
      "current_tasks": {
        "training": 1,
        "inference": 2
      }
    },
    {
      "id": 1,
      "device_name": "cuda:1",
      "name": "NVIDIA GeForce RTX 3080",
      "compute_capability": "8.6",
      "total_memory_gb": 10.0,
      "allocated_memory_gb": 2.1,
      "cached_memory_gb": 3.5,
      "free_memory_gb": 7.9,
      "utilization": 21.0,
      "current_tasks": {
        "training": 0,
        "inference": 1
      }
    }
  ]
}
```

## 🎯 最佳实践

### 1. 单GPU环境

```python
# 使用 cuda 或 cuda:0 都可以
device="cuda"  # 推荐
device="cuda:0"  # 也可以
```

### 2. 双GPU环境

**策略1：自动均衡**
```python
# 训练和推理都使用自动选择
device="cuda"  # 系统自动选择负载最小的GPU
```

**策略2：训练和推理分离**
```python
# 训练固定在GPU 0
training_device = "cuda:0"

# 推理固定在GPU 1
inference_device = "cuda:1"
```

**策略3：大小模型分离**
```python
# 大模型使用显存大的GPU
large_model_device = "cuda:0"  # 假设RTX 3090

# 小模型使用显存小的GPU
small_model_device = "cuda:1"  # 假设RTX 3080
```

### 3. 多GPU环境（3+）

**策略：按GPU能力分配**
```python
# 高性能GPU用于训练
training_devices = ["cuda:0", "cuda:1"]

# 中低性能GPU用于推理
inference_devices = ["cuda:2", "cuda:3"]
```

## 🔧 高级配置

### 调整每个GPU的并发限制

```bash
curl -X POST "http://localhost:8000/api/v2/resources/config" \
  -H "Content-Type: application/json" \
  -d '{
    "max_concurrent": {
      "cuda:0": {
        "training": 1,
        "inference": 4
      },
      "cuda:1": {
        "training": 2,
        "inference": 6
      }
    }
  }'
```

## 📈 性能优化建议

### 1. 显存管理

**大模型训练**：
```python
# 使用显存最大的GPU
device = "cuda:0"  # 假设是24GB的RTX 3090
batch_size = 32
```

**小批次推理**：
```python
# 可以在任何GPU上运行
device = "cuda"  # 自动选择
batch_size = 8
```

### 2. 并发控制

**单GPU多任务**：
- 训练：1个任务（占用大量显存）
- 推理：3-5个任务（显存占用小）

**多GPU负载均衡**：
```python
# 训练任务
train_tasks = [
    {"device": "cuda:0", ...},
    {"device": "cuda:1", ...},
]

# 推理任务自动分配
infer_tasks = [
    {"device": "cuda", ...},  # 系统自动选择
    {"device": "cuda", ...},
]
```

### 3. 避免显存碎片

**建议**：
- 同类型任务放在同一GPU
- 避免频繁切换设备
- 定期清理完成的任务

## 🐛 故障排查

### 问题1：指定的GPU不存在

**错误**：
```
RuntimeError: Device index 2 is out of range
```

**解决**：
```bash
# 查看可用GPU数量
curl http://localhost:8000/api/v2/resources/gpu

# 使用正确的设备编号（从0开始）
device = "cuda:0"  # 或 "cuda:1"
```

### 问题2：GPU显存不足

**错误**：
```
RuntimeError: CUDA out of memory
```

**解决**：
```python
# 方案1：降低batch_size
batch_size = 8  # 从16降到8

# 方案2：使用显存更大的GPU
device = "cuda:0"  # 切换到24GB的GPU

# 方案3：使用CPU
device = "cpu"
```

### 问题3：GPU被占用

**现象**：任务一直排队

**检查**：
```bash
# 查看GPU使用情况
curl http://localhost:8000/api/v2/resources

# 查看活动任务
curl http://localhost:8000/api/v2/tasks
```

**解决**：
```python
# 方案1：使用其他GPU
device = "cuda:1"

# 方案2：等待任务完成

# 方案3：取消不必要的任务
curl -X POST "http://localhost:8000/api/v2/tasks/{task_id}/cancel"
```

## 💡 实战示例

### 示例1：多模型并行训练

```python
client = RFUAVClient()

# 在GPU 0上训练ResNet
task1 = client.start_training(
    model="resnet50",
    num_classes=37,
    train_path="data/train",
    val_path="data/val",
    save_path="models/resnet50",
    device="cuda:0"
)

# 在GPU 1上训练ViT
task2 = client.start_training(
    model="vit_b_16",
    num_classes=37,
    train_path="data/train",
    val_path="data/val",
    save_path="models/vit",
    device="cuda:1"
)

print(f"ResNet训练任务: {task1['task_id']}")
print(f"ViT训练任务: {task2['task_id']}")
```

### 示例2：训练+推理同时进行

```python
# 在GPU 0上训练
training_task = client.start_training(
    model="resnet18",
    device="cuda:0",
    ...
)

# 在GPU 1上推理（使用已训练的模型）
inference_task = client.start_inference(
    cfg_path="configs/trained_model.yaml",
    weight_path="models/trained.pth",
    source_path="data/test",
    device="cuda:1"
)
```

### 示例3：批量推理负载均衡

```python
# 自动分配到不同GPU
test_paths = [
    "data/test1",
    "data/test2",
    "data/test3",
    "data/test4"
]

tasks = []
for path in test_paths:
    task = client.start_inference(
        cfg_path="configs/model.yaml",
        weight_path="models/best.pth",
        source_path=path,
        device="cuda"  # 自动选择最优GPU
    )
    tasks.append(task)

print(f"已启动 {len(tasks)} 个推理任务")
```

## 📚 相关文档

- [快速开始](QUICK_START_REFACTORED.md)
- [API路由表](API_ROUTES_TABLE.md)
- [项目结构](REFACTORED_STRUCTURE.md)
- [资源管理API](API_ROUTES_TABLE.md#资源管理接口)

---

## 🎉 总结

GPU设备选择功能特点：
- ✅ 简单易用 - 支持自动选择和手动指定
- ✅ 智能调度 - 自动选择负载最小的GPU
- ✅ 灵活配置 - 支持运行时调整
- ✅ 实时监控 - 随时查看GPU使用情况
- ✅ 多GPU支持 - 充分利用所有GPU资源

开始使用GPU设备选择，让您的深度学习任务更高效！🚀


