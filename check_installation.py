"""
安装检查脚本
验证所有依赖是否正确安装
"""
import sys
import importlib

# 终端颜色
class Colors:
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BLUE = '\033[94m'
    BOLD = '\033[1m'
    END = '\033[0m'

def check_package(package_name, import_name=None):
    """检查包是否安装"""
    if import_name is None:
        import_name = package_name
    
    try:
        mod = importlib.import_module(import_name)
        version = getattr(mod, '__version__', 'unknown')
        print(f"{Colors.GREEN}✅ {package_name:20s} : {version}{Colors.END}")
        return True
    except ImportError as e:
        print(f"{Colors.RED}❌ {package_name:20s} : 未安装 ({e}){Colors.END}")
        return False

def main():
    """主检查函数"""
    print(f"\n{Colors.BOLD}{'='*60}{Colors.END}")
    print(f"{Colors.BOLD}RFUAV Model Service - 安装检查{Colors.END}")
    print(f"{Colors.BOLD}{'='*60}{Colors.END}\n")
    
    # 核心依赖
    print(f"{Colors.BLUE}检查核心依赖...{Colors.END}")
    core_packages = [
        ('FastAPI', 'fastapi'),
        ('Uvicorn', 'uvicorn'),
        ('Pydantic', 'pydantic'),
        ('Pydantic Settings', 'pydantic_settings'),
        ('Python Dotenv', 'dotenv'),
    ]
    
    core_ok = all(check_package(name, imp) for name, imp in core_packages)
    
    # 深度学习框架
    print(f"\n{Colors.BLUE}检查深度学习框架...{Colors.END}")
    dl_packages = [
        ('PyTorch', 'torch'),
        ('TorchVision', 'torchvision'),
    ]
    
    dl_ok = all(check_package(name, imp) for name, imp in dl_packages)
    
    # 图像处理
    print(f"\n{Colors.BLUE}检查图像处理库...{Colors.END}")
    image_packages = [
        ('OpenCV', 'cv2'),
        ('Pillow', 'PIL'),
        ('ImageIO', 'imageio'),
        ('Albumentations', 'albumentations'),
    ]
    
    image_ok = all(check_package(name, imp) for name, imp in image_packages)
    
    # 数据处理
    print(f"\n{Colors.BLUE}检查数据处理库...{Colors.END}")
    data_packages = [
        ('NumPy', 'numpy'),
        ('Pandas', 'pandas'),
        ('SciPy', 'scipy'),
    ]
    
    data_ok = all(check_package(name, imp) for name, imp in data_packages)
    
    # 可视化
    print(f"\n{Colors.BLUE}检查可视化库...{Colors.END}")
    viz_packages = [
        ('Matplotlib', 'matplotlib'),
        ('Seaborn', 'seaborn'),
    ]
    
    viz_ok = all(check_package(name, imp) for name, imp in viz_packages)
    
    # 其他工具
    print(f"\n{Colors.BLUE}检查工具库...{Colors.END}")
    tool_packages = [
        ('PyYAML', 'yaml'),
        ('Requests', 'requests'),
        ('TQDM', 'tqdm'),
        ('Psutil', 'psutil'),
    ]
    
    tool_ok = all(check_package(name, imp) for name, imp in tool_packages)
    
    # GPU检查
    print(f"\n{Colors.BLUE}检查GPU...{Colors.END}")
    import torch
    
    gpu_available = torch.cuda.is_available()
    if gpu_available:
        print(f"{Colors.GREEN}✅ GPU可用{Colors.END}")
        print(f"{Colors.GREEN}   CUDA版本: {torch.version.cuda}{Colors.END}")
        print(f"{Colors.GREEN}   GPU数量: {torch.cuda.device_count()}{Colors.END}")
        
        for i in range(torch.cuda.device_count()):
            name = torch.cuda.get_device_name(i)
            props = torch.cuda.get_device_properties(i)
            memory = props.total_memory / 1024**3  # GB
            print(f"{Colors.GREEN}   GPU {i}: {name} ({memory:.1f}GB){Colors.END}")
    else:
        print(f"{Colors.YELLOW}⚠️  GPU不可用（将使用CPU）{Colors.END}")
    
    # Python版本检查
    print(f"\n{Colors.BLUE}检查Python版本...{Colors.END}")
    py_version = sys.version_info
    version_str = f"{py_version.major}.{py_version.minor}.{py_version.micro}"
    
    if py_version.major == 3 and 8 <= py_version.minor <= 11:
        print(f"{Colors.GREEN}✅ Python版本: {version_str} (符合要求){Colors.END}")
        py_ok = True
    else:
        print(f"{Colors.YELLOW}⚠️  Python版本: {version_str} (建议使用3.8-3.11){Colors.END}")
        py_ok = False
    
    # 总结
    print(f"\n{Colors.BOLD}{'='*60}{Colors.END}")
    print(f"{Colors.BOLD}检查结果{Colors.END}")
    print(f"{Colors.BOLD}{'='*60}{Colors.END}")
    
    results = [
        ('核心依赖', core_ok),
        ('深度学习框架', dl_ok),
        ('图像处理', image_ok),
        ('数据处理', data_ok),
        ('可视化', viz_ok),
        ('工具库', tool_ok),
        ('Python版本', py_ok),
    ]
    
    all_ok = all(ok for _, ok in results)
    
    for name, ok in results:
        status = f"{Colors.GREEN}✅ 通过{Colors.END}" if ok else f"{Colors.RED}❌ 失败{Colors.END}"
        print(f"{name:15s}: {status}")
    
    print(f"\n{Colors.BOLD}GPU状态{Colors.END}: ", end='')
    if gpu_available:
        print(f"{Colors.GREEN}✅ 可用 ({torch.cuda.device_count()} 个GPU){Colors.END}")
    else:
        print(f"{Colors.YELLOW}⚠️  不可用{Colors.END}")
    
    print(f"\n{Colors.BOLD}{'='*60}{Colors.END}")
    
    if all_ok:
        print(f"{Colors.GREEN}{Colors.BOLD}✅ 所有检查通过！环境配置正确。{Colors.END}")
        print(f"\n{Colors.BLUE}下一步:{Colors.END}")
        print(f"  1. 启动服务: python app_refactored.py")
        print(f"  2. 访问API文档: http://localhost:8000/docs")
        print(f"  3. 运行测试: python test_concurrency.py")
        return 0
    else:
        print(f"{Colors.RED}{Colors.BOLD}❌ 部分检查失败，请安装缺失的依赖。{Colors.END}")
        print(f"\n{Colors.YELLOW}解决方案:{Colors.END}")
        print(f"  pip install -r requirements.txt")
        return 1

if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print(f"\n{Colors.YELLOW}检查被中断{Colors.END}")
        sys.exit(1)
    except Exception as e:
        print(f"\n{Colors.RED}检查失败: {e}{Colors.END}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

