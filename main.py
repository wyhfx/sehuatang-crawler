#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Sehuatang 爬虫系统主应用
集成所有功能模块和API路由
"""

import os
import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager

# 导入数据库和模型
from db import engine, Base
from models_magnet import MagnetLink
from models_settings import Setting

# 导入路由
from routes.magnet_routes import router as magnet_router
from routes.settings_routes import router as settings_router
from routes.proxy_routes import router as proxy_router
# from routes.metadata_refresh import router as metadata_router
from routes.crawler_routes import router as crawler_router
from routes.jobs_routes import router as jobs_router
from routes.logs_routes import router as logs_router

# 导入设置管理器
from settings_manager import SettingsManager

@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    # 启动时执行
    print("🚀 启动 Sehuatang 爬虫系统...")
    
    # 创建数据库表
    Base.metadata.create_all(bind=engine)
    print("✅ 数据库表创建完成")
    
    # 初始化设置
    try:
        from migrate_settings_table import create_settings_table
        create_settings_table()
        print("✅ 设置表初始化完成")
    except Exception as e:
        print(f"⚠️ 设置表初始化失败: {e}")
    
    # 初始化磁力链接表
    try:
        from migrate_magnet_table import create_magnet_table
        create_magnet_table()
        print("✅ 磁力链接表初始化完成")
    except Exception as e:
        print(f"⚠️ 磁力链接表初始化失败: {e}")
    
    yield
    
    # 关闭时执行
    print("🛑 关闭 Sehuatang 爬虫系统...")

# 创建FastAPI应用
app = FastAPI(
    title="Sehuatang 爬虫系统",
    description="一个强大的磁力链接管理和元数据获取工具",
    version="1.0.0",
    lifespan=lifespan
)

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 生产环境中应该指定具体域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(magnet_router, tags=["磁力链接"])
app.include_router(settings_router, tags=["系统设置"])
app.include_router(proxy_router, tags=["代理管理"])
# app.include_router(metadata_router, tags=["元数据"]) # 注释掉metadata_refresh路由
app.include_router(crawler_router, tags=["爬虫管理"])
app.include_router(jobs_router, tags=["任务调度"])
app.include_router(logs_router, tags=["系统日志"])

# 静态文件服务（用于前端）
if os.path.exists("frontend/build"):
    app.mount("/assets", StaticFiles(directory="frontend/build/assets"), name="assets")

    # 提供前端主页
    @app.get("/", include_in_schema=False)
    def serve_frontend():
        """提供前端主页"""
        from fastapi.responses import FileResponse
        return FileResponse("frontend/build/index.html")

    # 提供 manifest.json
    @app.get("/manifest.json", include_in_schema=False)
    def serve_manifest():
        """提供 manifest.json 文件"""
        from fastapi.responses import FileResponse
        return FileResponse("frontend/build/manifest.json")

    # 提供 vite.svg (重定向到favicon.ico)
    @app.get("/vite.svg", include_in_schema=False)
    def serve_vite_svg():
        """提供 vite.svg 文件（重定向到favicon.ico）"""
        from fastapi.responses import FileResponse
        return FileResponse("frontend/build/favicon.ico")

# 健康检查
@app.get("/health")
def health_check():
    """健康检查接口"""
    return {
        "status": "healthy",
        "message": "Sehuatang 爬虫系统运行正常",
        "version": "1.0.0"
    }

# 系统信息
@app.get("/api/system/info")
def get_system_info():
    """获取系统信息"""
    try:
        from db import SessionLocal
        db = SessionLocal()
        
        # 获取统计信息
        magnet_count = db.query(MagnetLink).count()
        settings_count = db.query(Setting).count()
        
        db.close()
        
        return {
            "success": True,
            "data": {
                "magnet_count": magnet_count,
                "settings_count": settings_count,
                "version": "1.0.0"
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取系统信息失败: {str(e)}")

# 根路径重定向（仅在没有前端文件时使用）
if not os.path.exists("frontend/build"):
    @app.get("/")
    def root():
        """根路径处理"""
        return {"message": "Sehuatang 爬虫系统 API", "docs": "/docs"}

if __name__ == "__main__":
    # 获取配置
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", "8000"))
    debug = os.getenv("DEBUG", "false").lower() == "true"
    
    print(f"🌐 启动服务器: http://{host}:{port}")
    print(f"📚 API文档: http://{host}:{port}/docs")
    print(f"🔧 调试模式: {debug}")
    
    # 启动服务器
    uvicorn.run(
        "main:app",
        host=host,
        port=port,
        reload=debug,
        log_level="info"
    )
