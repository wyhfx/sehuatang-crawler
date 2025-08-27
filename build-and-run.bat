@echo off
chcp 65001 >nul

echo 🚀 Sehuatang 爬虫系统 - Docker 构建和运行脚本
echo ==================================================

REM 检查Docker是否安装
docker --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Docker 未安装，请先安装 Docker
    pause
    exit /b 1
)

docker-compose --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Docker Compose 未安装，请先安装 Docker Compose
    pause
    exit /b 1
)

REM 创建必要的目录
echo 📁 创建必要的目录...
if not exist "data" mkdir data
if not exist "logs" mkdir logs

REM 构建镜像
echo 🔨 构建 Docker 镜像...
docker-compose build
if errorlevel 1 (
    echo ❌ 构建失败
    pause
    exit /b 1
)

REM 启动服务
echo 🚀 启动服务...
docker-compose up -d
if errorlevel 1 (
    echo ❌ 启动失败
    pause
    exit /b 1
)

REM 等待服务启动
echo ⏳ 等待服务启动...
timeout /t 10 /nobreak >nul

REM 检查服务状态
echo 🔍 检查服务状态...
docker-compose ps

REM 检查健康状态
echo 🏥 检查健康状态...
curl -f http://localhost:8000/health >nul 2>&1
if errorlevel 1 (
    echo ❌ 服务启动失败，请检查日志：
    docker-compose logs
    pause
    exit /b 1
) else (
    echo ✅ 服务启动成功！
    echo.
    echo 🌐 访问地址：
    echo    - 主应用: http://localhost:8000
    echo    - API文档: http://localhost:8000/docs
    echo    - 健康检查: http://localhost:8000/health
    echo.
    echo 📋 可用命令：
    echo    - 查看日志: docker-compose logs -f
    echo    - 停止服务: docker-compose down
    echo    - 重启服务: docker-compose restart
    echo    - 更新镜像: docker-compose pull ^&^& docker-compose up -d
)

pause

