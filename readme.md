# RFUAV Model Service - 完整文档

> 🚀 无人机信号识别模型训练和推理服务 - 重构版 V2.4.0

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-green.svg)](https://fastapi.tiangolo.com/)
[![PyTorch](https://img.shields.io/badge/PyTorch-2.0+-red.svg)](https://pytorch.org/)

## 📑 目录

- [项目概述](#项目概述)
- [快速开始](#快速开始)
- [核心功能](#核心功能)
- [项目架构](#项目架构)
- [GPU设备选择](#gpu设备选择)
- [API接口](#api接口)
- [JSON格式规范](#json格式规范)
- [Web测试界面](#web测试界面)
- [配置说明](#配置说明)
- [使用示例](#使用示例)
- [故障排查](#故障排查)
- [版本历史](#版本历史)

---

## 项目概述

### 简介

RFUAV Model Service 是一个基于FastAPI的深度学习模型服务系统，专为无人机信号识别设计。系统采用清晰的分层架构，支持灵活的GPU设备选择和智能资源管理。

### 核心特性

#### 🎯 功能特性
- ✅ **参数化训练** - 无需配置文件，API直接指定所有训练参数
- ✅ **详细训练指标** - 实时返回loss、accuracy、F1、mAP等15+种指标
- ✅ **数据预处理** - 数据集分割、数据增强、图像裁剪一站式解决方案 ⭐新
- ✅ **灵活推理** - 支持单次推理和批量推理
- ✅ **实时日志流** - Server-Sent Events实时流式传输训练日志和指标
- ✅ **智能GPU调度** - 自动选择最优GPU或手动指定设备
- ✅ **多GPU支持** - 支持cuda:0、cuda:1等多GPU选择
- ✅ **并发优化** - 智能资源管理和任务队列调度
- ✅ **任务管理** - 完整的任务生命周期管理
- ✅ **标准JSON** - 所有请求和响应都是严格的JSON格式

#### 🏗️ 架构特性
- 📂 **清晰分层** - 路由层、服务层、模型层、核心层分离
- 🔄 **高内聚低耦合** - 模块职责单一，易于维护
- 🧪 **可测试性强** - 每层可独立测试
- 📈 **易于扩展** - 添加新功能只需3步
- 📖 **代码易读** - 结构清晰，注释完整

#### 🎮 GPU特性
- ✅ **启动显示GPU信息** - 服务启动时自动输出所有GPU详细信息
- ✅ **实时监控** - 显存使用、利用率、任务数量实时追踪
- ✅ **智能选择** - 系统自动选择负载最小的GPU
- ✅ **手动指定** - 支持指定具体GPU设备（cuda:0、cuda:1等）
- ✅ **负载均衡** - 多GPU环境下自动负载均衡

### 支持的模型

- **ResNet系列**: resnet18, resnet34, resnet50, resnet101, resnet152
- **ViT系列**: vit_b_16, vit_b_32, vit_l_16, vit_l_32
- **Swin Transformer**: swin_v2_t, swin_v2_s, swin_v2_b
- **MobileNet**: mobilenet_v3_large, mobilenet_v3_small

---

## 快速开始

### 1. 环境准备

#### 系统要求
- Python 3.8+
- CUDA 11.0+ (如果使用GPU)
- PyTorch 2.0+

#### 安装依赖

**基础安装**（推荐）：
```bash
# GPU版本（CUDA 11.8）
pip install torch==2.0.1+cu118 torchvision==0.15.2+cu118 --extra-index-url https://download.pytorch.org/whl/cu118
pip install -r requirements.txt
```

**其他安装方式**：
```bash
# CPU版本
pip install torch==2.0.1+cpu torchvision==0.15.2+cpu --extra-index-url https://download.pytorch.org/whl/cpu
pip install -r requirements.txt

# 开发环境（包含测试和代码检查工具）
pip install -r requirements-dev.txt

# 测试环境
pip install -r requirements-test.txt

# 生产环境（包含监控和优化工具）
pip install -r requirements-prod.txt
```

**验证安装**：
```bash
python check_installation.py
```

主要依赖：
```
# Web框架
fastapi>=0.104.0
uvicorn[standard]>=0.24.0

# 数据验证
pydantic>=2.0.0
pydantic-settings>=2.0.0

# 深度学习
torch>=2.0.0
torchvision>=0.15.0

# 图像处理
opencv-python>=4.8.0
Pillow>=10.0.0
albumentations>=1.4.0

# 数据处理
numpy>=1.24.0
pandas>=2.0.0
```

完整依赖列表参见 [INSTALLATION_GUIDE.md](INSTALLATION_GUIDE.md)

### 2. 配置环境（可选）

```bash
# 复制配置文件
cp env.example .env

# 编辑配置
nano .env
```

主要配置项：
```bash
# 服务器配置
HOST=0.0.0.0
PORT=8000

# 资源限制
MAX_TRAINING_CONCURRENT_GPU=1
MAX_INFERENCE_CONCURRENT_GPU=3

# 支持的模型
SUPPORTED_MODELS="resnet18,resnet50,vit_b_16,..."
```

### 3. 启动服务

> **注意**: 项目包含3个版本的app文件，推荐使用 `app_refactored.py` (V2.3.1)
> 
> 详细版本说明请参考：[APP_VERSIONS_GUIDE.md](APP_VERSIONS_GUIDE.md)

#### 方式1: Python直接运行（推荐）
```bash
python app_refactored.py
```

#### 方式2: Uvicorn
```bash
uvicorn app_refactored:app --host 0.0.0.0 --port 8000 --reload
```

#### 方式3: 使用启动脚本
```bash
# Windows
start_refactored.bat

# Linux/Mac
./start_refactored.sh
```

#### 其他版本（可选）
```bash
# V2.2.0 - 并发优化版
python app_concurrent.py

# V2.0.0 - 增强版
python app_enhanced.py
```

### 4. 验证服务

```bash
# 健康检查
curl http://localhost:8000/api/v1/health

# 查看GPU信息
curl http://localhost:8000/api/v2/resources/gpu

# 查看API文档
# 浏览器访问: http://localhost:8000/docs
```

### 5. 启动时GPU信息显示

服务启动后会自动显示：
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

---

## 核心功能

### 0. 数据预处理 ⭐新

在训练之前，您可能需要准备数据集。系统提供了完整的数据预处理功能。

#### 数据集分割
```python
from test_refactored_api import RFUAVClient

client = RFUAVClient("http://localhost:8000")

# 分割数据集为train/val/test
result = client.split_dataset(
    input_path="data/raw_dataset",
    output_path="data/split_dataset",
    train_ratio=0.7,   # 70% 训练集
    val_ratio=0.2      # 20% 验证集，剩余10%测试集
)
task_id = result['task_id']
print(f"分割任务已启动: {task_id}")
```

#### 数据增强
```python
# 对数据集进行增强
result = client.augment_dataset(
    dataset_path="data/split_dataset",
    output_path="data/augmented_dataset",
    methods=["CLAHE", "ColorJitter", "GaussNoise"]  # 选择增强方法
)
task_id = result['task_id']
print(f"增强任务已启动: {task_id}")
```

#### 图像裁剪
```python
# 批量裁剪图像
result = client.crop_images(
    input_path="data/images",
    output_path="data/cropped",
    x=100, y=100,
    width=500, height=500
)
task_id = result['task_id']
print(f"裁剪任务已启动: {task_id}")
```

**支持的数据增强方法**:
- **AdvancedBlur** - 高级模糊
- **CLAHE** - 对比度受限自适应直方图均衡化
- **ColorJitter** - 颜色抖动（亮度、对比度、饱和度）
- **GaussNoise** - 高斯噪声
- **ISONoise** - ISO噪声
- **Sharpen** - 锐化

详细使用指南：[数据预处理完整文档](./PREPROCESSING_GUIDE.md)

---

### 1. 训练任务

#### 启动训练
```python
from test_refactored_api import RFUAVClient

client = RFUAVClient("http://localhost:8000")

# 自动选择GPU
result = client.start_training(
    model="resnet18",
    num_classes=37,
    train_path="data/train",
    val_path="data/val",
    save_path="models/output",
    batch_size=16,
    num_epochs=50,
    device="cuda"  # 自动选择最优GPU
)

print(f"Task ID: {result['task_id']}")
print(f"Device: {result['device']}")
```

#### 指定GPU训练
```python
# 使用GPU 0
result = client.start_training(
    model="resnet50",
    num_classes=37,
    train_path="data/train",
    val_path="data/val",
    save_path="models/output_gpu0",
    device="cuda:0"  # 指定GPU 0
)
```

#### 查看训练状态（含详细指标）⭐新
```python
# 查询状态
status = client.get_task(task_id)
print(f"Status: {status['status']}")
print(f"Progress: {status['progress']}%")

# 查看详细训练指标
if status.get('latest_metrics'):
    metrics = status['latest_metrics']
    print(f"\n当前训练指标:")
    print(f"  Epoch: {status['current_epoch']}/{status['total_epochs']}")
    print(f"  训练损失: {metrics.get('train_loss', 'N/A')}")
    print(f"  训练准确率: {metrics.get('train_acc', 'N/A')}%")
    print(f"  验证损失: {metrics.get('val_loss', 'N/A')}")
    print(f"  验证准确率: {metrics.get('val_acc', 'N/A')}%")
    print(f"  Macro F1: {metrics.get('macro_f1', 'N/A')}")
    print(f"  mAP: {metrics.get('mAP', 'N/A')}")
    print(f"  Top-1准确率: {metrics.get('top1_acc', 'N/A')}%")
    print(f"  最佳准确率: {metrics.get('best_acc', 'N/A')}%")
```

#### 实时日志（含指标）⭐新
```python
# 连接日志流（包含训练指标）
for log in client.stream_training_logs(task_id):
    print(f"[{log['level']}] {log['message']}")
    
    # 如果日志包含训练指标，显示详细信息
    if log.get('metrics'):
        metrics = log['metrics']
        stage = log.get('stage', '')
        print(f"  └─ 阶段: {stage}")
        if metrics.get('train_acc'):
            print(f"  └─ 训练准确率: {metrics['train_acc']}%")
        if metrics.get('val_acc'):
            print(f"  └─ 验证准确率: {metrics['val_acc']}%")
```

### 2. 推理任务

#### 单次推理
```python
result = client.start_inference(
    cfg_path="configs/model.yaml",
    weight_path="models/best.pth",
    source_path="data/test",
    device="cuda:1"  # 使用GPU 1
)
```

#### 批量推理
```python
result = client.start_batch_inference(
    cfg_path="configs/model.yaml",
    weight_path="models/best.pth",
    source_paths=[
        "data/test1",
        "data/test2",
        "data/test3"
    ],
    device="cuda"  # 自动分配
)
print(f"Started {result['total']} tasks")
```

### 3. GPU设备选择

#### 三种选择方式

**1. 自动选择（推荐）**
```python
device = "cuda"  # 系统自动选择负载最小的GPU
```

**2. 指定GPU 0**
```python
device = "cuda:0"  # 固定使用第一块GPU
```

**3. 指定GPU 1**
```python
device = "cuda:1"  # 固定使用第二块GPU
```

**4. 使用CPU**
```python
device = "cpu"  # 使用CPU计算
```

#### 查看GPU信息
```python
gpu_info = client.get_gpu_info()
print(f"GPU Count: {gpu_info['count']}")
for device in gpu_info['devices']:
    print(f"GPU {device['id']}: {device['name']}")
    print(f"  Memory: {device['free_memory_gb']:.2f} GB free")
    print(f"  Tasks: {device['current_tasks']}")
```

### 4. 资源监控

```python
# 查看资源状态
resources = client.get_resources()

# 设备使用情况
for device, usage in resources['device_usage'].items():
    print(f"{device}: Train={usage['training']}, Infer={usage['inference']}")

# 资源限制
for device, limits in resources['limits'].items():
    print(f"{device}: Max Train={limits['training']}, Max Infer={limits['inference']}")
```

### 5. 任务管理

```python
# 获取所有任务
tasks = client.get_all_tasks()
print(f"Training: {tasks['total_training']}")
print(f"Inference: {tasks['total_inference']}")

# 取消任务
client.cancel_task(task_id)

# 删除任务记录
client.delete_task(task_id)
```

---

## 项目架构

### 目录结构

```
RFUAV-server/
│
├── app_refactored.py              # 主应用入口 ⭐
│
├── api/                           # API层 - 路由定义
│   └── routers/
│       ├── training.py            # 训练接口
│       ├── inference.py           # 推理接口
│       ├── tasks.py               # 任务管理
│       ├── resources.py           # 资源管理
│       └── health.py              # 健康检查
│
├── services/                      # 服务层 - 业务逻辑
│   ├── base_service.py            # 基础服务
│   ├── training_service.py        # 训练服务
│   ├── inference_service.py       # 推理服务
│   └── task_service.py            # 任务管理
│
├── models/                        # 数据模型层
│   └── schemas.py                 # Pydantic模型
│
├── core/                          # 核心层
│   ├── config.py                  # 配置管理
│   └── resource_manager.py        # 资源管理器
│
├── utils/                         # 工具层（原有）
│   ├── trainer.py                 # 训练器
│   └── benchmark.py               # 推理测试
│
├── test_web_ui.html              # Web测试界面
├── test_refactored_api.py        # Python测试客户端
└── test_json_format.py           # JSON格式测试
```

### 架构层次

```
┌─────────────────────────────────────────────┐
│         客户端请求 (JSON)                    │
└─────────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────────┐
│    路由层 (API Routers)                      │
│    - 接收请求                                │
│    - 参数验证 (Pydantic)                     │
│    - 调用服务层                              │
└─────────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────────┐
│    服务层 (Services)                         │
│    - 业务逻辑                                │
│    - 任务管理                                │
│    - 资源调度                                │
└─────────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────────┐
│    核心层 (Core)                             │
│    - 配置管理 (Settings)                     │
│    - 资源管理 (ResourceManager)              │
└─────────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────────┐
│    工具层 (Utils)                            │
│    - 训练器 (Trainer)                        │
│    - 推理器 (Benchmark)                      │
└─────────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────────┐
│         响应 (JSON)                          │
└─────────────────────────────────────────────┘
```

### 设计原则

1. **单一职责** - 每个模块只做一件事
2. **依赖倒置** - 高层模块不依赖低层模块
3. **接口隔离** - 客户端不依赖不需要的接口
4. **开闭原则** - 对扩展开放，对修改关闭

---

## GPU设备选择

### 自动选择算法

系统会自动选择负载最小的GPU：
```python
def _select_best_gpu(self, task_type: str) -> str:
    """选择负载最小的GPU"""
    best_gpu = None
    min_load = float('inf')
    
    for i in range(self.gpu_count):
        gpu_device = f"cuda:{i}"
        current_load = self.device_usage[gpu_device][task_type]
        if current_load < min_load:
            min_load = current_load
            best_gpu = gpu_device
    
    return best_gpu
```

### 使用场景

#### 单GPU环境
```python
# 使用 cuda 或 cuda:0 都可以
device = "cuda"  # 推荐
```

#### 双GPU - 训练推理分离
```python
# 训练固定在GPU 0（显存大）
train_device = "cuda:0"

# 推理固定在GPU 1（显存小但足够）
infer_device = "cuda:1"
```

#### 多GPU - 自动负载均衡
```python
# 所有任务使用 cuda，系统自动分配
device = "cuda"  # 系统自动选择负载最小的GPU
```

### GPU信息查询

```bash
# 查看GPU详细信息
curl http://localhost:8000/api/v2/resources/gpu

# 查看资源使用状态
curl http://localhost:8000/api/v2/resources
```

响应示例：
```json
{
  "available": true,
  "count": 2,
  "devices": [
    {
      "id": 0,
      "device_name": "cuda:0",
      "name": "NVIDIA GeForce RTX 3090",
      "total_memory_gb": 24.0,
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

## API接口

### 完整路由表

#### 训练接口
| 端点 | 方法 | 功能 |
|------|------|------|
| `/api/v2/training/start` | POST | 启动训练 |
| `/api/v2/training/{id}` | GET | 查询状态（含详细指标）|
| `/api/v2/training/{id}/logs` | GET | 日志流（含训练指标）|
| `/api/v2/training/{id}/stop` | POST | 停止训练 |

#### 数据预处理接口 ⭐新
| 端点 | 方法 | 功能 |
|------|------|------|
| `/api/v2/preprocessing/split` | POST | 数据集分割 |
| `/api/v2/preprocessing/augment` | POST | 数据增强 |
| `/api/v2/preprocessing/crop` | POST | 图像裁剪 |
| `/api/v2/preprocessing/{id}` | GET | 查询状态 |
| `/api/v2/preprocessing/{id}/logs` | GET | 日志流 |

#### 推理接口
| 端点 | 方法 | 功能 |
|------|------|------|
| `/api/v2/inference/start` | POST | 启动推理 |
| `/api/v2/inference/batch` | POST | 批量推理 |
| `/api/v2/inference/{id}` | GET | 查询状态 |

#### 任务管理
| 端点 | 方法 | 功能 |
|------|------|------|
| `/api/v2/tasks` | GET | 所有任务 |
| `/api/v2/tasks/{id}` | GET | 任务详情 |
| `/api/v2/tasks/{id}/logs` | GET | 任务日志 |
| `/api/v2/tasks/{id}/cancel` | POST | 取消任务 |
| `/api/v2/tasks/{id}` | DELETE | 删除任务 |

#### 资源管理
| 端点 | 方法 | 功能 |
|------|------|------|
| `/api/v2/resources` | GET | 资源状态 |
| `/api/v2/resources/gpu` | GET | GPU信息 |
| `/api/v2/resources/config` | POST | 更新配置 |

#### 系统状态
| 端点 | 方法 | 功能 |
|------|------|------|
| `/api/v1/health` | GET | 健康检查 |
| `/api/v1/info` | GET | 系统信息 |

### 详细API参数说明

#### 1. 启动训练 `POST /api/v2/training/start`

**请求参数 (TrainingRequest)**

| 参数 | 类型 | 必需 | 默认值 | 说明 |
|------|------|------|--------|------|
| `model` | string | ✅ | - | 模型名称 (resnet18/resnet50/vit_b_16等) |
| `num_classes` | integer | ✅ | - | 分类类别数 |
| `train_path` | string | ✅ | - | 训练集路径 |
| `val_path` | string | ✅ | - | 验证集路径 |
| `save_path` | string | ✅ | - | 模型保存路径 |
| `batch_size` | integer | ❌ | 8 | 批次大小 (≥1) |
| `num_epochs` | integer | ❌ | 100 | 训练轮数 (≥1) |
| `learning_rate` | float | ❌ | 0.0001 | 学习率 (>0) |
| `image_size` | integer | ❌ | 224 | 图像尺寸 (≥32) |
| `device` | string | ❌ | "cuda" | 设备 (cpu/cuda/cuda:0/cuda:1/...) |
| `weight_path` | string | ❌ | "" | 预训练权重路径 |
| `pretrained` | boolean | ❌ | true | 是否使用预训练 |
| `shuffle` | boolean | ❌ | true | 是否打乱数据 |
| `task_id` | string | ❌ | null | 自定义任务ID |
| `priority` | integer | ❌ | 5 | 优先级 (1-10) |
| `description` | string | ❌ | null | 任务描述 |

**响应字段 (TaskResponse)**

| 字段 | 类型 | 说明 |
|------|------|------|
| `task_id` | string | 任务唯一ID |
| `task_type` | string | 任务类型 (training) |
| `status` | string | 任务状态 (pending/running/completed/failed/cancelled) |
| `message` | string | 状态消息 |
| `progress` | integer | 进度百分比 (0-100) |
| `device` | string | 实际使用的设备 |
| `priority` | integer | 优先级 |
| `current_epoch` | integer | 当前训练轮次 ⭐新 |
| `total_epochs` | integer | 总训练轮次 ⭐新 |
| `latest_metrics` | object | 最新训练指标（详见下表）⭐新 |
| `created_at` | string | 创建时间 (ISO 8601格式) |
| `updated_at` | string | 更新时间 (ISO 8601格式) |

**latest_metrics 字段说明（15+种训练指标）** ⭐新

| 字段 | 类型 | 说明 |
|------|------|------|
| `epoch` | integer | 当前epoch |
| `total_epochs` | integer | 总epoch数 |
| `train_loss` | float | 训练损失 |
| `train_acc` | float | 训练准确率(%) |
| `val_loss` | float | 验证损失 |
| `val_acc` | float | 验证准确率(%) |
| `macro_f1` | float | Macro F1分数 |
| `micro_f1` | float | Micro F1分数 |
| `mAP` | float | 平均精度 |
| `top1_acc` | float | Top-1准确率 |
| `top3_acc` | float | Top-3准确率 |
| `top5_acc` | float | Top-5准确率 |
| `precision` | float | 精确度 |
| `recall` | float | 召回率 |
| `learning_rate` | float | 当前学习率 |
| `best_acc` | float | 最佳准确率(%) |

**示例**
```bash
curl -X POST "http://localhost:8000/api/v2/training/start" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "resnet18",
    "num_classes": 37,
    "train_path": "data/train",
    "val_path": "data/val",
    "save_path": "models/output",
    "device": "cuda:0",
    "batch_size": 16,
    "num_epochs": 50
  }'
```

响应：
```json
{
  "task_id": "550e8400-e29b-41d4-a716-446655440000",
  "task_type": "training",
  "status": "running",
  "message": "训练中...",
  "progress": 30,
  "device": "cuda:0",
  "priority": 5,
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
  "created_at": "2024-01-01T00:00:00",
  "updated_at": "2024-01-01T00:03:00"
}
```

---

#### 2. 启动推理 `POST /api/v2/inference/start`

**请求参数 (InferenceRequest)**

| 参数 | 类型 | 必需 | 默认值 | 说明 |
|------|------|------|--------|------|
| `cfg_path` | string | ✅ | - | 配置文件路径 (.yaml) |
| `weight_path` | string | ✅ | - | 模型权重路径 (.pth) |
| `source_path` | string | ✅ | - | 推理数据路径 |
| `save_path` | string | ❌ | null | 结果保存路径 |
| `device` | string | ❌ | "cuda" | 推理设备 (cpu/cuda/cuda:0/cuda:1/...) |
| `task_id` | string | ❌ | null | 自定义任务ID |
| `priority` | integer | ❌ | 3 | 优先级 (1-10) |

**响应字段 (TaskResponse)**

同训练接口，`task_type` 为 "inference"

**示例**
```bash
curl -X POST "http://localhost:8000/api/v2/inference/start" \
  -H "Content-Type: application/json" \
  -d '{
    "cfg_path": "configs/model.yaml",
    "weight_path": "models/best.pth",
    "source_path": "data/test",
    "device": "cuda:1"
  }'
```

---

#### 3. 批量推理 `POST /api/v2/inference/batch`

**请求参数 (BatchInferenceRequest)**

| 参数 | 类型 | 必需 | 默认值 | 说明 |
|------|------|------|--------|------|
| `cfg_path` | string | ✅ | - | 配置文件路径 |
| `weight_path` | string | ✅ | - | 模型权重路径 |
| `source_paths` | array[string] | ✅ | - | 数据路径列表 |
| `save_base_path` | string | ❌ | null | 结果保存基础路径 |
| `device` | string | ❌ | "cuda" | 推理设备 |
| `priority` | integer | ❌ | 3 | 优先级 |

**响应字段 (BatchInferenceResponse)**

| 字段 | 类型 | 说明 |
|------|------|------|
| `status` | string | 状态 (success) |
| `message` | string | 消息 |
| `task_ids` | array[string] | 所有任务ID列表 |
| `total` | integer | 任务总数 |

**示例**
```bash
curl -X POST "http://localhost:8000/api/v2/inference/batch" \
  -H "Content-Type: application/json" \
  -d '{
    "cfg_path": "configs/model.yaml",
    "weight_path": "models/best.pth",
    "source_paths": ["data/test1", "data/test2", "data/test3"],
    "device": "cuda"
  }'
```

响应：
```json
{
  "status": "success",
  "message": "已启动 3 个推理任务",
  "task_ids": ["task-1", "task-2", "task-3"],
  "total": 3
}
```

---

#### 4. 查询任务状态 `GET /api/v2/tasks/{task_id}`

**路径参数**

| 参数 | 类型 | 必需 | 说明 |
|------|------|------|------|
| `task_id` | string | ✅ | 任务ID |

**响应字段 (TaskResponse)**

同启动训练接口的响应

**示例**
```bash
curl http://localhost:8000/api/v2/tasks/550e8400-e29b-41d4-a716-446655440000
```

---

#### 5. 获取所有任务 `GET /api/v2/tasks`

**查询参数**

无

**响应字段 (TaskListResponse)**

| 字段 | 类型 | 说明 |
|------|------|------|
| `training_tasks` | array[TaskResponse] | 训练任务列表 |
| `inference_tasks` | array[TaskResponse] | 推理任务列表 |
| `total_training` | integer | 训练任务总数 |
| `total_inference` | integer | 推理任务总数 |

**示例**
```bash
curl http://localhost:8000/api/v2/tasks
```

响应：
```json
{
  "training_tasks": [...],
  "inference_tasks": [...],
  "total_training": 5,
  "total_inference": 10
}
```

---

#### 6. 停止训练 `POST /api/v2/training/{task_id}/stop`

**路径参数**

| 参数 | 类型 | 必需 | 说明 |
|------|------|------|------|
| `task_id` | string | ✅ | 任务ID |

**响应字段 (TaskActionResponse)**

| 字段 | 类型 | 说明 |
|------|------|------|
| `status` | string | 状态 (success/error) |
| `message` | string | 操作结果消息 |
| `task_id` | string | 任务ID |

**示例**
```bash
curl -X POST http://localhost:8000/api/v2/training/task-123/stop
```

响应：
```json
{
  "status": "success",
  "message": "训练任务已停止",
  "task_id": "task-123"
}
```

---

#### 7. 取消任务 `POST /api/v2/tasks/{task_id}/cancel`

**路径参数**

| 参数 | 类型 | 必需 | 说明 |
|------|------|------|------|
| `task_id` | string | ✅ | 任务ID |

**响应字段 (TaskActionResponse)**

同停止训练接口

**示例**
```bash
curl -X POST http://localhost:8000/api/v2/tasks/task-123/cancel
```

---

#### 8. 删除任务 `DELETE /api/v2/tasks/{task_id}`

**路径参数**

| 参数 | 类型 | 必需 | 说明 |
|------|------|------|------|
| `task_id` | string | ✅ | 任务ID |

**响应字段 (TaskActionResponse)**

同停止训练接口

**示例**
```bash
curl -X DELETE http://localhost:8000/api/v2/tasks/task-123
```

---

#### 9. 获取任务日志 `GET /api/v2/tasks/{task_id}/logs`

**路径参数**

| 参数 | 类型 | 必需 | 说明 |
|------|------|------|------|
| `task_id` | string | ✅ | 任务ID |

**响应**

返回JSON数组，每个元素包含：

| 字段 | 类型 | 说明 |
|------|------|------|
| `timestamp` | string | 时间戳 |
| `level` | string | 日志级别 (INFO/WARNING/ERROR) |
| `message` | string | 日志消息 |

**示例**
```bash
curl http://localhost:8000/api/v2/tasks/task-123/logs
```

响应：
```json
[
  {
    "timestamp": "2024-01-01T00:00:00",
    "level": "INFO",
    "message": "训练开始"
  },
  {
    "timestamp": "2024-01-01T00:01:00",
    "level": "INFO",
    "message": "Epoch 1/50, Loss: 2.345"
  }
]
```

---

#### 10. 获取训练实时日志流（含详细指标）`GET /api/v2/training/{task_id}/logs` ⭐新

**路径参数**

| 参数 | 类型 | 必需 | 说明 |
|------|------|------|------|
| `task_id` | string | ✅ | 任务ID |

**响应**

Server-Sent Events (SSE) 流，每条消息包含：

| 字段 | 类型 | 说明 |
|------|------|------|
| `timestamp` | string | 时间戳 |
| `level` | string | 日志级别 |
| `message` | string | 日志消息 |
| `metrics` | object | 训练指标（如果有）⭐ |
| `step` | integer | 训练步数（如果有）⭐ |
| `stage` | string | 训练阶段（epoch_start/training/validation/epoch_end/completed）⭐ |

**日志示例（基础日志）**：
```json
data: {"timestamp": "2024-01-01T00:00:00", "level": "INFO", "message": "训练开始..."}
```

**日志示例（含训练指标）** ⭐新：
```json
data: {
  "timestamp": "2024-01-01T00:01:00",
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

**日志示例（含验证指标）** ⭐新：
```json
data: {
  "timestamp": "2024-01-01T00:02:00",
  "level": "INFO",
  "message": "Validation Loss: 0.6123, Validation Accuracy: 78.92%",
  "metrics": {
    "epoch": 3,
    "val_loss": 0.6123,
    "val_acc": 78.92,
    "macro_f1": 0.7654,
    "mAP": 0.8123,
    "top1_acc": 78.92
  },
  "stage": "validation"
}
```

**示例 (Python) - 基础用法**
```python
import requests
import json

url = f"http://localhost:8000/api/v2/training/task-123/logs"
response = requests.get(url, stream=True)

for line in response.iter_lines():
    if line:
        line_str = line.decode('utf-8')
        if line_str.startswith('data: '):
            log_entry = json.loads(line_str[6:])
            print(f"[{log_entry['level']}] {log_entry['message']}")
```

**示例 (Python) - 含指标处理** ⭐新
```python
import requests
import json

url = f"http://localhost:8000/api/v2/training/task-123/logs"
response = requests.get(url, stream=True)

for line in response.iter_lines():
    if line:
        line_str = line.decode('utf-8')
        if line_str.startswith('data: '):
            log_entry = json.loads(line_str[6:])
            
            # 显示基本日志
            print(f"[{log_entry['level']}] {log_entry['message']}")
            
            # 如果有训练指标，详细显示
            if log_entry.get('metrics'):
                metrics = log_entry['metrics']
                stage = log_entry.get('stage', '')
                print(f"  └─ 阶段: {stage}")
                
                if metrics.get('train_acc'):
                    print(f"  └─ 训练准确率: {metrics['train_acc']}%")
                if metrics.get('val_acc'):
                    print(f"  └─ 验证准确率: {metrics['val_acc']}%")
                if metrics.get('macro_f1'):
                    print(f"  └─ Macro F1: {metrics['macro_f1']}")
```

---

#### 11. 获取资源状态 `GET /api/v2/resources`

**查询参数**

无

**响应字段 (ResourceStatusResponse)**

| 字段 | 类型 | 说明 |
|------|------|------|
| `device_usage` | object | 各设备当前使用情况 {设备名: {training: 数量, inference: 数量}} |
| `active_tasks` | object | 各设备活跃任务列表 {设备名: [任务列表]} |
| `limits` | object | 各设备并发限制 {设备名: {training: 最大值, inference: 最大值}} |
| `gpu_info` | object | GPU详细信息 |

**示例**
```bash
curl http://localhost:8000/api/v2/resources
```

响应：
```json
{
  "device_usage": {
    "cuda:0": {"training": 1, "inference": 2},
    "cuda:1": {"training": 0, "inference": 3}
  },
  "active_tasks": {
    "cuda:0": [
      {"id": "task-1", "type": "training"},
      {"id": "task-2", "type": "inference"}
    ]
  },
  "limits": {
    "cuda:0": {"training": 1, "inference": 3}
  },
  "gpu_info": {...}
}
```

---

#### 12. 获取GPU信息 `GET /api/v2/resources/gpu`

**查询参数**

无

**响应字段**

| 字段 | 类型 | 说明 |
|------|------|------|
| `available` | boolean | GPU是否可用 |
| `count` | integer | GPU数量 |
| `cuda_version` | string | CUDA版本 |
| `pytorch_version` | string | PyTorch版本 |
| `devices` | array[object] | GPU设备列表 |

**devices 数组中每个元素**

| 字段 | 类型 | 说明 |
|------|------|------|
| `id` | integer | GPU ID |
| `device_name` | string | 设备名称 (cuda:0/cuda:1) |
| `name` | string | GPU型号名称 |
| `compute_capability` | string | 计算能力 |
| `total_memory_gb` | float | 总显存 (GB) |
| `allocated_memory_gb` | float | 已分配显存 (GB) |
| `cached_memory_gb` | float | 缓存显存 (GB) |
| `free_memory_gb` | float | 空闲显存 (GB) |
| `utilization` | float | 利用率 (%) |
| `current_tasks` | object | 当前任务数 {training: 数量, inference: 数量} |

**示例**
```bash
curl http://localhost:8000/api/v2/resources/gpu
```

响应：
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

#### 13. 更新资源配置 `POST /api/v2/resources/config`

**请求参数 (ResourceConfigUpdate)**

| 参数 | 类型 | 必需 | 说明 |
|------|------|------|------|
| `max_concurrent` | object | ❌ | 并发限制配置 {设备名: {training: 数量, inference: 数量}} |

**响应字段 (ConfigUpdateResponse)**

| 字段 | 类型 | 说明 |
|------|------|------|
| `status` | string | 状态 (success) |
| `message` | string | 消息 |
| `current_config` | object | 更新后的配置 |

**示例**
```bash
curl -X POST "http://localhost:8000/api/v2/resources/config" \
  -H "Content-Type: application/json" \
  -d '{
    "max_concurrent": {
      "cuda:0": {"training": 2, "inference": 5}
    }
  }'
```

响应：
```json
{
  "status": "success",
  "message": "资源配置已更新",
  "current_config": {
    "cuda:0": {"training": 2, "inference": 5},
    "cuda:1": {"training": 1, "inference": 3}
  }
}
```

---

#### 14. 健康检查 `GET /api/v1/health`

**查询参数**

无

**响应字段 (HealthResponse)**

| 字段 | 类型 | 说明 |
|------|------|------|
| `status` | string | 服务状态 (healthy/unhealthy) |
| `timestamp` | string | 检查时间 |
| `version` | string | 服务版本 |
| `training_tasks` | integer | 训练任务数 |
| `inference_tasks` | integer | 推理任务数 |
| `active_log_streams` | integer | 活跃日志流数 |
| `resource_status` | object | 资源状态摘要 |

**示例**
```bash
curl http://localhost:8000/api/v1/health
```

响应：
```json
{
  "status": "healthy",
  "timestamp": "2024-01-01T00:00:00",
  "version": "2.3.1",
  "training_tasks": 2,
  "inference_tasks": 5,
  "active_log_streams": 3,
  "resource_status": {
    "gpu_available": true,
    "gpu_count": 2
  }
}
```

---

#### 15. 系统信息 `GET /api/v1/info`

**查询参数**

无

**响应字段 (InfoResponse)**

| 字段 | 类型 | 说明 |
|------|------|------|
| `app_name` | string | 应用名称 |
| `version` | string | 版本号 |
| `environment` | string | 运行环境 (development/production) |
| `supported_models` | array[string] | 支持的模型列表 |
| `resource_limits` | object | 资源限制配置 |
| `gpu_available` | boolean | GPU是否可用 |

**示例**
```bash
curl http://localhost:8000/api/v1/info
```

响应：
```json
{
  "app_name": "RFUAV Model Service",
  "version": "2.3.1",
  "environment": "production",
  "supported_models": [
    "resnet18", "resnet50", "vit_b_16", "swin_v2_t"
  ],
  "resource_limits": {
    "max_training_concurrent_gpu": 1,
    "max_inference_concurrent_gpu": 3
  },
  "gpu_available": true
}
```

---

## JSON格式规范

### 请求格式

所有请求必须：
- Content-Type: `application/json`
- 请求体为有效的JSON
- 字符串使用双引号

### 响应格式

所有响应保证：
- Content-Type: `application/json`
- 响应体符合Pydantic模型定义
- 类型安全，自动验证

### 响应模型

#### TaskResponse - 任务响应
```json
{
  "task_id": "xxx",
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

#### TaskActionResponse - 操作响应
```json
{
  "status": "success",
  "message": "任务已停止",
  "task_id": "xxx"
}
```

#### ResourceStatusResponse - 资源状态
```json
{
  "device_usage": {"cuda:0": {"training": 1, "inference": 2}},
  "active_tasks": {...},
  "limits": {...},
  "gpu_info": {...}
}
```

---

## Web测试界面

### 功能特点

打开 `test_web_ui.html` 可以：
- ✅ 查看GPU硬件信息
- ✅ 监控资源使用状态
- ✅ 启动训练任务
- ✅ 启动推理任务
- ✅ 查看任务列表
- ✅ 实时日志流

### 使用方法

1. **启动服务**
```bash
python app_refactored.py
```

2. **打开界面**
双击 `test_web_ui.html` 或在浏览器打开

3. **测试功能**
- 点击"刷新GPU信息"查看硬件
- 选择设备（cuda/cuda:0/cuda:1/cpu）
- 填写训练参数
- 点击"启动训练"
- 查看实时日志

### 界面截图说明

```
┌─────────────────────────────────────────┐
│  RFUAV Model Service - 测试面板          │
│  ✅ 服务连接正常                         │
└─────────────────────────────────────────┘

┌──────────────────┬──────────────────────┐
│  GPU硬件信息     │  资源使用状态         │
│  [刷新按钮]      │  [刷新按钮]           │
└──────────────────┴──────────────────────┘

┌──────────────────┬──────────────────────┐
│  启动训练任务    │  启动推理任务         │
│  - 设备选择 ⭐   │  - 设备选择 ⭐        │
└──────────────────┴──────────────────────┘

┌──────────────────┬──────────────────────┐
│  任务列表        │  实时日志             │
└──────────────────┴──────────────────────┘
```

---

## 配置说明

### 环境变量

创建 `.env` 文件：
```bash
# 应用配置
APP_NAME="RFUAV Model Service"
VERSION="2.3.1"
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

# 任务配置
DEFAULT_TRAIN_PRIORITY=5
DEFAULT_INFERENCE_PRIORITY=3
```

### 运行时更新

```bash
curl -X POST "http://localhost:8000/api/v2/resources/config" \
  -H "Content-Type: application/json" \
  -d '{
    "max_concurrent": {
      "cuda:0": {"training": 2, "inference": 5}
    }
  }'
```

---

## 使用示例

### Python完整示例

```python
from test_refactored_api import RFUAVClient
import time

# 创建客户端
client = RFUAVClient("http://localhost:8000")

# 1. 查看GPU信息
gpu_info = client.get_gpu_info()
print(f"GPU Count: {gpu_info['count']}")

# 2. 启动训练（自动选择GPU）
train_result = client.start_training(
    model="resnet18",
    num_classes=37,
    train_path="data/train",
    val_path="data/val",
    save_path="models/output",
    device="cuda",  # 自动选择
    batch_size=16,
    num_epochs=50
)
train_task_id = train_result['task_id']
print(f"Training started: {train_task_id}")
print(f"Using device: {train_result['device']}")

# 3. 启动推理（指定GPU 1）
infer_result = client.start_inference(
    cfg_path="configs/model.yaml",
    weight_path="models/best.pth",
    source_path="data/test",
    device="cuda:1"  # 指定GPU 1
)
infer_task_id = infer_result['task_id']
print(f"Inference started: {infer_task_id}")

# 4. 监控任务
while True:
    status = client.get_task(train_task_id)
    print(f"Status: {status['status']}, Progress: {status['progress']}%")
    
    if status['status'] in ['completed', 'failed', 'cancelled']:
        break
    
    time.sleep(5)

# 5. 查看资源
resources = client.get_resources()
print(f"Resource usage: {resources['device_usage']}")

# 6. 获取所有任务
tasks = client.get_all_tasks()
print(f"Total tasks: Training={tasks['total_training']}, Inference={tasks['total_inference']}")
```

### cURL示例

```bash
# 1. 健康检查
curl http://localhost:8000/api/v1/health

# 2. 查看GPU
curl http://localhost:8000/api/v2/resources/gpu

# 3. 启动训练
curl -X POST http://localhost:8000/api/v2/training/start \
  -H "Content-Type: application/json" \
  -d '{"model":"resnet18","device":"cuda:0",...}'

# 4. 查询状态
curl http://localhost:8000/api/v2/tasks/{task_id}

# 5. 停止任务
curl -X POST http://localhost:8000/api/v2/training/{task_id}/stop
```

---

## 并发安全保证

### 架构设计

系统采用**完全非阻塞的异步架构**，确保高并发场景下不会出现阻塞：

```
客户端请求 → FastAPI (async) → 后台任务 (非阻塞) → 工作线程池
                                            ↓
                                      资源管理器 (线程安全)
```

### 关键特性

#### 1. API层完全异步 ✅
- 所有接口使用 `async/await`
- 请求立即返回（< 50ms）
- 不会相互阻塞

#### 2. 后台任务执行 ✅
```python
@router.post("/start")
async def start_training(request, background_tasks):
    # 创建任务记录
    task_id = await service.start_training(request, background_tasks)
    return {"task_id": task_id}  # 立即返回，不等待训练完成
```

#### 3. 资源管理线程安全 ✅
```python
class ResourceManager:
    def __init__(self):
        self.lock = threading.Lock()
    
    def allocate(self, device, task_type, task_id):
        with self.lock:  # 保护共享资源
            # 线程安全的资源分配
```

#### 4. 智能任务调度 ✅
- 任务自动排队
- 优先级管理
- GPU负载均衡

### 并发能力

| 操作类型 | 并发量 | 响应时间 | 说明 |
|---------|--------|---------|------|
| 创建任务 | 500+/秒 | < 50ms | 立即返回任务ID |
| 查询状态 | 1000+/秒 | < 20ms | 内存读取 |
| 获取日志 | 100/秒 | < 100ms | 日志队列 |
| SSE连接 | 100并发 | - | 实时日志流 |

### 并发测试

运行并发性能测试：
```bash
# 安装依赖
pip install aiohttp

# 运行测试
python test_concurrency.py
```

**测试内容**：
- ✅ 并发创建20个任务
- ✅ 并发查询100次
- ✅ 混合工作负载
- ✅ 资源状态监控

**预期结果**：
```
测试1: 并发创建 20 个训练任务
✅ 成功: 20/20
⏱️  总耗时: 0.85秒
⏱️  平均响应: 42.50ms
📊 QPS: 23.53 请求/秒

测试2: 并发查询任务状态 100 次
✅ 成功: 100/100
⏱️  总耗时: 0.32秒
⏱️  平均响应: 3.20ms
📊 QPS: 312.50 请求/秒
```

### 生产部署配置

#### 推荐配置
```bash
# Uvicorn多进程部署
uvicorn app_refactored:app \
    --host 0.0.0.0 \
    --port 8000 \
    --workers 4 \              # 4个工作进程
    --limit-concurrency 1000 \ # 最大并发连接
    --backlog 2048 \           # 请求队列大小
    --timeout-keep-alive 30    # 保持连接30秒
```

#### GPU并发限制
```bash
# .env 配置
MAX_TRAINING_CONCURRENT_GPU=1   # 每个GPU最多1个训练任务
MAX_INFERENCE_CONCURRENT_GPU=3  # 每个GPU最多3个推理任务
```

### 性能监控

查看实时资源状态：
```bash
# 查看GPU使用
curl http://localhost:8000/api/v2/resources/gpu

# 查看任务队列
curl http://localhost:8000/api/v2/resources

# 健康检查
curl http://localhost:8000/api/v1/health
```

### 负载能力评估

**单机配置**（2×RTX 3090）：
- API请求: 1000+ QPS
- 同时运行任务: 8个（2 GPU × 4任务）
- 排队任务: 数百个
- 响应延迟: < 50ms

**扩展方案**（多机部署）：
- 使用Nginx负载均衡
- Redis共享任务队列
- 水平扩展至多台服务器
- 3台服务器可达 3000+ QPS

### 安全保证

| 保护机制 | 实现方式 | 作用 |
|---------|---------|------|
| **并发限制** | ResourceManager | 防止资源过载 |
| **任务排队** | 轮询等待 | 避免GPU显存溢出 |
| **线程安全** | threading.Lock | 防止数据竞争 |
| **异常隔离** | try-catch | 单个任务失败不影响其他任务 |
| **资源释放** | finally块 | 确保资源正确释放 |

### 详细分析

完整的并发安全性分析和性能测试，请参考：
- **[并发安全性分析报告](CONCURRENCY_ANALYSIS.md)** - 详细的架构分析
- **[并发测试脚本](test_concurrency.py)** - 实际性能测试

---

## 故障排查

### 常见问题

#### Q1: 服务无法启动
**A**: 
1. 检查端口是否被占用
2. 检查Python版本 (需要3.8+)
3. 检查依赖是否完整安装

```bash
# 检查端口
netstat -ano | findstr :8000

# 检查依赖
pip list | grep fastapi
```

#### Q2: GPU不可用
**A**:
1. 检查CUDA是否安装
2. 检查PyTorch是否支持CUDA
3. 使用CPU进行测试

```bash
python -c "import torch; print(torch.cuda.is_available())"
```

#### Q3: 任务一直排队
**A**:
1. 查看资源状态
2. 检查是否有任务占用GPU
3. 调整并发限制

```bash
curl http://localhost:8000/api/v2/resources
```

#### Q4: 显存不足
**A**:
1. 降低batch_size
2. 使用显存更大的GPU
3. 减少并发任务数

```python
device = "cuda:0"  # 使用24GB的GPU
batch_size = 8     # 从16降到8
```

### 日志查看

```bash
# 查看服务日志
tail -f logs/app.log

# 查看任务日志
curl http://localhost:8000/api/v2/tasks/{task_id}/logs
```

