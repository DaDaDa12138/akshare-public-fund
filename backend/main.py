"""
AkShare 基金平台后端主程序
整合 AKTools HTTP 服务 + 数据库 + 定时任务
"""
import uvicorn
from fastapi import FastAPI, HTTPException, Body
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from db import init_db, start_scheduler, stop_scheduler, get_db
from db.cache_helper import CacheHelper
from utils.export_utils import export_to_csv, export_to_excel
from utils.logger import setup_logging
from middleware import ErrorHandlerMiddleware, RequestLoggingMiddleware
import logging
import atexit
import akshare as ak
from datetime import datetime, timedelta
from typing import Dict, Any, Optional
import threading
from urllib.parse import quote

# 配置增强版日志系统
setup_logging(
    log_level="INFO",
    log_file="/app/logs/backend.log",
    enable_color=True,
    enable_file_rotation=True,
    max_bytes=10 * 1024 * 1024,  # 10MB
    backup_count=5
)
logger = logging.getLogger(__name__)

# ========== 基金类型推断工具函数 ==========
def infer_fund_type(fund_name: str) -> str:
    """
    从基金名称中智能推断基金类型

    Args:
        fund_name: 基金简称

    Returns:
        基金类型字符串（股票型、混合型、债券型、指数型、QDII、LOF、FOF、货币型、其他）
    """
    if not fund_name or not isinstance(fund_name, str):
        return '其他'

    # 基金类型关键词匹配（按优先级排序）
    type_keywords = [
        ('货币', '货币型'),
        ('QDII', 'QDII'),
        ('FOF', 'FOF'),
        ('LOF', 'LOF'),
        ('指数', '指数型'),
        ('债券', '债券型'),
        ('债', '债券型'),
        ('混合', '混合型'),
        ('股票', '股票型'),
        ('权益', '股票型'),  # 权益类基金通常归为股票型
    ]

    for keyword, fund_type in type_keywords:
        if keyword in fund_name:
            return fund_type

    return '其他'

# ========== 内存缓存系统 ==========
class FundRankCache:
    """基金排行数据内存缓存"""
    def __init__(self, ttl_minutes: int = 10):
        self.cache: Dict[str, Dict[str, Any]] = {}
        self.ttl = timedelta(minutes=ttl_minutes)
        self.lock = threading.Lock()

    def get(self, key: str) -> Optional[Any]:
        """获取缓存数据"""
        with self.lock:
            if key in self.cache:
                entry = self.cache[key]
                # 检查是否过期
                if datetime.now() < entry['expires_at']:
                    logger.info(f"[缓存命中] key={key}, 剩余时间={(entry['expires_at'] - datetime.now()).total_seconds():.0f}秒")
                    return entry['data']
                else:
                    # 过期则删除
                    logger.info(f"[缓存过期] key={key}")
                    del self.cache[key]
        return None

    def set(self, key: str, data: Any):
        """设置缓存数据"""
        with self.lock:
            expires_at = datetime.now() + self.ttl
            self.cache[key] = {
                'data': data,
                'expires_at': expires_at,
                'created_at': datetime.now()
            }
            logger.info(f"[缓存设置] key={key}, 数据量={len(data) if isinstance(data, list) else 'N/A'}, 有效期={self.ttl.total_seconds()/60}分钟")

    def clear(self):
        """清空所有缓存"""
        with self.lock:
            count = len(self.cache)
            self.cache.clear()
            logger.info(f"[缓存清空] 已清除 {count} 个缓存项")

    def get_stats(self) -> Dict[str, Any]:
        """获取缓存统计信息"""
        with self.lock:
            return {
                'total_entries': len(self.cache),
                'entries': [
                    {
                        'key': key,
                        'created_at': entry['created_at'].isoformat(),
                        'expires_at': entry['expires_at'].isoformat(),
                        'data_size': len(entry['data']) if isinstance(entry['data'], list) else 0
                    }
                    for key, entry in self.cache.items()
                ]
            }

# 创建全局缓存实例（10分钟TTL）
fund_rank_cache = FundRankCache(ttl_minutes=10)
logger.info("[缓存系统] 基金排行缓存已初始化，TTL=10分钟")

# 导入 AKTools 核心路由
try:
    from aktools.core.api import app_core
    logger.info("[启动] 成功导入 AKTools 核心路由")
    aktools_imported = True
except ImportError as e:
    logger.error(f"[启动] 无法导入 AKTools: {e}")
    aktools_imported = False

# 创建 FastAPI 应用
app = FastAPI(title="AkShare Fund Platform API", version="1.5.0")

# 配置 CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 添加错误处理和请求日志中间件
app.add_middleware(ErrorHandlerMiddleware)
app.add_middleware(RequestLoggingMiddleware)
logger.info("[中间件] 已添加错误处理和请求日志中间件")

# 挂载 AKTools 核心 API 路由
# AKTools 的路由是 /public/{item_id}，所以挂载到 /api 前缀
# 最终路径: /api/public/{item_id}（与前端的 baseURL: '/api/public' 匹配）
if aktools_imported:
    app.include_router(app_core, prefix="/api", tags=["AkShare数据接口"])
    logger.info("[启动] 已挂载 AKTools 核心路由到 /api，完整路径: /api/public/{item_id}")
else:
    logger.warning("[启动] AKTools 路由未挂载，前端 API 请求可能失败")


# ========== 自定义 API 端点 ==========

@app.get("/api/fund_estimation/batch")
async def get_fund_estimation_batch(symbols: str):
    """
    批量获取基金估值数据
    参数: symbols - 基金代码列表，逗号分隔，如 "110011,000001,163406"
    注意：此路由必须放在 /api/fund_estimation/{symbol} 之前
    """
    try:
        symbol_list = [s.strip() for s in symbols.split(',') if s.strip()]

        if not symbol_list:
            raise HTTPException(status_code=400, detail="参数 symbols 不能为空")

        if len(symbol_list) > 100:
            raise HTTPException(status_code=400, detail="最多支持查询 100 个基金")

        conn = get_db()
        cursor = conn.cursor()

        # 构建查询（使用 IN 子句）
        placeholders = ','.join('?' * len(symbol_list))
        query = f'''
            SELECT 基金代码, 基金名称, 估算值, 估算增长率, 估算时间
            FROM fund_value_estimation
            WHERE 基金代码 IN ({placeholders})
        '''

        cursor.execute(query, symbol_list)
        rows = cursor.fetchall()

        # 转换为字典列表
        results = [dict(row) for row in rows]
        return results

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"批量查询估值失败: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/fund_estimation/{symbol}")
async def get_fund_estimation(symbol: str):
    """
    获取单个基金的实时估值数据
    注意：此路由必须放在 /api/fund_estimation/batch 之后
    """
    try:
        conn = get_db()
        cursor = conn.cursor()

        cursor.execute('''
            SELECT 基金代码, 基金名称, 估算时间, 估算值, 估算增长率,
                   单位净值, 日增长率, 估算偏差, 更新时间
            FROM fund_value_estimation
            WHERE 基金代码 = ?
        ''', (symbol,))

        row = cursor.fetchone()

        if row is None:
            raise HTTPException(status_code=404, detail=f"基金 {symbol} 估值数据不存在")

        # 转换为字典
        result = dict(row)
        return result

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"查询估值失败: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/estimation_stats")
async def get_estimation_stats():
    """
    获取估值数据统计信息
    """
    try:
        conn = get_db()
        cursor = conn.cursor()

        cursor.execute('SELECT COUNT(*) as total FROM fund_value_estimation')
        total = cursor.fetchone()['total']

        cursor.execute('SELECT MAX(更新时间) as last_update FROM fund_value_estimation')
        last_update = cursor.fetchone()['last_update']

        return {
            "total_funds": total,
            "last_update": last_update
        }

    except Exception as e:
        logger.error(f"查询统计信息失败: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/fund_money")
async def get_money_funds():
    """
    获取货币基金实时数据
    支持数据库缓存（10分钟）
    """
    try:
        logger.info("[货币基金] 查询货币基金数据")

        # 1. 检查数据库缓存
        conn = get_db()
        cursor = conn.cursor()

        # 检查缓存是否存在且未过期（10分钟）
        cursor.execute('''
            SELECT COUNT(*) as count, MAX(更新时间) as last_update
            FROM fund_money_cache
            WHERE datetime(更新时间) > datetime('now', '-10 minutes')
        ''')
        cache_info = cursor.fetchone()

        if cache_info['count'] > 0:
            logger.info(f"[货币基金] 使用缓存数据，共 {cache_info['count']} 条记录")

            cursor.execute('''
                SELECT 基金代码, 基金简称, 万份收益, 七日年化, 单位净值, 日涨幅,
                       成立日期, 基金经理, 手续费, 可购全部, 更新时间
                FROM fund_money_cache
                ORDER BY 七日年化 DESC
            ''')

            rows = cursor.fetchall()
            results = [dict(row) for row in rows]

            return {
                "success": True,
                "data": results,
                "source": "cache",
                "last_update": cache_info['last_update']
            }

        # 2. 缓存过期或不存在，调用AkShare API
        logger.info("[货币基金] 缓存过期，调用AkShare API")

        try:
            import akshare as ak
        except ImportError:
            raise HTTPException(status_code=500, detail="AkShare 库未安装")

        try:
            # 调用实时货币基金API
            df = ak.fund_money_fund_daily_em()

            if df.empty:
                logger.warning("[货币基金] API返回空数据")
                return {
                    "success": True,
                    "data": [],
                    "source": "api",
                    "message": "API返回空数据"
                }

            logger.info(f"[货币基金] API返回 {len(df)} 条记录")

            # 解析动态字段名（日期格式：YYYY-MM-DD-字段名）
            # 获取最新日期的字段
            date_columns = [col for col in df.columns if '-' in str(col) and str(col).count('-') >= 3]

            if not date_columns:
                logger.error("[货币基金] 未找到日期列")
                logger.error(f"[货币基金] 所有列名: {df.columns.tolist()}")
                raise HTTPException(status_code=500, detail="数据格式错误：未找到日期列")

            # 提取日期部分（前10个字符 YYYY-MM-DD）
            dates = sorted(set([str(col)[:10] for col in date_columns if len(str(col)) >= 10]), reverse=True)
            latest_date = dates[0] if dates else None

            logger.info(f"[货币基金] 找到日期: {dates}, 使用最新日期: {latest_date}")

            # 构建字段映射
            field_mapping = {}
            for col in df.columns:
                if latest_date and latest_date in str(col):
                    if '万份收益' in str(col):
                        field_mapping['万份收益'] = col
                    elif '7日年化' in str(col) or '七日年化' in str(col):
                        field_mapping['七日年化'] = col
                    elif '单位净值' in str(col):
                        field_mapping['单位净值'] = col
                    elif '日涨幅' in str(col):
                        field_mapping['日涨幅'] = col

            logger.info(f"[货币基金] 字段映射: {field_mapping}")

            # 清空旧缓存
            cursor.execute('DELETE FROM fund_money_cache')
            conn.commit()
            logger.info("[货币基金] 已清空旧缓存")

            # 准备批量插入数据
            records = []
            for _, row in df.iterrows():
                try:
                    # 解析数值，处理可能的字符串格式
                    wan_fen_shouyi = row.get(field_mapping.get('万份收益', ''), None)
                    qi_ri_nianhua = row.get(field_mapping.get('七日年化', ''), None)

                    # 转换万份收益为浮点数
                    try:
                        wan_fen_shouyi = float(wan_fen_shouyi) if wan_fen_shouyi not in [None, '', '--'] else None
                    except (ValueError, TypeError):
                        wan_fen_shouyi = None

                    # 七日年化保持字符串格式(包含%)
                    qi_ri_nianhua = str(qi_ri_nianhua) if qi_ri_nianhua not in [None, '', '--', 'None'] else ''

                    records.append((
                        str(row.get('基金代码', '')),
                        str(row.get('基金简称', '')),
                        wan_fen_shouyi,
                        qi_ri_nianhua,
                        str(row.get(field_mapping.get('单位净值', ''), '')),
                        str(row.get(field_mapping.get('日涨幅', ''), '')),
                        str(row.get('成立日期', '')),
                        str(row.get('基金经理', '')),
                        str(row.get('手续费', '')),
                        str(row.get('可购全部', ''))
                    ))
                except Exception as row_error:
                    logger.warning(f"[货币基金] 处理行数据失败: {row_error}")
                    continue

            # 批量插入
            if records:
                cursor.executemany('''
                    INSERT OR REPLACE INTO fund_money_cache
                    (基金代码, 基金简称, 万份收益, 七日年化, 单位净值, 日涨幅,
                     成立日期, 基金经理, 手续费, 可购全部, 更新时间)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
                ''', records)
                conn.commit()
                logger.info(f"[货币基金] 缓存 {len(records)} 条记录")

            # 转换为结果格式，按七日年化降序排序
            results = df.to_dict('records')

            # 标准化结果（使用解析后的字段名）
            standardized_results = []
            for item in results:
                try:
                    standardized_item = {
                        '基金代码': item.get('基金代码', ''),
                        '基金简称': item.get('基金简称', ''),
                        '万份收益': item.get(field_mapping.get('万份收益', ''), ''),
                        '七日年化': item.get(field_mapping.get('七日年化', ''), ''),
                        '单位净值': item.get(field_mapping.get('单位净值', ''), ''),
                        '日涨幅': item.get(field_mapping.get('日涨幅', ''), ''),
                        '成立日期': item.get('成立日期', ''),
                        '基金经理': item.get('基金经理', ''),
                        '手续费': item.get('手续费', ''),
                        '可购全部': item.get('可购全部', '')
                    }
                    standardized_results.append(standardized_item)
                except Exception as e:
                    logger.warning(f"[货币基金] 标准化数据失败: {e}")
                    continue

            # 按七日年化降序排序
            try:
                standardized_results.sort(
                    key=lambda x: float(x['七日年化']) if x['七日年化'] not in ['', '--', None] else 0,
                    reverse=True
                )
            except Exception as sort_error:
                logger.warning(f"[货币基金] 排序失败: {sort_error}")

            return {
                "success": True,
                "data": standardized_results,
                "source": "api",
                "total": len(standardized_results)
            }

        except Exception as api_error:
            logger.error(f"[货币基金] AkShare API调用失败: {api_error}", exc_info=True)
            return {
                "success": False,
                "data": [],
                "source": "api",
                "error": str(api_error)
            }

    except Exception as e:
        logger.error(f"获取货币基金数据失败: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/fund_open_fund_daily_em")
async def get_fund_open_daily():
    """
    获取开放式基金实时净值数据(完整列表)
    提供单位净值、累计净值、日增长值、日增长率等关键信息
    缓存策略: 1分钟(实时数据)
    数据源: 东方财富
    """
    try:
        logger.info("[开放式基金实时净值] 查询所有开放式基金实时净值数据")

        # 调用AkShare API
        try:
            import akshare as ak
        except ImportError:
            raise HTTPException(status_code=500, detail="AkShare 库未安装")

        try:
            # 调用fund_open_fund_daily_em API
            df = ak.fund_open_fund_daily_em()

            if df.empty:
                logger.warning("[开放式基金实时净值] API返回空数据")
                return []

            logger.info(f"[开放式基金实时净值] 成功获取 {len(df)} 条数据")

            # 解析动态日期字段
            # 字段格式: YYYY-MM-DD-单位净值, YYYY-MM-DD-累计净值
            date_columns = [col for col in df.columns if '-' in str(col) and str(col).count('-') >= 3]

            # 提取日期并找到最新的两个日期
            dates = sorted(set([str(col)[:10] for col in date_columns if len(str(col)) >= 10]), reverse=True)
            latest_date = dates[0] if len(dates) > 0 else None
            previous_date = dates[1] if len(dates) > 1 else None

            logger.info(f"[开放式基金实时净值] 检测到日期: {dates[:5]}..., 最新: {latest_date}, 前一日: {previous_date}")

            # 保留原始字段名(带日期前缀),前端需要动态解析日期字段
            results = []
            for _, row in df.iterrows():
                try:
                    item = {
                        '基金代码': str(row.get('基金代码', '')),
                        '基金简称': str(row.get('基金简称', '')),
                        '日增长值': str(row.get('日增长值', '')),
                        '日增长率': str(row.get('日增长率', '')),
                        '申购状态': str(row.get('申购状态', '')),
                        '赎回状态': str(row.get('赎回状态', '')),
                        '手续费': str(row.get('手续费', ''))
                    }

                    # 添加带日期前缀的字段(保持原始格式)
                    if latest_date:
                        item[f'{latest_date}-单位净值'] = str(row.get(f'{latest_date}-单位净值', ''))
                        item[f'{latest_date}-累计净值'] = str(row.get(f'{latest_date}-累计净值', ''))

                    if previous_date:
                        item[f'{previous_date}-单位净值'] = str(row.get(f'{previous_date}-单位净值', ''))
                        item[f'{previous_date}-累计净值'] = str(row.get(f'{previous_date}-累计净值', ''))

                    results.append(item)
                except Exception as row_error:
                    logger.warning(f"[开放式基金实时净值] 处理行数据失败: {row_error}")
                    continue

            logger.info(f"[开放式基金实时净值] 成功处理 {len(results)} 条数据")

            # 直接返回数组,与其他API保持一致
            return results

        except Exception as api_error:
            logger.error(f"[开放式基金实时净值] AkShare API调用失败: {api_error}", exc_info=True)
            # 返回空数组
            return []

    except Exception as e:
        logger.error(f"[开放式基金实时净值] 请求失败: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/fund_dividend/{symbol}")
async def get_fund_dividend(symbol: str):
    """
    获取单个基金的分红记录
    """
    try:
        conn = get_db()
        cursor = conn.cursor()

        cursor.execute('''
            SELECT 基金代码, 基金简称, 权益登记日, 除息日期, 分红, 分红发放日
            FROM fund_dividend
            WHERE 基金代码 = ?
            ORDER BY 除息日期 DESC
        ''', (symbol,))

        rows = cursor.fetchall()

        if not rows:
            # 返回空数组而非404，因为某些基金可能没有分红记录
            return []

        # 转换为字典列表
        results = [dict(row) for row in rows]
        return results

    except Exception as e:
        logger.error(f"查询分红记录失败 [{symbol}]: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/dividend_stats")
async def get_dividend_stats():
    """
    获取分红数据统计信息
    """
    try:
        conn = get_db()
        cursor = conn.cursor()

        cursor.execute('SELECT COUNT(*) as total FROM fund_dividend')
        total = cursor.fetchone()['total']

        cursor.execute('SELECT COUNT(DISTINCT 基金代码) as fund_count FROM fund_dividend')
        fund_count = cursor.fetchone()['fund_count']

        cursor.execute('SELECT MAX(更新时间) as last_update FROM fund_dividend')
        last_update = cursor.fetchone()['last_update']

        return {
            "total_records": total,
            "fund_count": fund_count,
            "last_update": last_update
        }

    except Exception as e:
        logger.error(f"查询分红统计信息失败: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/fund_bond_holdings/{symbol}")
async def get_fund_bond_holdings(symbol: str, quarter: str = None):
    """
    获取基金债券持仓数据
    参数:
    - symbol: 基金代码
    - quarter: 可选，指定季度（如 "2023年4季度"）
    """
    try:
        logger.info(f"[债券持仓] 查询基金 {symbol} 的债券持仓数据")

        # 首先尝试从缓存读取
        conn = get_db()
        cursor = conn.cursor()

        if quarter:
            cursor.execute('''
                SELECT 序号, 股票代码 as 债券代码, 股票名称 as 债券名称,
                       占净值比例, 持仓市值, 报告期 as 季度
                FROM fund_holdings_cache
                WHERE 基金代码 = ? AND 持仓类型 = 'bond' AND 报告期 LIKE ?
                ORDER BY 序号 ASC
            ''', (symbol, f'%{quarter}%'))
        else:
            cursor.execute('''
                SELECT 序号, 股票代码 as 债券代码, 股票名称 as 债券名称,
                       占净值比例, 持仓市值, 报告期 as 季度
                FROM fund_holdings_cache
                WHERE 基金代码 = ? AND 持仓类型 = 'bond'
                ORDER BY 报告期 DESC, 序号 ASC
            ''', (symbol,))

        cached_rows = cursor.fetchall()

        if cached_rows:
            logger.info(f"[债券持仓] 从缓存获取 {len(cached_rows)} 条记录")
            results = [dict(row) for row in cached_rows]

            # 提取可用季度
            quarters = list(set(row['季度'] for row in results))
            quarters.sort(reverse=True)

            return {
                "success": True,
                "data": results,
                "quarters": quarters,
                "source": "cache"
            }

        # 缓存未命中，从AkShare API获取
        logger.info(f"[债券持仓] 缓存未命中，从AkShare获取数据")

        try:
            df = ak.fund_portfolio_bond_hold_em(symbol=symbol)

            if df is None or df.empty:
                logger.info(f"[债券持仓] 基金 {symbol} 没有债券持仓数据")
                return {
                    "success": True,
                    "data": [],
                    "quarters": [],
                    "source": "api"
                }

            # 缓存到数据库
            records = []
            for _, row in df.iterrows():
                records.append((
                    symbol,
                    'bond',
                    str(row.get('季度', '')),
                    int(row.get('序号', 0)),
                    str(row.get('债券代码', '')),
                    str(row.get('债券名称', '')),
                    float(row.get('占净值比例', 0)),
                    0,  # 债券不需要持股数
                    float(row.get('持仓市值', 0))
                ))

            # 先删除旧缓存
            cursor.execute('''
                DELETE FROM fund_holdings_cache
                WHERE 基金代码 = ? AND 持仓类型 = 'bond'
            ''', (symbol,))

            # 批量插入新数据
            cursor.executemany('''
                INSERT INTO fund_holdings_cache
                (基金代码, 持仓类型, 报告期, 序号, 股票代码, 股票名称, 占净值比例, 持股数, 持仓市值, 更新时间)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
            ''', records)
            conn.commit()

            logger.info(f"[债券持仓] 缓存 {len(records)} 条债券持仓记录")

            # 转换为结果格式
            results = df.to_dict('records')

            # 提取可用季度
            quarters = df['季度'].unique().tolist() if '季度' in df.columns else []
            quarters.sort(reverse=True)

            # 如果指定了季度，过滤结果
            if quarter:
                results = [r for r in results if quarter in r.get('季度', '')]

            return {
                "success": True,
                "data": results,
                "quarters": quarters,
                "source": "api"
            }

        except Exception as api_error:
            logger.warning(f"[债券持仓] AkShare API调用失败: {api_error}")
            # API失败时返回空结果
            return {
                "success": True,
                "data": [],
                "quarters": [],
                "source": "api",
                "error": str(api_error)
            }

    except Exception as e:
        logger.error(f"获取债券持仓失败 [{symbol}]: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/fund_compare")
async def compare_funds(request: dict):
    """
    基金对比API
    接收参数: {"symbols": ["110011", "163406", "000001"]}
    返回: 多个基金的综合对比数据
    支持1-10个基金查询
    """
    try:
        symbols = request.get('symbols', [])

        if not symbols or not isinstance(symbols, list):
            raise HTTPException(status_code=400, detail="参数 symbols 必须是非空数组")

        if len(symbols) < 1:
            raise HTTPException(status_code=400, detail="至少需要1个基金")

        if len(symbols) > 10:
            raise HTTPException(status_code=400, detail="最多支持查询10个基金")

        # 导入 akshare
        try:
            import akshare as ak
        except ImportError:
            raise HTTPException(status_code=500, detail="AkShare 库未安装")

        results = []

        for symbol in symbols:
            fund_data = {
                "基金代码": symbol,
                "基础信息": {},
                "收益率": {},
                "风险指标": {},
                "评级": {},
                "分红统计": {}
            }

            # 1. 获取基金概况（基础信息）
            try:
                overview_df = ak.fund_overview_em(symbol=symbol)
                if not overview_df.empty:
                    overview_dict = overview_df.to_dict('records')[0]
                    fund_data["基础信息"] = {
                        "基金全称": overview_dict.get('基金全称', ''),
                        "基金简称": overview_dict.get('基金简称', ''),
                        "基金类型": overview_dict.get('基金类型', ''),
                        "成立日期": overview_dict.get('成立日期/规模', ''),
                        "基金经理人": overview_dict.get('基金经理人', ''),
                        "基金管理人": overview_dict.get('基金管理人', ''),
                        "资产规模": overview_dict.get('资产规模', ''),
                        "管理费率": overview_dict.get('管理费率', ''),
                        "托管费率": overview_dict.get('托管费率', '')
                    }
            except Exception as e:
                logger.warning(f"获取基金概况失败 [{symbol}]: {e}")

            # 2. 获取排行数据（收益率）
            try:
                rank_df = ak.fund_open_fund_rank_em(symbol="全部")
                fund_rank = rank_df[rank_df['基金代码'] == symbol]
                if not fund_rank.empty:
                    rank_dict = fund_rank.iloc[0].to_dict()
                    fund_data["收益率"] = {
                        "单位净值": rank_dict.get('单位净值-单位净值', ''),
                        "累计净值": rank_dict.get('累计净值', ''),
                        "日增长率": rank_dict.get('日增长率', ''),
                        "近1周": rank_dict.get('近1周', ''),
                        "近1月": rank_dict.get('近1月', ''),
                        "近3月": rank_dict.get('近3月', ''),
                        "近6月": rank_dict.get('近6月', ''),
                        "近1年": rank_dict.get('近1年', ''),
                        "近2年": rank_dict.get('近2年', ''),
                        "近3年": rank_dict.get('近3年', ''),
                        "今年来": rank_dict.get('今年来', ''),
                        "成立来": rank_dict.get('成立来', '')
                    }
            except Exception as e:
                logger.warning(f"获取排行数据失败 [{symbol}]: {e}")

            # 3. 获取风险指标（雪球）
            try:
                analysis_df = ak.fund_individual_analysis_xq(symbol=symbol)
                if not analysis_df.empty:
                    # 取近1年的数据
                    analysis_1y = analysis_df[analysis_df['周期'] == '近1年']
                    if not analysis_1y.empty:
                        analysis_dict = analysis_1y.iloc[0].to_dict()
                        fund_data["风险指标"] = {
                            "年化波动率": analysis_dict.get('年化波动率', ''),
                            "年化夏普比率": analysis_dict.get('年化夏普比率', ''),
                            "最大回撤": analysis_dict.get('最大回撤', '')
                        }
            except Exception as e:
                logger.warning(f"获取风险指标失败 [{symbol}]: {e}")

            # 4. 获取评级（从数据库）
            try:
                conn = get_db()
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT 上海证券, 招商证券, 济安金信, 晨星评级, "5星评级家数"
                    FROM fund_rating_all
                    WHERE 代码 = ?
                ''', (symbol,))
                rating_row = cursor.fetchone()
                if rating_row:
                    fund_data["评级"] = dict(rating_row)
            except Exception as e:
                logger.warning(f"获取评级失败 [{symbol}]: {e}")

            # 5. 获取分红统计（从数据库）
            try:
                conn = get_db()
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT COUNT(*) as 分红次数, SUM(分红) as 累计分红
                    FROM fund_dividend
                    WHERE 基金代码 = ?
                ''', (symbol,))
                dividend_row = cursor.fetchone()
                if dividend_row:
                    fund_data["分红统计"] = dict(dividend_row)
            except Exception as e:
                logger.warning(f"获取分红统计失败 [{symbol}]: {e}")

            results.append(fund_data)

        return {
            "success": True,
            "count": len(results),
            "data": results
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"基金对比失败: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


# ========== 应用生命周期管理 ==========

@app.on_event("startup")
async def startup_event():
    """
    应用启动时的初始化
    """
    logger.info("========== AkShare 基金平台启动 ==========")

    # 初始化数据库
    try:
        init_db()
        logger.info("[启动] 数据库初始化完成")
    except Exception as e:
        logger.error(f"[启动] 数据库初始化失败: {str(e)}", exc_info=True)

    # 启动定时任务调度器
    try:
        start_scheduler()
        logger.info("[启动] 定时任务调度器已启动")
    except Exception as e:
        logger.error(f"[启动] 定时任务启动失败: {str(e)}", exc_info=True)

    logger.info("========== 系统启动完成 ==========")


@app.on_event("shutdown")
async def shutdown_event():
    """
    应用关闭时的清理
    """
    logger.info("========== 系统关闭中 ==========")

    # 停止定时任务
    try:
        stop_scheduler()
        logger.info("[关闭] 定时任务调度器已停止")
    except Exception as e:
        logger.error(f"[关闭] 停止定时任务失败: {str(e)}", exc_info=True)

    logger.info("========== 系统已关闭 ==========")


# 注册清理函数（进程退出时）
atexit.register(stop_scheduler)


# ========== 数据管理API ==========

@app.get("/api/admin/data_status")
async def get_data_status():
    """
    获取所有数据的状态信息
    """
    try:
        conn = get_db()
        cursor = conn.cursor()

        # 估值数据统计
        cursor.execute('SELECT COUNT(*) as count, MAX(更新时间) as last_update FROM fund_value_estimation')
        estimation_stats = cursor.fetchone()

        # 分红数据统计
        cursor.execute('SELECT COUNT(*) as count, COUNT(DISTINCT 基金代码) as fund_count, MAX(更新时间) as last_update FROM fund_dividend')
        dividend_stats = cursor.fetchone()

        # 评级数据统计
        cursor.execute('SELECT COUNT(*) as count, MAX(更新时间) as last_update FROM fund_rating_all')
        rating_stats = cursor.fetchone()

        return {
            "success": True,
            "data": {
                "estimation": {
                    "total": estimation_stats['count'],
                    "last_update": estimation_stats['last_update']
                },
                "dividend": {
                    "total": dividend_stats['count'],
                    "fund_count": dividend_stats['fund_count'],
                    "last_update": dividend_stats['last_update']
                },
                "rating": {
                    "total": rating_stats['count'],
                    "last_update": rating_stats['last_update']
                }
            }
        }
    except Exception as e:
        logger.error(f"获取数据状态失败: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/admin/scheduler_status")
async def get_scheduler_status():
    """
    获取定时任务调度器状态
    """
    try:
        from db.scheduler import scheduler

        if scheduler is None:
            return {
                "success": False,
                "message": "调度器未启动"
            }

        jobs_info = []
        for job in scheduler.get_jobs():
            jobs_info.append({
                "id": job.id,
                "name": job.func.__name__,
                "trigger": str(job.trigger),
                "next_run_time": job.next_run_time.isoformat() if job.next_run_time else None
            })

        return {
            "success": True,
            "data": {
                "running": scheduler.running,
                "jobs": jobs_info
            }
        }
    except Exception as e:
        logger.error(f"获取调度器状态失败: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/admin/update_estimation")
async def manual_update_estimation():
    """
    手动触发估值数据更新
    """
    try:
        from db.scheduler import update_fund_estimation
        logger.info("[手动更新] 开始更新估值数据")

        # 在后台线程执行更新（避免阻塞请求）
        import threading
        thread = threading.Thread(target=update_fund_estimation)
        thread.daemon = True
        thread.start()

        return {
            "success": True,
            "message": "估值数据更新已启动，请稍后查看数据状态"
        }
    except Exception as e:
        logger.error(f"手动更新估值失败: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/admin/update_dividend")
async def manual_update_dividend():
    """
    手动触发分红数据更新
    """
    try:
        from db.scheduler import update_fund_dividend
        logger.info("[手动更新] 开始更新分红数据")

        # 在后台线程执行更新（避免阻塞请求）
        import threading
        thread = threading.Thread(target=update_fund_dividend)
        thread.daemon = True
        thread.start()

        return {
            "success": True,
            "message": "分红数据更新已启动，这可能需要1-2分钟，请稍后查看数据状态"
        }
    except Exception as e:
        logger.error(f"手动更新分红失败: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/admin/update_rating")
async def manual_update_rating():
    """
    手动触发评级数据更新
    """
    try:
        from db.scheduler import update_fund_rating
        logger.info("[手动更新] 开始更新评级数据")

        # 在后台线程执行更新（避免阻塞请求）
        import threading
        thread = threading.Thread(target=update_fund_rating)
        thread.daemon = True
        thread.start()

        return {
            "success": True,
            "message": "评级数据更新已启动，这可能需要1-2分钟，请稍后查看数据状态"
        }
    except Exception as e:
        logger.error(f"手动更新评级失败: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/admin/cache_status")
async def get_cache_status():
    """
    获取缓存统计信息
    """
    try:
        stats = fund_rank_cache.get_stats()
        return {
            "success": True,
            "data": stats
        }
    except Exception as e:
        logger.error(f"获取缓存状态失败: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/admin/clear_cache")
async def clear_cache():
    """
    清空所有缓存
    """
    try:
        fund_rank_cache.clear()
        return {
            "success": True,
            "message": "缓存已清空"
        }
    except Exception as e:
        logger.error(f"清空缓存失败: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


# Pydantic模型用于接收POST请求的JSON body
class FundRankFilterRequest(BaseModel):
    symbol: str = "全部"
    rating_min: Optional[float] = None
    return_1m_min: Optional[float] = None
    return_1m_max: Optional[float] = None
    return_3m_min: Optional[float] = None
    return_3m_max: Optional[float] = None
    return_6m_min: Optional[float] = None
    return_6m_max: Optional[float] = None
    return_1y_min: Optional[float] = None
    return_1y_max: Optional[float] = None
    fee_max: Optional[float] = None


@app.post("/api/fund_rank_filtered")
async def get_fund_rank_filtered(request: FundRankFilterRequest):
    """
    获取基金排行数据并根据条件筛选（带缓存）

    参数:
    - symbol: 基金类型（全部、股票型、混合型、债券型、指数型、QDII、LOF、FOF）
    - rating_min: 最低晨星评级（1-5星）
    - return_1m_min/max: 近1月收益率范围（%）
    - return_3m_min/max: 近3月收益率范围（%）
    - return_6m_min/max: 近6月收益率范围（%）
    - return_1y_min/max: 近1年收益率范围（%）
    - fee_max: 最大手续费率（%）
    """
    try:
        symbol = request.symbol
        rating_min = request.rating_min
        return_1m_min = request.return_1m_min
        return_1m_max = request.return_1m_max
        return_3m_min = request.return_3m_min
        return_3m_max = request.return_3m_max
        return_6m_min = request.return_6m_min
        return_6m_max = request.return_6m_max
        return_1y_min = request.return_1y_min
        return_1y_max = request.return_1y_max
        fee_max = request.fee_max
        import pandas as pd
        from db.database import get_db

        # DEBUG: 打印接收到的参数
        logger.info(f"[API DEBUG] 接收到的参数 - symbol: '{symbol}', type: {type(symbol)}")
        logger.info(f"[API DEBUG] request对象: {request}")

        # 尝试从数据库缓存获取
        cached_data = CacheHelper.get_fund_ranking(symbol)

        if cached_data is not None:
            # 使用数据库缓存数据
            rank_df = pd.DataFrame(cached_data)
            logger.info(f"[API] 使用数据库缓存数据: symbol={symbol}, 数据量={len(rank_df)}")
        else:
            # 从AkShare API获取
            logger.info(f"[API] 缓存未命中,从AkShare获取数据: symbol={symbol}")
            rank_df = ak.fund_open_fund_rank_em(symbol=symbol)
            logger.info(f"[API DEBUG] AkShare返回数据量: {len(rank_df) if rank_df is not None else 0}")

            if rank_df is not None and not rank_df.empty:
                # 添加基金类型列
                if symbol == '全部':
                    # 对于"全部"分类，从基金名称智能推断类型
                    rank_df['基金类型'] = rank_df['基金简称'].apply(infer_fund_type)
                else:
                    # 对于特定分类，使用查询参数作为类型
                    rank_df['基金类型'] = symbol
                # 存入数据库缓存（转为字典列表格式）
                cache_data = rank_df.to_dict('records')
                CacheHelper.set_fund_ranking(symbol, cache_data)

        if rank_df is None or rank_df.empty:
            return {"success": True, "data": [], "total": 0, "filtered": 0}

        original_count = len(rank_df)

        # 获取评级数据（如果需要按评级筛选）
        rating_dict = {}
        if rating_min is not None:
            conn = get_db()
            cursor = conn.cursor()
            cursor.execute('SELECT 代码, 晨星评级 FROM fund_rating_all WHERE 晨星评级 IS NOT NULL')
            rows = cursor.fetchall()
            rating_dict = {row['代码']: row['晨星评级'] for row in rows if row['晨星评级'] is not None}

        # 应用筛选条件
        filtered_indices = []

        for idx, row in rank_df.iterrows():
            # 评级筛选
            if rating_min is not None:
                fund_code = str(row.get('基金代码', ''))
                fund_rating = rating_dict.get(fund_code)
                if fund_rating is None or fund_rating < rating_min:
                    continue

            # 收益率筛选（需要将字符串转换为浮点数）
            def get_float_value(val):
                if val is None or val == '' or val == '-' or val == '---':
                    return None
                try:
                    return float(val)
                except:
                    return None

            # 近1月收益率筛选
            if return_1m_min is not None or return_1m_max is not None:
                val = get_float_value(row.get('近1月'))
                if val is None:
                    continue
                if return_1m_min is not None and val < return_1m_min:
                    continue
                if return_1m_max is not None and val > return_1m_max:
                    continue

            # 近3月收益率筛选
            if return_3m_min is not None or return_3m_max is not None:
                val = get_float_value(row.get('近3月'))
                if val is None:
                    continue
                if return_3m_min is not None and val < return_3m_min:
                    continue
                if return_3m_max is not None and val > return_3m_max:
                    continue

            # 近6月收益率筛选
            if return_6m_min is not None or return_6m_max is not None:
                val = get_float_value(row.get('近6月'))
                if val is None:
                    continue
                if return_6m_min is not None and val < return_6m_min:
                    continue
                if return_6m_max is not None and val > return_6m_max:
                    continue

            # 近1年收益率筛选
            if return_1y_min is not None or return_1y_max is not None:
                val = get_float_value(row.get('近1年'))
                if val is None:
                    continue
                if return_1y_min is not None and val < return_1y_min:
                    continue
                if return_1y_max is not None and val > return_1y_max:
                    continue

            # 手续费筛选（从评级表获取）
            if fee_max is not None:
                # 这里可以从评级表获取手续费信息
                # 由于排行榜数据不包含手续费，暂时跳过此筛选
                pass

            filtered_indices.append(idx)

        # 筛选后的数据
        filtered_df = rank_df.loc[filtered_indices]
        filtered_count = len(filtered_df)

        # 转换为JSON格式前,需要替换NaN和Inf值
        filtered_df = filtered_df.fillna('')  # 将NaN替换为空字符串
        result = filtered_df.to_dict('records')

        logger.info(f"基金筛选完成: 原始 {original_count} 条，筛选后 {filtered_count} 条")

        return {
            "success": True,
            "data": result,
            "total": original_count,
            "filtered": filtered_count
        }

    except Exception as e:
        logger.error(f"基金筛选失败: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/fund_etf_hist/{symbol}")
def get_fund_etf_hist(
    symbol: str,
    period: str = 'daily',
    adjust: str = 'qfq',
    start_date: Optional[str] = None,
    end_date: Optional[str] = None
):
    """
    获取ETF历史行情数据（K线数据）

    Args:
        symbol: 基金代码（如 510300）
        period: 时间周期 - daily(日k), weekly(周k), monthly(月k)
        adjust: 复权类型 - 空(不复权), qfq(前复权), hfq(后复权)
        start_date: 起始日期 (YYYY-MM-DD)，可选
        end_date: 结束日期 (YYYY-MM-DD)，可选

    Returns:
        {
            "success": true,
            "data": [...],
            "source": "cache|api",
            "total": 数据总条数,
            "symbol": 基金代码,
            "period": 周期,
            "adjust": 复权类型
        }

    缓存策略:
        - 日K线: 缓存60分钟（每天数据更新一次）
        - 周K线: 缓存120分钟
        - 月K线: 缓存180分钟
        - 查询缓存，如果有缓存数据且未过期，直接返回
        - 否则调用AkShare API，存入缓存
    """
    try:
        logger.info(f"[ETF历史行情] 请求: symbol={symbol}, period={period}, adjust={adjust}")

        conn = get_db()
        cursor = conn.cursor()

        # 确定缓存有效期（分钟）
        cache_ttl_map = {
            'daily': 60,    # 日K线缓存60分钟
            'weekly': 120,  # 周K线缓存120分钟
            'monthly': 180  # 月K线缓存180分钟
        }
        cache_ttl = cache_ttl_map.get(period, 60)

        # 检查缓存（根据symbol, period, adjust查询）
        # 注意：不考虑start_date/end_date，因为数据库存的是全量数据，前端筛选即可
        # 使用UTC时间比较（CURRENT_TIMESTAMP是UTC）
        cursor.execute('''
            SELECT 日期, 开盘, 收盘, 最高, 最低, 成交量, 成交额, 振幅, 涨跌幅, 涨跌额, 换手率, 更新时间
            FROM fund_etf_hist_cache
            WHERE 基金代码 = ?
            AND datetime(更新时间, '+' || ? || ' minutes') > datetime('now')
            ORDER BY 日期 ASC
        ''', (symbol, cache_ttl))

        cached_rows = cursor.fetchall()

        if cached_rows:
            # 缓存命中
            data = [dict(row) for row in cached_rows]

            # 根据前端请求的日期范围筛选
            if start_date:
                data = [r for r in data if r['日期'] >= start_date]
            if end_date:
                data = [r for r in data if r['日期'] <= end_date]

            logger.info(f"[ETF历史行情] 缓存命中: symbol={symbol}, 数据量={len(data)}")

            return {
                "success": True,
                "data": data,
                "source": "cache",
                "total": len(data),
                "symbol": symbol,
                "period": period,
                "adjust": adjust
            }

        # 缓存未命中，调用AkShare API
        logger.info(f"[ETF历史行情] 缓存未命中，调用AkShare API: symbol={symbol}")

        df = ak.fund_etf_hist_em(
            symbol=symbol,
            period=period,
            adjust=adjust
        )

        if df is None or df.empty:
            logger.warning(f"[ETF历史行情] API返回空数据: symbol={symbol}")
            return {
                "success": False,
                "error": "无数据",
                "data": [],
                "source": "api",
                "total": 0,
                "symbol": symbol
            }

        # 准备批量插入数据
        records = []
        for _, row in df.iterrows():
            records.append((
                symbol,
                str(row['日期']),
                float(row['开盘']) if row['开盘'] is not None else None,
                float(row['收盘']) if row['收盘'] is not None else None,
                float(row['最高']) if row['最高'] is not None else None,
                float(row['最低']) if row['最低'] is not None else None,
                int(row['成交量']) if row['成交量'] is not None else None,
                float(row['成交额']) if row['成交额'] is not None else None,
                float(row['振幅']) if row['振幅'] is not None else None,
                float(row['涨跌幅']) if row['涨跌幅'] is not None else None,
                float(row['涨跌额']) if row['涨跌额'] is not None else None,
                float(row['换手率']) if row['换手率'] is not None else None
            ))

        # 清空旧数据
        cursor.execute('DELETE FROM fund_etf_hist_cache WHERE 基金代码 = ?', (symbol,))
        conn.commit()

        # 批量插入新数据
        from db.database import execute_many
        insert_query = '''
            INSERT INTO fund_etf_hist_cache
            (基金代码, 日期, 开盘, 收盘, 最高, 最低, 成交量, 成交额, 振幅, 涨跌幅, 涨跌额, 换手率, 更新时间)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
        '''
        row_count = execute_many(insert_query, records)
        logger.info(f"[ETF历史行情] 数据已缓存: symbol={symbol}, 插入 {row_count} 条")

        # 转换为返回格式
        result_data = df.to_dict('records')

        # 根据前端请求的日期范围筛选
        if start_date:
            result_data = [r for r in result_data if r['日期'] >= start_date]
        if end_date:
            result_data = [r for r in result_data if r['日期'] <= end_date]

        logger.info(f"[ETF历史行情] API调用成功: symbol={symbol}, 总数据量={len(df)}, 返回={len(result_data)}")

        return {
            "success": True,
            "data": result_data,
            "source": "api",
            "total": len(result_data),
            "symbol": symbol,
            "period": period,
            "adjust": adjust
        }

    except Exception as e:
        logger.error(f"[ETF历史行情] 失败: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/fund_rating/{symbol}")
async def get_fund_rating(symbol: str):
    """
    获取基金评级信息

    参数:
    - symbol: 基金代码

    返回基金的各项评级信息(上海证券、招商证券、济安金信、晨星评级等)
    """
    try:
        from db.database import execute_query

        logger.info(f"[基金评级] 查询基金: {symbol}")

        # 从数据库查询评级数据
        query = '''
            SELECT
                代码, 简称, 基金经理, 基金公司,
                "5星评级家数",
                上海证券, 招商证券, 济安金信, 晨星评级,
                手续费, 类型, 更新时间
            FROM fund_rating_all
            WHERE 代码 = ?
        '''

        results = execute_query(query, (symbol,))

        if not results:
            logger.warning(f"[基金评级] 未找到基金: {symbol}")
            return {
                "success": True,
                "data": None,
                "source": "database",
                "message": "该基金暂无评级数据"
            }

        rating_data = results[0]

        logger.info(f"[基金评级] 成功获取基金评级: {symbol}")

        return {
            "success": True,
            "data": rating_data,
            "source": "database"
        }

    except Exception as e:
        logger.error(f"[基金评级] 失败: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/fund_dividend_rank")
async def get_fund_dividend_rank(
    limit: int = 100,
    sort_by: str = "累计分红"  # 支持: 累计分红, 累计次数
):
    """
    获取基金分红排行榜

    参数:
    - limit: 返回数量限制 (默认100)
    - sort_by: 排序字段 (累计分红 或 累计次数，默认累计分红)

    返回基金分红排行数据（东方财富数据源）
    """
    try:
        import akshare as ak

        logger.info(f"[分红排行] 查询参数 - limit: {limit}, sort_by: {sort_by}")

        # 从AkShare获取分红排行数据
        df = ak.fund_fh_rank_em()

        # 根据排序字段排序
        if sort_by == "累计次数":
            df = df.sort_values(by='累计次数', ascending=False)
        else:
            # 默认按累计分红排序（已经是这个顺序）
            df = df.sort_values(by='累计分红', ascending=False)

        # 限制返回数量
        if limit > 0:
            df = df.head(limit)

        # 转换为字典列表
        data = df.to_dict('records')

        logger.info(f"[分红排行] 成功获取 {len(data)} 条排行数据")

        return {
            "success": True,
            "count": len(data),
            "data": data,
            "sort_by": sort_by,
            "source": "eastmoney"
        }

    except Exception as e:
        logger.error(f"[分红排行] 失败: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/fund_dividend/{symbol}")
async def get_fund_dividend_history(symbol: str):
    """
    获取指定基金的历史分红记录

    参数:
    - symbol: 基金代码

    返回该基金所有历史分红记录,按除息日期倒序排列
    """
    try:
        from db.database import execute_query

        logger.info(f"[基金分红] 查询基金: {symbol}")

        # 从数据库查询分红记录
        query = '''
            SELECT
                基金代码, 基金简称, 权益登记日, 除息日期,
                分红, 分红发放日, 更新时间
            FROM fund_dividend
            WHERE 基金代码 = ?
            ORDER BY 除息日期 DESC
        '''

        results = execute_query(query, (symbol,))

        if not results:
            logger.warning(f"[基金分红] 未找到基金分红记录: {symbol}")
            return {
                "success": True,
                "data": [],
                "count": 0,
                "source": "database",
                "message": "该基金暂无分红记录"
            }

        logger.info(f"[基金分红] 成功获取 {len(results)} 条分红记录")

        return {
            "success": True,
            "data": results,
            "count": len(results),
            "source": "database"
        }

    except Exception as e:
        logger.error(f"[基金分红] 失败: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/fund_risk_indicators/{symbol}")
async def get_fund_risk_indicators(symbol: str, force_update: bool = False):
    """
    获取指定基金的雪球风险指标数据

    参数:
    - symbol: 基金代码
    - force_update: 是否强制更新数据（默认False，使用缓存）

    返回:
    {
        "success": true,
        "data": [
            {
                "周期": "近1年",
                "较同类风险收益比": 25,
                "较同类抗风险波动": 62,
                "年化波动率": 19.64,
                "年化夏普比率": 0.59,
                "最大回撤": 14.05
            },
            ...
        ],
        "count": 3,
        "source": "database"/"xueqiu"
    }
    """
    try:
        from datetime import datetime, timedelta
        from db.scheduler import update_fund_risk_indicators_single

        conn = get_db()
        cursor = conn.cursor()

        # 检查是否有缓存数据且未过期（TTL: 7天）
        cursor.execute('''
            SELECT * FROM fund_risk_indicators_xq
            WHERE 基金代码 = ?
            AND datetime(更新时间) > datetime('now', '-7 days')
            ORDER BY
                CASE 周期
                    WHEN '近1年' THEN 1
                    WHEN '近3年' THEN 2
                    WHEN '近5年' THEN 3
                    ELSE 4
                END
        ''', (symbol,))

        results = [dict(row) for row in cursor.fetchall()]

        # 如果没有数据或force_update=True，则更新数据
        if not results or force_update:
            logger.info(f"[风险指标] 正在更新基金 {symbol} 的风险指标数据...")
            success = update_fund_risk_indicators_single(symbol)

            if not success:
                return {
                    "success": False,
                    "message": f"基金 {symbol} 无风险指标数据",
                    "data": [],
                    "count": 0
                }

            # 重新查询数据
            cursor.execute('''
                SELECT * FROM fund_risk_indicators_xq
                WHERE 基金代码 = ?
                ORDER BY
                    CASE 周期
                        WHEN '近1年' THEN 1
                        WHEN '近3年' THEN 2
                        WHEN '近5年' THEN 3
                        ELSE 4
                    END
            ''', (symbol,))

            results = [dict(row) for row in cursor.fetchall()]
            source = "xueqiu"
        else:
            source = "database"

        # 移除不必要的字段
        for item in results:
            item.pop('id', None)
            item.pop('基金代码', None)
            item.pop('更新时间', None)

        logger.info(f"[风险指标] 成功获取 {len(results)} 条风险指标")

        return {
            "success": True,
            "data": results,
            "count": len(results),
            "source": source
        }

    except Exception as e:
        logger.error(f"[风险指标] 失败: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/fund_portfolio_hold")
async def get_fund_portfolio_hold(
    symbol: str,
    date: str = "20231231"  # 默认最近一个季度
):
    """
    获取基金重仓股票持仓明细

    参数:
    - symbol: 基金代码
    - date: 季度日期 (格式: YYYYMMDD，例如: 20231231)

    返回基金的前10大重仓股票明细（东方财富数据源）
    """
    try:
        import akshare as ak

        logger.info(f"[基金持仓] 查询参数 - symbol: {symbol}, date: {date}")

        # 从AkShare获取持仓数据
        df = ak.fund_portfolio_hold_em(symbol=symbol, date=date)

        # 转换为字典列表
        data = df.to_dict('records')

        logger.info(f"[基金持仓] 成功获取 {len(data)} 条持仓数据")

        return {
            "success": True,
            "count": len(data),
            "data": data,
            "fund_code": symbol,
            "date": date,
            "source": "eastmoney"
        }

    except Exception as e:
        logger.error(f"[基金持仓] 失败: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/fund_portfolio_change")
async def get_fund_portfolio_change(
    symbol: str,
    date: str = "20231231"  # 默认最近一个季度
):
    """
    获取基金持仓变动明细(累计买入)

    参数:
    - symbol: 基金代码
    - date: 季度日期 (格式: YYYYMMDD，例如: 20231231)

    返回基金的持仓变动明细（东方财富数据源）
    """
    try:
        import akshare as ak

        logger.info(f"[持仓变动] 查询参数 - symbol: {symbol}, date: {date}")

        # 从AkShare获取持仓变动数据
        df = ak.fund_portfolio_change_em(symbol=symbol, date=date)

        # 转换为字典列表
        data = df.to_dict('records')

        logger.info(f"[持仓变动] 成功获取 {len(data)} 条变动数据")

        return {
            "success": True,
            "count": len(data),
            "data": data,
            "fund_code": symbol,
            "date": date,
            "source": "eastmoney"
        }

    except KeyError as e:
        # akshare库在没有数据时可能抛出KeyError（如'序号'列不存在）
        logger.warning(f"[持仓变动] 该基金暂无持仓变动数据: {str(e)}")
        return {
            "success": True,
            "count": 0,
            "data": [],
            "fund_code": symbol,
            "date": date,
            "source": "eastmoney",
            "message": "该基金暂无持仓变动数据"
        }
    except Exception as e:
        error_msg = str(e)
        # 检查是否是数据不存在的常见错误
        if "no data" in error_msg.lower() or "empty" in error_msg.lower():
            logger.warning(f"[持仓变动] 该基金暂无持仓变动数据: {error_msg}")
            return {
                "success": True,
                "count": 0,
                "data": [],
                "fund_code": symbol,
                "date": date,
                "source": "eastmoney",
                "message": "该基金暂无持仓变动数据"
            }
        logger.error(f"[持仓变动] 失败: {error_msg}", exc_info=True)
        raise HTTPException(status_code=500, detail=error_msg)


@app.get("/api/fund_net_value_history/{symbol}")
async def get_fund_net_value_history(
    symbol: str,
    indicator: str = "单位净值走势"
):
    """
    获取基金完整历史净值数据

    参数:
    - symbol: 基金代码 (例如: 110011)
    - indicator: 数据类型,可选值:
        - "单位净值走势" (默认)
        - "累计净值走势"
        - "累计收益率走势"
        - "同类排名走势"
        - "同类排名百分比"

    返回:
    {
        "success": true,
        "symbol": "110011",
        "indicator": "单位净值走势",
        "total": 4196,
        "data": [
            {
                "净值日期": "2008-06-19",
                "单位净值": 1.0000,
                "日增长率": 0.0000
            },
            ...
        ],
        "source": "eastmoney"
    }

    数据来源: 东方财富网 - fund_open_fund_info_em API
    缓存策略: 10分钟
    """
    try:
        logger.info(f"[历史净值] 查询参数 - symbol: {symbol}, indicator: {indicator}")

        # 调用AkShare API
        df = ak.fund_open_fund_info_em(symbol=symbol, indicator=indicator)

        if df is None or df.empty:
            logger.warning(f"[历史净值] 基金 {symbol} 没有{indicator}数据")
            return {
                "success": True,
                "symbol": symbol,
                "indicator": indicator,
                "total": 0,
                "data": [],
                "source": "eastmoney",
                "message": f"该基金暂无{indicator}数据"
            }

        # 反转数据顺序(从新到旧)
        df = df.iloc[::-1].reset_index(drop=True)

        # 转换为字典列表
        data = df.to_dict('records')

        logger.info(f"[历史净值] 成功获取 {len(data)} 条{indicator}数据(已按日期降序排列)")

        return {
            "success": True,
            "symbol": symbol,
            "indicator": indicator,
            "total": len(data),
            "data": data,
            "source": "eastmoney"
        }

    except Exception as e:
        logger.error(f"[历史净值] 失败 [{symbol}]: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/fund_industry_allocation/{symbol}")
async def get_fund_industry_allocation(symbol: str):
    """
    获取基金行业配置数据（带错误处理的包装）

    参数:
    - symbol: 基金代码 (例如: 007955)

    返回:
    {
        "success": true,
        "count": 10,
        "data": [...],
        "fund_code": "007955",
        "source": "eastmoney"
    }

    数据来源: 东方财富网
    """
    try:
        logger.info(f"[行业配置] 查询参数 - symbol: {symbol}")

        df = ak.fund_portfolio_industry_allocation_em(symbol=symbol)

        if df is None or df.empty:
            logger.warning(f"[行业配置] 基金 {symbol} 暂无行业配置数据")
            return {
                "success": True,
                "count": 0,
                "data": [],
                "fund_code": symbol,
                "source": "eastmoney",
                "message": "该基金暂无行业配置数据"
            }

        data = df.to_dict('records')
        logger.info(f"[行业配置] 成功获取 {len(data)} 条行业配置数据")

        return {
            "success": True,
            "count": len(data),
            "data": data,
            "fund_code": symbol,
            "source": "eastmoney"
        }

    except KeyError as e:
        # akshare库在没有数据时可能抛出KeyError
        logger.warning(f"[行业配置] 该基金暂无行业配置数据: {str(e)}")
        return {
            "success": True,
            "count": 0,
            "data": [],
            "fund_code": symbol,
            "source": "eastmoney",
            "message": "该基金暂无行业配置数据"
        }
    except ValueError as e:
        # akshare库在数据格式不匹配时可能抛出ValueError（如列数不匹配）
        error_msg = str(e)
        if "length mismatch" in error_msg.lower() or "length of values" in error_msg.lower():
            logger.warning(f"[行业配置] 该基金暂无行业配置数据（数据格式问题）: {error_msg}")
            return {
                "success": True,
                "count": 0,
                "data": [],
                "fund_code": symbol,
                "source": "eastmoney",
                "message": "该基金暂无行业配置数据"
            }
        logger.error(f"[行业配置] 失败: {error_msg}", exc_info=True)
        raise HTTPException(status_code=500, detail=error_msg)
    except Exception as e:
        error_msg = str(e)
        if "no data" in error_msg.lower() or "empty" in error_msg.lower():
            logger.warning(f"[行业配置] 该基金暂无行业配置数据: {error_msg}")
            return {
                "success": True,
                "count": 0,
                "data": [],
                "fund_code": symbol,
                "source": "eastmoney",
                "message": "该基金暂无行业配置数据"
            }
        logger.error(f"[行业配置] 失败: {error_msg}", exc_info=True)
        raise HTTPException(status_code=500, detail=error_msg)


# ========== 基金申购赎回状态 API ==========

@app.get("/api/fund_purchase_status")
async def get_fund_purchase_status(
    purchase_status: Optional[str] = None,
    redeem_status: Optional[str] = None,
    fund_type: Optional[str] = None,
    limit: int = 100,
    offset: int = 0
):
    """
    获取基金申购赎回状态列表

    查询参数:
    - purchase_status: 申购状态筛选（开放申购、暂停申购、封闭期等）
    - redeem_status: 赎回状态筛选（开放赎回、暂停赎回、封闭期等）
    - fund_type: 基金类型筛选
    - limit: 返回记录数限制（默认100）
    - offset: 偏移量（分页用，默认0）
    """
    try:
        conn = get_db()
        cursor = conn.cursor()

        # 构建查询条件
        conditions = []
        params = []

        if purchase_status:
            conditions.append("申购状态 = ?")
            params.append(purchase_status)

        if redeem_status:
            conditions.append("赎回状态 = ?")
            params.append(redeem_status)

        if fund_type:
            conditions.append("基金类型 = ?")
            params.append(fund_type)

        where_clause = " AND ".join(conditions) if conditions else "1=1"

        # 查询总数
        count_query = f"SELECT COUNT(*) as total FROM fund_purchase_status WHERE {where_clause}"
        cursor.execute(count_query, params)
        total = cursor.fetchone()['total']

        # 查询数据
        query = f"""
            SELECT
                序号, 基金代码, 基金简称, 基金类型,
                最新净值万份收益, 最新净值万份收益报告时间,
                申购状态, 赎回状态, 下一开放日,
                购买起点, 日累计限定金额, 手续费, 更新时间
            FROM fund_purchase_status
            WHERE {where_clause}
            ORDER BY 序号 ASC
            LIMIT ? OFFSET ?
        """
        params.extend([limit, offset])
        cursor.execute(query, params)
        rows = cursor.fetchall()

        data = [dict(row) for row in rows]

        logger.info(f"[申购赎回状态] 查询成功: {len(data)} 条记录")
        return {
            "success": True,
            "total": total,
            "count": len(data),
            "limit": limit,
            "offset": offset,
            "data": data,
            "source": "database",
            "message": f"成功获取 {len(data)} 条申购赎回状态记录"
        }

    except Exception as e:
        error_msg = str(e)
        logger.error(f"[申购赎回状态] 查询失败: {error_msg}", exc_info=True)
        raise HTTPException(status_code=500, detail=error_msg)


@app.get("/api/fund_purchase_status/{symbol}")
async def get_fund_purchase_status_by_code(symbol: str):
    """
    根据基金代码查询申购赎回状态

    路径参数:
    - symbol: 基金代码（如：110011）
    """
    try:
        conn = get_db()
        cursor = conn.cursor()

        query = """
            SELECT
                序号, 基金代码, 基金简称, 基金类型,
                最新净值万份收益, 最新净值万份收益报告时间,
                申购状态, 赎回状态, 下一开放日,
                购买起点, 日累计限定金额, 手续费, 更新时间
            FROM fund_purchase_status
            WHERE 基金代码 = ?
        """
        cursor.execute(query, (symbol,))
        row = cursor.fetchone()

        if not row:
            logger.warning(f"[申购赎回状态] 基金 {symbol} 未找到")
            return {
                "success": False,
                "data": None,
                "fund_code": symbol,
                "message": "该基金暂无申购赎回状态数据"
            }

        data = dict(row)
        logger.info(f"[申购赎回状态] 基金 {symbol} 查询成功")
        return {
            "success": True,
            "data": data,
            "fund_code": symbol,
            "source": "database",
            "message": "成功获取基金申购赎回状态"
        }

    except Exception as e:
        error_msg = str(e)
        logger.error(f"[申购赎回状态] 基金 {symbol} 查询失败: {error_msg}", exc_info=True)
        raise HTTPException(status_code=500, detail=error_msg)


@app.get("/api/fund_purchase_status_stats")
async def get_fund_purchase_status_stats():
    """
    获取申购赎回状态统计信息
    """
    try:
        conn = get_db()
        cursor = conn.cursor()

        # 统计各种申购状态的数量
        cursor.execute("""
            SELECT
                申购状态,
                COUNT(*) as count
            FROM fund_purchase_status
            GROUP BY 申购状态
            ORDER BY count DESC
        """)
        purchase_stats = [dict(row) for row in cursor.fetchall()]

        # 统计各种赎回状态的数量
        cursor.execute("""
            SELECT
                赎回状态,
                COUNT(*) as count
            FROM fund_purchase_status
            GROUP BY 赎回状态
            ORDER BY count DESC
        """)
        redeem_stats = [dict(row) for row in cursor.fetchall()]

        # 统计基金类型分布
        cursor.execute("""
            SELECT
                基金类型,
                COUNT(*) as count
            FROM fund_purchase_status
            GROUP BY 基金类型
            ORDER BY count DESC
        """)
        type_stats = [dict(row) for row in cursor.fetchall()]

        # 获取最新更新时间
        cursor.execute("SELECT MAX(更新时间) as latest_update FROM fund_purchase_status")
        latest_update = cursor.fetchone()['latest_update']

        # 获取总记录数
        cursor.execute("SELECT COUNT(*) as total FROM fund_purchase_status")
        total = cursor.fetchone()['total']

        logger.info("[申购赎回状态] 统计查询成功")
        return {
            "success": True,
            "data": {
                "total_funds": total,
                "purchase_status_distribution": purchase_stats,
                "redeem_status_distribution": redeem_stats,
                "fund_type_distribution": type_stats,
                "latest_update": latest_update
            },
            "message": "成功获取申购赎回状态统计"
        }

    except Exception as e:
        error_msg = str(e)
        logger.error(f"[申购赎回状态] 统计查询失败: {error_msg}", exc_info=True)
        raise HTTPException(status_code=500, detail=error_msg)


# ========== 基金公司规模数据 API ==========

@app.get("/api/fund_company_aum")
async def get_fund_company_aum(
    limit: int = 100,
    offset: int = 0,
    min_scale: Optional[float] = None,
    sort_by: str = '全部管理规模'
):
    """
    获取基金公司规模排行榜

    Args:
        limit: 返回记录数限制 (默认100)
        offset: 偏移量 (默认0)
        min_scale: 最小管理规模筛选 (亿元)
        sort_by: 排序字段 (全部管理规模/全部基金数/全部经理数，默认: 全部管理规模)
    """
    try:
        conn = get_db()
        cursor = conn.cursor()

        # 构建WHERE子句
        where_clauses = []
        params = []

        if min_scale is not None:
            where_clauses.append("全部管理规模 >= ?")
            params.append(min_scale)

        where_clause = " AND ".join(where_clauses) if where_clauses else "1=1"

        # 构建ORDER BY子句（确保安全）
        allowed_sort_fields = ['全部管理规模', '全部基金数', '全部经理数', '成立时间']
        if sort_by not in allowed_sort_fields:
            sort_by = '全部管理规模'

        # 获取总记录数
        count_query = f"SELECT COUNT(*) as total FROM fund_company_aum WHERE {where_clause}"
        cursor.execute(count_query, params)
        total = cursor.fetchone()['total']

        # 查询数据
        query = f"""
            SELECT * FROM fund_company_aum
            WHERE {where_clause}
            ORDER BY {sort_by} DESC
            LIMIT ? OFFSET ?
        """
        cursor.execute(query, params + [limit, offset])
        rows = [dict(row) for row in cursor.fetchall()]

        logger.info(f"[基金公司规模] 查询成功: {len(rows)} 条记录")
        return {
            "success": True,
            "total": total,
            "count": len(rows),
            "limit": limit,
            "offset": offset,
            "data": rows,
            "source": "database",
            "message": f"成功获取 {len(rows)} 条基金公司规模数据"
        }

    except Exception as e:
        error_msg = str(e)
        logger.error(f"[基金公司规模] 查询失败: {error_msg}", exc_info=True)
        raise HTTPException(status_code=500, detail=error_msg)


@app.get("/api/fund_company_aum/{company_name}")
async def get_fund_company_aum_by_name(company_name: str):
    """
    根据基金公司名称查询规模数据
    """
    try:
        conn = get_db()
        cursor = conn.cursor()

        cursor.execute(
            "SELECT * FROM fund_company_aum WHERE 基金公司 = ?",
            (company_name,)
        )
        row = cursor.fetchone()

        if not row:
            logger.warning(f"[基金公司规模] 未找到公司: {company_name}")
            return {
                "success": False,
                "data": None,
                "company_name": company_name,
                "message": f"未找到基金公司: {company_name}"
            }

        logger.info(f"[基金公司规模] 查询成功: {company_name}")
        return {
            "success": True,
            "data": dict(row),
            "company_name": company_name,
            "source": "database",
            "message": "成功获取基金公司规模数据"
        }

    except Exception as e:
        error_msg = str(e)
        logger.error(f"[基金公司规模] 查询失败: {error_msg}", exc_info=True)
        raise HTTPException(status_code=500, detail=error_msg)


@app.get("/api/fund_company_aum_hist/{company_name}")
async def get_fund_company_aum_hist(company_name: str):
    """
    获取基金公司规模历史数据（年度趋势）
    """
    try:
        conn = get_db()
        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT * FROM fund_company_aum_hist
            WHERE 基金公司 = ?
            ORDER BY 年份 DESC
            """,
            (company_name,)
        )
        rows = [dict(row) for row in cursor.fetchall()]

        if not rows:
            logger.warning(f"[基金公司历史规模] 未找到公司: {company_name}")
            return {
                "success": False,
                "data": [],
                "company_name": company_name,
                "message": f"未找到基金公司历史数据: {company_name}"
            }

        logger.info(f"[基金公司历史规模] 查询成功: {company_name}, {len(rows)} 年数据")
        return {
            "success": True,
            "data": rows,
            "count": len(rows),
            "company_name": company_name,
            "source": "database",
            "message": f"成功获取 {len(rows)} 年历史规模数据"
        }

    except Exception as e:
        error_msg = str(e)
        logger.error(f"[基金公司历史规模] 查询失败: {error_msg}", exc_info=True)
        raise HTTPException(status_code=500, detail=error_msg)


@app.get("/api/fund_market_trend")
async def get_fund_market_trend():
    """
    获取基金市场规模趋势数据（季度数据）
    """
    try:
        conn = get_db()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT * FROM fund_market_aum_trend
            ORDER BY 日期 DESC
        """)
        rows = [dict(row) for row in cursor.fetchall()]

        if not rows:
            logger.warning("[市场规模趋势] 数据为空")
            return {
                "success": False,
                "data": [],
                "message": "暂无市场规模趋势数据"
            }

        # 转换为前端图表友好格式
        chart_data = {
            "dates": [row['日期'] for row in reversed(rows)],
            "values": [row['市场总规模'] for row in reversed(rows)]
        }

        logger.info(f"[市场规模趋势] 查询成功: {len(rows)} 条记录")
        return {
            "success": True,
            "data": rows,
            "chart_data": chart_data,
            "count": len(rows),
            "source": "database",
            "message": f"成功获取 {len(rows)} 条市场规模趋势数据"
        }

    except Exception as e:
        error_msg = str(e)
        logger.error(f"[市场规模趋势] 查询失败: {error_msg}", exc_info=True)
        raise HTTPException(status_code=500, detail=error_msg)


@app.get("/api/fund_company_stats")
async def get_fund_company_stats():
    """
    获取基金公司数据统计信息
    """
    try:
        conn = get_db()
        cursor = conn.cursor()

        # 统计基金公司总数
        cursor.execute("SELECT COUNT(*) as total FROM fund_company_aum")
        total_companies = cursor.fetchone()['total']

        # 统计各规模段公司数量
        cursor.execute("""
            SELECT
                CASE
                    WHEN 全部管理规模 >= 5000 THEN '超大型(>5000亿)'
                    WHEN 全部管理规模 >= 2000 THEN '大型(2000-5000亿)'
                    WHEN 全部管理规模 >= 1000 THEN '中大型(1000-2000亿)'
                    WHEN 全部管理规模 >= 500 THEN '中型(500-1000亿)'
                    WHEN 全部管理规模 >= 200 THEN '中小型(200-500亿)'
                    ELSE '小型(<200亿)'
                END as scale_level,
                COUNT(*) as count
            FROM fund_company_aum
            GROUP BY scale_level
            ORDER BY MIN(全部管理规模) DESC
        """)
        scale_distribution = [dict(row) for row in cursor.fetchall()]

        # TOP 10 基金公司
        cursor.execute("""
            SELECT 基金公司, 全部管理规模, 全部基金数, 全部经理数
            FROM fund_company_aum
            ORDER BY 全部管理规模 DESC
            LIMIT 10
        """)
        top_companies = [dict(row) for row in cursor.fetchall()]

        # 获取最新更新时间
        cursor.execute("SELECT MAX(更新时间) as latest_update FROM fund_company_aum")
        latest_update = cursor.fetchone()['latest_update']

        logger.info("[基金公司统计] 查询成功")
        return {
            "success": True,
            "data": {
                "total_companies": total_companies,
                "scale_distribution": scale_distribution,
                "top_10_companies": top_companies,
                "latest_update": latest_update
            },
            "message": "成功获取基金公司统计数据"
        }

    except Exception as e:
        error_msg = str(e)
        logger.error(f"[基金公司统计] 查询失败: {error_msg}", exc_info=True)
        raise HTTPException(status_code=500, detail=error_msg)


# ========== 数据导出API端点 ==========

@app.post("/api/export/ranking")
async def export_fund_ranking(
    filters: dict = Body(...),
    format: str = Body("csv", description="导出格式: csv 或 excel")
):
    """
    导出基金排行数据（支持CSV和Excel）

    请求体示例:
    {
        "filters": {
            "基金类型": "股票型",
            "minNetWorth": 1.0,
            "maxNetWorth": 10.0
        },
        "format": "csv"  # 或 "excel"
    }
    """
    try:
        logger.info(f"[导出排行数据] 开始导出, 格式={format}, 筛选条件={filters}")

        # 从AkShare获取基金排行数据
        df = ak.fund_open_fund_rank_em(symbol="全部")

        # 转换为列表字典
        data = df.to_dict('records')

        # 应用筛选条件
        if filters.get('基金类型') and filters['基金类型'] != '全部':
            data = [row for row in data if row.get('基金类型') == filters['基金类型']]

        if filters.get('minNetWorth'):
            min_val = float(filters['minNetWorth'])
            data = [row for row in data if row.get('单位净值') and float(row.get('单位净值', 0)) >= min_val]

        if filters.get('maxNetWorth'):
            max_val = float(filters['maxNetWorth'])
            data = [row for row in data if row.get('单位净值') and float(row.get('单位净值', 0)) <= max_val]

        if not data:
            raise HTTPException(status_code=404, detail="没有找到符合条件的数据")

        # 根据format格式导出
        if format.lower() == "excel":
            file_stream, filename = export_to_excel(data, "基金排行数据", "基金排行")
            media_type = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        else:
            file_stream, filename = export_to_csv(data, "基金排行数据")
            media_type = "text/csv"

        logger.info(f"[导出排行数据] 导出成功, 文件={filename}, 记录数={len(data)}")

        # 使用RFC 5987格式处理中文文件名
        encoded_filename = quote(filename)
        return StreamingResponse(
            file_stream,
            media_type=media_type,
            headers={
                "Content-Disposition": f"attachment; filename*=UTF-8''{encoded_filename}"
            }
        )

    except HTTPException:
        raise
    except Exception as e:
        error_msg = str(e)
        logger.error(f"[导出排行数据] 导出失败: {error_msg}", exc_info=True)
        raise HTTPException(status_code=500, detail=error_msg)


@app.get("/api/export/company_ranking/{format}")
async def export_company_ranking(format: str):
    """
    导出基金公司规模排行数据

    Args:
        format: 导出格式 (csv 或 excel)
    """
    try:
        logger.info(f"[导出公司排行] 开始导出, 格式={format}")

        # 从AkShare获取基金公司规模数据
        df = ak.fund_scale_open_sina()

        # 转换为列表字典
        data = df.to_dict('records')

        if not data:
            raise HTTPException(status_code=404, detail="没有找到数据")

        # 根据format格式导出
        if format.lower() == "excel":
            file_stream, filename = export_to_excel(data, "基金公司规模排行", "公司排行")
            media_type = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        else:
            file_stream, filename = export_to_csv(data, "基金公司规模排行")
            media_type = "text/csv"

        logger.info(f"[导出公司排行] 导出成功, 文件={filename}, 记录数={len(data)}")

        # 使用RFC 5987格式处理中文文件名
        encoded_filename = quote(filename)
        return StreamingResponse(
            file_stream,
            media_type=media_type,
            headers={
                "Content-Disposition": f"attachment; filename*=UTF-8''{encoded_filename}"
            }
        )

    except HTTPException:
        raise
    except Exception as e:
        error_msg = str(e)
        logger.error(f"[导出公司排行] 导出失败: {error_msg}", exc_info=True)
        raise HTTPException(status_code=500, detail=error_msg)


@app.get("/api/export/dividend_rank/{format}")
async def export_dividend_rank(format: str):
    """
    导出基金分红排行数据

    Args:
        format: 导出格式 (csv 或 excel)
    """
    try:
        logger.info(f"[导出分红排行] 开始导出, 格式={format}")

        # 从AkShare获取基金分红排行数据
        df = ak.fund_fh_rank_em()

        # 转换为列表字典
        data = df.to_dict('records')

        if not data:
            raise HTTPException(status_code=404, detail="没有找到数据")

        # 根据format格式导出
        if format.lower() == "excel":
            file_stream, filename = export_to_excel(data, "基金分红排行", "分红排行")
            media_type = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        else:
            file_stream, filename = export_to_csv(data, "基金分红排行")
            media_type = "text/csv"

        logger.info(f"[导出分红排行] 导出成功, 文件={filename}, 记录数={len(data)}")

        # 使用RFC 5987格式处理中文文件名
        encoded_filename = quote(filename)
        return StreamingResponse(
            file_stream,
            media_type=media_type,
            headers={
                "Content-Disposition": f"attachment; filename*=UTF-8''{encoded_filename}"
            }
        )

    except HTTPException:
        raise
    except Exception as e:
        error_msg = str(e)
        logger.error(f"[导出分红排行] 导出失败: {error_msg}", exc_info=True)
        raise HTTPException(status_code=500, detail=error_msg)


if __name__ == "__main__":
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8080,
        log_level="info"
    )
