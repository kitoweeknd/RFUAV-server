# API参数速查手册

> RFUAV Model Service - 所有API接口的请求参数和响应字段完整参考

## 📋 目录

- [训练接口](#训练接口)
- [推理接口](#推理接口)
- [任务管理接口](#任务管理接口)
- [资源管理接口](#资源管理接口)
- [系统状态接口](#系统状态接口)
- [通用响应模型](#通用响应模型)

---

## 训练接口

### POST /api/v2/training/start - 启动训练

#### 请求参数 (TrainingRequest)

| 参数 | 类型 | 必需 | 默认值 | 约束 | 说明 |
|------|------|------|--------|------|------|
| `model` | string | ✅ | - | - | 模型名称 (resnet18/resnet50/vit_b_16等) |
| `num_classes` | integer | ✅ | - | - | 分类类别数 |
| `train_path` | string | ✅ | - | - | 训练集路径 |
| `val_path` | string | ✅ | - | - | 验证集路径 |
| `save_path` | string | ✅ | - | - | 模型保存路径 |
| `batch_size` | integer | ❌ | 8 | ≥1 | 批次大小 |
| `num_epochs` | integer | ❌ | 100 | ≥1 | 训练轮数 |
| `learning_rate` | float | ❌ | 0.0001 | >0 | 学习率 |
| `image_size` | integer | ❌ | 224 | ≥32 | 图像尺寸 |
| `device` | string | ❌ | "cuda" | - | 设备 (cpu/cuda/cuda:0/cuda:1) |
| `weight_path` | string | ❌ | "" | - | 预训练权重路径 |
| `pretrained` | boolean | ❌ | true | - | 是否使用预训练 |
| `shuffle` | boolean | ❌ | true | - | 是否打乱数据 |
| `task_id` | string | ❌ | null | - | 自定义任务ID |
| `priority` | integer | ❌ | 5 | 1-10 | 优先级 |
| `description` | string | ❌ | null | - | 任务描述 |

#### 响应字段 (TaskResponse)

| 字段 | 类型 | 可为空 | 说明 |
|------|------|-------|------|
| `task_id` | string | ❌ | 任务唯一ID |
| `task_type` | string | ❌ | 任务类型 (training) |
| `status` | string | ❌ | 任务状态 |
| `message` | string | ✅ | 状态消息 |
| `progress` | integer | ✅ | 进度百分比 (0-100) |
| `device` | string | ✅ | 实际使用的设备 |
| `priority` | integer | ✅ | 优先级 |
| `created_at` | string | ❌ | 创建时间 (ISO 8601) |
| `updated_at` | string | ❌ | 更新时间 (ISO 8601) |

**状态值**: `pending`, `running`, `completed`, `failed`, `cancelled`

#### 示例
```json
// 请求
{
  "model": "resnet18",
  "num_classes": 37,
  "train_path": "data/train",
  "val_path": "data/val",
  "save_path": "models/output",
  "device": "cuda:0",
  "batch_size": 16,
  "num_epochs": 50
}

// 响应
{
  "task_id": "550e8400-e29b-41d4-a716-446655440000",
  "task_type": "training",
  "status": "pending",
  "message": "训练任务已创建",
  "progress": 0,
  "device": "cuda:0",
  "priority": 5,
  "created_at": "2024-01-01T00:00:00",
  "updated_at": "2024-01-01T00:00:00"
}
```

---

### GET /api/v2/training/{task_id} - 查询训练状态

#### 路径参数

| 参数 | 类型 | 必需 | 说明 |
|------|------|------|------|
| `task_id` | string | ✅ | 任务ID |

#### 响应字段

同 `POST /api/v2/training/start`

---

### GET /api/v2/training/{task_id}/logs - 实时日志流

#### 路径参数

| 参数 | 类型 | 必需 | 说明 |
|------|------|------|------|
| `task_id` | string | ✅ | 任务ID |

#### 响应

Server-Sent Events (SSE) 流

**每条消息格式**:
```json
{
  "timestamp": "2024-01-01T00:00:00",
  "level": "INFO",
  "message": "训练中..."
}
```

**日志级别**: `INFO`, `WARNING`, `ERROR`

---

### POST /api/v2/training/{task_id}/stop - 停止训练

#### 路径参数

| 参数 | 类型 | 必需 | 说明 |
|------|------|------|------|
| `task_id` | string | ✅ | 任务ID |

#### 响应字段 (TaskActionResponse)

| 字段 | 类型 | 说明 |
|------|------|------|
| `status` | string | 状态 (success/error) |
| `message` | string | 操作结果消息 |
| `task_id` | string | 任务ID |

---

## 推理接口

### POST /api/v2/inference/start - 启动推理

#### 请求参数 (InferenceRequest)

| 参数 | 类型 | 必需 | 默认值 | 约束 | 说明 |
|------|------|------|--------|------|------|
| `cfg_path` | string | ✅ | - | - | 配置文件路径 (.yaml) |
| `weight_path` | string | ✅ | - | - | 模型权重路径 (.pth) |
| `source_path` | string | ✅ | - | - | 推理数据路径 |
| `save_path` | string | ❌ | null | - | 结果保存路径 |
| `device` | string | ❌ | "cuda" | - | 推理设备 (cpu/cuda/cuda:0/cuda:1) |
| `task_id` | string | ❌ | null | - | 自定义任务ID |
| `priority` | integer | ❌ | 3 | 1-10 | 优先级 |

#### 响应字段 (TaskResponse)

同训练接口，`task_type` 为 "inference"

#### 示例
```json
// 请求
{
  "cfg_path": "configs/model.yaml",
  "weight_path": "models/best.pth",
  "source_path": "data/test",
  "device": "cuda:1"
}

// 响应
{
  "task_id": "task-inference-001",
  "task_type": "inference",
  "status": "pending",
  "device": "cuda:1",
  ...
}
```

---

### POST /api/v2/inference/batch - 批量推理

#### 请求参数 (BatchInferenceRequest)

| 参数 | 类型 | 必需 | 默认值 | 约束 | 说明 |
|------|------|------|--------|------|------|
| `cfg_path` | string | ✅ | - | - | 配置文件路径 |
| `weight_path` | string | ✅ | - | - | 模型权重路径 |
| `source_paths` | array[string] | ✅ | - | - | 数据路径列表 |
| `save_base_path` | string | ❌ | null | - | 结果保存基础路径 |
| `device` | string | ❌ | "cuda" | - | 推理设备 |
| `priority` | integer | ❌ | 3 | 1-10 | 优先级 |

#### 响应字段 (BatchInferenceResponse)

| 字段 | 类型 | 说明 |
|------|------|------|
| `status` | string | 状态 (success) |
| `message` | string | 消息 |
| `task_ids` | array[string] | 所有任务ID列表 |
| `total` | integer | 任务总数 |

#### 示例
```json
// 请求
{
  "cfg_path": "configs/model.yaml",
  "weight_path": "models/best.pth",
  "source_paths": ["data/test1", "data/test2", "data/test3"],
  "device": "cuda"
}

// 响应
{
  "status": "success",
  "message": "已启动 3 个推理任务",
  "task_ids": ["task-1", "task-2", "task-3"],
  "total": 3
}
```

---

### GET /api/v2/inference/{task_id} - 查询推理状态

#### 路径参数

| 参数 | 类型 | 必需 | 说明 |
|------|------|------|------|
| `task_id` | string | ✅ | 任务ID |

#### 响应字段

同训练接口

---

## 任务管理接口

### GET /api/v2/tasks - 获取所有任务

#### 查询参数

无

#### 响应字段 (TaskListResponse)

| 字段 | 类型 | 说明 |
|------|------|------|
| `training_tasks` | array[TaskResponse] | 训练任务列表 |
| `inference_tasks` | array[TaskResponse] | 推理任务列表 |
| `total_training` | integer | 训练任务总数 |
| `total_inference` | integer | 推理任务总数 |

---

### GET /api/v2/tasks/{task_id} - 获取任务详情

#### 路径参数

| 参数 | 类型 | 必需 | 说明 |
|------|------|------|------|
| `task_id` | string | ✅ | 任务ID |

#### 响应字段

TaskResponse (同训练接口)

---

### GET /api/v2/tasks/{task_id}/logs - 获取任务日志

#### 路径参数

| 参数 | 类型 | 必需 | 说明 |
|------|------|------|------|
| `task_id` | string | ✅ | 任务ID |

#### 响应

返回JSON数组

**数组元素格式**:
```json
{
  "timestamp": "2024-01-01T00:00:00",
  "level": "INFO",
  "message": "训练开始"
}
```

---

### POST /api/v2/tasks/{task_id}/cancel - 取消任务

#### 路径参数

| 参数 | 类型 | 必需 | 说明 |
|------|------|------|------|
| `task_id` | string | ✅ | 任务ID |

#### 响应字段

TaskActionResponse (同停止训练接口)

---

### DELETE /api/v2/tasks/{task_id} - 删除任务

#### 路径参数

| 参数 | 类型 | 必需 | 说明 |
|------|------|------|------|
| `task_id` | string | ✅ | 任务ID |

#### 响应字段

TaskActionResponse (同停止训练接口)

---

## 资源管理接口

### GET /api/v2/resources - 获取资源状态

#### 查询参数

无

#### 响应字段 (ResourceStatusResponse)

| 字段 | 类型 | 说明 |
|------|------|------|
| `device_usage` | object | 各设备当前使用情况 |
| `active_tasks` | object | 各设备活跃任务列表 |
| `limits` | object | 各设备并发限制 |
| `gpu_info` | object | GPU详细信息 |

**device_usage 结构**:
```json
{
  "cuda:0": {"training": 1, "inference": 2},
  "cuda:1": {"training": 0, "inference": 3}
}
```

**active_tasks 结构**:
```json
{
  "cuda:0": [
    {"id": "task-1", "type": "training"},
    {"id": "task-2", "type": "inference"}
  ]
}
```

**limits 结构**:
```json
{
  "cuda:0": {"training": 1, "inference": 3}
}
```

---

### GET /api/v2/resources/gpu - 获取GPU信息

#### 查询参数

无

#### 响应字段

| 字段 | 类型 | 说明 |
|------|------|------|
| `available` | boolean | GPU是否可用 |
| `count` | integer | GPU数量 |
| `cuda_version` | string | CUDA版本 |
| `pytorch_version` | string | PyTorch版本 |
| `devices` | array[GPUDevice] | GPU设备列表 |

**GPUDevice 对象**:

| 字段 | 类型 | 说明 |
|------|------|------|
| `id` | integer | GPU ID |
| `device_name` | string | 设备名称 (cuda:0/cuda:1) |
| `name` | string | GPU型号名称 |
| `compute_capability` | string | 计算能力 (如 "8.6") |
| `total_memory_gb` | float | 总显存 (GB) |
| `allocated_memory_gb` | float | 已分配显存 (GB) |
| `cached_memory_gb` | float | 缓存显存 (GB) |
| `free_memory_gb` | float | 空闲显存 (GB) |
| `utilization` | float | 利用率 (%) |
| `current_tasks` | object | 当前任务数 {training: 数量, inference: 数量} |

#### 示例
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
      "cached_memory_gb": 0.3,
      "free_memory_gb": 15.5,
      "utilization": 35.4,
      "current_tasks": {
        "training": 1,
        "inference": 2
      }
    }
  ]
}
```

---

### POST /api/v2/resources/config - 更新资源配置

#### 请求参数 (ResourceConfigUpdate)

| 参数 | 类型 | 必需 | 说明 |
|------|------|------|------|
| `max_concurrent` | object | ❌ | 并发限制配置 |

**max_concurrent 结构**:
```json
{
  "cuda:0": {"training": 2, "inference": 5},
  "cuda:1": {"training": 1, "inference": 3}
}
```

#### 响应字段 (ConfigUpdateResponse)

| 字段 | 类型 | 说明 |
|------|------|------|
| `status` | string | 状态 (success) |
| `message` | string | 消息 |
| `current_config` | object | 更新后的配置 |

---

## 系统状态接口

### GET /api/v1/health - 健康检查

#### 查询参数

无

#### 响应字段 (HealthResponse)

| 字段 | 类型 | 说明 |
|------|------|------|
| `status` | string | 服务状态 (healthy/unhealthy) |
| `timestamp` | string | 检查时间 |
| `version` | string | 服务版本 |
| `training_tasks` | integer | 训练任务数 |
| `inference_tasks` | integer | 推理任务数 |
| `active_log_streams` | integer | 活跃日志流数 |
| `resource_status` | object | 资源状态摘要 |

**resource_status 结构**:
```json
{
  "gpu_available": true,
  "gpu_count": 2
}
```

---

### GET /api/v1/info - 系统信息

#### 查询参数

无

#### 响应字段 (InfoResponse)

| 字段 | 类型 | 说明 |
|------|------|------|
| `app_name` | string | 应用名称 |
| `version` | string | 版本号 |
| `environment` | string | 运行环境 (development/production) |
| `supported_models` | array[string] | 支持的模型列表 |
| `resource_limits` | object | 资源限制配置 |
| `gpu_available` | boolean | GPU是否可用 |

**supported_models 示例**:
```json
[
  "resnet18", "resnet34", "resnet50", "resnet101", "resnet152",
  "vit_b_16", "vit_b_32", "vit_l_16", "vit_l_32",
  "swin_v2_t", "swin_v2_s", "swin_v2_b",
  "mobilenet_v3_large", "mobilenet_v3_small"
]
```

**resource_limits 结构**:
```json
{
  "max_training_concurrent_gpu": 1,
  "max_inference_concurrent_gpu": 3,
  "max_training_concurrent_cpu": 2,
  "max_inference_concurrent_cpu": 4
}
```

---

## 通用响应模型

### ErrorResponse - 错误响应

| 字段 | 类型 | 说明 |
|------|------|------|
| `status` | string | 固定为 "error" |
| `message` | string | 错误消息 |
| `timestamp` | string | 错误时间 |
| `detail` | string | 详细错误信息 (可选) |

#### 示例
```json
{
  "status": "error",
  "message": "任务不存在",
  "timestamp": "2024-01-01T00:00:00",
  "detail": "Task ID: xxx not found"
}
```

---

### SuccessResponse - 成功响应

| 字段 | 类型 | 说明 |
|------|------|------|
| `status` | string | 固定为 "success" |
| `message` | string | 成功消息 |
| `data` | object | 额外数据 (可选) |

---

## 数据类型说明

### 基本类型

| 类型 | 说明 | 示例 |
|------|------|------|
| `string` | 字符串 | "resnet18" |
| `integer` | 整数 | 100 |
| `float` | 浮点数 | 0.0001 |
| `boolean` | 布尔值 | true/false |
| `array` | 数组 | ["item1", "item2"] |
| `object` | 对象 | {"key": "value"} |

### 时间格式

所有时间字段使用 **ISO 8601** 格式:
```
2024-01-01T00:00:00
2024-01-01T12:30:45.123
```

### 设备名称

| 格式 | 说明 |
|------|------|
| `"cuda"` | 自动选择GPU |
| `"cuda:0"` | 指定GPU 0 |
| `"cuda:1"` | 指定GPU 1 |
| `"cpu"` | 使用CPU |

---

## 常用查询模式

### 1. 启动训练并监控

```python
# 1. 启动训练
response = requests.post("/api/v2/training/start", json={...})
task_id = response.json()["task_id"]

# 2. 轮询状态
while True:
    status = requests.get(f"/api/v2/tasks/{task_id}").json()
    print(f"Progress: {status['progress']}%")
    if status['status'] in ['completed', 'failed']:
        break
    time.sleep(5)

# 3. 获取日志
logs = requests.get(f"/api/v2/tasks/{task_id}/logs").json()
```

### 2. 批量推理

```python
# 1. 批量启动
response = requests.post("/api/v2/inference/batch", json={
    "source_paths": ["path1", "path2", "path3"],
    ...
})
task_ids = response.json()["task_ids"]

# 2. 检查所有任务
for task_id in task_ids:
    status = requests.get(f"/api/v2/tasks/{task_id}").json()
    print(f"{task_id}: {status['status']}")
```

### 3. 资源监控

```python
# 定期检查资源
def monitor_resources():
    resources = requests.get("/api/v2/resources").json()
    gpu_info = requests.get("/api/v2/resources/gpu").json()
    
    for device in gpu_info["devices"]:
        print(f"{device['device_name']}: {device['utilization']}%")
```

---

## HTTP状态码

| 状态码 | 说明 |
|-------|------|
| `200` | 请求成功 |
| `201` | 创建成功 |
| `400` | 请求参数错误 |
| `404` | 资源不存在 |
| `500` | 服务器错误 |
| `503` | 服务不可用 |

---

## 更多信息

- **完整文档**: [README_COMPLETE.md](README_COMPLETE.md)
- **快速参考**: [QUICK_REFERENCE.md](QUICK_REFERENCE.md)
- **在线API文档**: http://localhost:8000/docs

---

**版本**: V2.3.1  
**最后更新**: 2024-01


