@echo off
REM RFUAV Model Service 重构版启动脚本 (Windows)
echo ========================================
echo RFUAV Model Service V2.3 重构版
echo ========================================
echo.

REM 检查Python
python --version >nul 2>&1
if errorlevel 1 (
    echo 错误: 未找到Python，请先安装Python 3.8+
    pause
    exit /b 1
)

REM 激活虚拟环境（如果存在）
if exist venv\Scripts\activate.bat (
    echo 激活虚拟环境...
    call venv\Scripts\activate.bat
)

REM 检查依赖
echo 检查依赖...
python -c "import fastapi" >nul 2>&1
if errorlevel 1 (
    echo 正在安装依赖...
    pip install -r requirements_refactored.txt
)

REM 启动服务
echo.
echo 启动服务...
echo API文档: http://localhost:8000/docs
echo 路由表: http://localhost:8000/
echo.
python app_refactored.py

pause


