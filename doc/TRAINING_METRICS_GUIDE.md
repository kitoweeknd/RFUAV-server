# 训练任务详细指标使用指南

## 概述

训练接口现已增强，支持返回详细的训练指标，包括损失值、准确率、F1分数、mAP、Top-k准确率等。这些指标会自动从训练器的日志中提取并实时更新。

## 功能特点

✅ **自动指标提取**: 自动从训练日志中解析并提取关键指标  
✅ **实时更新**: 训练过程中指标实时更新  
✅ **丰富的指标**: 支持loss、accuracy、F1、mAP、Top-k等多种指标  
✅ **无缝集成**: 在现有接口上直接增强，无需额外配置

## API接口

### 1. 启动训练任务
**端点**: `POST /api/v2/training/start`

**请求示例**:
```json
{
  "model": "resnet18",
  "num_classes": 37,
  "train_path": "/path/to/train",
  "val_path": "/path/to/val",
  "save_path": "/path/to/save",
  "batch_size": 8,
  "num_epochs": 10,
  "learning_rate": 0.0001,
  "device": "cuda:0",
  "priority": 5
}
```

**响应示例**:
```json
{
  "task_id": "abc-123-def-456",
  "task_type": "training",
  "status": "pending",
  "progress": 0,
  "device": "cuda:0",
  "total_epochs": 10,
  "created_at": "2025-10-29T10:00:00",
  "updated_at": "2025-10-29T10:00:00"
}
```

### 2. 获取训练状态（含详细指标）
**端点**: `GET /api/v2/training/{task_id}`

**响应示例**:
```json
{
  "task_id": "abc-123-def-456",
  "task_type": "training",
  "status": "running",
  "progress": 30,
  "device": "cuda:0",
  "current_epoch": 3,
  "total_epochs": 10,
  "latest_metrics": {
    "epoch": 3,
    "total_epochs": 10,
    "train_loss": 0.5234,
    "train_acc": 82.45,
    "val_loss": 0.6123,
    "val_acc": 78.92,
    "macro_f1": 0.7654,
    "micro_f1": 0.7892,
    "mAP": 0.8123,
    "top1_acc": 78.92,
    "top3_acc": 92.34,
    "top5_acc": 96.78,
    "best_acc": 79.12,
    "learning_rate": 0.0001
  },
  "created_at": "2025-10-29T10:00:00",
  "updated_at": "2025-10-29T10:15:00"
}
```

### 3. 获取训练日志流（含指标）
**端点**: `GET /api/v2/training/{task_id}/logs`

**响应格式**: Server-Sent Events (SSE)

**日志条目示例**:
```json
{
  "timestamp": "2025-10-29T10:15:23",
  "level": "INFO",
  "message": "Epoch [3/10] started",
  "metrics": {
    "epoch": 3,
    "total_epochs": 10
  },
  "stage": "epoch_start"
}
```

```json
{
  "timestamp": "2025-10-29T10:16:45",
  "level": "INFO",
  "message": "Train Loss: 0.5234, Train Accuracy: 82.45%",
  "metrics": {
    "epoch": 3,
    "total_epochs": 10,
    "train_loss": 0.5234,
    "train_acc": 82.45
  },
  "stage": "training"
}
```

```json
{
  "timestamp": "2025-10-29T10:17:12",
  "level": "INFO",
  "message": "Validation Loss: 0.6123, Validation Accuracy: 78.92%",
  "metrics": {
    "epoch": 3,
    "total_epochs": 10,
    "val_loss": 0.6123,
    "val_acc": 78.92
  },
  "stage": "validation"
}
```

## 支持的训练指标

| 指标 | 字段名 | 说明 | 示例值 |
|------|--------|------|--------|
| 当前轮次 | `epoch` | 当前训练轮次 | `3` |
| 总轮次 | `total_epochs` | 总训练轮次 | `10` |
| 训练损失 | `train_loss` | 训练集损失值 | `0.5234` |
| 训练准确率 | `train_acc` | 训练集准确率(%) | `82.45` |
| 验证损失 | `val_loss` | 验证集损失值 | `0.6123` |
| 验证准确率 | `val_acc` | 验证集准确率(%) | `78.92` |
| Macro F1 | `macro_f1` | Macro F1分数 | `0.7654` |
| Micro F1 | `micro_f1` | Micro F1分数 | `0.7892` |
| mAP | `mAP` | 平均精度均值 | `0.8123` |
| Top-1准确率 | `top1_acc` | Top-1准确率 | `78.92` |
| Top-3准确率 | `top3_acc` | Top-3准确率 | `92.34` |
| Top-5准确率 | `top5_acc` | Top-5准确率 | `96.78` |
| 精确度 | `precision` | 精确度 | `0.8234` |
| 召回率 | `recall` | 召回率 | `0.7892` |
| 学习率 | `learning_rate` | 当前学习率 | `0.0001` |
| 最佳准确率 | `best_acc` | 历史最佳准确率(%) | `79.12` |

## 训练阶段说明

| 阶段 | stage值 | 说明 |
|------|---------|------|
| Epoch开始 | `epoch_start` | 新一轮训练开始 |
| 训练中 | `training` | 训练阶段，输出训练损失和准确率 |
| 验证中 | `validation` | 验证阶段，输出验证指标 |
| Epoch结束 | `epoch_end` | 一轮训练结束，可能保存最佳模型 |
| 训练完成 | `completed` | 所有训练完成 |

## Python客户端示例

### 1. 启动训练并获取状态

```python
import requests
import time

BASE_URL = "http://localhost:8000"

# 启动训练
response = requests.post(f"{BASE_URL}/api/v2/training/start", json={
    "model": "resnet18",
    "num_classes": 37,
    "train_path": "/data/train",
    "val_path": "/data/val",
    "save_path": "/checkpoints",
    "num_epochs": 10,
    "device": "cuda:0"
})

task_id = response.json()["task_id"]
print(f"任务ID: {task_id}")

# 轮询获取训练状态
while True:
    response = requests.get(f"{BASE_URL}/api/v2/training/{task_id}")
    task = response.json()
    
    print(f"状态: {task['status']}, 进度: {task['progress']}%")
    
    if task.get('latest_metrics'):
        metrics = task['latest_metrics']
        print(f"Epoch {metrics.get('epoch')}/{metrics.get('total_epochs')}")
        print(f"  训练准确率: {metrics.get('train_acc')}%")
        print(f"  验证准确率: {metrics.get('val_acc')}%")
    
    if task['status'] in ['completed', 'failed', 'cancelled']:
        break
    
    time.sleep(5)
```

### 2. 实时监控训练日志

```python
import requests
import json

BASE_URL = "http://localhost:8000"
task_id = "your-task-id"

response = requests.get(
    f"{BASE_URL}/api/v2/training/{task_id}/logs",
    stream=True
)

for line in response.iter_lines():
    if line:
        line_str = line.decode('utf-8')
        if line_str.startswith('data: '):
            data = json.loads(line_str[6:])
            
            # 显示日志消息
            print(f"[{data['level']}] {data['message']}")
            
            # 显示训练指标
            if data.get('metrics'):
                print(f"  指标: {data['metrics']}")
```

### 3. JavaScript/Web客户端示例

```javascript
// 使用EventSource监听实时日志
const taskId = 'your-task-id';
const eventSource = new EventSource(`/api/v2/training/${taskId}/logs`);

eventSource.onmessage = (event) => {
    const logEntry = JSON.parse(event.data);
    console.log(`[${logEntry.level}] ${logEntry.message}`);
    
    // 如果有训练指标，更新UI
    if (logEntry.metrics) {
        updateMetricsDisplay(logEntry.metrics);
    }
};

function updateMetricsDisplay(metrics) {
    // 更新进度条
    if (metrics.epoch && metrics.total_epochs) {
        const progress = (metrics.epoch / metrics.total_epochs) * 100;
        document.getElementById('progress').style.width = `${progress}%`;
    }
    
    // 更新指标显示
    if (metrics.train_acc) {
        document.getElementById('train-acc').textContent = 
            `${metrics.train_acc.toFixed(2)}%`;
    }
    if (metrics.val_acc) {
        document.getElementById('val-acc').textContent = 
            `${metrics.val_acc.toFixed(2)}%`;
    }
}
```

## 指标提取机制

系统通过自定义日志处理器（`TrainingLogHandler`）自动从训练器的日志输出中提取指标：

1. **日志拦截**: 拦截训练器的日志输出
2. **模式匹配**: 使用正则表达式匹配特定的日志格式
3. **指标提取**: 提取数值并转换为结构化数据
4. **实时更新**: 立即更新任务状态和日志队列

支持的日志格式示例：
- `Epoch [3/10] started`
- `Train Loss: 0.5234, Train Accuracy: 82.45%`
- `Validation Loss: 0.6123, Validation Accuracy: 78.92%`
- `Validation macro_F1: 0.7654`
- `Validation Top-k Accuracy: {'top1': 78.92, 'top3': 92.34, 'top5': 96.78}`
- `New best model saved with Accuracy: 79.12%`

## 测试工具

项目提供了测试脚本 `test_training_metrics.py`，可以用来测试详细指标功能：

```bash
python test_training_metrics.py
```

测试脚本会：
1. 启动一个训练任务
2. 定期查询任务状态和最新指标
3. 实时监控训练日志流
4. 显示详细的训练指标

## 注意事项

1. **指标可用性**: 指标的可用性取决于训练器的日志输出格式
2. **实时性**: 指标会在日志输出时实时更新
3. **历史数据**: 所有指标变化都会保存在日志历史中
4. **性能影响**: 日志处理对训练性能影响极小（<1%）

## 故障排除

### 问题: 没有看到任何训练指标

**原因**: 训练器的日志格式可能与预期不匹配

**解决方案**:
1. 检查训练器的日志输出格式
2. 如需支持新的日志格式，在 `TrainingLogHandler` 中添加相应的正则表达式

### 问题: 某些指标总是为None

**原因**: 训练器未输出该指标的日志

**解决方案**:
1. 确认训练器配置是否启用了该指标的计算
2. 检查训练器是否正确记录了该指标

## 相关文档

- [API参数详细说明](./API_PARAMETERS_REFERENCE.md)
- [API使用指南](./API_ENHANCED_README.md)
- [快速开始指南](../README.md)

