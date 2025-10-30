# 设备选择说明

## 概述

所有训练、推理和基准测试接口都支持通过请求体指定运行设备（CPU或GPU）。

## 支持的设备类型

- **`cuda`** - 使用NVIDIA GPU（需要CUDA支持）
- **`cpu`** - 使用CPU

## API接口设备参数

### 1. 训练接口 `/api/v2/train`

**参数**: `device`（可选，默认值：`cuda`）

```json
{
  "model": "resnet18",
  "num_classes": 37,
  "train_path": "data/train",
  "val_path": "data/val",
  "batch_size": 32,
  "num_epochs": 100,
  "learning_rate": 0.0001,
  "save_path": "models/resnet18_exp",
  "device": "cuda"  // 或 "cpu"
}
```

### 2. 推理接口 `/api/v1/inference`

**参数**: `device`（可选，默认值：`cuda`）

```json
{
  "cfg_path": "configs/exp3.1_ResNet18.yaml",
  "weight_path": "models/best_model.pth",
  "source_path": "example/test_data/",
  "save_path": "results/inference/",
  "device": "cpu"  // 使用CPU进行推理
}
```

### 3. 基准测试接口 `/api/v1/benchmark`

**参数**: `device`（可选，默认值：`cuda`）

```json
{
  "cfg_path": "configs/exp3.1_ResNet18.yaml",
  "weight_path": "models/best_model.pth",
  "data_path": "data/benchmark/",
  "save_path": "results/benchmark/",
  "device": "cuda"  // 使用GPU进行测试
}
```

## 使用示例

### Python示例

#### 训练 - 使用CPU
```python
import requests

config = {
    "model": "resnet18",
    "num_classes": 37,
    "train_path": "data/train",
    "val_path": "data/val",
    "batch_size": 16,  # CPU时建议减小batch size
    "num_epochs": 100,
    "learning_rate": 0.0001,
    "save_path": "models/resnet18_cpu",
    "device": "cpu"  # 使用CPU
}

response = requests.post("http://localhost:8000/api/v2/train", json=config)
print(response.json())
```

#### 推理 - 使用GPU
```python
import requests

inference_config = {
    "cfg_path": "configs/exp3.1_ResNet18.yaml",
    "weight_path": "models/best_model.pth",
    "source_path": "example/test_data/",
    "device": "cuda"  # 使用GPU
}

response = requests.post("http://localhost:8000/api/v1/inference", json=inference_config)
result = response.json()
print(f"推理完成，使用设备: {result['device']}")
```

#### 基准测试 - 动态选择设备
```python
import requests
import torch

# 根据可用性自动选择设备
device = "cuda" if torch.cuda.is_available() else "cpu"

benchmark_config = {
    "cfg_path": "configs/exp3.1_ResNet18.yaml",
    "weight_path": "models/best_model.pth",
    "data_path": "data/benchmark/",
    "device": device
}

response = requests.post("http://localhost:8000/api/v1/benchmark", json=benchmark_config)
print(response.json())
```

### cURL示例

#### 训练 - 使用GPU
```bash
curl -X POST "http://localhost:8000/api/v2/train" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "resnet18",
    "num_classes": 37,
    "train_path": "data/train",
    "val_path": "data/val",
    "batch_size": 32,
    "num_epochs": 100,
    "learning_rate": 0.0001,
    "save_path": "models/resnet18_gpu",
    "device": "cuda"
  }'
```

#### 推理 - 使用CPU
```bash
curl -X POST "http://localhost:8000/api/v1/inference" \
  -H "Content-Type: application/json" \
  -d '{
    "cfg_path": "configs/exp3.1_ResNet18.yaml",
    "weight_path": "models/best_model.pth",
    "source_path": "example/test_data/",
    "device": "cpu"
  }'
```

#### 基准测试 - 使用GPU
```bash
curl -X POST "http://localhost:8000/api/v1/benchmark" \
  -H "Content-Type: application/json" \
  -d '{
    "cfg_path": "configs/exp3.1_ResNet18.yaml",
    "weight_path": "models/best_model.pth",
    "data_path": "data/benchmark/",
    "device": "cuda"
  }'
```

### JavaScript示例

```javascript
// 训练 - 使用GPU
async function trainModel() {
    const config = {
        model: "resnet18",
        num_classes: 37,
        train_path: "data/train",
        val_path: "data/val",
        batch_size: 32,
        num_epochs: 100,
        learning_rate: 0.0001,
        save_path: "models/resnet18_exp",
        device: "cuda"  // 指定GPU
    };

    const response = await fetch('/api/v2/train', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify(config)
    });

    const result = await response.json();
    console.log('任务ID:', result.task_id);
}

// 推理 - 使用CPU
async function runInference() {
    const config = {
        cfg_path: "configs/exp3.1_ResNet18.yaml",
        weight_path: "models/best_model.pth",
        source_path: "example/test_data/",
        device: "cpu"  // 指定CPU
    };

    const response = await fetch('/api/v1/inference', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify(config)
    });

    const result = await response.json();
    console.log('推理结果:', result);
}
```

## 性能对比

| 任务类型 | GPU (CUDA) | CPU |
|---------|-----------|-----|
| 训练速度 | ⚡⚡⚡⚡⚡ | ⚡ |
| 推理速度 | ⚡⚡⚡⚡ | ⚡⚡ |
| 内存占用 | 高（显存） | 中（内存） |
| 适用场景 | 大规模训练、快速推理 | 小规模实验、CPU环境 |

## 设备选择建议

### 训练
- **推荐使用GPU** - 训练速度快5-50倍
- **CPU适用于**: 小数据集实验、没有GPU的环境

### 推理
- **GPU适用于**: 大批量推理、实时性要求高
- **CPU适用于**: 单张图片推理、资源受限环境

### 基准测试
- **GPU** - 快速获得结果
- **CPU** - 评估模型在CPU环境下的性能

## 注意事项

1. **CUDA可用性检查**
   ```python
   import torch
   print(f"CUDA可用: {torch.cuda.is_available()}")
   print(f"CUDA版本: {torch.version.cuda}")
   print(f"GPU数量: {torch.cuda.device_count()}")
   ```

2. **内存管理**
   - GPU: 注意显存大小，batch_size不要过大
   - CPU: 注意内存占用，可能需要更小的batch_size

3. **批次大小调整**
   - GPU: 可以使用较大的batch_size（如32, 64, 128）
   - CPU: 建议使用较小的batch_size（如4, 8, 16）

4. **自动回退**
   ```python
   # 推荐：自动检测并选择设备
   import torch
   device = "cuda" if torch.cuda.is_available() else "cpu"
   
   config = {
       # ... 其他配置
       "device": device
   }
   ```

5. **配置文件覆盖**
   - 请求体中的`device`参数会覆盖配置文件中的设置
   - 推理和基准测试会创建临时配置文件以应用新的设备设置

## 错误处理

### CUDA不可用错误
如果指定`device="cuda"`但系统不支持CUDA，会出现错误：

**解决方法**:
1. 改用`device="cpu"`
2. 安装CUDA和对应版本的PyTorch
3. 检查GPU驱动是否正确安装

### 显存不足错误
如果出现`CUDA out of memory`错误：

**解决方法**:
1. 减小`batch_size`
2. 使用更小的模型
3. 清理GPU缓存：`torch.cuda.empty_cache()`

## 测试客户端

使用测试客户端时，可以在交互式菜单中指定设备：

```bash
python test_api_client.py
```

选择推理选项时会提示：
```
推理设备 [cuda]: cpu
```

输入`cpu`或`cuda`即可指定设备。

