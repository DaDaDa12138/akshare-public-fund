# 📦 部署指南

## 快速开始

### 方式一：使用启动脚本（推荐）

```bash
./start.sh
```

### 方式二：手动部署

```bash
# 1. 构建并启动所有服务
docker compose up -d --build

# 2. 查看服务状态
docker compose ps

# 3. 查看日志
docker compose logs -f
```

## ⏱️ 首次部署预计时间

- **后端构建**: ~30秒（下载 AKTools 镜像）
- **前端构建**: ~3-5分钟（npm install + build）
- **总计**: ~5-6分钟

## 🔍 检查部署状态

### 1. 检查容器状态

```bash
docker compose ps
```

期望输出：
```
NAME                  STATUS              PORTS
akshare-backend       Up (healthy)        0.0.0.0:8080->8080/tcp
akshare-frontend      Up (healthy)        0.0.0.0:80->80/tcp
```

### 2. 检查后端 API

```bash
curl http://localhost:8080/api/public/fund_name_em | head -c 200
```

期望看到 JSON 格式的基金数据。

### 3. 检查前端

在浏览器访问: http://localhost:9095

应该看到 "AkShare 基金数据平台" 主页。

## 🐛 常见问题排查

### 问题 1: 前端构建失败

**症状**:
```bash
docker compose ps
# frontend 容器状态为 Exited
```

**解决方案**:

```bash
# 查看详细日志
docker compose logs frontend

# 重新构建
docker compose build frontend --no-cache
docker compose up -d frontend
```

### 问题 2: 端口被占用

**症状**:
```
Error: bind: address already in use
```

**解决方案**:

修改 `docker-compose.yml` 中的端口映射：

```yaml
frontend:
  ports:
    - "3000:80"  # 改为 3000 端口

backend:
  ports:
    - "8081:8080"  # 改为 8081 端口
```

### 问题 3: 前端无法连接后端

**症状**:
前端页面显示，但数据加载失败。

**解决方案**:

```bash
# 1. 确认两个服务都在运行
docker compose ps

# 2. 检查网络连接
docker network inspect akshare_akshare-network

# 3. 测试后端API
curl http://localhost:8080/api/public/fund_name_em

# 4. 重启服务
docker compose restart
```

### 问题 4: 内存不足

**症状**:
```
Error: Cannot allocate memory
```

**解决方案**:

调整 Docker Desktop 内存限制：
- macOS/Windows: Docker Desktop → Settings → Resources → Memory (至少 4GB)
- Linux: 修改 `/etc/docker/daemon.json`

## 📊 监控和日志

### 实时查看日志

```bash
# 所有服务
docker compose logs -f

# 仅后端
docker compose logs -f backend

# 仅前端
docker compose logs -f frontend

# 最近100行
docker compose logs --tail=100
```

### 查看资源使用

```bash
docker stats akshare-backend akshare-frontend
```

## 🔄 更新和重启

### 更新代码后重新部署

```bash
# 停止服务
docker compose down

# 重新构建并启动
docker compose up -d --build
```

### 仅重启某个服务

```bash
# 重启前端
docker compose restart frontend

# 重启后端
docker compose restart backend
```

### 清理并重新部署

```bash
# 停止并删除所有容器、网络、镜像
docker compose down --rmi all

# 重新构建
docker compose up -d --build
```

## 🌐 生产环境部署建议

### 1. 使用环境变量

创建 `.env` 文件：

```env
# 前端端口
FRONTEND_PORT=80

# 后端端口
BACKEND_PORT=8080

# 环境
NODE_ENV=production
```

### 2. 启用 HTTPS

使用 Nginx 反向代理 + Let's Encrypt SSL 证书。

### 3. 添加访问认证

在 Nginx 配置中添加 Basic Auth：

```nginx
location / {
    auth_basic "Restricted Access";
    auth_basic_user_file /etc/nginx/.htpasswd;
    ...
}
```

### 4. 限流保护

```nginx
limit_req_zone $binary_remote_addr zone=api:10m rate=10r/s;

location /api/ {
    limit_req zone=api burst=20;
    ...
}
```

### 5. 监控告警

使用 Prometheus + Grafana 监控容器状态。

## 📋 健康检查

服务已配置健康检查：

- **后端**: 每30秒检查 `/docs` 接口
- **前端**: 每30秒检查首页

查看健康状态：

```bash
docker compose ps
# 健康的容器显示 "Up (healthy)"
```

## 🛑 完全停止和清理

```bash
# 停止所有服务
docker compose down

# 停止并删除镜像
docker compose down --rmi all

# 停止并删除所有数据（包括卷）
docker compose down -v
```

## ✅ 部署检查清单

- [ ] Docker 和 Docker Compose 已安装
- [ ] 端口 80 和 8080 未被占用
- [ ] Docker 至少分配 4GB 内存
- [ ] 网络连接正常（用于下载镜像和 npm 包）
- [ ] 所有配置文件已正确放置
- [ ] 执行 `docker compose up -d --build`
- [ ] 等待 5-6 分钟完成构建
- [ ] 访问 http://localhost:9095 验证前端
- [ ] 访问 http://localhost:8080/docs 验证后端
- [ ] 测试基金搜索功能
- [ ] 测试净值走势图表
- [ ] 测试基金排行榜

---

如有问题，请查看日志: `docker compose logs -f`
