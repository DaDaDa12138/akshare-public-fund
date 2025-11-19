# AkShare 公募基金 API 服务 v1.5.0
# 整合 AKTools + SQLite + 定时任务

FROM python:3.11-slim

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    curl \
    sqlite3 \
    && rm -rf /var/lib/apt/lists/*

# 设置工作目录
WORKDIR /app

# 复制依赖文件
COPY requirements.txt .

# 安装 Python 依赖
RUN pip install --no-cache-dir -r requirements.txt

# 复制应用代码
COPY . .

# 创建数据库目录（Volume 挂载点）
RUN mkdir -p /app/db

# 暴露端口
EXPOSE 8080

# 健康检查
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
  CMD curl -f http://localhost:8080/api/estimation_stats || exit 1

# 启动自定义主程序（整合 AKTools + 数据库 + 定时任务）
CMD ["python", "main.py"]
