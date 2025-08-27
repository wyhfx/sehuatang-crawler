# Sehuatang 爬虫系统

一个强大的磁力链接管理和元数据获取工具，支持从 Sehuatang 帖子中智能提取信息，并通过多数据源进行元数据补充和中文翻译。

## 🚀 功能特性

- **🎯 智能解析**：自动从 Sehuatang 帖子中提取番号、标题、容量、磁力链接等信息
- **🌐 多源数据**：支持 MetaTube、TPDB 等多种数据源，自动获取影片元数据
- **🔤 智能翻译**：自动将日文标题、标签翻译为中文，提升用户体验
- **🔗 磁力管理**：支持磁力链接的批量管理、搜索和导出
- **⚙️ 灵活配置**：支持代理设置、数据源选择等高级配置
- **📊 数据统计**：提供详细的统计信息和数据分析
- **🎨 现代化UI**：基于 React + Ant Design 的现代化用户界面

## 🏗️ 系统架构

```
sehuatang-crawler/
├── backend/                 # 后端服务
│   ├── enrichment/         # 数据源集成
│   ├── routes/            # API路由
│   ├── models/            # 数据模型
│   ├── utils/             # 工具函数
│   └── main.py            # 主应用入口
├── frontend/              # 前端应用
│   ├── src/              # 源代码
│   ├── public/           # 静态资源
│   └── package.json      # 依赖配置
├── docs/                 # 文档
└── README.md            # 项目说明
```

## 🛠️ 技术栈

### 后端
- **FastAPI** - 现代、快速的 Web 框架
- **SQLAlchemy** - ORM 数据库操作
- **SQLite** - 轻量级数据库
- **BeautifulSoup4** - HTML 解析
- **Requests** - HTTP 请求库
- **Pydantic** - 数据验证

### 前端
- **React 18** - 用户界面库
- **TypeScript** - 类型安全的 JavaScript
- **Ant Design** - 企业级 UI 组件库
- **React Router** - 路由管理
- **Day.js** - 日期处理库

## 📦 快速开始

### 环境要求

- Python 3.8+
- Node.js 16+
- npm 8+

### 1. 克隆项目

```bash
git clone https://github.com/your-username/sehuatang-crawler.git
cd sehuatang-crawler
```

### 2. 后端设置

```bash
# 安装 Python 依赖
pip install -r requirements.txt

# 设置环境变量
export METATUBE_URL="http://192.168.31.102:8080"
export METATUBE_PROVIDER="JavBus"
export METATUBE_FALLBACK="true"

# 可选：设置翻译服务
export TRANS_PROVIDER="baidu"
export BAIDU_APPID="your_appid"
export BAIDU_KEY="your_key"

# 可选：设置代理
export HTTP_PROXY="http://192.168.31.85:7891"
export HTTPS_PROXY="http://192.168.31.85:7891"
export NO_PROXY="localhost,127.0.0.1,192.168.31.102"
```

### 3. 启动后端服务

```bash
python main.py
```

后端服务将在 http://localhost:8000 启动，API 文档在 http://localhost:8000/docs

### 4. 前端设置

```bash
cd frontend

# 安装依赖
npm install

# 启动开发服务器
npm start
```

前端应用将在 http://localhost:3000 启动

### 5. 构建生产版本

```bash
# 构建前端
cd frontend
npm run build

# 启动生产服务器
cd ..
python main.py
```

## 📖 使用指南

### 1. 系统设置

访问 http://localhost:3000/settings/general 配置：

- **数据源设置**：MetaTube URL、Provider、Fallback
- **翻译设置**：翻译服务提供商和密钥
- **代理设置**：HTTP/SOCKS5 代理配置

### 2. 磁力链接管理

访问 http://localhost:3000/magnets 进行：

- **批量导入**：解析 Sehuatang 帖子 HTML
- **搜索过滤**：按番号、标题、女优搜索
- **数据导出**：批量导出磁力链接
- **图片预览**：查看影片截图

### 3. API 使用

#### 解析 Sehuatang 帖子

```bash
curl -X POST "http://localhost:8000/api/magnets/parse-sehuatang" \
  -H "Content-Type: application/json" \
  -d '{
    "html": "<html>...</html>",
    "source_url": "https://example.com/post"
  }'
```

#### 搜索磁力链接

```bash
curl "http://localhost:8000/api/magnets/search/START-398"
```

#### 获取系统设置

```bash
curl "http://localhost:8000/api/settings"
```

## 🔧 配置说明

### 环境变量

| 变量名 | 说明 | 默认值 |
|--------|------|--------|
| `METATUBE_URL` | MetaTube 服务地址 | `http://localhost:8080` |
| `METATUBE_PROVIDER` | 数据源提供商 | 空 |
| `METATUBE_FALLBACK` | 是否启用回退 | `true` |
| `TRANS_PROVIDER` | 翻译服务提供商 | 空 |
| `BAIDU_APPID` | 百度翻译 AppID | 空 |
| `BAIDU_KEY` | 百度翻译密钥 | 空 |
| `HTTP_PROXY` | HTTP 代理地址 | 空 |
| `HTTPS_PROXY` | HTTPS 代理地址 | 空 |
| `NO_PROXY` | 不使用代理的地址 | 空 |

### 数据库

系统使用 SQLite 数据库，数据文件位于 `sehuatang.db`：

- `magnet_links_v2` - 磁力链接数据
- `settings` - 系统设置

## 🚀 部署指南

### Docker 部署

```dockerfile
FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["python", "main.py"]
```

### Nginx 配置

```nginx
server {
    listen 80;
    server_name your-domain.com;
    
    # 静态文件
    location / {
        root /path/to/frontend/build;
        try_files $uri $uri/ /index.html;
    }
    
    # API 代理
    location /api/ {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

## 📊 性能优化

### 数据库优化

- 为常用字段创建索引
- 定期清理过期数据
- 使用连接池管理数据库连接

### 缓存策略

- 设置管理器使用内存缓存
- 翻译结果缓存
- 图片资源缓存

### 并发处理

- 异步处理大量数据
- 批量操作优化
- 连接池管理

## 🔍 故障排除

### 常见问题

1. **MetaTube 连接失败**
   - 检查 MetaTube 服务是否正常运行
   - 确认网络连接和代理设置
   - 查看日志获取详细错误信息

2. **翻译服务异常**
   - 验证翻译服务密钥是否正确
   - 检查网络连接
   - 确认翻译服务配额

3. **数据库错误**
   - 检查数据库文件权限
   - 确认磁盘空间充足
   - 查看数据库日志

### 日志查看

```bash
# 查看应用日志
tail -f logs/app.log

# 查看错误日志
tail -f logs/error.log
```

## 🤝 贡献指南

1. Fork 项目
2. 创建功能分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 创建 Pull Request

## 📄 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情。

## 🙏 致谢

- [MetaTube](https://github.com/javtube/javtube) - 元数据服务
- [Ant Design](https://ant.design/) - UI 组件库
- [FastAPI](https://fastapi.tiangolo.com/) - Web 框架

## 📞 联系方式

- 项目主页：https://github.com/your-username/sehuatang-crawler
- 问题反馈：https://github.com/your-username/sehuatang-crawler/issues
- 邮箱：your-email@example.com

---

⭐ 如果这个项目对你有帮助，请给它一个星标！

