# RFUAV模型服务API文档（增强版）

## 新特性

### 🚀 V2.4.0 最新功能 ⭐
1. **数据预处理接口** - 数据集分割、数据增强、图像裁剪一站式解决方案
2. **6种数据增强方法** - AdvancedBlur、CLAHE、ColorJitter、GaussNoise、ISONoise、Sharpen
3. **异步预处理任务** - 后台执行，实时进度查询，完整统计信息

### 🚀 V2.3.1 功能
1. **详细训练指标** - 实时返回loss、accuracy、F1、mAP等15+种训练指标
2. **增强日志流** - SSE日志包含结构化的训练指标和阶段信息
3. **指标历史追踪** - 完整记录训练过程中的所有指标变化

### 🚀 V2.0 新功能
1. **参数化训练配置** - 无需配置文件，直接通过JSON指定所有训练参数
2. **实时日志流** - 使用Server-Sent Events (SSE)实时获取训练日志
3. **完全解耦** - 模型、数据集、超参数完全独立配置
4. **向后兼容** - 保留V1版本API，支持配置文件方式

## 快速开始

### 启动服务
```bash
python app_enhanced.py
```

访问 http://localhost:8000/docs 查看交互式API文档

## API端点

### 1. 参数化训练 `/api/v2/train` ⭐新

完全参数化的训练接口，无需配置文件。

**请求方式**: POST

**请求体**:
```json
{
  "model": "resnet18",
  "num_classes": 37,
  "train_path": "data/train",
  "val_path": "data/val",
  "batch_size": 32,
  "num_epochs": 100,
  "learning_rate": 0.0001,
  "image_size": 224,
  "device": "cuda",
  "save_path": "models/resnet18_experiment",
  "weight_path": "",
  "shuffle": true,
  "pretrained": true,
  "description": "ResNet18训练实验"
}
```

**参数说明**:

| 参数 | 类型 | 必需 | 默认值 | 说明 |
|------|------|------|--------|------|
| model | string | 是 | - | 模型名称 |
| num_classes | integer | 是 | - | 分类类别数 |
| train_path | string | 是 | - | 训练集路径 |
| val_path | string | 是 | - | 验证集路径 |
| save_path | string | 是 | - | 模型保存路径 |
| batch_size | integer | 否 | 8 | 批次大小 |
| num_epochs | integer | 否 | 100 | 训练轮数 |
| learning_rate | float | 否 | 0.0001 | 学习率 |
| image_size | integer | 否 | 224 | 图像尺寸 |
| device | string | 否 | "cuda" | 设备 |
| weight_path | string | 否 | "" | 预训练权重路径 |
| shuffle | boolean | 否 | true | 是否打乱数据 |
| pretrained | boolean | 否 | true | 是否使用预训练 |
| task_id | string | 否 | 自动生成 | 任务ID |
| description | string | 否 | null | 任务描述 |

**支持的模型**:
- ResNet系列: `resnet18`, `resnet34`, `resnet50`, `resnet101`, `resnet152`
- ViT系列: `vit_b_16`, `vit_b_32`, `vit_l_16`, `vit_l_32`
- Swin Transformer: `swin_v2_t`, `swin_v2_s`, `swin_v2_b`
- MobileNet: `mobilenet_v3_large`, `mobilenet_v3_small`

**响应示例**:
```json
{
  "task_id": "abc123",
  "status": "pending",
  "message": "等待开始",
  "progress": 0,
  "created_at": "2024-01-01T12:00:00",
  "updated_at": "2024-01-01T12:00:00"
}
```

### 2. 实时日志流（含详细指标）`/api/v2/train/{task_id}/logs` ⭐新

获取训练任务的实时日志流，包含详细的训练指标。

**请求方式**: GET

**响应格式**: Server-Sent Events (SSE)

**日志格式（基础）**:
```json
{
  "timestamp": "2024-01-01T12:00:00",
  "level": "INFO",
  "message": "训练开始..."
}
```

**日志格式（含训练指标）** ⭐V2.3.1新增:
```json
{
  "timestamp": "2024-01-01T12:01:00",
  "level": "INFO",
  "message": "Train Loss: 0.5234, Train Accuracy: 82.45%",
  "metrics": {
    "epoch": 3,
    "train_loss": 0.5234,
    "train_acc": 82.45
  },
  "stage": "training"
}
```

**日志格式（含验证指标）** ⭐V2.3.1新增:
```json
{
  "timestamp": "2024-01-01T12:02:00",
  "level": "INFO",
  "message": "Validation Accuracy: 78.92%",
  "metrics": {
    "epoch": 3,
    "val_loss": 0.6123,
    "val_acc": 78.92,
    "macro_f1": 0.7654,
    "mAP": 0.8123,
    "top1_acc": 78.92,
    "top3_acc": 92.34,
    "top5_acc": 96.78
  },
  "stage": "validation"
}
```

**支持的训练指标（15+种）** ⭐V2.3.1新增:
- **基础指标**: epoch, train_loss, train_acc, val_loss, val_acc
- **F1分数**: macro_f1, micro_f1
- **mAP**: mAP
- **Top-k准确率**: top1_acc, top3_acc, top5_acc
- **其他**: precision, recall, learning_rate, best_acc

**训练阶段标识** ⭐V2.3.1新增:
- `epoch_start` - Epoch开始
- `training` - 训练阶段
- `validation` - 验证阶段
- `epoch_end` - Epoch结束
- `completed` - 训练完成

**使用示例（JavaScript）**:
```javascript
const taskId = "abc123";
const eventSource = new EventSource(`/api/v2/train/${taskId}/logs`);

eventSource.onmessage = (event) => {
    const log = JSON.parse(event.data);
    console.log(`[${log.level}] ${log.message}`);
};

eventSource.onerror = (error) => {
    console.error('Error:', error);
    eventSource.close();
};
```

**使用示例（Python）**:
```python
import requests
import json

task_id = "abc123"
url = f"http://localhost:8000/api/v2/train/{task_id}/logs"

response = requests.get(url, stream=True)
for line in response.iter_lines():
    if line:
        line_str = line.decode('utf-8')
        if line_str.startswith('data: '):
            data = json.loads(line_str[6:])
            print(f"[{data['level']}] {data['message']}")
```

**使用示例（curl）**:
```bash
curl -N http://localhost:8000/api/v2/train/abc123/logs
```

### 3. 配置文件训练 `/api/v1/train`

兼容旧版本的训练接口，使用配置文件。

**请求示例**:
```json
{
  "cfg_path": "configs/exp3.1_ResNet18.yaml",
  "description": "使用配置文件训练"
}
```

### 4. 查询任务状态（含详细指标）`/api/v1/tasks/{task_id}` ⭐V2.3.1增强

查询训练任务状态，包含详细的训练指标。

**请求方式**: GET

**响应示例**:
```json
{
  "task_id": "abc123",
  "task_type": "training",
  "status": "running",
  "message": "训练中...",
  "progress": 30,
  "device": "cuda:0",
  "current_epoch": 3,
  "total_epochs": 10,
  "latest_metrics": {
    "epoch": 3,
    "train_loss": 0.5234,
    "train_acc": 82.45,
    "val_loss": 0.6123,
    "val_acc": 78.92,
    "macro_f1": 0.7654,
    "mAP": 0.8123,
    "top1_acc": 78.92,
    "top3_acc": 92.34,
    "top5_acc": 96.78,
    "best_acc": 79.12,
    "learning_rate": 0.0001
  },
  "created_at": "2024-01-01T12:00:00",
  "updated_at": "2024-01-01T12:03:00"
}
```

**新增字段说明** ⭐V2.3.1:
- `current_epoch`: 当前训练轮次
- `total_epochs`: 总训练轮次
- `latest_metrics`: 最新的训练指标对象，包含15+种指标

### 5. 模型推理 `/api/v1/inference`

**请求示例**:
```json
{
  "cfg_path": "configs/exp3.1_ResNet18.yaml",
  "weight_path": "models/best_model.pth",
  "source_path": "example/test_data/",
  "save_path": "results/inference/",
  "device": "cuda"
}
```

**参数说明**:
- `cfg_path`: 配置文件路径（必需）
- `weight_path`: 模型权重路径（必需）
- `source_path`: 数据路径（必需）
- `save_path`: 结果保存路径（可选）
- `device`: 推理设备，`cuda`或`cpu`（可选，默认`cuda`）

### 6. 基准测试 `/api/v1/benchmark`

**请求示例**:
```json
{
  "cfg_path": "configs/exp3.1_ResNet18.yaml",
  "weight_path": "models/best_model.pth",
  "data_path": "data/benchmark/",
  "save_path": "results/benchmark/",
  "device": "cuda"
}
```

**参数说明**:
- `cfg_path`: 配置文件路径（必需）
- `weight_path`: 模型权重路径（必需）
- `data_path`: 测试数据路径（必需）
- `save_path`: 结果保存路径（可选）
- `device`: 测试设备，`cuda`或`cpu`（可选，默认`cuda`）

### 7. 健康检查 `/api/v1/health`

**响应示例**:
```json
{
  "status": "healthy",
  "timestamp": "2024-01-01T12:00:00",
  "training_tasks": 3,
  "active_log_streams": 2
}
```

## 完整使用示例

### Python完整示例（含训练指标处理）⭐V2.3.1增强

```python
import requests
import json
import time

# 1. 启动训练
train_config = {
    "model": "resnet18",
    "num_classes": 37,
    "train_path": "data/train",
    "val_path": "data/val",
    "batch_size": 32,
    "num_epochs": 100,
    "learning_rate": 0.0001,
    "image_size": 224,
    "device": "cuda",
    "save_path": "models/resnet18_exp1",
    "shuffle": True,
    "pretrained": True,
    "description": "ResNet18训练实验1"
}

response = requests.post("http://localhost:8000/api/v2/train", json=train_config)
task_data = response.json()
task_id = task_data["task_id"]
print(f"训练任务已启动，任务ID: {task_id}")

# 2. 实时获取日志（含训练指标处理）⭐V2.3.1新增
import threading

def stream_logs_with_metrics(task_id):
    """实时流式获取日志，并解析训练指标"""
    url = f"http://localhost:8000/api/v2/train/{task_id}/logs"
    response = requests.get(url, stream=True)
    for line in response.iter_lines():
        if line:
            line_str = line.decode('utf-8')
            if line_str.startswith('data: '):
                try:
                    data = json.loads(line_str[6:])
                    
                    # 显示基本日志
                    if 'message' in data:
                        print(f"[{data.get('level', 'INFO')}] {data['message']}")
                    
                    # 如果包含训练指标，详细显示 ⭐V2.3.1新增
                    if data.get('metrics'):
                        metrics = data['metrics']
                        stage = data.get('stage', '')
                        print(f"  └─ 阶段: {stage}")
                        
                        if metrics.get('train_acc'):
                            print(f"  └─ 训练准确率: {metrics['train_acc']:.2f}%")
                        if metrics.get('val_acc'):
                            print(f"  └─ 验证准确率: {metrics['val_acc']:.2f}%")
                        if metrics.get('macro_f1'):
                            print(f"  └─ Macro F1: {metrics['macro_f1']:.4f}")
                        if metrics.get('mAP'):
                            print(f"  └─ mAP: {metrics['mAP']:.4f}")
                        if metrics.get('best_acc'):
                            print(f"  └─ 🏆 最佳准确率: {metrics['best_acc']:.2f}%")
                    
                    if 'status' in data and data['status'] in ['completed', 'failed']:
                        break
                except json.JSONDecodeError:
                    pass

# 在后台线程中获取日志
log_thread = threading.Thread(target=stream_logs_with_metrics, args=(task_id,))
log_thread.start()

# 3. 定期查询任务状态（含训练指标）⭐V2.3.1增强
while True:
    status_response = requests.get(f"http://localhost:8000/api/v1/tasks/{task_id}")
    status_data = status_response.json()
    
    print(f"\n任务状态: {status_data['status']}, 进度: {status_data.get('progress', 0)}%")
    
    # 显示详细训练指标 ⭐V2.3.1新增
    if status_data.get('latest_metrics'):
        metrics = status_data['latest_metrics']
        print(f"当前Epoch: {status_data.get('current_epoch')}/{status_data.get('total_epochs')}")
        print(f"  训练准确率: {metrics.get('train_acc', 'N/A')}%")
        print(f"  验证准确率: {metrics.get('val_acc', 'N/A')}%")
        print(f"  最佳准确率: {metrics.get('best_acc', 'N/A')}%")
    
    if status_data['status'] in ['completed', 'failed']:
        print(f"任务结束: {status_data['message']}")
        break
    
    time.sleep(10)

log_thread.join()
```

### JavaScript/HTML完整示例

```html
<!DOCTYPE html>
<html>
<head>
    <title>RFUAV训练监控</title>
    <style>
        #logs {
            height: 400px;
            overflow-y: scroll;
            border: 1px solid #ccc;
            padding: 10px;
            font-family: monospace;
            background-color: #000;
            color: #0f0;
        }
    </style>
</head>
<body>
    <h1>RFUAV模型训练</h1>
    
    <button onclick="startTraining()">启动训练</button>
    <div id="status">状态: 未开始</div>
    <div id="logs"></div>

    <script>
        let taskId = null;
        let eventSource = null;

        async function startTraining() {
            const config = {
                model: "resnet18",
                num_classes: 37,
                train_path: "data/train",
                val_path: "data/val",
                batch_size: 32,
                num_epochs: 100,
                learning_rate: 0.0001,
                image_size: 224,
                device: "cuda",
                save_path: "models/resnet18_exp1",
                shuffle: true,
                pretrained: true
            };

            const response = await fetch('/api/v2/train', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify(config)
            });

            const data = await response.json();
            taskId = data.task_id;
            document.getElementById('status').innerText = `状态: ${data.status}`;

            // 开始监听日志
            streamLogs(taskId);
        }

        function streamLogs(taskId) {
            eventSource = new EventSource(`/api/v2/train/${taskId}/logs`);
            
            eventSource.onmessage = (event) => {
                const log = JSON.parse(event.data);
                const logsDiv = document.getElementById('logs');
                
                if (log.message) {
                    const logLine = document.createElement('div');
                    logLine.textContent = `[${log.level}] ${log.message}`;
                    logsDiv.appendChild(logLine);
                    logsDiv.scrollTop = logsDiv.scrollHeight;
                }

                if (log.status && ['completed', 'failed'].includes(log.status)) {
                    document.getElementById('status').innerText = `状态: ${log.status}`;
                    eventSource.close();
                }
            };

            eventSource.onerror = (error) => {
                console.error('Error:', error);
                eventSource.close();
            };
        }
    </script>
</body>
</html>
```

## 错误处理

所有错误响应格式：
```json
{
  "status": "error",
  "message": "错误详情",
  "timestamp": "2024-01-01T12:00:00"
}
```

常见错误码：
- `400`: 参数错误
- `404`: 任务不存在
- `500`: 服务器错误

## 注意事项

1. **实时日志流**：使用SSE技术，连接会保持打开直到训练完成
2. **资源清理**：任务完成后日志队列会自动清理
3. **并发训练**：支持多个训练任务同时运行
4. **参数验证**：所有参数都会进行验证，确保合法性
5. **路径检查**：训练前会检查数据集路径是否存在

## 性能建议

1. 使用适当的`batch_size`以充分利用GPU
2. 根据数据集大小调整`num_epochs`
3. 学习率建议从`0.0001`开始调整
4. 使用`pretrained=true`可以加快收敛

## 更多资源

### 详细文档
- **[数据预处理使用指南](./PREPROCESSING_GUIDE.md)** - 完整的数据预处理功能说明 ⭐V2.4.0新增
- **[训练指标使用指南](./TRAINING_METRICS_GUIDE.md)** - 完整的训练指标功能说明
- **[训练指标更新日志](./TRAINING_METRICS_CHANGELOG.md)** - 详细的代码修改记录
- **[API参数参考](./API_PARAMETERS_REFERENCE.md)** - 完整的API参数文档

### 测试工具
- **`test_preprocessing_api.py`** - 数据预处理功能测试脚本 ⭐V2.4.0新增
- **`test_training_metrics.py`** - 训练指标功能测试脚本
- **`test_web_ui.html`** - Web可视化测试界面

### 使用示例
```bash
# 测试数据预处理功能
python test_preprocessing_api.py

# 测试训练指标功能
python test_training_metrics.py

# 启动Web测试界面
# 双击打开 test_web_ui.html
```

### 数据准备工作流 ⭐V2.4.0新增

完整的数据准备到模型训练流程：

```python
import requests

BASE_URL = "http://localhost:8000"

# 步骤1: 数据集分割
split_response = requests.post(f"{BASE_URL}/api/v2/preprocessing/split", json={
    "input_path": "data/raw_dataset",
    "output_path": "data/split_dataset",
    "train_ratio": 0.7,
    "val_ratio": 0.2
})

# 步骤2: 数据增强
augment_response = requests.post(f"{BASE_URL}/api/v2/preprocessing/augment", json={
    "dataset_path": "data/split_dataset",
    "output_path": "data/augmented_dataset",
    "methods": ["CLAHE", "ColorJitter", "GaussNoise"]
})

# 步骤3: 开始训练（使用增强后的数据）
train_response = requests.post(f"{BASE_URL}/api/v2/train", json={
    "model": "resnet18",
    "num_classes": 37,
    "train_path": "data/augmented_dataset/train",
    "val_path": "data/augmented_dataset/valid",
    "save_path": "models/output",
    "num_epochs": 100,
    "device": "cuda:0"
})
```
