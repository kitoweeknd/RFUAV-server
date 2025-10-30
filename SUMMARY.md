# RFUAV模型服务 - 功能总结

## 📋 项目概述

RFUAV模型服务是一个基于FastAPI的完整机器学习服务平台，提供模型训练、推理和基准测试功能，支持实时日志流和灵活的设备选择。

## 🎯 核心特性

### 1. **参数化训练** ⭐
- ✅ 无需YAML配置文件
- ✅ 通过JSON直接指定所有参数
- ✅ 支持所有主流模型架构
- ✅ 灵活的超参数配置

### 2. **实时日志流** ⭐
- ✅ Server-Sent Events (SSE) 技术
- ✅ 实时推送训练日志
- ✅ 支持多客户端同时监听
- ✅ 自动任务完成检测

### 3. **设备选择** ⭐ NEW
- ✅ 训练时指定GPU/CPU
- ✅ 推理时指定GPU/CPU
- ✅ 基准测试时指定GPU/CPU
- ✅ 动态覆盖配置文件设置
- ✅ 自动设备检测

### 4. **完全解耦设计**
- ✅ 模型与数据集独立
- ✅ 超参数独立配置
- ✅ 设备选择独立
- ✅ 路径配置独立

### 5. **向后兼容**
- ✅ 保留V1配置文件接口
- ✅ V2参数化接口
- ✅ 平滑迁移路径

## 📁 文件结构

```
RFUAV-server/
├── app_enhanced.py              # 增强版FastAPI服务器 ⭐
├── test_api_client.py           # Python测试客户端
├── web_monitor.html             # Web可视化监控界面
├── device_selection_example.py  # 设备选择示例 ⭐ NEW
│
├── API_ENHANCED_README.md       # 完整API文档
├── START_ENHANCED.md            # 快速开始指南
├── DEVICE_USAGE.md              # 设备使用说明 ⭐ NEW
├── CHANGELOG.md                 # 更新日志 ⭐ NEW
├── SUMMARY.md                   # 本文件
│
├── train_examples.json          # 训练配置示例
├── requirements_enhanced.txt    # API依赖
│
├── configs/                     # 配置文件目录
├── utils/                       # 工具模块
│   ├── trainer.py              # 训练器
│   ├── benchmark.py            # 推理和基准测试
│   └── build.py                # 配置构建
└── ...
```

## 🚀 支持的模型

| 模型系列 | 模型名称 | 参数量 | 推荐用途 |
|---------|---------|--------|---------|
| **ResNet** | resnet18, resnet34, resnet50, resnet101, resnet152 | 11M-60M | 通用分类 |
| **ViT** | vit_b_16, vit_b_32, vit_l_16, vit_l_32 | 86M-304M | 大规模数据 |
| **Swin** | swin_v2_t, swin_v2_s, swin_v2_b | 28M-88M | 高精度任务 |
| **MobileNet** | mobilenet_v3_large, mobilenet_v3_small | 3M-5M | 轻量级部署 |

## 📡 API端点

### V2.1 接口（最新）

| 端点 | 方法 | 功能 | 新特性 |
|------|------|------|--------|
| `/api/v2/train` | POST | 参数化训练 | ✅ device参数 |
| `/api/v2/train/{id}/logs` | GET | 实时日志流 | - |
| `/api/v1/inference` | POST | 模型推理 | ✅ device参数 |
| `/api/v1/benchmark` | POST | 基准测试 | ✅ device参数 |
| `/api/v1/tasks/{id}` | GET | 任务状态 | - |
| `/api/v1/health` | GET | 健康检查 | - |

### V1接口（兼容）

| 端点 | 方法 | 功能 |
|------|------|------|
| `/api/v1/train` | POST | 配置文件训练 |

## 💡 使用场景

### 场景1：快速实验
```python
# 无需配置文件，直接指定参数
config = {
    "model": "resnet18",
    "num_classes": 37,
    "train_path": "data/train",
    "val_path": "data/val",
    "device": "cuda",
    # ... 其他参数
}
requests.post("/api/v2/train", json=config)
```

### 场景2：实时监控
```python
# 启动训练后立即获取实时日志
task_id = train_response.json()["task_id"]
response = requests.get(f"/api/v2/train/{task_id}/logs", stream=True)
for line in response.iter_lines():
    print(line)  # 实时显示训练日志
```

### 场景3：CPU环境
```python
# 在没有GPU的环境中训练
config = {
    # ... 其他参数
    "device": "cpu",
    "batch_size": 8  # CPU时减小batch size
}
```

### 场景4：自动设备选择
```python
# 自动检测并选择最佳设备
import torch
device = "cuda" if torch.cuda.is_available() else "cpu"
config = {"device": device, ...}
```

### 场景5：混合使用
```python
# GPU训练，CPU推理
train_config = {"device": "cuda", ...}  # GPU训练
infer_config = {"device": "cpu", ...}   # CPU推理
```

## 🔧 快速开始

### 1. 安装依赖
```bash
pip install -r requirements_enhanced.txt
```

### 2. 启动服务
```bash
python app_enhanced.py
```

### 3. 选择使用方式

#### 方式A：Web界面（最简单）
```bash
# 在浏览器中打开
open web_monitor.html
```

#### 方式B：Python客户端
```bash
python test_api_client.py
```

#### 方式C：设备选择示例
```bash
python device_selection_example.py
```

#### 方式D：直接调用API
```python
import requests

config = {
    "model": "resnet18",
    "num_classes": 37,
    "train_path": "data/train",
    "val_path": "data/val",
    "device": "cuda",
    # ... 其他参数
}

response = requests.post(
    "http://localhost:8000/api/v2/train",
    json=config
)
```

## 📊 性能对比

### GPU vs CPU

| 任务 | GPU | CPU | 加速比 |
|------|-----|-----|--------|
| ResNet18训练 | 100% | ~5% | ~20x |
| ResNet18推理 | 100% | ~20% | ~5x |
| MobileNet训练 | 100% | ~10% | ~10x |
| MobileNet推理 | 100% | ~30% | ~3x |

*实际性能取决于具体硬件配置*

## 🎓 学习路径

### 新手入门
1. 阅读 `START_ENHANCED.md`
2. 运行 `test_api_client.py`
3. 打开 `web_monitor.html` 体验

### 进阶使用
1. 阅读 `API_ENHANCED_README.md`
2. 学习 `train_examples.json` 中的配置
3. 尝试 `device_selection_example.py`

### 高级定制
1. 研究 `app_enhanced.py` 源码
2. 阅读 `DEVICE_USAGE.md` 了解设备管理
3. 根据需求修改和扩展

## 🔍 故障排除

### 问题1：无法连接服务
```bash
# 检查服务是否运行
curl http://localhost:8000/api/v1/health
```

### 问题2：CUDA不可用
```python
# 检查CUDA状态
import torch
print(torch.cuda.is_available())
```

### 问题3：显存不足
```python
# 减小batch_size
config = {
    "batch_size": 16,  # 从32降到16
    # ...
}
```

### 问题4：日志流中断
```python
# 重新连接即可
response = requests.get(f"/api/v2/train/{task_id}/logs", stream=True)
```

## 📚 文档索引

| 文档 | 内容 | 适合人群 |
|------|------|---------|
| `START_ENHANCED.md` | 快速开始 | 新手 |
| `API_ENHANCED_README.md` | 完整API文档 | 所有用户 |
| `DEVICE_USAGE.md` | 设备使用说明 | 进阶用户 |
| `CHANGELOG.md` | 更新日志 | 开发者 |
| `train_examples.json` | 配置示例 | 实践者 |

## 🎨 示例代码

### Python
- `test_api_client.py` - 完整客户端
- `device_selection_example.py` - 设备选择示例

### Web
- `web_monitor.html` - 可视化监控界面

### Shell
```bash
# cURL示例
curl -X POST "http://localhost:8000/api/v2/train" \
  -H "Content-Type: application/json" \
  -d '{"model": "resnet18", "device": "cuda", ...}'
```

## 🔄 版本历史

- **V2.1.0** (2024-10-29) - 添加设备选择支持
- **V2.0.0** (2024-10-29) - 参数化配置和实时日志流
- **V1.0.0** - 基础版本（配置文件）

## 🤝 贡献

欢迎提交Issue和Pull Request！

## 📞 支持

- 文档: 查看各个README文件
- 示例: 运行example文件
- API文档: http://localhost:8000/docs

## 🆕 V2.2 并发优化版

**新特性**:
- ✅ 训练和推理并发执行
- ✅ 智能资源管理
- ✅ 任务优先级队列
- ✅ GPU显存监控
- ✅ 动态资源配置

**适用场景**:
- 生产环境部署
- 训练时继续提供推理服务
- 批量推理任务
- 资源优化使用

**使用方式**:
```bash
python app_concurrent.py
python concurrent_example.py
```

详见: `CONCURRENT_USAGE.md` 和 `VERSION_COMPARISON.md`

## 🎯 版本选择

| 场景 | 推荐版本 | 启动文件 |
|------|---------|---------|
| 生产环境 | V2.2 并发优化 | `app_concurrent.py` |
| 开发测试 | V2.1 标准版 | `app_enhanced.py` |
| 学习入门 | V2.1 标准版 | `app_enhanced.py` |

## 🎯 下一步

1. ✅ 参数化训练配置
2. ✅ 实时日志流
3. ✅ 设备选择支持
4. ✅ 训练推理并发 ⭐ NEW
5. 🔜 多GPU训练
6. 🔜 混合精度训练
7. 🔜 分布式训练
8. 🔜 TensorBoard集成

---

**标准版**: `python app_enhanced.py` 🚀  
**并发版**: `python app_concurrent.py` ⚡
