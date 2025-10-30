# RFUAV Model Service

Integrate the RFUAV training and evaluation framework into a server. For the specific implementation of RFUAV, please refer to https://github.com/kitoweeknd/RFUAV

## 🚀 快速开始

```bash
# 安装依赖
pip install -r requirements.txt

# 启动服务（推荐使用重构版）
python app_refactored.py

# 访问API文档
http://localhost:8000/docs
```

## ✨ 核心特性

- ✅ **参数化训练** - 无需配置文件，API直接指定所有训练参数
- ✅ **详细训练指标** - 实时返回loss、accuracy、F1、mAP等15+种指标
- ✅ **数据预处理** - 数据集分割、数据增强、图像裁剪一键完成 ⭐新
- ✅ **实时日志流** - Server-Sent Events实时流式传输训练日志和指标
- ✅ **灵活推理** - 支持单次推理和批量推理
- ✅ **智能GPU调度** - 自动选择最优GPU或手动指定设备
- ✅ **多GPU支持** - 支持cuda:0、cuda:1等多GPU选择
- ✅ **并发优化** - 智能资源管理和任务队列调度
- ✅ **任务管理** - 完整的任务生命周期管理
- ✅ **Web测试界面** - 开箱即用的可视化测试工具

## 📖 详细文档

- [完整使用文档](doc/README_COMPLETE.md) - 详细的功能说明和使用指南
- [API参数参考](doc/API_PARAMETERS_REFERENCE.md) - 完整的API参数说明
- [训练指标指南](doc/TRAINING_METRICS_GUIDE.md) - 详细训练指标功能说明
- [数据预处理指南](doc/PREPROCESSING_GUIDE.md) - 数据预处理功能使用指南 ⭐新
- [APP版本说明](doc/APP_VERSIONS_GUIDE.md) - 不同版本的功能对比

## 🎯 训练指标功能（新）

训练接口现已支持实时返回详细的训练指标：

### 支持的指标（15+种）
- **基础指标**: epoch, train_loss, train_acc, val_loss, val_acc
- **F1分数**: macro_f1, micro_f1
- **mAP**: mAP
- **Top-k准确率**: top1_acc, top3_acc, top5_acc
- **其他**: precision, recall, learning_rate, best_acc

### 快速示例

```python
import requests

# 启动训练
response = requests.post("http://localhost:8000/api/v2/training/start", json={
    "model": "resnet18",
    "num_classes": 37,
    "train_path": "data/train",
    "val_path": "data/val",
    "save_path": "checkpoints",
    "num_epochs": 10,
    "device": "cuda:0"
})
task_id = response.json()["task_id"]

# 查询状态（含详细指标）
status = requests.get(f"http://localhost:8000/api/v2/training/{task_id}").json()
print(f"当前Epoch: {status['current_epoch']}/{status['total_epochs']}")
print(f"训练准确率: {status['latest_metrics']['train_acc']}%")
print(f"验证准确率: {status['latest_metrics']['val_acc']}%")
```

详细使用说明请查看：[训练指标使用指南](doc/TRAINING_METRICS_GUIDE.md)

## 🔧 数据预处理功能（新）

提供完整的数据集准备工作流：

### 支持的功能
- **数据集分割** - 按比例分割为train/val/test
- **数据增强** - 6种增强方法（CLAHE, ColorJitter, GaussNoise等）
- **图像裁剪** - 批量裁剪指定区域

### 快速示例

```python
import requests

# 1. 数据集分割
response = requests.post("http://localhost:8000/api/v2/preprocessing/split", json={
    "input_path": "data/raw_dataset",
    "output_path": "data/split_dataset",
    "train_ratio": 0.7,
    "val_ratio": 0.2
})

# 2. 数据增强
response = requests.post("http://localhost:8000/api/v2/preprocessing/augment", json={
    "dataset_path": "data/split_dataset",
    "methods": ["CLAHE", "ColorJitter", "GaussNoise"]
})

# 3. 图像裁剪
response = requests.post("http://localhost:8000/api/v2/preprocessing/crop", json={
    "input_path": "data/images",
    "output_path": "data/cropped",
    "x": 100, "y": 100, "width": 500, "height": 500
})
```

详细使用说明请查看：[数据预处理使用指南](doc/PREPROCESSING_GUIDE.md)

## 🧪 测试工具

```bash
# Python测试客户端
python test_refactored_api.py

# 训练指标测试
python test_training_metrics.py

# 数据预处理测试
python test_preprocessing_api.py

# Web测试界面
# 双击打开 test_web_ui.html
```

## 📊 版本信息

当前推荐版本：**V2.4.0** (`app_refactored.py`)

- V2.4.0: 重构版 + GPU选择 + Web界面 + 详细训练指标 + **数据预处理** ⭐
- V2.3.1: 重构版 + GPU选择 + Web界面 + 详细训练指标
- V2.2.0: 并发优化版
- V2.0.0: 增强版（参数化训练）

版本详细说明：[APP_VERSIONS_GUIDE.md](doc/APP_VERSIONS_GUIDE.md)

## 💡 技术支持

- 问题反馈：GitHub Issues
- 详细文档：见 `doc/` 目录
- API文档：http://localhost:8000/docs （启动服务后访问）