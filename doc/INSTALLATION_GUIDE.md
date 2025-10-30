# 安装指南

> RFUAV Model Service - 详细的安装和环境配置指南

## 📋 目录

- [系统要求](#系统要求)
- [快速安装](#快速安装)
- [详细安装步骤](#详细安装步骤)
- [不同环境安装](#不同环境安装)
- [验证安装](#验证安装)
- [常见问题](#常见问题)

---

## 系统要求

### 最低要求

| 组件 | 要求 |
|------|------|
| **操作系统** | Windows 10/11, Ubuntu 18.04+, macOS 10.15+ |
| **Python** | 3.8 - 3.11 |
| **内存** | 8GB RAM |
| **磁盘** | 10GB 可用空间 |
| **GPU** | 可选（推荐NVIDIA GPU with CUDA 11.8+） |

### 推荐配置

| 组件 | 推荐配置 |
|------|---------|
| **CPU** | 8核心或更多 |
| **内存** | 16GB RAM 或更多 |
| **GPU** | NVIDIA RTX 3090 (24GB) 或类似 |
| **磁盘** | SSD, 50GB+ 可用空间 |

---

## 快速安装

### 方式1: 自动安装（推荐）

```bash
# 1. 克隆仓库
git clone <repository-url>
cd RFUAV-server

# 2. 创建虚拟环境
python -m venv venv

# 3. 激活虚拟环境
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# 4. 安装依赖（GPU版本）
pip install torch==2.0.1+cu118 torchvision==0.15.2+cu118 --extra-index-url https://download.pytorch.org/whl/cu118
pip install -r requirements.txt

# 5. 启动服务
python app_refactored.py
```

### 方式2: CPU版本安装

```bash
# 安装CPU版本的PyTorch
pip install torch==2.0.1+cpu torchvision==0.15.2+cpu --extra-index-url https://download.pytorch.org/whl/cpu
pip install -r requirements.txt
```

---

## 详细安装步骤

### 1. 安装Python

#### Windows
```powershell
# 下载Python 3.10
# 访问 https://www.python.org/downloads/
# 安装时勾选 "Add Python to PATH"

# 验证安装
python --version
```

#### Ubuntu/Debian
```bash
sudo apt update
sudo apt install python3.10 python3.10-venv python3-pip
python3.10 --version
```

#### macOS
```bash
# 使用Homebrew
brew install python@3.10
python3.10 --version
```

---

### 2. 创建虚拟环境

```bash
# 创建虚拟环境
python -m venv venv

# 激活虚拟环境
# Windows (PowerShell):
.\venv\Scripts\Activate.ps1

# Windows (CMD):
.\venv\Scripts\activate.bat

# Linux/Mac:
source venv/bin/activate

# 升级pip
pip install --upgrade pip
```

---

### 3. 安装CUDA（GPU用户）

#### 检查CUDA版本
```bash
# NVIDIA驱动版本
nvidia-smi

# CUDA版本
nvcc --version
```

#### 安装CUDA 11.8
```bash
# Windows/Linux:
# 访问 https://developer.nvidia.com/cuda-11-8-0-download-archive
# 下载并安装CUDA Toolkit 11.8

# 验证
nvcc --version
```

---

### 4. 安装PyTorch

#### GPU版本（CUDA 11.8）
```bash
pip install torch==2.0.1+cu118 torchvision==0.15.2+cu118 torchaudio==2.0.2+cu118 \
  --extra-index-url https://download.pytorch.org/whl/cu118
```

#### CPU版本
```bash
pip install torch==2.0.1+cpu torchvision==0.15.2+cpu torchaudio==2.0.2+cpu \
  --extra-index-url https://download.pytorch.org/whl/cpu
```

#### 验证安装
```python
python -c "import torch; print(f'PyTorch版本: {torch.__version__}'); print(f'CUDA可用: {torch.cuda.is_available()}'); print(f'CUDA版本: {torch.version.cuda}')"
```

预期输出：
```
PyTorch版本: 2.0.1+cu118
CUDA可用: True
CUDA版本: 11.8
```

---

### 5. 安装项目依赖

#### 基础安装
```bash
pip install -r requirements.txt
```

#### 开发环境
```bash
pip install -r requirements-dev.txt
```

#### 测试环境
```bash
pip install -r requirements-test.txt
```

#### 生产环境
```bash
pip install -r requirements-prod.txt
```

---

## 不同环境安装

### 开发环境

```bash
# 完整开发环境
pip install -r requirements-dev.txt

# 配置开发工具
pre-commit install  # Git hooks

# 运行代码检查
black .             # 代码格式化
flake8 .            # 代码检查
mypy .              # 类型检查
```

### 测试环境

```bash
# 安装测试依赖
pip install -r requirements-test.txt

# 运行测试
pytest tests/                    # 所有测试
pytest --cov=.                   # 带覆盖率
pytest -n auto                   # 并行测试
```

### 生产环境

```bash
# 安装生产依赖
pip install -r requirements-prod.txt

# 配置环境变量
cp env.example .env
nano .env  # 编辑配置

# 使用Gunicorn运行（可选）
gunicorn app_refactored:app -w 4 -k uvicorn.workers.UvicornWorker
```

---

## Docker安装（可选）

### 创建Dockerfile

```dockerfile
FROM python:3.10-slim

WORKDIR /app

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    git \
    libgl1-mesa-glx \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# 复制依赖文件
COPY requirements.txt .

# 安装Python依赖
RUN pip install --no-cache-dir torch==2.0.1+cpu torchvision==0.15.2+cpu \
    --extra-index-url https://download.pytorch.org/whl/cpu
RUN pip install --no-cache-dir -r requirements.txt

# 复制项目文件
COPY . .

# 暴露端口
EXPOSE 8000

# 启动命令
CMD ["python", "app_refactored.py"]
```

### 构建和运行

```bash
# 构建镜像
docker build -t rfuav-server .

# 运行容器
docker run -p 8000:8000 rfuav-server

# 使用GPU (需要nvidia-docker)
docker run --gpus all -p 8000:8000 rfuav-server
```

---

## 验证安装

### 1. 检查Python包

```bash
pip list | grep -E "torch|fastapi|uvicorn"
```

预期输出：
```
fastapi              0.104.1
torch                2.0.1+cu118
torchvision          0.15.2+cu118
uvicorn              0.24.0
```

### 2. 运行健康检查脚本

```python
# check_installation.py
import sys
import importlib

packages = [
    'fastapi', 'uvicorn', 'pydantic', 'torch', 'torchvision',
    'cv2', 'numpy', 'pandas', 'yaml', 'PIL'
]

print("检查依赖包...")
for package in packages:
    try:
        mod = importlib.import_module(package)
        version = getattr(mod, '__version__', 'unknown')
        print(f"✅ {package}: {version}")
    except ImportError:
        print(f"❌ {package}: 未安装")
        sys.exit(1)

print("\n检查GPU...")
import torch
if torch.cuda.is_available():
    print(f"✅ GPU可用")
    print(f"   GPU数量: {torch.cuda.device_count()}")
    for i in range(torch.cuda.device_count()):
        print(f"   GPU {i}: {torch.cuda.get_device_name(i)}")
else:
    print(f"⚠️  GPU不可用（将使用CPU）")

print("\n✅ 所有检查通过！")
```

运行检查：
```bash
python check_installation.py
```

### 3. 启动服务测试

```bash
# 启动服务
python app_refactored.py

# 在另一个终端测试
curl http://localhost:8000/api/v1/health
```

预期响应：
```json
{
  "status": "healthy",
  "version": "2.3.1",
  ...
}
```

---

## 常见问题

### Q1: pip install 速度慢

**A**: 使用国内镜像源

```bash
# 临时使用
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple

# 永久配置
pip config set global.index-url https://pypi.tuna.tsinghua.edu.cn/simple
```

---

### Q2: CUDA版本不匹配

**A**: 检查CUDA版本并安装对应的PyTorch

```bash
# 检查CUDA版本
nvidia-smi

# CUDA 11.8
pip install torch==2.0.1+cu118 torchvision==0.15.2+cu118 --extra-index-url https://download.pytorch.org/whl/cu118

# CUDA 12.1
pip install torch==2.0.1+cu121 torchvision==0.15.2+cu121 --extra-index-url https://download.pytorch.org/whl/cu121
```

---

### Q3: Windows下OpenCV报错

**A**: 安装Visual C++运行库

```bash
# 下载并安装
# https://aka.ms/vs/17/release/vc_redist.x64.exe

# 或使用headless版本
pip uninstall opencv-python
pip install opencv-python-headless
```

---

### Q4: 内存不足

**A**: 减少batch_size或使用CPU

```bash
# 编辑 .env
MAX_TRAINING_CONCURRENT_GPU=1
MAX_INFERENCE_CONCURRENT_GPU=2

# 或在请求中指定较小的batch_size
{
  "batch_size": 4,  # 从8减到4
  ...
}
```

---

### Q5: 端口被占用

**A**: 更改端口或杀死占用进程

```bash
# Windows
netstat -ano | findstr :8000
taskkill /PID <PID> /F

# Linux/Mac
lsof -i :8000
kill -9 <PID>

# 或更改端口
# 编辑 .env
PORT=8001
```

---

### Q6: 虚拟环境激活失败（PowerShell）

**A**: 修改执行策略

```powershell
# 以管理员身份运行PowerShell
Set-ExecutionPolicy RemoteSigned -Scope CurrentUser

# 再次激活
.\venv\Scripts\Activate.ps1
```

---

## 卸载

### 完全卸载

```bash
# 停用虚拟环境
deactivate

# 删除虚拟环境
# Windows:
rmdir /s /q venv

# Linux/Mac:
rm -rf venv

# 删除缓存
pip cache purge
```

---

## 升级

### 升级依赖

```bash
# 升级所有包到最新版本
pip install --upgrade -r requirements.txt

# 升级单个包
pip install --upgrade fastapi

# 查看可升级的包
pip list --outdated
```

---

## 下一步

安装完成后：

1. ✅ 阅读 [README_COMPLETE.md](README_COMPLETE.md) 了解项目功能
2. ✅ 查看 [QUICK_START_REFACTORED.md](QUICK_START_REFACTORED.md) 快速开始
3. ✅ 运行 [test_concurrency.py](test_concurrency.py) 测试性能
4. ✅ 访问 http://localhost:8000/docs 查看API文档

---

**祝您使用愉快！** 🎉

如有问题，请查看文档或提交Issue。

