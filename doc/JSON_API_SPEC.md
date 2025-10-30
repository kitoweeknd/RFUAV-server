# JSON API 规范文档

## 📋 概述

RFUAV Model Service 的所有API接口都严格使用JSON格式进行请求和响应。

## 🔧 技术实现

### 请求格式
- **Content-Type**: `application/json`
- **数据验证**: 使用Pydantic模型自动验证
- **错误处理**: 返回标准的JSON错误响应

### 响应格式
- **Content-Type**: `application/json`
- **数据序列化**: FastAPI自动将Pydantic模型转换为JSON
- **统一结构**: 所有响应都有明确的类型定义

## 📊 响应模型类型

### 1. TaskResponse - 任务响应
用于返回单个任务的详细信息。

**使用场景**：
- 创建训练任务
- 创建推理任务
- 查询任务状态

**JSON格式**：
```json
{
  "task_id": "550e8400-e29b-41d4-a716-446655440000",
  "task_type": "training",
  "status": "running",
  "message": "训练中...",
  "progress": 45,
  "device": "cuda:0",
  "priority": 5,
  "created_at": "2024-01-01T00:00:00",
  "updated_at": "2024-01-01T00:05:00"
}
```

**字段说明**：
- `task_id`: 任务唯一标识符
- `task_type`: 任务类型 (training/inference)
- `status`: 任务状态 (pending/queued/running/completed/failed/cancelled)
- `message`: 状态描述信息
- `progress`: 进度百分比 (0-100)
- `device`: 使用的设备 (cuda/cuda:0/cuda:1/cpu)
- `priority`: 优先级 (1-10)
- `created_at`: 创建时间 (ISO 8601格式)
- `updated_at`: 更新时间 (ISO 8601格式)

### 2. TaskActionResponse - 任务操作响应
用于返回任务操作（停止、取消、删除）的结果。

**使用场景**：
- 停止训练任务
- 取消任务
- 删除任务记录

**JSON格式**：
```json
{
  "status": "success",
  "message": "训练任务已停止",
  "task_id": "550e8400-e29b-41d4-a716-446655440000"
}
```

**字段说明**：
- `status`: 操作状态 (success/error)
- `message`: 操作结果描述
- `task_id`: 相关任务ID

### 3. TaskListResponse - 任务列表响应
用于返回所有任务的列表。

**使用场景**：
- 查询所有任务
- 按类型过滤任务
- 按状态过滤任务

**JSON格式**：
```json
{
  "training_tasks": [
    {
      "task_id": "...",
      "task_type": "training",
      "status": "running",
      "progress": 50,
      "device": "cuda:0"
    }
  ],
  "inference_tasks": [
    {
      "task_id": "...",
      "task_type": "inference",
      "status": "completed",
      "device": "cuda:1"
    }
  ],
  "total_training": 5,
  "total_inference": 3
}
```

**字段说明**：
- `training_tasks`: 训练任务列表
- `inference_tasks`: 推理任务列表
- `total_training`: 训练任务总数
- `total_inference`: 推理任务总数

### 4. BatchInferenceResponse - 批量推理响应
用于返回批量推理任务的创建结果。

**使用场景**：
- 批量启动推理任务

**JSON格式**：
```json
{
  "status": "success",
  "message": "已启动 3 个推理任务",
  "task_ids": [
    "id1",
    "id2",
    "id3"
  ],
  "total": 3
}
```

**字段说明**：
- `status`: 操作状态
- `message`: 操作描述
- `task_ids`: 所有任务ID列表
- `total`: 任务总数

### 5. ResourceStatusResponse - 资源状态响应
用于返回系统资源使用情况。

**使用场景**：
- 查询资源状态
- 监控GPU使用

**JSON格式**：
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
      {"id": "task1", "type": "training"}
    ]
  },
  "limits": {
    "cuda:0": {
      "training": 1,
      "inference": 3
    }
  },
  "gpu_info": {
    "available": true,
    "count": 2,
    "devices": [...]
  }
}
```

### 6. ConfigUpdateResponse - 配置更新响应
用于返回配置更新的结果。

**使用场景**：
- 更新资源配置

**JSON格式**：
```json
{
  "status": "success",
  "message": "资源配置已更新",
  "current_config": {
    "cuda:0": {
      "training": 2,
      "inference": 5
    }
  }
}
```

### 7. HealthResponse - 健康检查响应
用于返回系统健康状态。

**使用场景**：
- 健康检查
- 系统监控

**JSON格式**：
```json
{
  "status": "healthy",
  "timestamp": "2024-01-01T00:00:00",
  "version": "2.3.1",
  "training_tasks": 5,
  "inference_tasks": 3,
  "active_log_streams": 2,
  "resource_status": {...}
}
```

### 8. InfoResponse - 系统信息响应
用于返回系统配置信息。

**使用场景**：
- 查询系统信息
- 获取支持的模型列表

**JSON格式**：
```json
{
  "app_name": "RFUAV Model Service",
  "version": "2.3.1",
  "environment": "production",
  "supported_models": ["resnet18", "resnet50", ...],
  "resource_limits": {...},
  "gpu_available": true
}
```

## 🔍 完整API示例

### 1. 启动训练任务

**请求**：
```bash
POST /api/v2/training/start
Content-Type: application/json

{
  "model": "resnet18",
  "num_classes": 37,
  "train_path": "data/train",
  "val_path": "data/val",
  "save_path": "models/output",
  "batch_size": 16,
  "num_epochs": 50,
  "learning_rate": 0.0001,
  "device": "cuda:0"
}
```

**响应**：
```json
{
  "task_id": "550e8400-e29b-41d4-a716-446655440000",
  "task_type": "training",
  "status": "pending",
  "message": "等待开始",
  "progress": 0,
  "device": "cuda:0",
  "priority": 5,
  "created_at": "2024-01-01T00:00:00",
  "updated_at": "2024-01-01T00:00:00"
}
```

### 2. 查询任务状态

**请求**：
```bash
GET /api/v2/tasks/550e8400-e29b-41d4-a716-446655440000
```

**响应**：
```json
{
  "task_id": "550e8400-e29b-41d4-a716-446655440000",
  "task_type": "training",
  "status": "running",
  "message": "训练中...",
  "progress": 45,
  "device": "cuda:0",
  "priority": 5,
  "created_at": "2024-01-01T00:00:00",
  "updated_at": "2024-01-01T00:05:00"
}
```

### 3. 停止任务

**请求**：
```bash
POST /api/v2/training/550e8400-e29b-41d4-a716-446655440000/stop
```

**响应**：
```json
{
  "status": "success",
  "message": "训练任务已停止",
  "task_id": "550e8400-e29b-41d4-a716-446655440000"
}
```

### 4. 批量推理

**请求**：
```bash
POST /api/v2/inference/batch
Content-Type: application/json

{
  "cfg_path": "configs/model.yaml",
  "weight_path": "models/best.pth",
  "source_paths": ["data/test1", "data/test2", "data/test3"],
  "device": "cuda"
}
```

**响应**：
```json
{
  "status": "success",
  "message": "已启动 3 个推理任务",
  "task_ids": [
    "id1",
    "id2",
    "id3"
  ],
  "total": 3
}
```

### 5. 查看GPU信息

**请求**：
```bash
GET /api/v2/resources/gpu
```

**响应**：
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
    }
  ]
}
```

## ⚠️ 错误响应

所有错误都返回标准的HTTP状态码和JSON错误信息。

### 404 - 未找到
```json
{
  "detail": "任务 xxx 不存在"
}
```

### 500 - 服务器错误
```json
{
  "detail": "训练失败: 路径不存在"
}
```

### 422 - 验证错误
```json
{
  "detail": [
    {
      "loc": ["body", "num_classes"],
      "msg": "field required",
      "type": "value_error.missing"
    }
  ]
}
```

## 🔐 请求头

所有请求都应该包含：
```
Content-Type: application/json
Accept: application/json
```

## 📱 客户端示例

### Python
```python
import requests
import json

# 发送JSON请求
response = requests.post(
    "http://localhost:8000/api/v2/training/start",
    headers={"Content-Type": "application/json"},
    json={
        "model": "resnet18",
        "num_classes": 37,
        "train_path": "data/train",
        "val_path": "data/val",
        "save_path": "models/output",
        "device": "cuda:0"
    }
)

# 解析JSON响应
result = response.json()
print(f"Task ID: {result['task_id']}")
print(f"Status: {result['status']}")
```

### JavaScript
```javascript
// 发送JSON请求
fetch('http://localhost:8000/api/v2/training/start', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({
    model: 'resnet18',
    num_classes: 37,
    train_path: 'data/train',
    val_path: 'data/val',
    save_path: 'models/output',
    device: 'cuda:0'
  })
})
.then(response => response.json())
.then(data => {
  console.log('Task ID:', data.task_id);
  console.log('Status:', data.status);
});
```

### cURL
```bash
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

## ✅ 验证规范

1. **所有请求必须是有效的JSON**
   - 使用正确的JSON语法
   - 字符串用双引号
   - 正确的数据类型

2. **所有响应都是JSON格式**
   - Content-Type自动设置为application/json
   - 响应体符合定义的模型

3. **自动数据验证**
   - Pydantic自动验证请求数据
   - 类型错误会返回422错误
   - 字段缺失会返回明确的错误信息

4. **类型安全**
   - 所有字段都有明确的类型定义
   - IDE可以提供自动补全
   - 减少运行时错误

## 📚 相关文档

- [API路由表](API_ROUTES_TABLE.md) - 完整的API端点列表
- [快速开始](QUICK_START_REFACTORED.md) - 使用指南
- [数据模型定义](models/schemas.py) - Pydantic模型源代码

---

**版本**: V2.3.1  
**更新日期**: 2024-01-XX  
**JSON规范**: 严格遵循


