# RFUAV模型服务增强版 - 快速开始

## 新特性概览

### ✨ 主要改进
1. **完全参数化配置** - 无需YAML配置文件，通过JSON直接指定所有参数
2. **实时日志流** - Server-Sent Events实时推送训练日志
3. **解耦设计** - 模型、数据集、超参数完全独立配置
4. **向后兼容** - 保留原有配置文件接口

## 安装依赖

```bash
pip install -r requirements_enhanced.txt
```

## 启动服务

```bash
python app_enhanced.py
```

服务启动后访问：
- 主页: http://localhost:8000
- API文档: http://localhost:8000/docs
- 健康检查: http://localhost:8000/api/v1/health

## 快速使用

### 方式1：使用测试客户端（推荐）

```bash
python test_api_client.py
```

交互式菜单，可选择：
1. 启动训练并实时监控
2. 监控已有任务
3. 自定义日志处理
4. 模型推理

### 方式2：Python代码

```python
import requests

# 启动训练
config = {
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
    "pretrained": True
}

response = requests.post("http://localhost:8000/api/v2/train", json=config)
task_data = response.json()
task_id = task_data["task_id"]
print(f"任务ID: {task_id}")

# 实时获取日志
import json
url = f"http://localhost:8000/api/v2/train/{task_id}/logs"
response = requests.get(url, stream=True)

for line in response.iter_lines():
    if line and line.decode('utf-8').startswith('data: '):
        log = json.loads(line.decode('utf-8')[6:])
        if 'message' in log:
            print(log['message'])
```

### 方式3：cURL命令

```bash
# 启动训练
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
    "image_size": 224,
    "device": "cuda",
    "save_path": "models/resnet18_exp1",
    "shuffle": true,
    "pretrained": true
  }'

# 实时查看日志（task_id从上一步获取）
curl -N "http://localhost:8000/api/v2/train/{task_id}/logs"
```

### 方式4：浏览器（JavaScript）

```javascript
// 启动训练
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

fetch('/api/v2/train', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify(config)
})
.then(res => res.json())
.then(data => {
    const taskId = data.task_id;
    
    // 实时监听日志
    const eventSource = new EventSource(`/api/v2/train/${taskId}/logs`);
    eventSource.onmessage = (event) => {
        const log = JSON.parse(event.data);
        console.log(log.message);
    };
});
```

## 支持的模型

- **ResNet**: resnet18, resnet34, resnet50, resnet101, resnet152
- **ViT**: vit_b_16, vit_b_32, vit_l_16, vit_l_32
- **Swin Transformer**: swin_v2_t, swin_v2_s, swin_v2_b
- **MobileNet**: mobilenet_v3_large, mobilenet_v3_small

## 参数说明

| 参数 | 类型 | 必需 | 默认值 | 说明 |
|------|------|------|--------|------|
| model | string | ✅ | - | 模型名称 |
| num_classes | int | ✅ | - | 类别数 |
| train_path | string | ✅ | - | 训练集路径 |
| val_path | string | ✅ | - | 验证集路径 |
| save_path | string | ✅ | - | 保存路径 |
| batch_size | int | ❌ | 8 | 批次大小 |
| num_epochs | int | ❌ | 100 | 训练轮数 |
| learning_rate | float | ❌ | 0.0001 | 学习率 |
| image_size | int | ❌ | 224 | 图像尺寸 |
| device | string | ❌ | "cuda" | 设备 |
| shuffle | bool | ❌ | true | 打乱数据 |
| pretrained | bool | ❌ | true | 预训练 |

## 示例配置

查看 `train_examples.json` 获取更多配置示例。

## API接口对比

### V2（新版）- 参数化
```
POST /api/v2/train
GET /api/v2/train/{task_id}/logs
```

### V1（旧版）- 配置文件
```
POST /api/v1/train
GET /api/v1/tasks/{task_id}
```

## 设备选择

所有接口都支持指定运行设备：

```json
{
  "device": "cuda"  // 或 "cpu"
}
```

- **训练**: 在请求体中指定`device`参数
- **推理**: 添加`device`参数，覆盖配置文件设置
- **基准测试**: 添加`device`参数

详见 [设备使用说明](DEVICE_USAGE.md)

## 详细文档

- [API详细文档](API_ENHANCED_README.md)
- [设备使用说明](DEVICE_USAGE.md)
- [训练示例](train_examples.json)
- [测试客户端](test_api_client.py)

## 故障排除

### 无法连接服务
```bash
# 检查服务是否运行
curl http://localhost:8000/api/v1/health
```

### 日志流中断
日志流使用SSE技术，需要保持连接。如果中断，重新连接即可。

### 路径不存在错误
确保训练集和验证集路径存在且包含正确的数据结构：
```
data/
├── train/
│   ├── class1/
│   ├── class2/
│   └── ...
└── val/
    ├── class1/
    ├── class2/
    └── ...
```

## 下一步

1. 阅读 [API详细文档](API_ENHANCED_README.md)
2. 运行 `test_api_client.py` 体验功能
3. 查看 `train_examples.json` 了解更多配置
4. 访问 http://localhost:8000/docs 查看交互式文档
