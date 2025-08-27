@echo off
chcp 65001 >nul
echo 🚀 启动 Sehuatang 爬虫系统...

REM 检查Python环境
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python 未安装，请先安装 Python 3.8+
    pause
    exit /b 1
)

REM 检查Node.js环境
node --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Node.js 未安装，请先安装 Node.js 16+
    pause
    exit /b 1
)

REM 检查npm
npm --version >nul 2>&1
if errorlevel 1 (
    echo ❌ npm 未安装，请先安装 npm 8+
    pause
    exit /b 1
)

echo ✅ 环境检查通过

REM 安装Python依赖
echo 📦 安装 Python 依赖...
pip install -r requirements.txt

REM 安装前端依赖
echo 📦 安装前端依赖...
cd frontend
npm install
cd ..

REM 构建前端
echo 🔨 构建前端应用...
cd frontend
npm run build
cd ..

REM 启动后端服务
echo 🌐 启动后端服务...
python main.py

pause
