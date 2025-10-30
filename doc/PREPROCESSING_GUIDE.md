# 数据预处理API使用指南

## 📑 目录

- [概述](#概述)
- [功能特性](#功能特性)
- [API接口](#api接口)
  - [数据集分割](#1-数据集分割)
  - [数据增强](#2-数据增强)
  - [图像裁剪](#3-图像裁剪)
- [使用示例](#使用示例)
- [常见问题](#常见问题)

---

## 概述

数据预处理API提供了完整的数据集准备功能，包括数据集分割、数据增强和图像裁剪。所有操作都以异步任务的形式执行，支持实时日志流和进度查询。

### 为什么需要数据预处理？

1. **数据集分割** - 将原始数据按比例分为训练集、验证集和测试集
2. **数据增强** - 通过各种变换增加数据多样性，提高模型泛化能力
3. **图像裁剪** - 提取图像中感兴趣的区域，减少无关信息干扰

---

## 功能特性

### ✅ 数据集分割
- 支持二分割（train/val）或三分割（train/val/test）
- 自定义分割比例
- 自动保持类别结构
- 随机打乱数据
- 完整的统计信息

### ✅ 数据增强
- 支持6种增强方法：
  - **AdvancedBlur** - 高级模糊
  - **CLAHE** - 对比度受限自适应直方图均衡化
  - **ColorJitter** - 颜色抖动
  - **GaussNoise** - 高斯噪声
  - **ISONoise** - ISO噪声
  - **Sharpen** - 锐化
- 可选择特定方法或使用全部方法
- 保留原图并生成增强版本
- 保持目录结构

### ✅ 图像裁剪
- 精确指定裁剪区域
- 支持单个文件或整个目录
- 递归处理保持目录结构
- 批量处理能力

### ✅ 异步任务管理
- 后台执行，不阻塞请求
- 实时进度查询
- Server-Sent Events日志流
- 完整的错误处理

---

## API接口

### 基础URL
```
http://localhost:8000/api/v2/preprocessing
```

---

### 1. 数据集分割

**端点**: `POST /api/v2/preprocessing/split`

#### 请求参数

| 参数 | 类型 | 必需 | 说明 |
|------|------|------|------|
| `input_path` | string | ✅ | 输入数据集路径 |
| `output_path` | string | ✅ | 输出路径 |
| `train_ratio` | float | ❌ | 训练集比例（默认0.8，范围0.1-0.9） |
| `val_ratio` | float | ❌ | 验证集比例（可选，用于三分割） |
| `task_id` | string | ❌ | 自定义任务ID |
| `description` | string | ❌ | 任务描述 |

#### 数据集结构

**输入结构**（按类别组织）:
```
input_path/
    ├── class1/
    │   ├── img1.jpg
    │   ├── img2.jpg
    │   └── img3.jpg
    ├── class2/
    │   ├── img1.jpg
    │   └── img2.jpg
    └── class3/
        └── img1.jpg
```

**输出结构**（二分割）:
```
output_path/
    ├── train/
    │   ├── class1/
    │   ├── class2/
    │   └── class3/
    └── valid/
        ├── class1/
        ├── class2/
        └── class3/
```

**输出结构**（三分割，指定val_ratio）:
```
output_path/
    ├── train/
    │   ├── class1/
    │   └── ...
    ├── valid/
    │   ├── class1/
    │   └── ...
    └── test/
        ├── class1/
        └── ...
```

#### 请求示例

```bash
curl -X POST "http://localhost:8000/api/v2/preprocessing/split" \
  -H "Content-Type: application/json" \
  -d '{
    "input_path": "data/raw_dataset",
    "output_path": "data/split_dataset",
    "train_ratio": 0.7,
    "val_ratio": 0.2
  }'
```

```python
import requests

response = requests.post(
    "http://localhost:8000/api/v2/preprocessing/split",
    json={
        "input_path": "data/raw_dataset",
        "output_path": "data/split_dataset",
        "train_ratio": 0.7,   # 70% 训练集
        "val_ratio": 0.2,     # 20% 验证集，剩余10%测试集
        "description": "分割RFUAV数据集"
    }
)
task = response.json()
print(f"任务ID: {task['task_id']}")
```

#### 响应示例

```json
{
  "task_id": "abc-123-def-456",
  "task_type": "dataset_split",
  "status": "pending",
  "progress": 0,
  "input_path": "data/raw_dataset",
  "output_path": "data/split_dataset",
  "created_at": "2025-10-29T10:00:00",
  "updated_at": "2025-10-29T10:00:00"
}
```

---

### 2. 数据增强

**端点**: `POST /api/v2/preprocessing/augment`

#### 请求参数

| 参数 | 类型 | 必需 | 说明 |
|------|------|------|------|
| `dataset_path` | string | ✅ | 数据集路径（应包含train和valid文件夹） |
| `output_path` | string | ❌ | 输出路径（默认为dataset_aug） |
| `methods` | array | ❌ | 增强方法列表（见下表） |
| `task_id` | string | ❌ | 自定义任务ID |
| `description` | string | ❌ | 任务描述 |

#### 支持的增强方法

| 方法名 | 说明 | 效果 |
|--------|------|------|
| `AdvancedBlur` | 高级模糊 | 模糊图像，模拟运动模糊或失焦 |
| `CLAHE` | 对比度受限自适应直方图均衡化 | 增强图像对比度 |
| `ColorJitter` | 颜色抖动 | 随机调整亮度、对比度、饱和度 |
| `GaussNoise` | 高斯噪声 | 添加高斯噪声 |
| `ISONoise` | ISO噪声 | 模拟相机ISO噪声 |
| `Sharpen` | 锐化 | 增强图像边缘 |

#### 数据集结构

**输入**:
```
dataset_path/
    ├── train/
    │   ├── class1/
    │   └── class2/
    └── valid/
        ├── class1/
        └── class2/
```

**输出**（每张原图会生成原图+多个增强版本）:
```
output_path/
    ├── train/
    │   ├── class1/
    │   │   ├── img1_origin.jpg
    │   │   ├── img1_AugM0.jpg  (AdvancedBlur)
    │   │   ├── img1_AugM1.jpg  (CLAHE)
    │   │   └── ...
    │   └── class2/
    └── valid/
```

#### 请求示例

```bash
# 使用默认的全部6种方法
curl -X POST "http://localhost:8000/api/v2/preprocessing/augment" \
  -H "Content-Type: application/json" \
  -d '{
    "dataset_path": "data/split_dataset"
  }'

# 指定特定方法
curl -X POST "http://localhost:8000/api/v2/preprocessing/augment" \
  -H "Content-Type: application/json" \
  -d '{
    "dataset_path": "data/split_dataset",
    "output_path": "data/augmented_dataset",
    "methods": ["CLAHE", "ColorJitter", "GaussNoise"]
  }'
```

```python
import requests

# 使用全部默认方法
response = requests.post(
    "http://localhost:8000/api/v2/preprocessing/augment",
    json={
        "dataset_path": "data/split_dataset",
        "output_path": "data/augmented_dataset"
    }
)

# 或者只使用特定方法
response = requests.post(
    "http://localhost:8000/api/v2/preprocessing/augment",
    json={
        "dataset_path": "data/split_dataset",
        "output_path": "data/augmented_dataset",
        "methods": ["CLAHE", "ColorJitter", "GaussNoise"]
    }
)

task = response.json()
print(f"任务ID: {task['task_id']}")
```

---

### 3. 图像裁剪

**端点**: `POST /api/v2/preprocessing/crop`

#### 请求参数

| 参数 | 类型 | 必需 | 说明 |
|------|------|------|------|
| `input_path` | string | ✅ | 输入路径（文件或目录） |
| `output_path` | string | ✅ | 输出路径 |
| `x` | integer | ✅ | 裁剪区域左上角X坐标 |
| `y` | integer | ✅ | 裁剪区域左上角Y坐标 |
| `width` | integer | ✅ | 裁剪宽度 |
| `height` | integer | ✅ | 裁剪高度 |
| `task_id` | string | ❌ | 自定义任务ID |
| `description` | string | ❌ | 任务描述 |

#### 裁剪说明

- 如果`input_path`是文件，则裁剪该文件并保存到`output_path`
- 如果`input_path`是目录，则递归处理所有图像并保持目录结构

#### 请求示例

```bash
# 裁剪单个文件
curl -X POST "http://localhost:8000/api/v2/preprocessing/crop" \
  -H "Content-Type: application/json" \
  -d '{
    "input_path": "data/test.jpg",
    "output_path": "data/cropped/test.jpg",
    "x": 100,
    "y": 100,
    "width": 500,
    "height": 500
  }'

# 批量裁剪目录
curl -X POST "http://localhost:8000/api/v2/preprocessing/crop" \
  -H "Content-Type: application/json" \
  -d '{
    "input_path": "data/images",
    "output_path": "data/cropped_images",
    "x": 100,
    "y": 100,
    "width": 500,
    "height": 500
  }'
```

```python
import requests

# 裁剪整个目录
response = requests.post(
    "http://localhost:8000/api/v2/preprocessing/crop",
    json={
        "input_path": "data/images",
        "output_path": "data/cropped_images",
        "x": 100,
        "y": 100,
        "width": 500,
        "height": 500,
        "description": "裁剪图像中心区域"
    }
)

task = response.json()
print(f"任务ID: {task['task_id']}")
```

---

### 4. 查询任务状态

**端点**: `GET /api/v2/preprocessing/{task_id}`

#### 响应示例

```json
{
  "task_id": "abc-123-def-456",
  "task_type": "data_augmentation",
  "status": "completed",
  "message": "数据增强完成",
  "progress": 100,
  "input_path": "data/split_dataset",
  "output_path": "data/augmented_dataset",
  "stats": {
    "original_images": 1000,
    "augmented_images": 6000,
    "methods_used": 6,
    "classes": ["class1", "class2", "class3"]
  },
  "created_at": "2025-10-29T10:00:00",
  "updated_at": "2025-10-29T10:15:00"
}
```

---

### 5. 获取实时日志

**端点**: `GET /api/v2/preprocessing/{task_id}/logs`

#### 使用示例

```python
import requests
import json

task_id = "abc-123-def-456"
response = requests.get(
    f"http://localhost:8000/api/v2/preprocessing/{task_id}/logs",
    stream=True
)

for line in response.iter_lines():
    if line:
        line_str = line.decode('utf-8')
        if line_str.startswith('data: '):
            log_entry = json.loads(line_str[6:])
            print(f"[{log_entry['level']}] {log_entry['message']}")
```

---

## 使用示例

### 完整的数据准备流程

```python
import requests
import time

BASE_URL = "http://localhost:8000"

# 1. 数据集分割
print("步骤1: 分割数据集...")
split_response = requests.post(
    f"{BASE_URL}/api/v2/preprocessing/split",
    json={
        "input_path": "data/raw_dataset",
        "output_path": "data/split_dataset",
        "train_ratio": 0.7,
        "val_ratio": 0.2
    }
)
split_task_id = split_response.json()['task_id']

# 等待分割完成
while True:
    status = requests.get(f"{BASE_URL}/api/v2/preprocessing/{split_task_id}").json()
    if status['status'] in ['completed', 'failed']:
        print(f"分割完成: {status['message']}")
        print(f"统计: {status.get('stats')}")
        break
    time.sleep(2)

# 2. 数据增强
print("\n步骤2: 数据增强...")
augment_response = requests.post(
    f"{BASE_URL}/api/v2/preprocessing/augment",
    json={
        "dataset_path": "data/split_dataset",
        "output_path": "data/augmented_dataset",
        "methods": ["CLAHE", "ColorJitter", "GaussNoise"]
    }
)
augment_task_id = augment_response.json()['task_id']

# 等待增强完成
while True:
    status = requests.get(f"{BASE_URL}/api/v2/preprocessing/{augment_task_id}").json()
    if status['status'] in ['completed', 'failed']:
        print(f"增强完成: {status['message']}")
        print(f"统计: {status.get('stats')}")
        break
    time.sleep(2)

# 3. 开始训练
print("\n步骤3: 开始训练...")
train_response = requests.post(
    f"{BASE_URL}/api/v2/training/start",
    json={
        "model": "resnet18",
        "num_classes": 37,
        "train_path": "data/augmented_dataset/train",
        "val_path": "data/augmented_dataset/valid",
        "save_path": "models/output",
        "num_epochs": 50,
        "device": "cuda:0"
    }
)
print(f"训练已启动: {train_response.json()['task_id']}")
```

---

## 常见问题

### Q1: 数据集分割后图像数量不对？
**A**: 分割是随机的，每次运行结果可能略有不同。检查`stats`字段中的统计信息，确保总数正确。

### Q2: 数据增强后图像数量增加了多少？
**A**: 如果使用全部6种方法，每张原图会生成1张原图 + 6张增强图 = 7张图。可以在任务完成后查看`stats`字段。

### Q3: 可以自定义增强参数吗？
**A**: 当前版本使用预设参数。如需自定义，可以修改`services/preprocessing_service.py`中的增强方法配置。

### Q4: 裁剪会改变原文件吗？
**A**: 不会。所有操作都会将结果保存到`output_path`，不会修改原始文件。

### Q5: 任务可以取消吗？
**A**: 可以使用`POST /api/v2/preprocessing/{task_id}/cancel`取消任务，但已经开始的操作会继续执行完当前文件。

### Q6: 支持哪些图像格式？
**A**: 支持常见格式：`.png`, `.jpg`, `.jpeg`, `.bmp`

---

## 性能建议

1. **数据集分割**
   - 对于大型数据集（>10000张），建议设置合适的`train_ratio`
   - 确保输出路径有足够的磁盘空间

2. **数据增强**
   - 增强会显著增加数据量（6倍或更多）
   - 建议先在小数据集上测试，确认效果后再处理完整数据集
   - 可以选择部分增强方法而非全部使用

3. **图像裁剪**
   - 批量处理时建议使用目录而非逐个文件
   - 确保裁剪区域在图像范围内，否则会失败

---

## 相关文档

- [API参数参考](./API_PARAMETERS_REFERENCE.md)
- [完整使用文档](./README_COMPLETE.md)
- [训练指标指南](./TRAINING_METRICS_GUIDE.md)

---

**更新时间**: 2025-10-29
**版本**: V2.4.0

