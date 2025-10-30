# RFUAV Model Service - 重构版 V2.3

> 🚀 无人机信号识别模型训练和推理服务 - 清晰的分层架构

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-green.svg)](https://fastapi.tiangolo.com/)
[![PyTorch](https://img.shields.io/badge/PyTorch-2.0+-red.svg)](https://pytorch.org/)

## ✨ 特性

### 🎯 核心功能
- ✅ **参数化训练** - 无需配置文件，API直接指定参数
- ✅ **灵活推理** - 单次推理、批量推理
- ✅ **实时日志** - Server-Sent Events流式传输
- ✅ **设备选择** - 动态选择GPU/CPU，支持多GPU选择
- ✅ **智能GPU调度** - 自动选择最优GPU，支持具体GPU指定（cuda:0, cuda:1等）
- ✅ **并发优化** - 智能资源管理和任务调度
- ✅ **任务管理** - 完整的任务生命周期管理
- ✅ **GPU监控** - 启动时显示GPU信息，实时追踪使用情况
- ✅ **标准JSON格式** - 所有请求和响应都是严格的JSON格式，类型安全

### 🏗️ 架构优势
- 📂 **清晰分层** - 路由、服务、模型、核心层次分明
- 🔄 **高内聚低耦合** - 模块职责单一，易于维护
- 🧪 **可测试性强** - 每层可独立测试
- 📈 **易于扩展** - 添加新功能只需3步
- 📖 **代码易读** - 结构清晰，注释完整

## 📊 架构对比

### 旧版本
```
app.py (600+ 行)
├── 所有路由混在一起
├── 业务逻辑和路由耦合
├── 难以维护和扩展
└── 代码重复多
```

### 重构版 (V2.3)
```
app_refactored.py (150 行)
├── api/routers/         ← 路由层（清晰的端点定义）
├── services/            ← 服务层（业务逻辑）
├── models/              ← 数据模型层（类型安全）
├── core/                ← 核心层（配置和资源管理）
└── utils/               ← 工具层（原有功能）
```

## 🚀 快速开始

### 安装
```bash
pip install -r requirements_refactored.txt
```

### 配置（可选）
```bash
cp env.example .env
# 编辑 .env 修改配置
```

### 启动
```bash
python app_refactored.py
```

### 访问
- 📖 API文档: http://localhost:8000/docs
- 📋 路由表: http://localhost:8000/
- 🏥 健康检查: http://localhost:8000/api/v1/health

## 📋 API路由表

### 🎓 训练接口
| 端点 | 方法 | 功能 |
|------|------|------|
| `/api/v2/training/start` | POST | 启动训练 |
| `/api/v2/training/{id}` | GET | 查询状态 |
| `/api/v2/training/{id}/logs` | GET | 日志流 |
| `/api/v2/training/{id}/stop` | POST | 停止训练 |

### 🔍 推理接口
| 端点 | 方法 | 功能 |
|------|------|------|
| `/api/v2/inference/start` | POST | 启动推理 |
| `/api/v2/inference/batch` | POST | 批量推理 |
| `/api/v2/inference/{id}` | GET | 查询状态 |

### 📊 任务管理
| 端点 | 方法 | 功能 |
|------|------|------|
| `/api/v2/tasks` | GET | 所有任务 |
| `/api/v2/tasks/{id}` | GET | 任务详情 |
| `/api/v2/tasks/{id}/logs` | GET | 任务日志 |
| `/api/v2/tasks/{id}/cancel` | POST | 取消任务 |
| `/api/v2/tasks/{id}` | DELETE | 删除任务 |

### ⚙️ 资源管理
| 端点 | 方法 | 功能 |
|------|------|------|
| `/api/v2/resources` | GET | 资源状态 |
| `/api/v2/resources/gpu` | GET | GPU信息 |
| `/api/v2/resources/config` | POST | 更新配置 |

### 🏥 系统状态
| 端点 | 方法 | 功能 |
|------|------|------|
| `/api/v1/health` | GET | 健康检查 |
| `/api/v1/info` | GET | 系统信息 |

## 💡 使用示例

### Python客户端
```python
from test_refactored_api import RFUAVClient

client = RFUAVClient("http://localhost:8000")

# 启动训练（自动选择GPU）
result = client.start_training(
    model="resnet18",
    num_classes=37,
    train_path="data/train",
    val_path="data/val",
    save_path="models/output",
    device="cuda"  # 自动选择最优GPU
)
task_id = result["task_id"]

# 或者指定具体GPU
result = client.start_training(
    model="resnet50",
    num_classes=37,
    train_path="data/train",
    val_path="data/val",
    save_path="models/output_gpu0",
    device="cuda:0"  # 指定GPU 0
)

# 等待完成
client.wait_for_task(task_id)
```

### cURL
```bash
# 启动训练
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

# 查询状态
curl http://localhost:8000/api/v2/tasks/{task_id}

# 资源状态
curl http://localhost:8000/api/v2/resources
```

## 🎮 GPU设备选择

### 启动时自动显示GPU信息

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
======================================================================
```

### 三种设备选择方式

```python
# 1. 自动选择（推荐） - 系统选择负载最小的GPU
device="cuda"

# 2. 指定GPU 0
device="cuda:0"

# 3. 指定GPU 1
device="cuda:1"

# 4. 使用CPU
device="cpu"
```

### 查看GPU使用情况

```bash
# 查看资源状态
curl http://localhost:8000/api/v2/resources

# 查看GPU详细信息
curl http://localhost:8000/api/v2/resources/gpu
```

**详细说明**: 查看 [GPU设备选择指南](GPU_SELECTION_GUIDE.md)

---

## 📁 项目结构

```
RFUAV-server/
│
├── app_refactored.py              # 主入口 ⭐
│
├── api/                           # API层
│   └── routers/                   # 路由模块
│       ├── training.py            # 训练路由
│       ├── inference.py           # 推理路由
│       ├── tasks.py               # 任务管理
│       ├── resources.py           # 资源管理
│       └── health.py              # 健康检查
│
├── services/                      # 服务层
│   ├── base_service.py            # 基础服务
│   ├── training_service.py        # 训练服务
│   ├── inference_service.py       # 推理服务
│   └── task_service.py            # 任务服务
│
├── models/                        # 数据模型层
│   └── schemas.py                 # Pydantic模型
│
├── core/                          # 核心层
│   ├── config.py                  # 配置管理
│   └── resource_manager.py        # 资源管理器
│
├── utils/                         # 工具层（原有）
│   ├── trainer.py
│   └── benchmark.py
│
└── docs/                          # 文档
    ├── REFACTORED_STRUCTURE.md    # 架构说明
    ├── QUICK_START_REFACTORED.md  # 快速开始
    └── README_REFACTORED.md       # 本文件
```

## 🎯 设计原则

### 1. 分层清晰
```
请求 → 路由层 → 服务层 → 工具层
       ↓        ↓
    参数验证  业务逻辑
```

### 2. 单一职责
- 每个模块只做一件事
- 路由只负责接收请求
- 服务只负责业务逻辑

### 3. 依赖注入
- 服务通过构造函数注入
- 配置通过环境变量
- 资源通过管理器分配

### 4. 类型安全
- Pydantic模型验证
- 类型注解完整
- IDE友好

## 🔧 配置管理

### 环境变量
在 `.env` 文件中配置：

```bash
# 服务器
HOST=0.0.0.0
PORT=8000

# 资源限制
MAX_TRAINING_CONCURRENT_GPU=1
MAX_INFERENCE_CONCURRENT_GPU=3
MAX_TRAINING_CONCURRENT_CPU=2
MAX_INFERENCE_CONCURRENT_CPU=4
```

### 代码中使用
```python
from core.config import settings

print(settings.PORT)  # 8000
print(settings.MAX_TRAINING_CONCURRENT_GPU)  # 1
```

### 运行时更新
```bash
curl -X POST "http://localhost:8000/api/v2/resources/config" \
  -d '{"max_concurrent": {"cuda": {"training": 2}}}'
```

## 📈 扩展示例

### 添加新功能：模型评估接口

#### 1. 定义数据模型
```python
# models/schemas.py
class EvaluationRequest(BaseModel):
    cfg_path: str
    weight_path: str
    test_path: str
    device: str = "cuda"
```

#### 2. 创建服务
```python
# services/evaluation_service.py
class EvaluationService(BaseService):
    async def start_evaluation(self, request, background_tasks):
        # 评估逻辑
        pass
```

#### 3. 添加路由
```python
# api/routers/evaluation.py
@router.post("/start")
async def start_evaluation(request: EvaluationRequest, ...):
    return await evaluation_service.start_evaluation(request, ...)
```

#### 4. 注册路由
```python
# app_refactored.py
from api.routers import evaluation

app.include_router(
    evaluation.router,
    prefix="/api/v2/evaluation",
    tags=["Evaluation"]
)
```

完成！新接口立即可用。

## 🧪 测试

### 运行测试客户端
```bash
python test_refactored_api.py
```

### 健康检查
```bash
curl http://localhost:8000/api/v1/health
```

### 系统信息
```bash
curl http://localhost:8000/api/v1/info
```

## 📚 文档

- 📖 [架构说明](REFACTORED_STRUCTURE.md) - 详细的架构设计
- 🚀 [快速开始](QUICK_START_REFACTORED.md) - 使用指南
- 🎮 [GPU设备选择指南](GPU_SELECTION_GUIDE.md) - GPU选择和使用 ⭐
- 📋 [API路由表](API_ROUTES_TABLE.md) - 完整API参考
- 📝 [JSON API规范](JSON_API_SPEC.md) - JSON格式说明 ⭐
- 🔄 [JSON格式更新](JSON_FORMAT_UPDATE.md) - 格式标准化说明
- 🆚 [版本对比](VERSION_COMPARISON_REFACTORED.md) - 新旧版本对比
- 🔧 [配置说明](env.example) - 环境变量
- 🌐 [API文档](http://localhost:8000/docs) - 在线API文档
- 🌐 [Web测试界面](test_web_ui.html) - 浏览器测试工具

## 🆚 版本对比

| 特性 | V2.2 (旧版) | V2.3 (重构版) |
|------|-------------|---------------|
| 代码行数 | ~600行 | ~150行(入口) |
| 模块化 | ⚠️ 一般 | ✅ 优秀 |
| 可维护性 | ⚠️ 一般 | ✅ 优秀 |
| 可扩展性 | ⚠️ 困难 | ✅ 简单 |
| 可测试性 | ⚠️ 困难 | ✅ 简单 |
| 功能完整性 | ✅ 完整 | ✅ 完整 |
| 性能 | ✅ 优秀 | ✅ 优秀 |

## 🤝 贡献

欢迎贡献！请遵循以下步骤：

1. Fork项目
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启Pull Request

## 📝 更新日志

### V2.3.0 (重构版)
- ✨ 重构整个项目结构
- 📂 清晰的分层架构
- 🔄 服务和路由解耦
- 📖 完整的代码注释
- 🧪 更好的可测试性

### V2.2.0
- ✨ 并发优化
- ✨ 资源管理器
- ✨ 任务调度器

### V2.1.0
- ✨ 参数化训练
- ✨ 实时日志流
- ✨ 设备选择

## 📄 许可证

MIT License

## 👥 作者

RFUAV Team

## 🙏 致谢

- FastAPI - Web框架
- PyTorch - 深度学习框架
- Uvicorn - ASGI服务器

---

⭐ 如果这个项目对你有帮助，请给我们一个Star！

