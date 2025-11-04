# API路由表 - 完整参考

> **版本**: V2.4.0 | **更新日期**: 2025-10-29

## 📋 路由总览

访问 http://localhost:8000/ 可查看交互式路由表。

## 🗺️ 路由结构

```
/                                   # 根路径 - API概览
│
├── /api/v1/                       # V1版本 - 系统接口
│   ├── /health                    # 健康检查
│   └── /info                      # 系统信息
│
└── /api/v2/                       # V2版本 - 核心功能
    ├── /preprocessing/            # 数据预处理 ⭐新
    │   ├── /split                 # 数据集分割
    │   ├── /augment               # 数据增强
    │   ├── /crop                  # 图像裁剪
    │   ├── /{id}                  # 查询状态
    │   └── /{id}/logs             # 获取日志流
    │
    ├── /training/                 # 训练接口
    │   ├── /start                 # 启动训练
    │   ├── /{id}                  # 查询状态（含详细指标）
    │   ├── /{id}/logs             # 获取日志流（含训练指标）
    │   └── /{id}/stop             # 停止训练
    │
    ├── /inference/                # 推理接口
    │   ├── /start                 # 启动推理
    │   ├── /batch                 # 批量推理
    │   └── /{id}                  # 查询状态
    │
    ├── /tasks/                    # 任务管理
    │   ├── /                      # 所有任务
    │   ├── /{id}                  # 任务详情
    │   ├── /{id}/logs             # 任务日志
    │   ├── /{id}/cancel           # 取消任务
    │   └── /{id}                  # 删除任务 (DELETE)
    │
    └── /resources/                # 资源管理
        ├── /                      # 资源状态
        ├── /cpu                   # CPU信息 ⭐新
        ├── /gpu                   # GPU信息
        └── /config                # 更新配置
```

## 📖 详细接口说明

---

### 🏠 根路径

#### `GET /`
**功能**: API概览和路由表

**响应**:
```json
{
  "name": "RFUAV Model Service",
  "version": "2.3.0",
  "features": [...],
  "endpoints": {...}
}
```

**示例**:
```bash
curl http://localhost:8000/
```

---

## 🔧 数据预处理接口 ⭐新

### `POST /api/v2/preprocessing/split`
**功能**: 数据集分割（train/val/test）

**请求体**:
```json
{
  "input_path": "data/raw_dataset",
  "output_path": "data/split_dataset",
  "train_ratio": 0.7,
  "val_ratio": 0.2,
  "task_id": "可选的自定义任务ID",
  "description": "数据集分割任务"
}
```

**参数说明**:
- `input_path`: 输入数据集路径（必需）
- `output_path`: 输出数据集路径（必需）
- `train_ratio`: 训练集比例（0.1-0.9），默认0.8
- `val_ratio`: 验证集比例（可选，0.05-0.5）
  - 不指定：二分割（train/valid）
  - 指定：三分割（train/valid/test）
- `task_id`: 自定义任务ID（可选）
- `description`: 任务描述（可选）

**响应**:
```json
{
  "task_id": "550e8400-e29b-41d4-a716-446655440000",
  "task_type": "dataset_split",
  "status": "pending",
  "progress": 0,
  "input_path": "data/raw_dataset",
  "output_path": "data/split_dataset",
  "created_at": "2024-01-01T00:00:00",
  "updated_at": "2024-01-01T00:00:00"
}
```

**示例**:
```bash
# 二分割（train/valid）
curl -X POST "http://localhost:8000/api/v2/preprocessing/split" \
  -H "Content-Type: application/json" \
  -d '{
    "input_path": "data/raw_dataset",
    "output_path": "data/split_dataset",
    "train_ratio": 0.8
  }'

# 三分割（train/valid/test）
curl -X POST "http://localhost:8000/api/v2/preprocessing/split" \
  -H "Content-Type: application/json" \
  -d '{
    "input_path": "data/raw_dataset",
    "output_path": "data/split_dataset",
    "train_ratio": 0.7,
    "val_ratio": 0.2
  }'
```

---

### `POST /api/v2/preprocessing/augment`
**功能**: 数据增强

**请求体**:
```json
{
  "dataset_path": "data/split_dataset",
  "output_path": "data/augmented_dataset",
  "methods": ["CLAHE", "ColorJitter", "GaussNoise"],
  "task_id": "可选的自定义任务ID",
  "description": "数据增强任务"
}
```

**参数说明**:
- `dataset_path`: 数据集路径（必需，应包含train和valid文件夹）
- `output_path`: 输出路径（可选，默认为dataset_aug）
- `methods`: 增强方法列表（可选，默认使用全部6种方法）
  - **AdvancedBlur**: 高级模糊
  - **CLAHE**: 对比度受限自适应直方图均衡化
  - **ColorJitter**: 颜色抖动
  - **GaussNoise**: 高斯噪声
  - **ISONoise**: ISO噪声
  - **Sharpen**: 锐化
- `task_id`: 自定义任务ID（可选）
- `description`: 任务描述（可选）

**响应**:
```json
{
  "task_id": "650e8400-e29b-41d4-a716-446655440000",
  "task_type": "data_augmentation",
  "status": "pending",
  "progress": 0,
  "input_path": "data/split_dataset",
  "output_path": "data/augmented_dataset",
  "created_at": "2024-01-01T00:00:00",
  "updated_at": "2024-01-01T00:00:00"
}
```

**示例**:
```bash
# 使用指定的增强方法
curl -X POST "http://localhost:8000/api/v2/preprocessing/augment" \
  -H "Content-Type: application/json" \
  -d '{
    "dataset_path": "data/split_dataset",
    "output_path": "data/augmented",
    "methods": ["CLAHE", "ColorJitter", "GaussNoise"]
  }'

# 使用全部增强方法（不指定methods）
curl -X POST "http://localhost:8000/api/v2/preprocessing/augment" \
  -H "Content-Type: application/json" \
  -d '{
    "dataset_path": "data/split_dataset"
  }'
```

---

### `POST /api/v2/preprocessing/crop`
**功能**: 图像裁剪

**请求体**:
```json
{
  "input_path": "data/images",
  "output_path": "data/cropped",
  "x": 100,
  "y": 100,
  "width": 500,
  "height": 500,
  "task_id": "可选的自定义任务ID",
  "description": "图像裁剪任务"
}
```

**参数说明**:
- `input_path`: 输入图像路径（必需，可以是单个文件或目录）
- `output_path`: 输出路径（必需）
- `x`: 裁剪区域左上角X坐标（必需，≥0）
- `y`: 裁剪区域左上角Y坐标（必需，≥0）
- `width`: 裁剪宽度（必需，>0）
- `height`: 裁剪高度（必需，>0）
- `task_id`: 自定义任务ID（可选）
- `description`: 任务描述（可选）

**响应**:
```json
{
  "task_id": "750e8400-e29b-41d4-a716-446655440000",
  "task_type": "image_crop",
  "status": "pending",
  "progress": 0,
  "input_path": "data/images",
  "output_path": "data/cropped",
  "created_at": "2024-01-01T00:00:00",
  "updated_at": "2024-01-01T00:00:00"
}
```

**示例**:
```bash
# 裁剪单个文件
curl -X POST "http://localhost:8000/api/v2/preprocessing/crop" \
  -H "Content-Type: application/json" \
  -d '{
    "input_path": "data/image.jpg",
    "output_path": "data/cropped_image.jpg",
    "x": 100,
    "y": 100,
    "width": 500,
    "height": 500
  }'

# 批量裁剪目录
curl -X POST "http://localhost:8000/api/v2/preprocessing/crop" \
  -H "Content-Type: application/json" \
  -d '{
    "input_path": "data/images",
    "output_path": "data/cropped",
    "x": 100,
    "y": 100,
    "width": 500,
    "height": 500
  }'
```

---

### `GET /api/v2/preprocessing/{task_id}`
**功能**: 查询预处理任务状态

**路径参数**:
- `task_id`: 任务ID

**响应**:
```json
{
  "task_id": "550e8400-e29b-41d4-a716-446655440000",
  "task_type": "dataset_split",
  "status": "completed",
  "message": "数据集分割完成",
  "progress": 100,
  "input_path": "data/raw_dataset",
  "output_path": "data/split_dataset",
  "stats": {
    "total_images": 1000,
    "train_images": 700,
    "val_images": 200,
    "test_images": 100,
    "classes": ["class1", "class2", "class3"]
  },
  "created_at": "2024-01-01T00:00:00",
  "updated_at": "2024-01-01T00:05:00"
}
```

**状态说明**:
- `pending`: 等待开始
- `running`: 运行中
- `completed`: 已完成
- `failed`: 失败
- `cancelled`: 已取消

**统计信息示例**:
```json
// 数据集分割
{
  "stats": {
    "total_images": 1000,
    "train_images": 700,
    "val_images": 200,
    "test_images": 100,
    "classes": ["class1", "class2"]
  }
}

// 数据增强
{
  "stats": {
    "original_images": 1000,
    "augmented_images": 6000,
    "methods_used": 6,
    "classes": ["class1", "class2"]
  }
}

// 图像裁剪
{
  "stats": {
    "total_images": 100,
    "success": 98,
    "failed": 2
  }
}
```

**示例**:
```bash
curl http://localhost:8000/api/v2/preprocessing/{task_id}
```

---

### `GET /api/v2/preprocessing/{task_id}/logs`
**功能**: 获取预处理任务实时日志流 (SSE)

**路径参数**:
- `task_id`: 任务ID

**响应**: Server-Sent Events流
```
data: {"timestamp": "2024-01-01T00:00:00", "level": "INFO", "message": "开始数据集分割..."}

data: {"timestamp": "2024-01-01T00:00:05", "level": "INFO", "message": "处理类别: class1"}

data: {"timestamp": "2024-01-01T00:00:10", "level": "INFO", "message": "分割完成，总计1000张图像"}

data: {"status": "completed", "message": "任务结束"}
```

**Python示例**:
```python
import requests

url = f"http://localhost:8000/api/v2/preprocessing/{task_id}/logs"
with requests.get(url, stream=True) as response:
    for line in response.iter_lines():
        if line and line.startswith(b'data: '):
            print(line[6:].decode('utf-8'))
```

**JavaScript示例**:
```javascript
const eventSource = new EventSource(`/api/v2/preprocessing/${taskId}/logs`);
eventSource.onmessage = (event) => {
    const log = JSON.parse(event.data);
    console.log(`[${log.level}] ${log.message}`);
};
```

**示例**:
```bash
curl http://localhost:8000/api/v2/preprocessing/{task_id}/logs
```

---

## 🎓 训练接口

### `POST /api/v2/training/start`
**功能**: 启动模型训练任务

**请求体**:
```json
{
  "model": "resnet18",
  "num_classes": 37,
  "train_path": "data/train",
  "val_path": "data/val",
  "save_path": "models/output",
  "name": "exp_train_001",
  "batch_size": 16,
  "num_epochs": 50,
  "learning_rate": 0.0001,
  "image_size": 224,
  "device": "cuda",
  "weight_path": "",
  "pretrained": true,
  "shuffle": true,
  "priority": 5,
  "description": "训练描述（可选）"
}
```

**参数说明**:
- `model`: 模型名称（必需）
  - 支持: resnet18/34/50/101/152, vit_b_16, swin_v2_t, mobilenet_v3_large等
- `num_classes`: 分类类别数（必需）
- `train_path`: 训练集路径（必需）
- `val_path`: 验证集路径（必需）
- `save_path`: 模型保存路径（必需）
- `name`: 自定义保存名称（可选，将作为子目录附加到保存路径）
- `batch_size`: 批次大小，默认8
- `num_epochs`: 训练轮数，默认100
- `learning_rate`: 学习率，默认0.0001
- `image_size`: 图像尺寸，默认224
- `device`: 设备 (cuda/cpu)，默认cuda
- `priority`: 优先级 (1-10)，默认5
- `weight_path`: 预训练权重路径（可选）
- `pretrained`: 是否使用预训练，默认true
- `shuffle`: 是否打乱数据，默认true

**响应**:
```json
{
  "task_id": "550e8400-e29b-41d4-a716-446655440000",
  "task_type": "training",
  "status": "pending",
  "device": "cuda",
  "priority": 5,
  "created_at": "2024-01-01T00:00:00",
  "updated_at": "2024-01-01T00:00:00"
}
```

**示例**:
```bash
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
```

---

### `GET /api/v2/training/{task_id}`
**功能**: 查询训练任务状态（含详细训练指标）

**路径参数**:
- `task_id`: 任务ID

**响应**:
```json
{
  "task_id": "550e8400-e29b-41d4-a716-446655440000",
  "task_type": "training",
  "status": "running",
  "message": "训练中...",
  "progress": 45,
  "device": "cuda",
  "priority": 5,
  "current_epoch": 45,
  "total_epochs": 100,
  "latest_metrics": {
    "epoch": 45,
    "train_loss": 0.234,
    "train_acc": 0.892,
    "val_loss": 0.267,
    "val_acc": 0.875,
    "f1_score": 0.88,
    "precision": 0.87,
    "recall": 0.89,
    "learning_rate": 0.0001,
    "best_acc": 0.895
  },
  "created_at": "2024-01-01T00:00:00",
  "updated_at": "2024-01-01T00:05:00"
}
```

**状态说明**:
- `pending`: 等待开始
- `queued`: 排队中
- `running`: 运行中
- `completed`: 已完成
- `failed`: 失败
- `cancelled`: 已取消

**示例**:
```bash
curl http://localhost:8000/api/v2/training/{task_id}
```

---

### `GET /api/v2/training/{task_id}/logs`
**功能**: 获取训练任务实时日志流（含详细训练指标）(SSE)

**路径参数**:
- `task_id`: 任务ID

**响应**: Server-Sent Events流
```
data: {"timestamp": "2024-01-01T00:00:00", "level": "INFO", "message": "开始训练...", "stage": "epoch_start"}

data: {"timestamp": "2024-01-01T00:00:05", "level": "INFO", "message": "Epoch 1/50...", "metrics": {"epoch": 1, "total_epochs": 50, "train_loss": 0.5, "train_acc": 0.7}, "stage": "training"}

data: {"timestamp": "2024-01-01T00:00:10", "level": "INFO", "message": "验证中...", "metrics": {"val_loss": 0.45, "val_acc": 0.75}, "stage": "validation"}

data: {"status": "completed", "message": "任务结束"}
```

**Python示例**:
```python
import requests

url = f"http://localhost:8000/api/v2/training/{task_id}/logs"
with requests.get(url, stream=True) as response:
    for line in response.iter_lines():
        if line and line.startswith(b'data: '):
            print(line[6:].decode('utf-8'))
```

**JavaScript示例**:
```javascript
const eventSource = new EventSource(`/api/v2/training/${taskId}/logs`);
eventSource.onmessage = (event) => {
    const log = JSON.parse(event.data);
    console.log(`[${log.level}] ${log.message}`);
};
```

---

### `POST /api/v2/training/{task_id}/stop`
**功能**: 停止训练任务

**路径参数**:
- `task_id`: 任务ID

**响应**:
```json
{
  "status": "success",
  "message": "训练任务已停止",
  "task_id": "550e8400-e29b-41d4-a716-446655440000"
}
```

**示例**:
```bash
curl -X POST "http://localhost:8000/api/v2/training/{task_id}/stop"
```

---

## 🔍 推理接口

### `POST /api/v2/inference/start`
**功能**: 启动推理任务

**请求体**:
```json
{
  "cfg_path": "configs/model.yaml",
  "weight_path": "models/best.pth",fres
  "source_path": "data/test",
  "save_path": "results/",
  "name": "exp_infer_001",
  "device": "cuda",
  "priority": 3
}
```

**参数说明**:
- `cfg_path`: 配置文件路径（必需）
- `weight_path`: 模型权重路径（必需）
- `source_path`: 待推理数据路径（必需）
- `save_path`: 结果保存路径（可选）
- `name`: 自定义保存名称（可选，将作为子目录附加到保存路径）
- `device`: 设备 (cuda/cpu)，默认cuda
- `priority`: 优先级，默认3

**响应**:
```json
{
  "task_id": "650e8400-e29b-41d4-a716-446655440000",
  "task_type": "inference",
  "status": "pending",
  "device": "cuda",
  "priority": 3,
  "created_at": "2024-01-01T00:00:00"
}
```

**示例**:
```bash
curl -X POST "http://localhost:8000/api/v2/inference/start" \
  -H "Content-Type: application/json" \
  -d '{
    "cfg_path": "configs/model.yaml",
    "weight_path": "models/best.pth",
    "source_path": "data/test",
    "device": "cuda"
  }'
```

---

### `POST /api/v2/inference/batch`
**功能**: 批量推理任务

**请求体**:
```json
{
  "cfg_path": "configs/model.yaml",
  "weight_path": "models/best.pth",
  "source_paths": [
    "data/test1",
    "data/test2",
    "data/test3"
  ],
  "save_base_path": "results/batch/",
  "device": "cuda",
  "priority": 3
}
```

**参数说明**:
- `source_paths`: 数据路径列表（必需）
- 其他参数同单次推理

**响应**:
```json
{
  "status": "success",
  "message": "已启动 3 个推理任务",
  "task_ids": [
    "id1", "id2", "id3"
  ]
}
```

**示例**:
```bash
curl -X POST "http://localhost:8000/api/v2/inference/batch" \
  -H "Content-Type: application/json" \
  -d '{
    "cfg_path": "configs/model.yaml",
    "weight_path": "models/best.pth",
    "source_paths": ["data/test1", "data/test2"],
    "device": "cuda"
  }'
```

---

### `GET /api/v2/inference/{task_id}`
**功能**: 查询推理任务状态

**路径参数**:
- `task_id`: 任务ID

**响应**: 同训练任务状态

**示例**:
```bash
curl http://localhost:8000/api/v2/inference/{task_id}
```

---

## 📊 任务管理接口

### `GET /api/v2/tasks`
**功能**: 获取所有任务列表

**查询参数**:
- `status`: 过滤状态 (pending/running/completed/failed)
- `task_type`: 过滤类型 (training/inference)
- `limit`: 返回数量限制，默认100

**响应**:
```json
{
  "training_tasks": [
    {
      "task_id": "...",
      "status": "running",
      "progress": 50
    }
  ],
  "inference_tasks": [...],
  "total_training": 5,
  "total_inference": 3
}
```

**示例**:
```bash
# 所有任务
curl http://localhost:8000/api/v2/tasks

# 只看运行中的训练任务
curl "http://localhost:8000/api/v2/tasks?status=running&task_type=training"

# 最近10个任务
curl "http://localhost:8000/api/v2/tasks?limit=10"
```

---

### `GET /api/v2/tasks/{task_id}`
**功能**: 获取任务详情

**路径参数**:
- `task_id`: 任务ID

**响应**: 同训练/推理任务状态

**示例**:
```bash
curl http://localhost:8000/api/v2/tasks/{task_id}
```

---

### `GET /api/v2/tasks/{task_id}/logs`
**功能**: 获取任务日志流

**路径参数**:
- `task_id`: 任务ID

**响应**: SSE流，同训练日志流

**示例**:
```bash
curl http://localhost:8000/api/v2/tasks/{task_id}/logs
```

---

### `POST /api/v2/tasks/{task_id}/cancel`
**功能**: 取消任务

**路径参数**:
- `task_id`: 任务ID

**响应**:
```json
{
  "status": "success",
  "message": "任务已取消",
  "task_id": "..."
}
```

**示例**:
```bash
curl -X POST "http://localhost:8000/api/v2/tasks/{task_id}/cancel"
```

---

### `DELETE /api/v2/tasks/{task_id}`
**功能**: 删除任务记录

**路径参数**:
- `task_id`: 任务ID

**注意**: 只能删除已完成/失败/取消的任务

**响应**:
```json
{
  "status": "success",
  "message": "任务记录已删除",
  "task_id": "..."
}
```

**示例**:
```bash
curl -X DELETE "http://localhost:8000/api/v2/tasks/{task_id}"
```

---

## ⚙️ 资源管理接口

### `GET /api/v2/resources`
**功能**: 获取资源使用状态

**响应**:
```json
{
  "device_usage": {
    "cuda": {
      "training": 1,
      "inference": 2
    },
    "cpu": {
      "training": 0,
      "inference": 1
    }
  },
  "active_tasks": {
    "cuda": [
      {"id": "task1", "type": "training"},
      {"id": "task2", "type": "inference"}
    ]
  },
  "limits": {
    "cuda": {
      "training": 1,
      "inference": 3
    },
    "cpu": {
      "training": 2,
      "inference": 4
    }
  },
  "gpu_info": {
    "available": true,
    "count": 1,
    "devices": [...]
  }
}
```

**示例**:
```bash
curl http://localhost:8000/api/v2/resources
```

---

### `GET /api/v2/resources/gpu`
**功能**: 获取GPU详细信息

**响应**:
```json
{
  "available": true,
  "count": 1,
  "devices": [
    {
      "id": 0,
      "name": "NVIDIA GeForce RTX 3090",
      "total_memory_gb": 24.0,
      "allocated_memory_gb": 8.5,
      "cached_memory_gb": 10.2,
      "free_memory_gb": 15.5
    }
  ]
}
```

**示例**:
```bash
curl http://localhost:8000/api/v2/resources/gpu
```

---

### `GET /api/v2/resources/cpu` ⭐新
**功能**: 获取CPU与内存关键指标

**响应**:
```json
{
  "percent": 23.5,
  "per_cpu_percent": [12.3, 34.5, 18.0, 29.1],
  "cores": 8,
  "physical_cores": 4,
  "freq_mhz": 3292.0,
  "load_avg": {"1": 0.85, "5": 0.72, "15": 0.60},
  "memory_percent": 41.8
}
```

**示例**:
```bash
curl http://localhost:8000/api/v2/resources/cpu
```

---

### `POST /api/v2/resources/config`
**功能**: 动态更新资源配置

**请求体**:
```json
{
  "max_concurrent": {
    "cuda": {
      "training": 2,
      "inference": 5
    },
    "cpu": {
      "training": 3,
      "inference": 6
    }
  }
}
```

**响应**:
```json
{
  "status": "success",
  "message": "资源配置已更新",
  "current_config": {...}
}
```

**示例**:
```bash
curl -X POST "http://localhost:8000/api/v2/resources/config" \
  -H "Content-Type: application/json" \
  -d '{
    "max_concurrent": {
      "cuda": {"training": 2, "inference": 5}
    }
  }'
```

---

## 🏥 系统状态接口

### `GET /api/v1/health`
**功能**: 健康检查

**响应**:
```json
{
  "status": "healthy",
  "timestamp": "2024-01-01T00:00:00",
  "version": "2.3.0",
  "training_tasks": 5,
  "inference_tasks": 3,
  "active_log_streams": 2,
  "resource_status": {...}
}
```

**示例**:
```bash
curl http://localhost:8000/api/v1/health
```

---

### `GET /api/v1/info`
**功能**: 系统信息

**响应**:
```json
{
  "app_name": "RFUAV Model Service",
  "version": "2.3.0",
  "environment": "production",
  "supported_models": [
    "resnet18", "resnet50", "vit_b_16", ...
  ],
  "resource_limits": {...},
  "gpu_available": true
}
```

**示例**:
```bash
curl http://localhost:8000/api/v1/info
```

---

## 📝 常见使用流程

### 流程0: 数据准备（完整工作流）⭐新
```bash
# 1. 数据集分割
SPLIT_TASK=$(curl -X POST http://localhost:8000/api/v2/preprocessing/split \
  -H "Content-Type: application/json" \
  -d '{
    "input_path": "data/raw_dataset",
    "output_path": "data/split_dataset",
    "train_ratio": 0.7,
    "val_ratio": 0.2
  }' | jq -r '.task_id')

# 2. 监控分割进度
curl http://localhost:8000/api/v2/preprocessing/$SPLIT_TASK

# 3. 数据增强（等分割完成后）
AUGMENT_TASK=$(curl -X POST http://localhost:8000/api/v2/preprocessing/augment \
  -H "Content-Type: application/json" \
  -d '{
    "dataset_path": "data/split_dataset",
    "output_path": "data/augmented_dataset",
    "methods": ["CLAHE", "ColorJitter", "GaussNoise"]
  }' | jq -r '.task_id')

# 4. 监控增强进度
curl http://localhost:8000/api/v2/preprocessing/$AUGMENT_TASK

# 5. 可选：裁剪图像
CROP_TASK=$(curl -X POST http://localhost:8000/api/v2/preprocessing/crop \
  -H "Content-Type: application/json" \
  -d '{
    "input_path": "data/images",
    "output_path": "data/cropped",
    "x": 100, "y": 100, "width": 500, "height": 500
  }' | jq -r '.task_id')

# 6. 开始训练（使用增强后的数据）
TRAIN_TASK=$(curl -X POST http://localhost:8000/api/v2/training/start \
  -H "Content-Type: application/json" \
  -d '{
    "model": "resnet18",
    "num_classes": 37,
    "train_path": "data/augmented_dataset/train",
    "val_path": "data/augmented_dataset/valid",
    "save_path": "models/output",
    "num_epochs": 100,
    "device": "cuda"
  }' | jq -r '.task_id')
```

### 流程1: 训练模型
```bash
# 1. 启动训练
TASK_ID=$(curl -X POST .../api/v2/training/start -d {...} | jq -r '.task_id')

# 2. 查询状态（含详细指标）
curl .../api/v2/tasks/$TASK_ID

# 3. 获取日志（可选，含训练指标）
curl .../api/v2/training/$TASK_ID/logs

# 4. 等待完成或停止
curl -X POST .../api/v2/training/$TASK_ID/stop
```

### 流程2: 批量推理
```bash
# 1. 启动批量推理
curl -X POST .../api/v2/inference/batch -d {...}

# 2. 查看所有推理任务
curl ".../api/v2/tasks?task_type=inference"

# 3. 查看资源使用
curl .../api/v2/resources
```

### 流程3: 监控系统
```bash
# 1. 健康检查
curl .../api/v1/health

# 2. 查看GPU状态
curl .../api/v2/resources/gpu

# 3. 查看所有任务
curl .../api/v2/tasks

# 4. 动态调整资源
curl -X POST .../api/v2/resources/config -d {...}
```

---

## 📚 相关文档

- [完整使用文档](README_COMPLETE.md)
- [数据预处理指南](PREPROCESSING_GUIDE.md) ⭐新
- [训练指标使用指南](TRAINING_METRICS_GUIDE.md)
- [API参数参考](API_PARAMETERS_REFERENCE.md)
- [交互式API文档](http://localhost:8000/docs)

## 🧪 测试工具

- **test_preprocessing_api.py** - 数据预处理功能测试 ⭐新
- **test_training_metrics.py** - 训练指标功能测试
- **test_refactored_api.py** - 完整API测试
- **test_web_ui.html** - Web可视化测试界面

---

**版本**: V2.4.0  
**更新日期**: 2025-10-29  
**维护**: RFUAV Team


