"""
基金分红数据初始化脚本
用于首次启动时加载分红数据到数据库
"""
import sys
import os

# 添加父目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from db.scheduler import update_fund_dividend
import logging

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

if __name__ == "__main__":
    logger.info("========== 开始初始化基金分红数据 ==========")
    try:
        update_fund_dividend()
        logger.info("========== 分红数据初始化完成 ==========")
    except Exception as e:
        logger.error(f"========== 分红数据初始化失败: {e} ==========", exc_info=True)
        sys.exit(1)
