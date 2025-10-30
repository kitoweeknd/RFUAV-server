# 更新日志

## [2.1.0] - 2024-10-29

### 新增功能 ✨
- **设备选择支持**: 所有API接口现在都支持通过请求体指定运行设备
  - 训练接口 (`/api/v2/train`): 添加 `device` 参数
  - 推理接口 (`/api/v1/inference`): 添加 `device` 参数
  - 基准测试接口 (`/api/v1/benchmark`): 添加 `device` 参数
- 推理和基准测试会动态覆盖配置文件中的设备设置
- 支持 `cuda` 和 `cpu` 两种设备类型

### 改进 🔧
- 推理接口响应中增加使用的设备信息
- 基准测试接口响应中增加使用的设备信息
- 使用临时配置文件机制，不修改原始配置文件

### 文档更新 📚
- 新增 `DEVICE_USAGE.md` - 详细的设备使用说明
- 更新 `API_ENHANCED_README.md` - 添加设备参数说明
- 更新 `START_ENHANCED.md` - 添加设备选择章节
- 新增 `device_selection_example.py` - 设备选择示例代码
- 新增 `CHANGELOG.md` - 更新日志

### 示例代码 📝
- 测试客户端 (`test_api_client.py`) 添加设备选择支持
- 新增多个设备使用示例

## [2.0.0] - 2024-10-29

### 重大更新 🚀
- **参数化训练配置**: 无需YAML配置文件，直接通过JSON指定所有参数
- **实时日志流**: 使用Server-Sent Events实时推送训练日志
- **完全解耦设计**: 模型、数据集、超参数完全独立配置

### 核心功能
- 新增 `/api/v2/train` - 参数化训练接口
- 新增 `/api/v2/train/{task_id}/logs` - 实时日志流接口
- 保留 `/api/v1/*` 接口，保持向后兼容

### 支持的模型
- ResNet系列: 18, 34, 50, 101, 152
- Vision Transformer: B/16, B/32, L/16, L/32
- Swin Transformer V2: Tiny, Small, Base
- MobileNet V3: Large, Small

### 工具和文档
- `app_enhanced.py` - 增强版FastAPI服务器
- `test_api_client.py` - Python测试客户端
- `web_monitor.html` - Web可视化监控界面
- 完整的API文档和使用示例

## API变更

### V2.1.0 新增参数

#### 训练接口
```json
{
  "device": "cuda"  // 新增：指定训练设备
}
```

#### 推理接口
```json
{
  "device": "cuda"  // 新增：指定推理设备
}
```

#### 基准测试接口
```json
{
  "device": "cuda"  // 新增：指定测试设备
}
```

### 响应格式变更

#### 推理接口响应
```json
{
  "status": "success",
  "message": "推理完成",
  "source_path": "example/test_data/",
  "save_path": "results/inference/",
  "device": "cuda"  // 新增：返回使用的设备
}
```

#### 基准测试接口响应
```json
{
  "status": "success",
  "message": "基准测试完成",
  "data_path": "data/benchmark/",
  "save_path": "results/benchmark/",
  "device": "cuda"  // 新增：返回使用的设备
}
```

## 使用示例

### 指定GPU训练
```python
config = {
    "model": "resnet18",
    "num_classes": 37,
    "train_path": "data/train",
    "val_path": "data/val",
    "device": "cuda",  # 使用GPU
    # ... 其他参数
}
```

### 指定CPU推理
```python
config = {
    "cfg_path": "configs/exp3.1_ResNet18.yaml",
    "weight_path": "models/best_model.pth",
    "source_path": "example/test_data/",
    "device": "cpu"  # 使用CPU
}
```

### 自动选择设备
```python
import torch
device = "cuda" if torch.cuda.is_available() else "cpu"

config = {
    # ... 其他参数
    "device": device
}
```

## 迁移指南

### 从V2.0升级到V2.1

1. **训练接口** - 无需修改，默认使用cuda
2. **推理接口** - 可选添加 `device` 参数
3. **基准测试接口** - 可选添加 `device` 参数

### 兼容性
- ✅ 完全向后兼容V2.0
- ✅ 保留V1.0接口
- ✅ 默认行为不变（默认使用cuda）

## 已知问题

无

## 未来计划

- [ ] 支持多GPU训练
- [ ] 添加混合精度训练支持
- [ ] 支持分布式训练
- [ ] 添加更多模型架构
- [ ] 性能监控和可视化

## 贡献者

感谢所有贡献者的支持！

