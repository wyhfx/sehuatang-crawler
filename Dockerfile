# 第一阶段：构建前端
FROM node:18-alpine AS frontend-builder

WORKDIR /app/frontend

# 复制前端依赖文件
COPY frontend/package*.json ./

# 安装前端依赖
RUN npm install

# 复制前端源代码
COPY frontend/ ./

# 构建前端（添加调试信息）
RUN echo "开始构建前端..." && \
    ls -la && \
    npm run build && \
    echo "前端构建完成" && \
    ls -la dist/ && \
    echo "检查index.html是否存在:" && \
    ls -la dist/index.html && \
    echo "检查assets目录:" && \
    ls -la dist/assets/

# 第二阶段：构建后端
FROM python:3.9-slim

# 设置环境变量
ENV PYTHONUNBUFFERED=1
ENV DEBIAN_FRONTEND=noninteractive

# 使用国内镜像源安装系统 chromium 与 chromedriver
RUN echo "deb https://mirrors.aliyun.com/debian/ trixie main" > /etc/apt/sources.list && \
    echo "deb https://mirrors.aliyun.com/debian-security/ trixie-security main" >> /etc/apt/sources.list && \
    echo "deb https://mirrors.aliyun.com/debian/ trixie-updates main" >> /etc/apt/sources.list && \
    apt-get update && \
    apt-get install -y --no-install-recommends \
        chromium \
        chromium-driver \
        fonts-liberation ca-certificates curl jq && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app

# 复制依赖文件并安装Python依赖
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 复制后端应用代码
COPY *.py ./
COPY routes/ ./routes/
COPY models_*.py ./
COPY utils/ ./utils/
COPY enrichment/ ./enrichment/

# 从前端构建阶段复制构建结果
COPY --from=frontend-builder /app/frontend/dist ./frontend/build

# 创建必要的目录
RUN mkdir -p data logs

# 验证前端文件
RUN echo "验证前端构建结果:" && \
    ls -la frontend/build/ && \
    echo "检查index.html:" && \
    ls -la frontend/build/index.html && \
    echo "检查assets目录:" && \
    ls -la frontend/build/assets/ && \
    echo "前端文件验证完成"

# 暴露端口
EXPOSE 8000

# 启动命令
CMD ["python", "main.py"]
