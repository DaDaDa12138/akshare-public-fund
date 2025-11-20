# AkShare Public Fund - Docker Hub 快速部署指南

[![Docker Hub](https://img.shields.io/badge/Docker%20Hub-nick404-blue?logo=docker)](https://hub.docker.com/u/nick404)

本指南提供从 Docker Hub 快速部署 AkShare Public Fund 项目的完整步骤。

---

## 📦 Docker Hub 镜像信息

| 镜像 | 标签 | 大小 | 拉取命令 |
|------|------|------|----------|
| **后端** | `nick404/akshare-backend:latest` | 453MB | `docker pull nick404/akshare-backend:latest` |
| **后端** | `nick404/akshare-backend:v1.4.0` | 453MB | `docker pull nick404/akshare-backend:v1.4.0` |
| **前端** | `nick404/akshare-frontend:latest` | 55.6MB | `docker pull nick404/akshare-frontend:latest` |
| **前端** | `nick404/akshare-frontend:v1.4.0` | 55.6MB | `docker pull nick404/akshare-frontend:v1.4.0` |

**镜像地址**:
- 后端: https://hub.docker.com/r/nick404/akshare-backend
- 前端: https://hub.docker.com/r/nick404/akshare-frontend

---

## 🚀 方法一：一键快速部署（推荐）

### 前置要求
- Docker 20.10+
- Docker Compose 1.29+

### 步骤 1: 下载配置文件

```bash
# 下载 docker-compose.hub.yml
wget https://raw.githubusercontent.com/DaDaDa12138/akshare-public-fund/main/docker-compose.hub.yml

# 或者使用 curl
curl -O https://raw.githubusercontent.com/DaDaDa12138/akshare-public-fund/main/docker-compose.hub.yml
```

### 步骤 2: 创建数据目录

```bash
mkdir -p backend/db
```

### 步骤 3: 启动服务

```bash
# 使用指定的配置文件启动
docker compose -f docker-compose.hub.yml up -d

# 或者重命名文件后启动
mv docker-compose.hub.yml docker-compose.yml
docker compose up -d
```

### 步骤 4: 验证服务

```bash
# 查看容器状态
docker compose ps

# 查看日志
docker compose logs -f
```

### 步骤 5: 访问应用

- **前端界面**: http://localhost:9095
- **后端API文档**: http://localhost:8080/docs
- **ReDoc文档**: http://localhost:8080/redoc

---

## 🐳 方法二：手动拉取镜像部署

### 步骤 1: 拉取镜像

```bash
# 拉取最新版本
docker pull nick404/akshare-backend:latest
docker pull nick404/akshare-frontend:latest

# 或拉取指定版本
docker pull nick404/akshare-backend:v1.4.0
docker pull nick404/akshare-frontend:v1.4.0
```

### 步骤 2: 创建网络

```bash
docker network create akshare-network
```

### 步骤 3: 创建数据目录

```bash
mkdir -p $(pwd)/backend/db
```

### 步骤 4: 启动后端容器

```bash
docker run -d \
  --name akshare-backend \
  --network akshare-network \
  -p 8080:8080 \
  -v $(pwd)/backend/db:/app/db \
  -e TZ=Asia/Shanghai \
  --restart unless-stopped \
  nick404/akshare-backend:latest
```

### 步骤 5: 启动前端容器

```bash
docker run -d \
  --name akshare-frontend \
  --network akshare-network \
  -p 9095:80 \
  -e TZ=Asia/Shanghai \
  --restart unless-stopped \
  nick404/akshare-frontend:latest
```

### 步骤 6: 验证服务

```bash
# 检查容器状态
docker ps | grep akshare

# 测试后端API
curl http://localhost:8080/api/estimation_stats

# 测试前端
curl -I http://localhost:9095/
```

---

## 📝 方法三：创建配置文件部署

### 步骤 1: 创建 docker-compose.yml

在您的工作目录创建 `docker-compose.yml` 文件：

```yaml
services:
  # 后端服务
  backend:
    image: nick404/akshare-backend:latest
    container_name: akshare-backend
    ports:
      - "8080:8080"
    volumes:
      - ./backend/db:/app/db
    environment:
      - TZ=Asia/Shanghai
    restart: unless-stopped
    networks:
      - akshare-network
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8080/api/estimation_stats"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s

  # 前端服务
  frontend:
    image: nick404/akshare-frontend:latest
    container_name: akshare-frontend
    ports:
      - "9095:80"
    environment:
      - TZ=Asia/Shanghai
    depends_on:
      - backend
    restart: unless-stopped
    networks:
      - akshare-network
    healthcheck:
      test: ["CMD", "wget", "--quiet", "--tries=1", "--spider", "http://localhost/"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 10s

networks:
  akshare-network:
    driver: bridge
```

### 步骤 2: 创建数据目录

```bash
mkdir -p backend/db
```

### 步骤 3: 启动服务

```bash
docker compose up -d
```

---

## 🔧 自定义配置

### 修改端口

如果默认端口冲突，修改 `docker-compose.yml`:

```yaml
# 修改前端端口为 8095
frontend:
  ports:
    - "8095:80"

# 修改后端端口为 8090
backend:
  ports:
    - "8090:8080"
```

### 使用指定版本

```yaml
backend:
  image: nick404/akshare-backend:v1.4.0  # 使用指定版本

frontend:
  image: nick404/akshare-frontend:v1.4.0  # 使用指定版本
```

### 资源限制（生产环境）

```yaml
backend:
  deploy:
    resources:
      limits:
        cpus: '2.0'
        memory: 2G
      reservations:
        cpus: '1.0'
        memory: 1G
```

---

## 🛠️ 常用管理命令

### 查看状态

```bash
# 查看容器状态
docker compose ps

# 查看实时日志
docker compose logs -f

# 查看后端日志
docker compose logs -f backend

# 查看前端日志
docker compose logs -f frontend
```

### 服务控制

```bash
# 停止服务
docker compose stop

# 启动服务
docker compose start

# 重启服务
docker compose restart

# 停止并删除容器（数据不会丢失）
docker compose down

# 停止并删除容器和数据卷
docker compose down -v
```

### 更新镜像

```bash
# 拉取最新镜像
docker compose pull

# 重新创建容器
docker compose up -d --force-recreate

# 或者一步完成
docker compose pull && docker compose up -d --force-recreate
```

### 数据备份

```bash
# 备份数据库
cp backend/db/akshare.db backend/db/akshare.db.backup.$(date +%Y%m%d)

# 恢复数据库
cp backend/db/akshare.db.backup.20251120 backend/db/akshare.db
docker compose restart backend
```

---

## 🌐 生产环境部署建议

### 1. 使用反向代理

#### Nginx 配置示例

```nginx
server {
    listen 80;
    server_name your-domain.com;

    # 前端
    location / {
        proxy_pass http://localhost:9095;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # 后端API
    location /api {
        proxy_pass http://localhost:8080;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

### 2. 启用 HTTPS

```bash
# 使用 Certbot 获取免费 SSL 证书
certbot --nginx -d your-domain.com
```

### 3. 配置环境变量

创建 `.env` 文件：

```env
# 端口配置
BACKEND_PORT=8080
FRONTEND_PORT=9095

# 时区配置
TZ=Asia/Shanghai

# 资源限制
BACKEND_CPU_LIMIT=2.0
BACKEND_MEM_LIMIT=2G
```

在 `docker-compose.yml` 中引用：

```yaml
backend:
  ports:
    - "${BACKEND_PORT}:8080"
  environment:
    - TZ=${TZ}
```

### 4. 设置自动重启

```yaml
services:
  backend:
    restart: always  # 总是重启

  frontend:
    restart: unless-stopped  # 除非手动停止，否则总是重启
```

---

## 🧪 验证部署

### 后端API测试

```bash
# 测试健康检查
curl http://localhost:8080/api/estimation_stats

# 测试基金查询
curl "http://localhost:8080/api/fund_open_fund_info_em?symbol=000001"

# 测试基金排行
curl "http://localhost:8080/api/fund_open_fund_rank_em"
```

### 前端访问测试

在浏览器中访问以下页面：
- 首页：http://localhost:9095/
- 基金详情：http://localhost:9095/detail/000001
- 基金排行榜：http://localhost:9095/ranking
- 另类数据：http://localhost:9095/alternative
- API文档：http://localhost:8080/docs

---

## 🐛 故障排查

### 镜像拉取失败

```bash
# 如果拉取速度慢，配置镜像加速器
# 编辑 /etc/docker/daemon.json
{
  "registry-mirrors": [
    "https://mirror.ccs.tencentyun.com",
    "https://docker.mirrors.ustc.edu.cn"
  ]
}

# 重启 Docker
sudo systemctl restart docker

# 重新拉取
docker compose pull
```

### 容器无法启动

```bash
# 查看详细日志
docker compose logs backend
docker compose logs frontend

# 检查端口占用
netstat -tuln | grep -E '8080|9095'

# 清理并重新创建
docker compose down
docker compose up -d
```

### 数据库问题

```bash
# 进入容器检查
docker exec -it akshare-backend bash

# 查看数据库文件
ls -lh /app/db/

# 测试数据库连接
sqlite3 /app/db/akshare.db ".tables"

# 如果数据库损坏，删除后重启容器会自动创建
rm backend/db/akshare.db
docker compose restart backend
```

### 前端无法访问后端API

检查网络连接：

```bash
# 检查容器网络
docker network inspect akshare-network

# 测试容器间通信
docker exec akshare-frontend ping -c 3 backend

# 检查后端健康状态
docker exec akshare-backend curl http://localhost:8080/api/estimation_stats
```

---

## 📊 性能监控

### 查看资源使用

```bash
# 实时监控
docker stats

# 查看特定容器
docker stats akshare-backend akshare-frontend
```

### 日志管理

```bash
# 限制日志大小（在 docker-compose.yml 中配置）
services:
  backend:
    logging:
      driver: "json-file"
      options:
        max-size: "10m"
        max-file: "3"
```

---

## 📚 功能特性

### 基金数据分析
- ✅ 22,958+ 只公募基金数据
- ✅ 实时净值估算
- ✅ 历史净值走势图
- ✅ 收益率统计（1月/3月/6月/1年/3年/成立来）
- ✅ 季度持仓明细（股票/债券/现金）
- ✅ 历史分红记录
- ✅ 风险指标（最大回撤、波动率、夏普比率）

### 市场数据
- ✅ 基金排行榜
- ✅ 基金公司排名
- ✅ 基金对比分析
- ✅ 货币基金专区
- ✅ 场内基金行情（ETF/LOF）

### 另类数据
- ✅ 汽车销量（乘联会数据）
- ✅ 空气质量（全国城市监测）
- ✅ 电影票房（实时/日/周/月/年榜单）
- ✅ 财富排行（财富500强、福布斯、胡润）

### 技术特性
- ✅ 多层缓存优化（内存 + SQLite）
- ✅ 定时任务自动更新
- ✅ Docker 一键部署
- ✅ RESTful API
- ✅ Swagger 文档
- ✅ 健康检查
- ✅ 数据持久化

---

## 🔗 相关链接

- **GitHub 仓库**: https://github.com/DaDaDa12138/akshare-public-fund
- **Docker Hub - 后端**: https://hub.docker.com/r/nick404/akshare-backend
- **Docker Hub - 前端**: https://hub.docker.com/r/nick404/akshare-frontend
- **AkShare 官网**: https://akshare.akfamily.xyz/

---

## 📄 许可证

MIT License

---

## 🙏 致谢

- [AkShare](https://github.com/akfamily/akshare) - 金融数据接口库
- [FastAPI](https://fastapi.tiangolo.com/) - Python Web 框架
- [Vue.js](https://vuejs.org/) - 前端框架
- [Docker](https://www.docker.com/) - 容器化平台

---

## 📧 支持与反馈

- **GitHub Issues**: https://github.com/DaDaDa12138/akshare-public-fund/issues
- **Pull Requests**: 欢迎贡献代码

---

<div align="center">

**⭐ 如果这个项目对你有帮助，请给一个 Star！⭐**

Made with ❤️ by AkShare Community

</div>
