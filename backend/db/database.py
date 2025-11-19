"""
SQLite 数据库管理模块
"""
import sqlite3
import os
from contextlib import contextmanager
from typing import Optional
import threading

# 数据库文件路径
DB_DIR = os.path.join(os.path.dirname(__file__))
DB_PATH = os.path.join(DB_DIR, 'akshare.db')

# 线程本地存储（每个线程独立的数据库连接）
_thread_local = threading.local()


def get_db() -> sqlite3.Connection:
    """
    获取当前线程的数据库连接（线程安全）
    """
    if not hasattr(_thread_local, 'connection'):
        _thread_local.connection = sqlite3.connect(
            DB_PATH,
            check_same_thread=False,
            timeout=30.0
        )
        # 返回字典格式的行
        _thread_local.connection.row_factory = sqlite3.Row
        # 启用 WAL 模式（提升并发性能）
        _thread_local.connection.execute('PRAGMA journal_mode=WAL')
        # 启用外键约束
        _thread_local.connection.execute('PRAGMA foreign_keys=ON')

    return _thread_local.connection


def close_db():
    """
    关闭当前线程的数据库连接
    """
    if hasattr(_thread_local, 'connection'):
        _thread_local.connection.close()
        delattr(_thread_local, 'connection')


@contextmanager
def get_db_context():
    """
    数据库上下文管理器（自动提交/回滚）
    """
    conn = get_db()
    try:
        yield conn
        conn.commit()
    except Exception as e:
        conn.rollback()
        raise e


def init_db():
    """
    初始化数据库表结构
    """
    conn = get_db()
    cursor = conn.cursor()

    # 创建实时估值表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS fund_value_estimation (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            基金代码 TEXT NOT NULL UNIQUE,
            基金名称 TEXT,
            估算时间 TEXT,
            估算值 TEXT,
            估算增长率 TEXT,
            单位净值 TEXT,
            日增长率 TEXT,
            估算偏差 TEXT,
            更新时间 TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # 创建索引
    cursor.execute('''
        CREATE INDEX IF NOT EXISTS idx_fund_code
        ON fund_value_estimation(基金代码)
    ''')

    # 创建分红记录表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS fund_dividend (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            基金代码 TEXT NOT NULL,
            基金简称 TEXT,
            权益登记日 TEXT,
            除息日期 TEXT,
            分红 REAL,
            分红发放日 TEXT,
            更新时间 TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(基金代码, 除息日期)
        )
    ''')

    cursor.execute('''
        CREATE INDEX IF NOT EXISTS idx_fund_code_div
        ON fund_dividend(基金代码)
    ''')

    cursor.execute('''
        CREATE INDEX IF NOT EXISTS idx_ex_dividend_date
        ON fund_dividend(除息日期)
    ''')

    # 创建基金评级表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS fund_rating_all (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            代码 TEXT NOT NULL UNIQUE,
            简称 TEXT,
            基金经理 TEXT,
            基金公司 TEXT,
            "5星评级家数" INTEGER,
            上海证券 REAL,
            招商证券 REAL,
            济安金信 REAL,
            晨星评级 REAL,
            手续费 REAL,
            类型 TEXT,
            更新时间 TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    cursor.execute('''
        CREATE INDEX IF NOT EXISTS idx_fund_code_rating
        ON fund_rating_all(代码)
    ''')

    # 创建历史净值缓存表（支持激进缓存策略）
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS fund_net_value_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            基金代码 TEXT NOT NULL,
            日期 TEXT NOT NULL,
            单位净值 REAL,
            累计净值 REAL,
            日增长率 REAL,
            申购状态 TEXT,
            赎回状态 TEXT,
            分红送配 TEXT,
            更新时间 TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(基金代码, 日期)
        )
    ''')

    # 为历史净值表创建优化索引
    cursor.execute('''
        CREATE INDEX IF NOT EXISTS idx_net_value_fund_code
        ON fund_net_value_history(基金代码)
    ''')

    cursor.execute('''
        CREATE INDEX IF NOT EXISTS idx_net_value_date
        ON fund_net_value_history(日期)
    ''')

    cursor.execute('''
        CREATE INDEX IF NOT EXISTS idx_net_value_fund_date
        ON fund_net_value_history(基金代码, 日期 DESC)
    ''')

    # 创建持仓缓存表（季度持仓数据）
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS fund_holdings_cache (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            基金代码 TEXT NOT NULL,
            持仓类型 TEXT NOT NULL,  -- 'stock' 或 'bond'
            报告期 TEXT NOT NULL,     -- 如 '2024年4季度报告'
            序号 INTEGER,
            股票代码 TEXT,            -- 股票/债券代码
            股票名称 TEXT,            -- 股票/债券名称
            占净值比例 REAL,
            持股数 REAL,              -- 持股数量（万股）
            持仓市值 REAL,            -- 持仓市值（万元）
            更新时间 TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(基金代码, 持仓类型, 报告期, 序号)
        )
    ''')

    cursor.execute('''
        CREATE INDEX IF NOT EXISTS idx_holdings_fund_code
        ON fund_holdings_cache(基金代码)
    ''')

    cursor.execute('''
        CREATE INDEX IF NOT EXISTS idx_holdings_type
        ON fund_holdings_cache(持仓类型)
    ''')

    cursor.execute('''
        CREATE INDEX IF NOT EXISTS idx_holdings_report
        ON fund_holdings_cache(报告期)
    ''')

    # 创建货币基金缓存表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS fund_money_cache (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            基金代码 TEXT NOT NULL UNIQUE,
            基金简称 TEXT,
            万份收益 REAL,
            七日年化 REAL,
            单位净值 TEXT,
            日涨幅 TEXT,
            成立日期 TEXT,
            基金经理 TEXT,
            手续费 TEXT,
            可购全部 TEXT,
            更新时间 TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    cursor.execute('''
        CREATE INDEX IF NOT EXISTS idx_money_fund_code
        ON fund_money_cache(基金代码)
    ''')

    # 创建ETF历史行情缓存表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS fund_etf_hist_cache (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            基金代码 TEXT NOT NULL,
            日期 TEXT NOT NULL,
            开盘 REAL,
            收盘 REAL,
            最高 REAL,
            最低 REAL,
            成交量 INTEGER,
            成交额 REAL,
            振幅 REAL,
            涨跌幅 REAL,
            涨跌额 REAL,
            换手率 REAL,
            更新时间 TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(基金代码, 日期)
        )
    ''')

    cursor.execute('''
        CREATE INDEX IF NOT EXISTS idx_etf_hist_fund_code
        ON fund_etf_hist_cache(基金代码)
    ''')

    cursor.execute('''
        CREATE INDEX IF NOT EXISTS idx_etf_hist_date
        ON fund_etf_hist_cache(日期)
    ''')

    cursor.execute('''
        CREATE INDEX IF NOT EXISTS idx_etf_hist_fund_date
        ON fund_etf_hist_cache(基金代码, 日期 DESC)
    ''')

    # ========== 新增3个缓存表 (2025-11-16优化) ==========

    # 1. 基金基本信息缓存表 (TTL: 30分钟)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS fund_basic_info_cache (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            基金代码 TEXT NOT NULL UNIQUE,
            基金简称 TEXT,
            基金类型 TEXT,
            基金公司 TEXT,
            基金经理 TEXT,
            成立日期 TEXT,
            最新规模 TEXT,
            托管银行 TEXT,
            业绩比较基准 TEXT,
            投资目标 TEXT,
            投资策略 TEXT,
            更新时间 TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    cursor.execute('''
        CREATE INDEX IF NOT EXISTS idx_basic_info_fund_code
        ON fund_basic_info_cache(基金代码)
    ''')

    cursor.execute('''
        CREATE INDEX IF NOT EXISTS idx_basic_info_update_time
        ON fund_basic_info_cache(更新时间)
    ''')

    # 2. 实时净值缓存表 (TTL: 5分钟)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS fund_daily_nav_cache (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            基金代码 TEXT NOT NULL UNIQUE,
            基金简称 TEXT,
            净值日期 TEXT,
            单位净值 REAL,
            累计净值 REAL,
            日增长率 TEXT,
            日增长值 TEXT,
            申购状态 TEXT,
            赎回状态 TEXT,
            手续费 TEXT,
            更新时间 TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    cursor.execute('''
        CREATE INDEX IF NOT EXISTS idx_daily_nav_fund_code
        ON fund_daily_nav_cache(基金代码)
    ''')

    cursor.execute('''
        CREATE INDEX IF NOT EXISTS idx_daily_nav_update_time
        ON fund_daily_nav_cache(更新时间)
    ''')

    # 3. 基金排行榜缓存表 (TTL: 10分钟)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS fund_ranking_cache (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            基金类型 TEXT NOT NULL,
            排行数据 TEXT NOT NULL,  -- JSON格式存储完整排行数据
            总记录数 INTEGER,
            更新时间 TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(基金类型)
        )
    ''')

    cursor.execute('''
        CREATE INDEX IF NOT EXISTS idx_ranking_fund_type
        ON fund_ranking_cache(基金类型)
    ''')

    cursor.execute('''
        CREATE INDEX IF NOT EXISTS idx_ranking_update_time
        ON fund_ranking_cache(更新时间)
    ''')

    # 4. 雪球风险指标缓存表 (TTL: 24小时,每周更新)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS fund_risk_indicators_xq (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            基金代码 TEXT NOT NULL,
            周期 TEXT NOT NULL,
            较同类风险收益比 INTEGER,
            较同类抗风险波动 INTEGER,
            年化波动率 REAL,
            年化夏普比率 REAL,
            最大回撤 REAL,
            更新时间 TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(基金代码, 周期)
        )
    ''')

    cursor.execute('''
        CREATE INDEX IF NOT EXISTS idx_risk_fund_code
        ON fund_risk_indicators_xq(基金代码)
    ''')

    cursor.execute('''
        CREATE INDEX IF NOT EXISTS idx_risk_period
        ON fund_risk_indicators_xq(周期)
    ''')

    cursor.execute('''
        CREATE INDEX IF NOT EXISTS idx_risk_update_time
        ON fund_risk_indicators_xq(更新时间)
    ''')

    # 5. 基金申购赎回状态表 (TTL: 每日更新)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS fund_purchase_status (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            序号 INTEGER,
            基金代码 TEXT NOT NULL UNIQUE,
            基金简称 TEXT,
            基金类型 TEXT,
            最新净值万份收益 TEXT,
            最新净值万份收益报告时间 TEXT,
            申购状态 TEXT,
            赎回状态 TEXT,
            下一开放日 TEXT,
            购买起点 TEXT,
            日累计限定金额 TEXT,
            手续费 TEXT,
            更新时间 TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    cursor.execute('''
        CREATE INDEX IF NOT EXISTS idx_purchase_fund_code
        ON fund_purchase_status(基金代码)
    ''')

    cursor.execute('''
        CREATE INDEX IF NOT EXISTS idx_purchase_status
        ON fund_purchase_status(申购状态, 赎回状态)
    ''')

    cursor.execute('''
        CREATE INDEX IF NOT EXISTS idx_purchase_update_time
        ON fund_purchase_status(更新时间)
    ''')

    cursor.execute('''
        CREATE INDEX IF NOT EXISTS idx_purchase_type
        ON fund_purchase_status(基金类型)
    ''')

    # 6. 基金公司规模数据表 (TTL: 每周更新)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS fund_company_aum (\n            id INTEGER PRIMARY KEY AUTOINCREMENT,
            序号 INTEGER,
            基金公司 TEXT NOT NULL UNIQUE,
            成立时间 TEXT,
            全部管理规模 REAL,
            全部基金数 INTEGER,
            全部经理数 INTEGER,
            更新日期 TEXT,
            更新时间 TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    cursor.execute('''
        CREATE INDEX IF NOT EXISTS idx_company_aum_name
        ON fund_company_aum(基金公司)
    ''')

    cursor.execute('''
        CREATE INDEX IF NOT EXISTS idx_company_aum_scale
        ON fund_company_aum(全部管理规模 DESC)
    ''')

    cursor.execute('''
        CREATE INDEX IF NOT EXISTS idx_company_aum_update_time
        ON fund_company_aum(更新时间)
    ''')

    # 7. 基金公司规模历史数据表 (年度数据)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS fund_company_aum_hist (\n            id INTEGER PRIMARY KEY AUTOINCREMENT,
            序号 INTEGER,
            基金公司 TEXT NOT NULL,
            年份 TEXT NOT NULL,
            总规模 REAL,
            股票型 REAL,
            混合型 REAL,
            债券型 REAL,
            指数型 REAL,
            QDII REAL,
            货币型 REAL,
            更新时间 TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(基金公司, 年份)
        )
    ''')

    cursor.execute('''
        CREATE INDEX IF NOT EXISTS idx_company_hist_name
        ON fund_company_aum_hist(基金公司)
    ''')

    cursor.execute('''
        CREATE INDEX IF NOT EXISTS idx_company_hist_year
        ON fund_company_aum_hist(年份)
    ''')

    cursor.execute('''
        CREATE INDEX IF NOT EXISTS idx_company_hist_name_year
        ON fund_company_aum_hist(基金公司, 年份 DESC)
    ''')

    # 8. 基金市场规模趋势表 (季度数据)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS fund_market_aum_trend (\n            id INTEGER PRIMARY KEY AUTOINCREMENT,
            日期 TEXT NOT NULL UNIQUE,
            市场总规模 REAL,
            更新时间 TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    cursor.execute('''
        CREATE INDEX IF NOT EXISTS idx_market_trend_date
        ON fund_market_aum_trend(日期 DESC)
    ''')

    conn.commit()
    print(f"[数据库] 初始化完成: {DB_PATH}")


def execute_query(query: str, params: tuple = ()) -> list:
    """
    执行查询并返回结果
    """
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute(query, params)
    rows = cursor.fetchall()

    # 将 Row 对象转换为字典
    return [dict(row) for row in rows]


def execute_update(query: str, params: tuple = ()) -> int:
    """
    执行更新/插入/删除操作
    返回影响的行数
    """
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute(query, params)
    conn.commit()
    return cursor.rowcount


def execute_many(query: str, params_list: list) -> int:
    """
    批量执行操作（用于批量插入/更新）
    返回影响的行数
    """
    conn = get_db()
    cursor = conn.cursor()
    cursor.executemany(query, params_list)
    conn.commit()
    return cursor.rowcount
