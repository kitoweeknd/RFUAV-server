"""
RFUAV模型服务 - 重构版
清晰的分层架构和路由表
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging

# 导入路由
from api.routers import training, inference, tasks, resources, health, preprocessing

# 导入配置
from core.config import settings
from core.resource_manager import resource_manager


# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    # 启动时
    logger.info("启动RFUAV模型服务...")
    logger.info(f"版本: {settings.VERSION}")
    logger.info(f"环境: {settings.ENVIRONMENT}")
    
    # 输出GPU信息
    resource_manager.print_gpu_info()
    
    yield
    
    # 关闭时
    logger.info("关闭服务...")


# 创建FastAPI应用
app = FastAPI(
    title=settings.APP_NAME,
    description=settings.DESCRIPTION,
    version=settings.VERSION,
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc"
)

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ==================== 路由表 ====================

@app.get("/", tags=["Root"])
async def root():
    """
    根路径 - API概览
    """
    return {
        "name": settings.APP_NAME,
        "version": settings.VERSION,
        "environment": settings.ENVIRONMENT,
        "features": [
            "参数化训练配置",
            "实时日志流",
            "训练推理并发",
            "智能资源管理",
            "设备灵活选择"
        ],
        "endpoints": {
            "训练接口": {
                "启动训练": "POST /api/v2/training/start",
                "训练状态（含详细指标）": "GET /api/v2/training/{task_id}",
                "训练日志流（含指标）": "GET /api/v2/training/{task_id}/logs",
                "停止训练": "POST /api/v2/training/{task_id}/stop"
            },
            "推理接口": {
                "启动推理": "POST /api/v2/inference/start",
                "推理状态": "GET /api/v2/inference/{task_id}",
                "批量推理": "POST /api/v2/inference/batch"
            },
            "数据预处理接口": {
                "数据集分割": "POST /api/v2/preprocessing/split",
                "数据增强": "POST /api/v2/preprocessing/augment",
                "图像裁剪": "POST /api/v2/preprocessing/crop",
                "任务状态": "GET /api/v2/preprocessing/{task_id}",
                "任务日志": "GET /api/v2/preprocessing/{task_id}/logs"
            },
            "任务管理": {
                "所有任务": "GET /api/v2/tasks",
                "任务详情": "GET /api/v2/tasks/{task_id}",
                "任务日志": "GET /api/v2/tasks/{task_id}/logs",
                "取消任务": "POST /api/v2/tasks/{task_id}/cancel"
            },
            "资源管理": {
                "资源状态": "GET /api/v2/resources",
                "GPU信息": "GET /api/v2/resources/gpu",
                "更新配置": "POST /api/v2/resources/config"
            },
            "系统状态": {
                "健康检查": "GET /api/v1/health",
                "系统信息": "GET /api/v1/info"
            }
        },
        "documentation": {
            "swagger": "/docs",
            "redoc": "/redoc"
        }
    }


# 注册路由模块
app.include_router(
    training.router,
    prefix="/api/v2/training",
    tags=["Training"]
)

app.include_router(
    inference.router,
    prefix="/api/v2/inference",
    tags=["Inference"]
)

app.include_router(
    tasks.router,
    prefix="/api/v2/tasks",
    tags=["Tasks"]
)

app.include_router(
    resources.router,
    prefix="/api/v2/resources",
    tags=["Resources"]
)

app.include_router(
    health.router,
    prefix="/api/v1",
    tags=["Health"]
)

app.include_router(
    preprocessing.router,
    prefix="/api/v2/preprocessing",
    tags=["Preprocessing"]
)


# ==================== 启动服务 ====================

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app_refactored:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG
    )

