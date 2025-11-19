"""
缓存助手模块 - 实现智能缓存读写逻辑
"""
import json
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any
from .database import get_db, execute_query, execute_update


class CacheHelper:
    """缓存助手类 - 提供统一的缓存操作接口"""

    # 缓存TTL配置 (分钟)
    TTL_CONFIG = {
        'fund_basic_info': 30,      # 基金基本信息: 30分钟
        'fund_daily_nav': 5,         # 实时净值: 5分钟
        'fund_ranking': 10,          # 排行榜: 10分钟
        'fund_value_estimation': 5,  # 实时估值: 5分钟
        'fund_dividend': 1440,       # 分红记录: 24小时
        'fund_rating': 60,           # 基金评级: 1小时
    }

    @staticmethod
    def is_cache_valid(update_time_str: str, ttl_minutes: int) -> bool:
        """
        检查缓存是否有效

        Args:
            update_time_str: 更新时间字符串
            ttl_minutes: TTL时长(分钟)

        Returns:
            bool: 缓存是否有效
        """
        try:
            update_time = datetime.strptime(update_time_str, '%Y-%m-%d %H:%M:%S')
            expiry_time = update_time + timedelta(minutes=ttl_minutes)
            return datetime.now() < expiry_time
        except Exception:
            return False

    @classmethod
    def get_fund_basic_info(cls, fund_code: str) -> Optional[Dict[str, Any]]:
        """
        获取基金基本信息缓存

        Args:
            fund_code: 基金代码

        Returns:
            Dict or None: 基金信息字典,缓存过期返回None
        """
        query = '''
            SELECT * FROM fund_basic_info_cache
            WHERE 基金代码 = ?
        '''
        results = execute_query(query, (fund_code,))

        if results:
            data = results[0]
            if cls.is_cache_valid(data['更新时间'], cls.TTL_CONFIG['fund_basic_info']):
                return data

        return None

    @classmethod
    def set_fund_basic_info(cls, data: Dict[str, Any]) -> bool:
        """
        设置基金基本信息缓存

        Args:
            data: 基金信息字典

        Returns:
            bool: 是否成功
        """
        try:
            query = '''
                INSERT OR REPLACE INTO fund_basic_info_cache
                (基金代码, 基金简称, 基金类型, 基金公司, 基金经理,
                 成立日期, 最新规模, 托管银行, 业绩比较基准, 投资目标, 投资策略, 更新时间)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
            '''
            params = (
                data.get('基金代码'),
                data.get('基金简称'),
                data.get('基金类型'),
                data.get('基金公司'),
                data.get('基金经理'),
                data.get('成立日期'),
                data.get('最新规模'),
                data.get('托管银行'),
                data.get('业绩比较基准'),
                data.get('投资目标'),
                data.get('投资策略')
            )
            execute_update(query, params)
            return True
        except Exception as e:
            print(f"[缓存] 基金基本信息缓存失败: {e}")
            return False

    @classmethod
    def get_fund_daily_nav(cls, fund_code: str) -> Optional[Dict[str, Any]]:
        """
        获取实时净值缓存

        Args:
            fund_code: 基金代码

        Returns:
            Dict or None: 净值数据,缓存过期返回None
        """
        query = '''
            SELECT * FROM fund_daily_nav_cache
            WHERE 基金代码 = ?
        '''
        results = execute_query(query, (fund_code,))

        if results:
            data = results[0]
            if cls.is_cache_valid(data['更新时间'], cls.TTL_CONFIG['fund_daily_nav']):
                return data

        return None

    @classmethod
    def set_fund_daily_nav(cls, data: Dict[str, Any]) -> bool:
        """
        设置实时净值缓存

        Args:
            data: 净值数据字典

        Returns:
            bool: 是否成功
        """
        try:
            query = '''
                INSERT OR REPLACE INTO fund_daily_nav_cache
                (基金代码, 基金简称, 净值日期, 单位净值, 累计净值,
                 日增长率, 日增长值, 申购状态, 赎回状态, 手续费, 更新时间)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
            '''
            params = (
                data.get('基金代码'),
                data.get('基金简称'),
                data.get('净值日期'),
                data.get('单位净值'),
                data.get('累计净值'),
                data.get('日增长率'),
                data.get('日增长值'),
                data.get('申购状态'),
                data.get('赎回状态'),
                data.get('手续费')
            )
            execute_update(query, params)
            return True
        except Exception as e:
            print(f"[缓存] 实时净值缓存失败: {e}")
            return False

    @classmethod
    def get_fund_ranking(cls, fund_type: str) -> Optional[List[Dict[str, Any]]]:
        """
        获取排行榜缓存

        Args:
            fund_type: 基金类型(全部/股票型/混合型/债券型/指数型/FOF/QDII)

        Returns:
            List[Dict] or None: 排行数据列表,缓存过期返回None
        """
        query = '''
            SELECT * FROM fund_ranking_cache
            WHERE 基金类型 = ?
        '''
        results = execute_query(query, (fund_type,))

        if results:
            data = results[0]
            if cls.is_cache_valid(data['更新时间'], cls.TTL_CONFIG['fund_ranking']):
                try:
                    return json.loads(data['排行数据'])
                except Exception:
                    return None

        return None

    @classmethod
    def set_fund_ranking(cls, fund_type: str, ranking_data: List[Dict[str, Any]]) -> bool:
        """
        设置排行榜缓存

        Args:
            fund_type: 基金类型
            ranking_data: 排行数据列表

        Returns:
            bool: 是否成功
        """
        try:
            query = '''
                INSERT OR REPLACE INTO fund_ranking_cache
                (基金类型, 排行数据, 总记录数, 更新时间)
                VALUES (?, ?, ?, CURRENT_TIMESTAMP)
            '''
            params = (
                fund_type,
                json.dumps(ranking_data, ensure_ascii=False),
                len(ranking_data)
            )
            execute_update(query, params)
            return True
        except Exception as e:
            print(f"[缓存] 排行榜缓存失败: {e}")
            return False

    @classmethod
    def clear_expired_cache(cls):
        """
        清理所有过期的缓存数据
        """
        try:
            conn = get_db()
            cursor = conn.cursor()

            # 清理基金基本信息缓存
            cursor.execute(f'''
                DELETE FROM fund_basic_info_cache
                WHERE datetime(更新时间) < datetime('now', '-{cls.TTL_CONFIG["fund_basic_info"]} minutes')
            ''')

            # 清理实时净值缓存
            cursor.execute(f'''
                DELETE FROM fund_daily_nav_cache
                WHERE datetime(更新时间) < datetime('now', '-{cls.TTL_CONFIG["fund_daily_nav"]} minutes')
            ''')

            # 清理排行榜缓存
            cursor.execute(f'''
                DELETE FROM fund_ranking_cache
                WHERE datetime(更新时间) < datetime('now', '-{cls.TTL_CONFIG["fund_ranking"]} minutes')
            ''')

            conn.commit()
            print("[缓存] 过期缓存清理完成")
            return True
        except Exception as e:
            print(f"[缓存] 清理失败: {e}")
            return False


# 创建全局实例
cache = CacheHelper()
