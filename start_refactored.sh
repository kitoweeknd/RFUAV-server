#!/bin/bash
# RFUAV Model Service 重构版启动脚本 (Linux/Mac)

echo "========================================"
echo "RFUAV Model Service V2.3 重构版"
echo "========================================"
echo

# 检查Python
if ! command -v python3 &> /dev/null; then
    echo "错误: 未找到Python3，请先安装Python 3.8+"
    exit 1
fi

# 激活虚拟环境（如果存在）
if [ -d "venv" ]; then
    echo "激活虚拟环境..."
    source venv/bin/activate
fi

# 检查依赖
echo "检查依赖..."
python3 -c "import fastapi" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "正在安装依赖..."
    pip3 install -r requirements_refactored.txt
fi

# 启动服务
echo
echo "启动服务..."
echo "API文档: http://localhost:8000/docs"
echo "路由表: http://localhost:8000/"
echo

python3 app_refactored.py


