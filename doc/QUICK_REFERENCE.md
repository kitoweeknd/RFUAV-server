# 快速参考卡 (Quick Reference Card)

> 一页纸快速查阅所有重要信息

## 📚 文档快速索引

| 需求 | 推荐文档 | 时间 |
|------|---------|------|
| **第一次使用** | [README_COMPLETE.md](README_COMPLETE.md) | 30min |
| **快速开始** | [QUICK_START_REFACTORED.md](QUICK_START_REFACTORED.md) | 15min |
| **版本选择** | [APP_VERSIONS_GUIDE.md](APP_VERSIONS_GUIDE.md) ⭐ | 10min |
| **代码审阅** | [CODE_CHANGE_LOG.md](CODE_CHANGE_LOG.md) ⭐ | 2-3h |
| **GPU使用** | [GPU_SELECTION_GUIDE.md](GPU_SELECTION_GUIDE.md) | 1h |
| **API开发** | [API_ROUTES_TABLE.md](API_ROUTES_TABLE.md) | 1h |
| **Web测试** | [test_web_ui.html](test_web_ui.html) | 即时 |
| **文档导航** | [DOCUMENTATION_INDEX.md](DOCUMENTATION_INDEX.md) | 5min |

---

## 🚀 快速命令

### 启动服务
```bash
python app_refactored.py
```

### 测试功能
```bash
# JSON格式测试
python test_json_format.py

# GPU功能测试
python test_gpu_feature.py

# API客户端测试
python test_refactored_api.py
```

### 查看文档
```bash
# 浏览器访问
http://localhost:8000/docs        # Swagger UI
http://localhost:8000/redoc       # ReDoc
http://localhost:8000/             # 路由表

# 打开Web界面
# 双击 test_web_ui.html
```

---

## 🎮 GPU设备选择

### 三种方式
```python
device = "cuda"     # 自动选择最优GPU（推荐）
device = "cuda:0"   # 指定GPU 0
device = "cuda:1"   # 指定GPU 1
device = "cpu"      # 使用CPU
```

### 查看GPU
```bash
curl http://localhost:8000/api/v2/resources/gpu
```

---

## 📋 API端点速查

### 训练接口

| 端点 | 方法 | 必需参数 | 可选参数 |
|------|------|---------|---------|
| `/api/v2/training/start` | POST | model, num_classes, train_path, val_path, save_path | batch_size, num_epochs, learning_rate, device, ... |
| `/api/v2/training/{id}` | GET | task_id (路径) | - |
| `/api/v2/training/{id}/logs` | GET | task_id (路径) | - |
| `/api/v2/training/{id}/stop` | POST | task_id (路径) | - |

### 推理接口

| 端点 | 方法 | 必需参数 | 可选参数 |
|------|------|---------|---------|
| `/api/v2/inference/start` | POST | cfg_path, weight_path, source_path | save_path, device, priority |
| `/api/v2/inference/batch` | POST | cfg_path, weight_path, source_paths | save_base_path, device |
| `/api/v2/inference/{id}` | GET | task_id (路径) | - |

### 任务管理

| 端点 | 方法 | 必需参数 | 响应类型 |
|------|------|---------|---------|
| `/api/v2/tasks` | GET | - | TaskListResponse |
| `/api/v2/tasks/{id}` | GET | task_id (路径) | TaskResponse |
| `/api/v2/tasks/{id}/logs` | GET | task_id (路径) | array[LogEntry] |
| `/api/v2/tasks/{id}/cancel` | POST | task_id (路径) | TaskActionResponse |
| `/api/v2/tasks/{id}` | DELETE | task_id (路径) | TaskActionResponse |

### 资源管理

| 端点 | 方法 | 返回信息 |
|------|------|---------|
| `/api/v2/resources` | GET | device_usage, active_tasks, limits, gpu_info |
| `/api/v2/resources/gpu` | GET | GPU详细信息(型号、显存、利用率等) |
| `/api/v2/resources/config` | POST | 更新并发限制配置 |

### 系统状态

| 端点 | 方法 | 返回信息 |
|------|------|---------|
| `/api/v1/health` | GET | status, version, 任务统计, 资源状态 |
| `/api/v1/info` | GET | 应用信息, 支持的模型, 资源限制 |

### 关键参数说明

**训练请求 (TrainingRequest)**
- 必需: `model`, `num_classes`, `train_path`, `val_path`, `save_path`
- 常用可选: `device` (默认"cuda"), `batch_size` (默认8), `num_epochs` (默认100)

**推理请求 (InferenceRequest)**
- 必需: `cfg_path`, `weight_path`, `source_path`
- 常用可选: `device` (默认"cuda"), `save_path`, `priority`

**响应字段 (TaskResponse)**
- 核心字段: `task_id`, `task_type`, `status`, `progress`, `device`
- 时间字段: `created_at`, `updated_at`
- 状态值: pending, running, completed, failed, cancelled

---

## 💡 代码示例

### Python启动训练
```python
from test_refactored_api import RFUAVClient

client = RFUAVClient("http://localhost:8000")

result = client.start_training(
    model="resnet18",
    num_classes=37,
    train_path="data/train",
    val_path="data/val",
    save_path="models/output",
    device="cuda",  # 自动选择
    batch_size=16,
    num_epochs=50
)

print(f"Task ID: {result['task_id']}")
print(f"Device: {result['device']}")
```

### cURL启动训练
```bash
curl -X POST http://localhost:8000/api/v2/training/start \
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

---

## 🗂️ 项目结构

```
RFUAV-server/
├── app_refactored.py          # 主入口 ⭐
├── api/routers/               # API路由
├── services/                  # 业务逻辑
├── models/schemas.py          # 数据模型
├── core/                      # 核心模块
│   ├── config.py             # 配置
│   └── resource_manager.py   # 资源管理
├── test_web_ui.html          # Web测试界面
└── test_refactored_api.py    # Python客户端
```

---

## ⚙️ 配置文件

### .env 示例
```bash
HOST=0.0.0.0
PORT=8000
MAX_TRAINING_CONCURRENT_GPU=1
MAX_INFERENCE_CONCURRENT_GPU=3
```

---

## 🐛 故障排查

| 问题 | 解决方案 |
|------|---------|
| 服务无法启动 | 检查端口、Python版本、依赖 |
| GPU不可用 | 检查CUDA、PyTorch |
| 任务排队 | 查看资源状态、调整限制 |
| 显存不足 | 降低batch_size、使用其他GPU |

### 快速检查
```bash
# 检查服务
curl http://localhost:8000/api/v1/health

# 查看GPU
curl http://localhost:8000/api/v2/resources/gpu

# 查看资源
curl http://localhost:8000/api/v2/resources
```

---

## 📊 关键指标

| 指标 | 值 |
|------|-----|
| 启动时间 | ~2.5秒 |
| API响应 | ~50ms |
| 支持模型 | 14+ |
| 并发任务 | 可配置 |

---

## 🔗 重要链接

- **完整文档**: [README_COMPLETE.md](README_COMPLETE.md)
- **代码日志**: [CODE_CHANGE_LOG.md](CODE_CHANGE_LOG.md)
- **文档索引**: [DOCUMENTATION_INDEX.md](DOCUMENTATION_INDEX.md)
- **在线文档**: http://localhost:8000/docs

---

## ✅ 检查清单

### 首次使用
- [ ] 安装PyTorch: `pip install torch==2.0.1+cu118 torchvision==0.15.2+cu118 --extra-index-url https://download.pytorch.org/whl/cu118`
- [ ] 安装依赖: `pip install -r requirements.txt`
- [ ] 验证安装: `python check_installation.py`
- [ ] 启动服务: `python app_refactored.py`
- [ ] 验证服务: `curl http://localhost:8000/api/v1/health`
- [ ] 查看GPU: `curl http://localhost:8000/api/v2/resources/gpu`
- [ ] 打开Web界面: 双击 `test_web_ui.html`

### 代码审阅
- [ ] 阅读 [CODE_CHANGE_LOG.md](CODE_CHANGE_LOG.md)
- [ ] 检查 [REFACTORED_STRUCTURE.md](REFACTORED_STRUCTURE.md)
- [ ] 查看源代码
- [ ] 运行测试: `python test_json_format.py`
- [ ] 验证GPU功能: `python test_gpu_feature.py`

---

**版本**: V2.3.1  
**最后更新**: 2024-01  

**需要帮助？** 查看 [DOCUMENTATION_INDEX.md](DOCUMENTATION_INDEX.md)

