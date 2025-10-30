# 快速开始 - 重构版

## 🚀 启动服务

### 1. 安装依赖
```bash
pip install -r requirements_refactored.txt
```

### 2. 配置环境（可选）
```bash
cp env.example .env
# 编辑 .env 文件修改配置
```

### 3. 启动服务
```bash
python app_refactored.py
```

或者使用uvicorn：
```bash
uvicorn app_refactored:app --host 0.0.0.0 --port 8000 --reload
```

### 4. 访问API文档
打开浏览器访问：
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc
- 路由表: http://localhost:8000/

## 📋 路由表概览

### 根路径
```bash
GET /
```
返回完整的路由表和API概览

### 训练接口
```bash
POST   /api/v2/training/start        # 启动训练
GET    /api/v2/training/{task_id}    # 查询状态
GET    /api/v2/training/{task_id}/logs # 获取日志流
POST   /api/v2/training/{task_id}/stop # 停止训练
```

### 推理接口
```bash
POST   /api/v2/inference/start       # 启动推理
POST   /api/v2/inference/batch       # 批量推理
GET    /api/v2/inference/{task_id}   # 查询状态
```

### 任务管理
```bash
GET    /api/v2/tasks                 # 所有任务
GET    /api/v2/tasks/{task_id}       # 任务详情
GET    /api/v2/tasks/{task_id}/logs  # 任务日志
POST   /api/v2/tasks/{task_id}/cancel # 取消任务
DELETE /api/v2/tasks/{task_id}       # 删除任务
```

### 资源管理
```bash
GET    /api/v2/resources             # 资源状态
GET    /api/v2/resources/gpu         # GPU信息
POST   /api/v2/resources/config      # 更新配置
```

### 系统状态
```bash
GET    /api/v1/health                # 健康检查
GET    /api/v1/info                  # 系统信息
```

## 💡 使用示例

### 1. 启动训练任务
```bash
curl -X POST "http://localhost:8000/api/v2/training/start" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "resnet18",
    "num_classes": 37,
    "train_path": "data/train",
    "val_path": "data/val",
    "save_path": "models/output",
    "batch_size": 16,
    "num_epochs": 50,
    "learning_rate": 0.0001,
    "device": "cuda",
    "priority": 5
  }'
```

响应：
```json
{
  "task_id": "xxx-xxx-xxx",
  "task_type": "training",
  "status": "pending",
  "device": "cuda",
  "created_at": "2024-01-01T00:00:00"
}
```

### 2. 查询任务状态
```bash
curl http://localhost:8000/api/v2/tasks/{task_id}
```

### 3. 获取实时日志
```python
import requests

url = f"http://localhost:8000/api/v2/training/{task_id}/logs"
with requests.get(url, stream=True) as response:
    for line in response.iter_lines():
        if line:
            print(line.decode('utf-8'))
```

### 4. 启动推理任务
```bash
curl -X POST "http://localhost:8000/api/v2/inference/start" \
  -H "Content-Type: application/json" \
  -d '{
    "cfg_path": "configs/model.yaml",
    "weight_path": "models/best.pth",
    "source_path": "data/test",
    "save_path": "results/",
    "device": "cuda"
  }'
```

### 5. 批量推理
```bash
curl -X POST "http://localhost:8000/api/v2/inference/batch" \
  -H "Content-Type: application/json" \
  -d '{
    "cfg_path": "configs/model.yaml",
    "weight_path": "models/best.pth",
    "source_paths": [
      "data/test1",
      "data/test2",
      "data/test3"
    ],
    "device": "cuda"
  }'
```

### 6. 查看资源状态
```bash
curl http://localhost:8000/api/v2/resources
```

响应：
```json
{
  "device_usage": {
    "cuda": {
      "training": 1,
      "inference": 2
    }
  },
  "limits": {
    "cuda": {
      "training": 1,
      "inference": 3
    }
  },
  "gpu_info": {
    "available": true,
    "count": 1,
    "devices": [...]
  }
}
```

### 7. 健康检查
```bash
curl http://localhost:8000/api/v1/health
```

### 8. 取消任务
```bash
curl -X POST "http://localhost:8000/api/v2/tasks/{task_id}/cancel"
```

## 🔧 配置说明

### 环境变量
在 `.env` 文件中配置：

```bash
# 服务器
HOST=0.0.0.0
PORT=8000
DEBUG=true

# 资源限制
MAX_TRAINING_CONCURRENT_GPU=1    # GPU训练任务并发数
MAX_INFERENCE_CONCURRENT_GPU=3   # GPU推理任务并发数
MAX_TRAINING_CONCURRENT_CPU=2    # CPU训练任务并发数
MAX_INFERENCE_CONCURRENT_CPU=4   # CPU推理任务并发数
```

### 运行时更新配置
```bash
curl -X POST "http://localhost:8000/api/v2/resources/config" \
  -H "Content-Type: application/json" \
  -d '{
    "max_concurrent": {
      "cuda": {
        "training": 2,
        "inference": 5
      }
    }
  }'
```

## 🐍 Python客户端示例

### 安装客户端库
```bash
pip install requests
```

### 使用示例
```python
import requests
import time

# 服务器地址
BASE_URL = "http://localhost:8000"

# 1. 启动训练
response = requests.post(
    f"{BASE_URL}/api/v2/training/start",
    json={
        "model": "resnet18",
        "num_classes": 37,
        "train_path": "data/train",
        "val_path": "data/val",
        "save_path": "models/output",
        "batch_size": 16,
        "num_epochs": 50,
        "device": "cuda"
    }
)
task_id = response.json()["task_id"]
print(f"训练任务ID: {task_id}")

# 2. 轮询任务状态
while True:
    response = requests.get(f"{BASE_URL}/api/v2/tasks/{task_id}")
    task = response.json()
    print(f"状态: {task['status']}, 进度: {task.get('progress', 0)}%")
    
    if task["status"] in ["completed", "failed", "cancelled"]:
        break
    
    time.sleep(5)

# 3. 启动推理
response = requests.post(
    f"{BASE_URL}/api/v2/inference/start",
    json={
        "cfg_path": "configs/model.yaml",
        "weight_path": "models/best.pth",
        "source_path": "data/test",
        "device": "cuda"
    }
)
print(f"推理任务ID: {response.json()['task_id']}")

# 4. 查看所有任务
response = requests.get(f"{BASE_URL}/api/v2/tasks")
tasks = response.json()
print(f"训练任务: {tasks['total_training']}")
print(f"推理任务: {tasks['total_inference']}")
```

## 📊 监控和日志

### 实时日志流
```python
import requests

task_id = "your-task-id"
url = f"http://localhost:8000/api/v2/training/{task_id}/logs"

with requests.get(url, stream=True) as response:
    for line in response.iter_lines():
        if line:
            # 解析SSE格式
            if line.startswith(b'data: '):
                data = line[6:]  # 移除 'data: ' 前缀
                print(data.decode('utf-8'))
```

### Web监控界面
```bash
# 使用之前的 web_monitor.html
# 修改其中的API端点为新的路由
```

## 🧪 测试

### 健康检查
```bash
curl http://localhost:8000/api/v1/health
```

### GPU状态
```bash
curl http://localhost:8000/api/v2/resources/gpu
```

### 系统信息
```bash
curl http://localhost:8000/api/v1/info
```

## 🔍 故障排查

### 服务无法启动
1. 检查端口是否被占用
2. 检查依赖是否安装完整
3. 查看错误日志

### 任务一直排队
1. 检查资源状态: `GET /api/v2/resources`
2. 查看是否有任务占用资源
3. 调整并发限制配置

### GPU内存不足
1. 降低batch_size
2. 减少GPU并发任务数
3. 使用CPU进行推理

## 📚 更多文档

- [项目结构说明](REFACTORED_STRUCTURE.md) - 详细的架构说明
- [API文档](http://localhost:8000/docs) - 完整的API文档
- [配置说明](env.example) - 环境变量说明

## 🆚 与旧版本对比

### V2.2 → V2.3 重构版
✅ 代码结构更清晰
✅ 分层更明确
✅ 更易于维护和扩展
✅ 功能完全兼容
✅ 性能无损失

### 迁移指南
旧版端点仍然可用，新版建议使用 `/api/v2/*` 端点。

| 旧版 | 新版 |
|------|------|
| `POST /train` | `POST /api/v2/training/start` |
| `POST /inference` | `POST /api/v2/inference/start` |
| `GET /task/{id}` | `GET /api/v2/tasks/{id}` |


