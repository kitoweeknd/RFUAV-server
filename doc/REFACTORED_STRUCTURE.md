# 重构版项目结构说明

## 📁 项目结构

```
RFUAV-server/
├── app_refactored.py          # 主应用入口（重构版）⭐
├── .env                        # 环境配置文件
│
├── api/                        # API层 - 路由定义
│   ├── __init__.py
│   └── routers/               # 路由模块
│       ├── __init__.py
│       ├── training.py        # 训练路由
│       ├── inference.py       # 推理路由
│       ├── tasks.py           # 任务管理路由
│       ├── resources.py       # 资源管理路由
│       └── health.py          # 健康检查路由
│
├── services/                   # 服务层 - 业务逻辑
│   ├── __init__.py
│   ├── base_service.py        # 基础服务类
│   ├── training_service.py    # 训练服务
│   ├── inference_service.py   # 推理服务
│   └── task_service.py        # 任务管理服务
│
├── models/                     # 数据模型层
│   ├── __init__.py
│   └── schemas.py             # Pydantic模型定义
│
├── core/                       # 核心模块
│   ├── __init__.py
│   ├── config.py              # 配置管理
│   └── resource_manager.py    # 资源管理器
│
├── utils/                      # 工具模块（原有）
│   ├── trainer.py             # 训练器
│   ├── benchmark.py           # 推理和测试
│   └── ...
│
└── docs/                       # 文档
    ├── REFACTORED_STRUCTURE.md # 本文件
    └── API_ROUTES.md          # 路由表文档
```

## 🏗️ 架构层次

### 1. 入口层 (Entry Layer)
**文件**: `app_refactored.py`

**职责**:
- 创建FastAPI应用
- 配置中间件
- 注册路由
- 应用生命周期管理

**特点**:
- 代码简洁（< 150行）
- 只负责组装，不包含业务逻辑
- 清晰的路由注册

### 2. 路由层 (Router Layer)
**目录**: `api/routers/`

**职责**:
- 定义API端点
- 参数验证（通过Pydantic）
- 调用服务层
- 返回响应

**特点**:
- 每个模块专注一个功能域
- RESTful设计
- 完整的API文档注释

**路由模块**:
```python
training.py    → /api/v2/training/*
inference.py   → /api/v2/inference/*
tasks.py       → /api/v2/tasks/*
resources.py   → /api/v2/resources/*
health.py      → /api/v1/health, /api/v1/info
```

### 3. 服务层 (Service Layer)
**目录**: `services/`

**职责**:
- 业务逻辑实现
- 任务管理
- 资源调度
- 日志处理

**特点**:
- 单一职责原则
- 可测试性强
- 复用性高

**服务模块**:
```python
base_service.py        # 基础功能（日志、状态管理）
training_service.py    # 训练业务逻辑
inference_service.py   # 推理业务逻辑
task_service.py        # 任务统一管理
```

### 4. 模型层 (Model Layer)
**目录**: `models/`

**职责**:
- 数据模型定义
- 请求/响应模型
- 数据验证

**特点**:
- 使用Pydantic
- 类型安全
- 自动文档生成

### 5. 核心层 (Core Layer)
**目录**: `core/`

**职责**:
- 配置管理
- 资源管理
- 公共组件

**特点**:
- 单例模式（ResourceManager）
- 全局配置（Settings）
- 线程安全

### 6. 工具层 (Utils Layer)
**目录**: `utils/`

**职责**:
- 模型训练（Trainer）
- 模型推理（Benchmark）
- 数据处理

**特点**:
- 原有代码保持不变
- 被服务层调用
- 独立可测试

## 🔄 数据流

```
请求 → 路由层 → 服务层 → 工具层 → 服务层 → 路由层 → 响应
         ↓        ↓
      验证参数   业务逻辑
         ↓        ↓
      模型层   资源管理
```

### 示例：训练请求流程

```python
1. 客户端 → POST /api/v2/training/start
            ↓
2. training.py (路由层)
   - 接收请求
   - 验证TrainingRequest模型
            ↓
3. training_service.py (服务层)
   - 生成任务ID
   - 检查资源
   - 创建后台任务
            ↓
4. resource_manager.py (核心层)
   - 分配GPU/CPU资源
            ↓
5. trainer.py (工具层)
   - 执行实际训练
            ↓
6. 返回任务信息 → 客户端
```

## 🎯 设计优势

### 1. 清晰的分层
```
每一层只负责自己的职责
代码职责单一，易于理解
```

### 2. 高内聚低耦合
```
模块间通过接口通信
易于修改和扩展
```

### 3. 可测试性
```
每层可独立测试
Mock依赖简单
```

### 4. 可维护性
```
代码组织清晰
容易定位问题
新人上手快
```

### 5. 可扩展性
```
添加新功能只需：
1. models/schemas.py 添加模型
2. api/routers/ 添加路由
3. services/ 添加服务
```

## 📋 路由表

### 训练接口
| 端点 | 方法 | 功能 |
|------|------|------|
| `/api/v2/training/start` | POST | 启动训练 |
| `/api/v2/training/{id}` | GET | 查询状态 |
| `/api/v2/training/{id}/logs` | GET | 获取日志流 |
| `/api/v2/training/{id}/stop` | POST | 停止训练 |

### 推理接口
| 端点 | 方法 | 功能 |
|------|------|------|
| `/api/v2/inference/start` | POST | 启动推理 |
| `/api/v2/inference/batch` | POST | 批量推理 |
| `/api/v2/inference/{id}` | GET | 查询状态 |

### 任务管理
| 端点 | 方法 | 功能 |
|------|------|------|
| `/api/v2/tasks` | GET | 所有任务 |
| `/api/v2/tasks/{id}` | GET | 任务详情 |
| `/api/v2/tasks/{id}/logs` | GET | 任务日志 |
| `/api/v2/tasks/{id}/cancel` | POST | 取消任务 |
| `/api/v2/tasks/{id}` | DELETE | 删除任务 |

### 资源管理
| 端点 | 方法 | 功能 |
|------|------|------|
| `/api/v2/resources` | GET | 资源状态 |
| `/api/v2/resources/gpu` | GET | GPU信息 |
| `/api/v2/resources/config` | POST | 更新配置 |

### 系统状态
| 端点 | 方法 | 功能 |
|------|------|------|
| `/api/v1/health` | GET | 健康检查 |
| `/api/v1/info` | GET | 系统信息 |

## 🔧 配置管理

### 环境变量
创建 `.env` 文件：
```bash
# 应用配置
APP_NAME="RFUAV Model Service"
VERSION="2.3.0"
ENVIRONMENT="production"

# 服务器配置
HOST="0.0.0.0"
PORT=8000
DEBUG=false

# 资源限制
MAX_TRAINING_CONCURRENT_GPU=1
MAX_INFERENCE_CONCURRENT_GPU=3
MAX_TRAINING_CONCURRENT_CPU=2
MAX_INFERENCE_CONCURRENT_CPU=4
```

### 代码中使用
```python
from core.config import settings

print(settings.APP_NAME)
print(settings.MAX_TRAINING_CONCURRENT_GPU)
```

## 🚀 快速开始

### 1. 安装依赖
```bash
pip install -r requirements_refactored.txt
```

### 2. 配置环境
```bash
cp .env.example .env
# 编辑 .env 文件
```

### 3. 启动服务
```bash
python app_refactored.py
```

### 4. 访问文档
```
http://localhost:8000/docs
```

## 📝 添加新功能示例

### 场景：添加批量训练接口

#### 步骤1: 添加数据模型
```python
# models/schemas.py
class BatchTrainingRequest(BaseModel):
    configs: List[TrainingRequest]
```

#### 步骤2: 添加服务方法
```python
# services/training_service.py
async def start_batch_training(self, request, background_tasks):
    task_ids = []
    for config in request.configs:
        task_id = await self.start_training(config, background_tasks)
        task_ids.append(task_id)
    return task_ids
```

#### 步骤3: 添加路由
```python
# api/routers/training.py
@router.post("/batch")
async def batch_training(request: BatchTrainingRequest, ...):
    return await training_service.start_batch_training(request, ...)
```

完成！新接口 `POST /api/v2/training/batch` 可用。

## 🧪 测试建议

### 单元测试
```python
# tests/test_training_service.py
def test_generate_task_id():
    service = TrainingService()
    task_id = service.generate_task_id()
    assert len(task_id) == 36  # UUID length
```

### 集成测试
```python
# tests/test_api.py
def test_start_training():
    response = client.post("/api/v2/training/start", json={...})
    assert response.status_code == 200
```

## 📚 相关文档

- [API路由表](API_ROUTES.md)
- [配置说明](CONFIG.md)
- [开发指南](DEVELOPMENT.md)
- [部署指南](DEPLOYMENT.md)

