# Sehuatang 爬虫系统 - Docker 部署指南

## 🚀 快速开始

### 前置要求

- Docker Desktop (Windows/Mac) 或 Docker Engine (Linux)
- Docker Compose
- 至少 2GB 可用内存

### 一键部署

#### Windows 用户
```bash
# 双击运行
build-and-run.bat
```

#### Linux/Mac 用户
```bash
# 给脚本执行权限
chmod +x build-and-run.sh

# 运行脚本
./build-and-run.sh
```

#### 手动部署
```bash
# 1. 创建必要目录
mkdir -p data logs

# 2. 构建镜像
docker-compose build

# 3. 启动服务
docker-compose up -d

# 4. 查看状态
docker-compose ps
```

## 🌐 访问地址

启动成功后，可以通过以下地址访问：

- **主应用**: http://localhost:8000
- **API文档**: http://localhost:8000/docs
- **健康检查**: http://localhost:8000/health

## ⚙️ 配置说明

### 环境变量配置

在 `docker-compose.yml` 中可以配置以下环境变量：

#### MetaTube 配置
```yaml
environment:
  - METATUBE_URL=http://192.168.31.102:8080
  - METATUBE_PROVIDER=JavBus
  - METATUBE_FALLBACK=true
```

#### 翻译配置（可选）
```yaml
environment:
  - TRANS_PROVIDER=baidu
  - BAIDU_APPID=your_appid
  - BAIDU_KEY=your_key
```

#### 代理配置（可选）
```yaml
environment:
  - HTTP_PROXY=http://192.168.31.85:7891
  - HTTPS_PROXY=http://192.168.31.85:7891
  - NO_PROXY=localhost,127.0.0.1,192.168.31.102
```

### 数据持久化

系统会自动创建以下目录用于数据持久化：

- `./data/` - 数据库文件
- `./logs/` - 日志文件

## 📋 常用命令

### 服务管理
```bash
# 查看服务状态
docker-compose ps

# 查看日志
docker-compose logs -f

# 停止服务
docker-compose down

# 重启服务
docker-compose restart

# 更新镜像
docker-compose pull && docker-compose up -d
```

### 进入容器
```bash
# 进入主应用容器
docker-compose exec sehuatang-crawler bash

# 查看容器日志
docker-compose logs sehuatang-crawler
```

## 🔧 故障排除

### 常见问题

#### 1. 端口被占用
```bash
# 检查端口占用
netstat -an | grep 8000

# 修改端口（在 docker-compose.yml 中）
ports:
  - "8080:8000"  # 改为 8080 端口
```

#### 2. Chrome 启动失败
```bash
# 查看容器日志
docker-compose logs sehuatang-crawler

# 检查 Chrome 安装
docker-compose exec sehuatang-crawler google-chrome --version
```

#### 3. 内存不足
```bash
# 增加 Docker 内存限制
# 在 Docker Desktop 设置中增加内存限制到 4GB 或更多
```

#### 4. 网络问题
```bash
# 检查网络连接
docker-compose exec sehuatang-crawler curl -I http://sehuatang.org

# 配置代理（在 docker-compose.yml 中）
environment:
  - HTTP_PROXY=http://your-proxy:port
  - HTTPS_PROXY=http://your-proxy:port
```

### 日志查看

```bash
# 查看所有服务日志
docker-compose logs

# 查看特定服务日志
docker-compose logs sehuatang-crawler

# 实时查看日志
docker-compose logs -f sehuatang-crawler

# 查看最近100行日志
docker-compose logs --tail=100 sehuatang-crawler
```

## 🗂️ 目录结构

```
sehuatang-crawler-main/
├── data/                    # 数据持久化目录
├── logs/                    # 日志目录
├── frontend/                # 前端代码
├── routes/                  # API路由
├── models_*.py             # 数据模型
├── *.py                    # 核心模块
├── Dockerfile              # Docker镜像配置
├── docker-compose.yml      # Docker编排配置
├── nginx.conf              # Nginx配置
├── requirements.txt        # Python依赖
├── build-and-run.sh        # Linux/Mac启动脚本
├── build-and-run.bat       # Windows启动脚本
└── README_DOCKER.md        # 本文档
```

## 🔒 安全建议

1. **生产环境部署**
   - 修改默认端口
   - 配置 HTTPS
   - 设置防火墙规则
   - 定期更新镜像

2. **数据备份**
   ```bash
   # 备份数据库
   docker-compose exec sehuatang-crawler cp /app/data/*.db /app/backup/
   
   # 备份整个数据目录
   tar -czf backup-$(date +%Y%m%d).tar.gz data/
   ```

3. **监控告警**
   - 配置健康检查
   - 设置日志监控
   - 配置资源使用告警

## 📞 技术支持

如果遇到问题，请：

1. 查看容器日志：`docker-compose logs`
2. 检查系统资源使用情况
3. 确认网络连接正常
4. 查看本文档的故障排除部分

## 🔄 更新升级

```bash
# 1. 停止服务
docker-compose down

# 2. 拉取最新代码
git pull

# 3. 重新构建镜像
docker-compose build --no-cache

# 4. 启动服务
docker-compose up -d

# 5. 检查状态
docker-compose ps
```

