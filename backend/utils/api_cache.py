"""
统一API缓存装饰器模块
提供简单易用的内存缓存装饰器，支持灵活的TTL配置和缓存键生成
"""
import functools
import threading
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, Callable
import logging
import hashlib
import json

logger = logging.getLogger(__name__)


class APICache:
    """
    统一的API内存缓存类

    特性:
    - 线程安全
    - 自动过期清理
    - 支持自定义TTL
    - 支持自定义缓存键
    - 提供缓存统计信息
    """

    def __init__(self):
        """初始化缓存"""
        self.cache: Dict[str, Dict[str, Any]] = {}
        self.lock = threading.Lock()
        self.stats = {
            'hits': 0,
            'misses': 0,
            'sets': 0,
            'evictions': 0
        }

    def get(self, key: str) -> Optional[Any]:
        """
        获取缓存数据

        Args:
            key: 缓存键

        Returns:
            缓存的数据，如果不存在或已过期则返回None
        """
        with self.lock:
            if key in self.cache:
                entry = self.cache[key]
                if datetime.now() < entry['expires_at']:
                    self.stats['hits'] += 1
                    remaining = (entry['expires_at'] - datetime.now()).total_seconds()
                    logger.debug(f"[缓存命中] key={key[:50]}..., 剩余{remaining:.0f}秒")
                    return entry['data']
                else:
                    # 过期则删除
                    del self.cache[key]
                    self.stats['evictions'] += 1
                    logger.debug(f"[缓存过期] key={key[:50]}...")

            self.stats['misses'] += 1
            return None

    def set(self, key: str, data: Any, ttl_seconds: int):
        """
        设置缓存数据

        Args:
            key: 缓存键
            data: 要缓存的数据
            ttl_seconds: 过期时间（秒）
        """
        with self.lock:
            expires_at = datetime.now() + timedelta(seconds=ttl_seconds)
            self.cache[key] = {
                'data': data,
                'expires_at': expires_at,
                'created_at': datetime.now()
            }
            self.stats['sets'] += 1

            data_size = len(data) if isinstance(data, (list, dict)) else 'N/A'
            logger.debug(f"[缓存设置] key={key[:50]}..., 数据量={data_size}, TTL={ttl_seconds}秒")

    def clear(self):
        """清空所有缓存"""
        with self.lock:
            count = len(self.cache)
            self.cache.clear()
            self.stats['evictions'] += count
            logger.info(f"[缓存清空] 已清除 {count} 个缓存项")

    def get_stats(self) -> Dict[str, Any]:
        """
        获取缓存统计信息

        Returns:
            包含缓存统计的字典
        """
        with self.lock:
            total_requests = self.stats['hits'] + self.stats['misses']
            hit_rate = (self.stats['hits'] / total_requests * 100) if total_requests > 0 else 0

            return {
                'cache_size': len(self.cache),
                'hits': self.stats['hits'],
                'misses': self.stats['misses'],
                'sets': self.stats['sets'],
                'evictions': self.stats['evictions'],
                'hit_rate': f"{hit_rate:.2f}%",
                'total_requests': total_requests
            }

    def clear_expired(self):
        """
        清理所有过期的缓存项

        Returns:
            清理的项数
        """
        with self.lock:
            now = datetime.now()
            expired_keys = [
                key for key, entry in self.cache.items()
                if now >= entry['expires_at']
            ]

            for key in expired_keys:
                del self.cache[key]

            self.stats['evictions'] += len(expired_keys)

            if expired_keys:
                logger.info(f"[缓存清理] 已清除 {len(expired_keys)} 个过期项")

            return len(expired_keys)


# 全局缓存实例
api_cache = APICache()


def cache_response(ttl_seconds: int = 300, key_prefix: str = "", use_args: bool = True):
    """
    API响应缓存装饰器

    Args:
        ttl_seconds: 缓存过期时间（秒），默认5分钟
        key_prefix: 缓存键前缀，建议使用API端点路径
        use_args: 是否将函数参数包含在缓存键中，默认True

    Usage:
        @cache_response(ttl_seconds=600, key_prefix="/api/fund_info")
        async def get_fund_info(fund_code: str):
            # ... 实际的API逻辑
            return {"code": fund_code, "name": "基金名称"}

    Example:
        # 缓存10分钟，键包含fund_code参数
        @cache_response(ttl_seconds=600, key_prefix="/api/fund")
        async def fund_detail(fund_code: str):
            return await fetch_fund_data(fund_code)

        # 缓存30分钟，键不包含参数（适合静态数据）
        @cache_response(ttl_seconds=1800, key_prefix="/api/stats", use_args=False)
        async def get_stats():
            return await calculate_stats()
    """
    def decorator(func: Callable):
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            # 生成缓存键
            if use_args:
                # 将参数转换为字符串并生成哈希
                params_str = json.dumps({
                    'args': [str(arg) for arg in args],
                    'kwargs': {k: str(v) for k, v in kwargs.items()}
                }, sort_keys=True)
                params_hash = hashlib.md5(params_str.encode()).hexdigest()[:8]
                cache_key = f"{key_prefix}:{params_hash}"
            else:
                cache_key = key_prefix

            # 尝试从缓存获取
            cached_data = api_cache.get(cache_key)
            if cached_data is not None:
                return cached_data

            # 缓存未命中，执行实际函数
            result = await func(*args, **kwargs)

            # 缓存结果
            api_cache.set(cache_key, result, ttl_seconds)

            return result

        return wrapper
    return decorator


def get_cache_stats() -> Dict[str, Any]:
    """
    获取全局缓存统计信息

    Returns:
        缓存统计字典
    """
    return api_cache.get_stats()


def clear_cache():
    """清空所有缓存"""
    api_cache.clear()


def clear_expired_cache():
    """清理过期缓存"""
    return api_cache.clear_expired()
