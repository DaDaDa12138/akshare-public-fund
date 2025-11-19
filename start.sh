#!/bin/bash

echo "======================================="
echo "  AkShare 公募基金数据平台"
echo "======================================="
echo ""

echo "正在启动服务..."
echo ""

# 构建并启动服务
docker compose up -d --build

echo ""
echo "======================================="
echo "  服务启动完成！"
echo "======================================="
echo ""
echo "访问地址："
echo "  - 前端应用: http://localhost:9095"
echo "  - 后端 API: http://localhost:8080/docs"
echo ""
echo "查看服务状态:"
echo "  docker compose ps"
echo ""
echo "查看服务日志:"
echo "  docker compose logs -f"
echo ""
echo "停止服务:"
echo "  docker compose down"
echo ""
echo "======================================="
