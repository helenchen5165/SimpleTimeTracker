"""
SimpleTimeTracker FastAPI Application
主应用程序入口
"""

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn
import sys
import os

# 添加父目录到Python路径，以便导入原有模块
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from api.config.settings import get_settings
from api.routes import auth, goals, time_records, reports, notion, dashboard
from api.middleware.auth import JWTMiddleware

# 加载配置
settings = get_settings()

# 创建FastAPI应用
app = FastAPI(
    title="SimpleTimeTracker API",
    description="智能时间记录与目标管理系统 API",
    version="2.1.0",
    docs_url="/docs" if settings.debug else None,
    redoc_url="/redoc" if settings.debug else None,
)

# CORS中间件配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# JWT认证中间件
app.add_middleware(JWTMiddleware)

# 路由注册
app.include_router(auth.router, prefix="/v1/auth", tags=["认证"])
app.include_router(goals.router, prefix="/v1/goals", tags=["目标管理"])  
app.include_router(time_records.router, prefix="/v1/time-records", tags=["时间记录"])
app.include_router(reports.router, prefix="/v1/reports", tags=["报告统计"])
app.include_router(notion.router, prefix="/v1/notion", tags=["Notion集成"])
app.include_router(dashboard.router, prefix="/v1/dashboard", tags=["仪表板"])

# 全局异常处理
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """全局异常处理器"""
    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "error": {
                "code": "SERVER_ERROR",
                "message": "服务器内部错误",
                "details": str(exc) if settings.debug else None
            }
        }
    )

# 健康检查端点
@app.get("/health")
async def health_check():
    """健康检查"""
    return {
        "success": True,
        "data": {
            "status": "healthy",
            "version": "2.1.0",
            "service": "SimpleTimeTracker API"
        }
    }

# 根路径
@app.get("/")
async def root():
    """API根路径"""
    return {
        "success": True,
        "data": {
            "message": "SimpleTimeTracker API",
            "version": "2.1.0",
            "docs": "/docs" if settings.debug else "Documentation disabled in production"
        }
    }

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug,
        log_level="info"
    )