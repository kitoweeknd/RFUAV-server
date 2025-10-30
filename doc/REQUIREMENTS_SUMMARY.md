# Requirements 依赖说明

> RFUAV Model Service - 依赖管理和安装指南

## 📋 依赖文件说明

项目提供了4个不同的requirements文件，根据使用场景选择：

### 1. requirements.txt ⭐ 推荐
**用途**: 生产和开发的基础环境

**包含**:
- Web框架 (FastAPI, Uvicorn)
- 深度学习 (PyTorch, TorchVision)
- 图像处理 (OpenCV, Pillow, Albumentations)
- 数据处理 (NumPy, Pandas, SciPy)
- 可视化 (Matplotlib, Seaborn)
- 工具库 (PyYAML, TQDM, Psutil, etc.)

**安装**:
```bash
# GPU版本（推荐）
pip install torch==2.0.1+cu118 torchvision==0.15.2+cu118 --extra-index-url https://download.pytorch.org/whl/cu118
pip install -r requirements.txt

# CPU版本
pip install torch==2.0.1+cpu torchvision==0.15.2+cpu --extra-index-url https://download.pytorch.org/whl/cpu
pip install -r requirements.txt
```

---

### 2. requirements-dev.txt
**用途**: 开发环境，包含代码质量工具

**额外包含**:
- 代码格式化 (Black, isort, autopep8)
- 代码检查 (flake8, mypy)
- 测试工具 (pytest, pytest-asyncio, pytest-cov)
- 文档工具 (mkdocs, mkdocs-material)
- 调试工具 (ipython, ipdb, jupyter)
- 性能分析 (line-profiler, memory-profiler)

**安装**:
```bash
pip install -r requirements-dev.txt
```

**使用**:
```bash
# 代码格式化
black .

# 代码检查
flake8 .
mypy .

# 运行测试
pytest tests/

# 生成文档
mkdocs serve
```

---

### 3. requirements-test.txt
**用途**: 仅用于CI/CD测试环境

**额外包含**:
- 测试框架 (pytest, pytest-asyncio)
- HTTP测试 (httpx, aiohttp)
- Mock工具 (faker, factory-boy)
- 覆盖率 (coverage)

**安装**:
```bash
pip install -r requirements-test.txt
```

**使用**:
```bash
# 运行所有测试
pytest

# 带覆盖率
pytest --cov=.

# 并行测试
pytest -n auto
```

---

### 4. requirements-prod.txt
**用途**: 生产环境，包含监控和优化工具

**额外包含**:
- 服务器 (Gunicorn)
- 缓存 (Redis, hiredis)
- 监控 (Prometheus, Sentry)
- 性能 (orjson, ujson)
- 安全 (slowapi, python-jose, passlib)

**安装**:
```bash
pip install -r requirements-prod.txt
```

**使用**:
```bash
# 使用Gunicorn
gunicorn app_refactored:app -w 4 -k uvicorn.workers.UvicornWorker

# 配置监控
# 参见生产环境配置文档
```

---

## 📦 核心依赖详解

### Web框架

| 包名 | 版本 | 用途 |
|------|------|------|
| fastapi | >=0.104.0 | 现代Web框架 |
| uvicorn[standard] | >=0.24.0 | ASGI服务器 |
| python-multipart | >=0.0.6 | 文件上传支持 |

### 深度学习

| 包名 | 版本 | 用途 |
|------|------|------|
| torch | >=2.0.0 | PyTorch核心 |
| torchvision | >=0.15.0 | 视觉模型 |
| torchaudio | >=2.0.0 | 音频处理（可选） |

### 图像处理

| 包名 | 版本 | 用途 |
|------|------|------|
| opencv-python | >=4.8.0 | 图像处理 |
| Pillow | >=10.0.0 | 图像IO |
| imageio | >=2.31.0 | 图像读写 |
| albumentations | >=1.4.0 | 数据增强 |

### 数据处理

| 包名 | 版本 | 用途 |
|------|------|------|
| numpy | >=1.24.0 | 数值计算 |
| pandas | >=2.0.0 | 数据分析 |
| scipy | >=1.13.0 | 科学计算 |

### 数据验证

| 包名 | 版本 | 用途 |
|------|------|------|
| pydantic | >=2.0.0 | 数据验证 |
| pydantic-settings | >=2.0.0 | 配置管理 |

---

## 🔧 安装建议

### 按环境选择

#### 本地开发
```bash
pip install -r requirements-dev.txt
```
**包含**: 所有开发工具 + 测试工具 + 基础依赖

#### CI/CD测试
```bash
pip install -r requirements-test.txt
```
**包含**: 测试工具 + 基础依赖

#### 生产部署
```bash
pip install -r requirements-prod.txt
```
**包含**: 监控工具 + 优化工具 + 基础依赖

#### 最小安装
```bash
pip install -r requirements.txt
```
**包含**: 仅基础依赖

---

## 🚀 快速安装

### 一键安装脚本

创建 `install.sh` (Linux/Mac):
```bash
#!/bin/bash
set -e

echo "安装RFUAV Model Service..."

# 创建虚拟环境
python3 -m venv venv
source venv/bin/activate

# 升级pip
pip install --upgrade pip

# 安装PyTorch (GPU)
pip install torch==2.0.1+cu118 torchvision==0.15.2+cu118 \
    --extra-index-url https://download.pytorch.org/whl/cu118

# 安装依赖
pip install -r requirements.txt

# 验证安装
python check_installation.py

echo "✅ 安装完成！"
echo "启动服务: python app_refactored.py"
```

创建 `install.bat` (Windows):
```batch
@echo off
echo 安装RFUAV Model Service...

REM 创建虚拟环境
python -m venv venv
call venv\Scripts\activate.bat

REM 升级pip
pip install --upgrade pip

REM 安装PyTorch (GPU)
pip install torch==2.0.1+cu118 torchvision==0.15.2+cu118 --extra-index-url https://download.pytorch.org/whl/cu118

REM 安装依赖
pip install -r requirements.txt

REM 验证安装
python check_installation.py

echo.
echo 安装完成！
echo 启动服务: python app_refactored.py
pause
```

---

## 🐛 常见问题

### Q1: 安装失败，提示找不到某个包

**A**: 使用国内镜像源
```bash
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
```

### Q2: PyTorch版本冲突

**A**: 先安装PyTorch，再安装其他依赖
```bash
# 1. 先安装PyTorch
pip install torch==2.0.1+cu118 torchvision==0.15.2+cu118 --extra-index-url https://download.pytorch.org/whl/cu118

# 2. 再安装其他依赖
pip install -r requirements.txt
```

### Q3: CUDA版本不匹配

**A**: 根据CUDA版本选择PyTorch
```bash
# 查看CUDA版本
nvidia-smi

# CUDA 11.8
pip install torch==2.0.1+cu118 torchvision==0.15.2+cu118 --extra-index-url https://download.pytorch.org/whl/cu118

# CUDA 12.1
pip install torch==2.0.1+cu121 torchvision==0.15.2+cu121 --extra-index-url https://download.pytorch.org/whl/cu121

# CPU版本
pip install torch==2.0.1+cpu torchvision==0.15.2+cpu --extra-index-url https://download.pytorch.org/whl/cpu
```

### Q4: Windows下编译错误

**A**: 安装Visual C++ Build Tools
```
下载地址: https://visualstudio.microsoft.com/visual-cpp-build-tools/
或使用预编译的二进制包（wheel文件）
```

---

## 📊 依赖统计

### 总体统计

| 文件 | 包数量 | 大小估算 | 安装时间 |
|------|--------|---------|---------|
| requirements.txt | ~25个 | ~3GB | ~5-10分钟 |
| requirements-dev.txt | ~45个 | ~4GB | ~10-15分钟 |
| requirements-test.txt | ~30个 | ~3.5GB | ~5-10分钟 |
| requirements-prod.txt | ~35个 | ~3.5GB | ~5-10分钟 |

### 按类别统计

| 类别 | 包数量 | 主要用途 |
|------|--------|---------|
| Web框架 | 3 | API服务 |
| 深度学习 | 3 | 模型训练和推理 |
| 图像处理 | 4 | 图像预处理 |
| 数据处理 | 3 | 数据分析 |
| 可视化 | 2 | 图表绘制 |
| 工具库 | 10+ | 日志、配置、性能等 |

---

## 🔄 依赖更新

### 查看可更新的包
```bash
pip list --outdated
```

### 更新所有包
```bash
pip install --upgrade -r requirements.txt
```

### 更新单个包
```bash
pip install --upgrade fastapi
```

### 锁定版本
```bash
# 生成当前环境的精确版本
pip freeze > requirements.lock

# 使用锁定版本安装
pip install -r requirements.lock
```

---

## 📝 维护建议

1. **定期更新**: 每月检查一次依赖更新
2. **安全审计**: 使用 `pip-audit` 检查安全漏洞
3. **版本锁定**: 生产环境使用精确版本
4. **虚拟环境**: 始终使用虚拟环境隔离依赖
5. **文档更新**: 添加新依赖时更新本文档

---

## 🔗 相关文档

- **[INSTALLATION_GUIDE.md](INSTALLATION_GUIDE.md)** - 完整安装指南
- **[README_COMPLETE.md](README_COMPLETE.md)** - 项目主文档
- **[check_installation.py](check_installation.py)** - 安装验证脚本

---

**最后更新**: 2024-01  
**版本**: V2.3.1

