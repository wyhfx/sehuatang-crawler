#!/bin/bash

echo "🚀 启动 Sehuatang 爬虫系统..."

# 检查Python环境
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 未安装，请先安装 Python 3.8+"
    exit 1
fi

# 检查Node.js环境
if ! command -v node &> /dev/null; then
    echo "❌ Node.js 未安装，请先安装 Node.js 16+"
    exit 1
fi

# 检查npm
if ! command -v npm &> /dev/null; then
    echo "❌ npm 未安装，请先安装 npm 8+"
    exit 1
fi

echo "✅ 环境检查通过"

# 安装Python依赖
echo "📦 安装 Python 依赖..."
pip3 install -r requirements.txt

# 安装前端依赖
echo "📦 安装前端依赖..."
cd frontend
npm install
cd ..

# 构建前端
echo "🔨 构建前端应用..."
cd frontend
npm run build
cd ..

# 启动后端服务
echo "🌐 启动后端服务..."
python3 main.py
