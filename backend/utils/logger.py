"""
增强的日志配置模块
提供结构化日志、彩色输出和文件轮转
"""
import logging
import logging.handlers
import sys
from pathlib import Path
from datetime import datetime
from typing import Optional


class ColoredFormatter(logging.Formatter):
    """彩色日志格式化器(仅在终端输出时使用)"""

    # ANSI颜色代码
    COLORS = {
        'DEBUG': '\033[36m',     # 青色
        'INFO': '\033[32m',      # 绿色
        'WARNING': '\033[33m',   # 黄色
        'ERROR': '\033[31m',     # 红色
        'CRITICAL': '\033[35m',  # 紫色
        'RESET': '\033[0m'       # 重置
    }

    def format(self, record):
        """格式化日志记录"""
        # 添加颜色
        levelname = record.levelname
        if levelname in self.COLORS:
            record.levelname = f"{self.COLORS[levelname]}{levelname}{self.COLORS['RESET']}"

        # 调用父类方法
        result = super().format(record)

        return result


class StructuredFormatter(logging.Formatter):
    """结构化日志格式化器"""

    def format(self, record):
        """
        格式化为结构化日志
        输出格式: timestamp | level | module | message | extra_fields
        """
        timestamp = datetime.fromtimestamp(record.created).strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]
        level = record.levelname.ljust(8)
        module = f"{record.name}:{record.funcName}:{record.lineno}"

        # 基础信息
        result = f"{timestamp} | {level} | {module}"

        # 添加消息
        if record.msg:
            result += f" | {record.getMessage()}"

        # 添加额外字段
        extra_fields = {}
        for key, value in record.__dict__.items():
            if key not in ['name', 'msg', 'args', 'created', 'filename', 'funcName',
                           'levelname', 'levelno', 'lineno', 'module', 'msecs',
                           'pathname', 'process', 'processName', 'relativeCreated',
                           'thread', 'threadName', 'exc_info', 'exc_text', 'stack_info']:
                extra_fields[key] = value

        if extra_fields:
            result += f" | extra={extra_fields}"

        # 添加异常信息
        if record.exc_info:
            result += f"\n{self.formatException(record.exc_info)}"

        return result


def setup_logging(
    log_level: str = "INFO",
    log_file: Optional[str] = None,
    enable_color: bool = True,
    enable_file_rotation: bool = True,
    max_bytes: int = 10 * 1024 * 1024,  # 10MB
    backup_count: int = 5
) -> logging.Logger:
    """
    配置应用程序日志系统

    Args:
        log_level: 日志级别 (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: 日志文件路径,如果为None则只输出到控制台
        enable_color: 是否启用彩色输出(仅控制台)
        enable_file_rotation: 是否启用日志文件轮转
        max_bytes: 单个日志文件最大字节数
        backup_count: 保留的备份文件数量

    Returns:
        配置好的logger对象
    """
    # 获取根logger
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, log_level.upper()))

    # 清除现有handlers
    root_logger.handlers.clear()

    # 控制台handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(getattr(logging, log_level.upper()))

    if enable_color and sys.stdout.isatty():
        # 终端环境使用彩色输出
        console_formatter = ColoredFormatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
    else:
        # 非终端环境使用结构化格式
        console_formatter = StructuredFormatter()

    console_handler.setFormatter(console_formatter)
    root_logger.addHandler(console_handler)

    # 文件handler(如果指定了日志文件)
    if log_file:
        # 确保日志目录存在
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)

        if enable_file_rotation:
            # 使用轮转文件handler
            file_handler = logging.handlers.RotatingFileHandler(
                log_file,
                maxBytes=max_bytes,
                backupCount=backup_count,
                encoding='utf-8'
            )
        else:
            # 使用普通文件handler
            file_handler = logging.FileHandler(log_file, encoding='utf-8')

        file_handler.setLevel(getattr(logging, log_level.upper()))

        # 文件使用结构化格式
        file_formatter = StructuredFormatter()
        file_handler.setFormatter(file_formatter)
        root_logger.addHandler(file_handler)

    return root_logger


class RequestLogger:
    """请求日志辅助类"""

    @staticmethod
    def log_api_call(logger: logging.Logger, endpoint: str, duration_ms: float, status_code: int = 200, **kwargs):
        """
        记录API调用

        Args:
            logger: logger对象
            endpoint: API端点
            duration_ms: 耗时(毫秒)
            status_code: HTTP状态码
            **kwargs: 其他信息
        """
        extra_info = {
            'endpoint': endpoint,
            'duration_ms': f"{duration_ms:.2f}",
            'status_code': status_code,
            **kwargs
        }

        if status_code >= 500:
            logger.error(f"API调用失败: {endpoint}", extra=extra_info)
        elif status_code >= 400:
            logger.warning(f"API调用错误: {endpoint}", extra=extra_info)
        else:
            logger.info(f"API调用成功: {endpoint}", extra=extra_info)

    @staticmethod
    def log_database_query(logger: logging.Logger, query: str, duration_ms: float, rows: int = 0):
        """
        记录数据库查询

        Args:
            logger: logger对象
            query: SQL查询语句
            duration_ms: 耗时(毫秒)
            rows: 受影响行数
        """
        logger.debug(
            f"数据库查询完成",
            extra={
                'query': query[:100] + '...' if len(query) > 100 else query,
                'duration_ms': f"{duration_ms:.2f}",
                'rows': rows
            }
        )

    @staticmethod
    def log_cache_operation(logger: logging.Logger, operation: str, key: str, hit: bool = True):
        """
        记录缓存操作

        Args:
            logger: logger对象
            operation: 操作类型 (get/set/delete)
            key: 缓存键
            hit: 是否命中(仅对get操作有效)
        """
        if operation == 'get':
            if hit:
                logger.debug(f"缓存命中: {key}")
            else:
                logger.debug(f"缓存未命中: {key}")
        elif operation == 'set':
            logger.debug(f"缓存设置: {key}")
        elif operation == 'delete':
            logger.debug(f"缓存删除: {key}")


# 默认配置
def get_default_logger(name: str = __name__) -> logging.Logger:
    """
    获取默认配置的logger

    Args:
        name: logger名称

    Returns:
        logger对象
    """
    return logging.getLogger(name)
