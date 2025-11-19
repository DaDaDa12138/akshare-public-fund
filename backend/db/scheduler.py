"""
定时任务调度器
"""
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.interval import IntervalTrigger
from datetime import datetime, time
import akshare as ak
from .database import get_db, execute_many
from .cache_helper import CacheHelper
import logging

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 全局调度器实例
scheduler: BackgroundScheduler = None


def update_fund_estimation():
    """
    更新基金实时估值数据
    """
    try:
        start_time = datetime.now()
        logger.info("[定时任务] 开始更新基金估值数据...")

        # 调用 AkShare API 获取全量估值数据
        df = ak.fund_value_estimation_em()

        if df is None or df.empty:
            logger.warning("[定时任务] 获取估值数据为空")
            return

        # 准备批量插入的数据
        records = []
        for _, row in df.iterrows():
            # 提取估算值和单位净值（字段名包含日期，需要动态查找）
            估算值 = None
            估算增长率 = None
            单位净值 = None
            日增长率 = None
            估算时间 = None

            for col in row.index:
                if '估算数据-估算值' in col:
                    估算值 = str(row[col]) if row[col] is not None else None
                elif '估算数据-估算增长率' in col:
                    估算增长率 = str(row[col]) if row[col] is not None else None
                    # 提取估算时间（从列名中）
                    if 估算时间 is None:
                        date_part = col.split('-')[0]  # 如 "2025-11-15"
                        估算时间 = f"{date_part} {datetime.now().strftime('%H:%M')}"
                elif '公布数据-单位净值' in col:
                    单位净值 = str(row[col]) if row[col] is not None else None
                elif '公布数据-日增长率' in col:
                    日增长率 = str(row[col]) if row[col] is not None else None

            records.append((
                row.get('基金代码', ''),
                row.get('基金名称', ''),
                估算时间,
                估算值,
                估算增长率,
                单位净值,
                日增长率,
                row.get('估算偏差', '')
            ))

        # 批量更新数据库（使用 REPLACE INTO 自动覆盖）
        query = '''
            REPLACE INTO fund_value_estimation
            (基金代码, 基金名称, 估算时间, 估算值, 估算增长率, 单位净值, 日增长率, 估算偏差, 更新时间)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
        '''

        row_count = execute_many(query, records)

        elapsed = (datetime.now() - start_time).total_seconds()
        logger.info(f"[定时任务] 估值更新完成: {row_count} 条记录，耗时 {elapsed:.2f}秒")

    except Exception as e:
        logger.error(f"[定时任务] 估值更新失败: {str(e)}", exc_info=True)


def update_fund_dividend():
    """
    更新基金分红数据（每周执行一次）
    """
    try:
        start_time = datetime.now()
        logger.info("[定时任务] 开始更新基金分红数据...")

        # 调用 AkShare API 获取全量分红数据
        df = ak.fund_fh_em()

        if df is None or df.empty:
            logger.warning("[定时任务] 获取分红数据为空")
            return

        logger.info(f"[定时任务] 获取到原始数据 {len(df)} 条分红记录")

        # 去重（按基金代码和除息日期去重，保留第一条）
        df = df.drop_duplicates(subset=['基金代码', '除息日期'], keep='first')
        logger.info(f"[定时任务] 去重后数据 {len(df)} 条分红记录")

        # 准备批量插入的数据
        records = []
        for _, row in df.iterrows():
            records.append((
                str(row.get('基金代码', '')),
                str(row.get('基金简称', '')),
                str(row.get('权益登记日', '')),
                str(row.get('除息日期', '')),
                float(row.get('分红', 0)),
                str(row.get('分红发放日', ''))
            ))

        # 先清空旧数据
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute('DELETE FROM fund_dividend')
        conn.commit()
        logger.info("[定时任务] 已清空旧分红数据")

        # 批量插入新数据
        query = '''
            INSERT INTO fund_dividend
            (基金代码, 基金简称, 权益登记日, 除息日期, 分红, 分红发放日, 更新时间)
            VALUES (?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
        '''

        row_count = execute_many(query, records)

        elapsed = (datetime.now() - start_time).total_seconds()
        logger.info(f"[定时任务] 分红数据更新完成: {row_count} 条记录，耗时 {elapsed:.2f}秒")

    except Exception as e:
        logger.error(f"[定时任务] 分红数据更新失败: {str(e)}", exc_info=True)


def update_fund_rating():
    """
    更新基金评级数据（每周执行一次）
    """
    try:
        start_time = datetime.now()
        logger.info("[定时任务] 开始更新基金评级数据...")

        # 调用 AkShare API 获取全量评级数据
        df = ak.fund_rating_all()

        if df is None or df.empty:
            logger.warning("[定时任务] 获取评级数据为空")
            return

        logger.info(f"[定时任务] 获取到 {len(df)} 条评级记录")

        # 准备批量插入的数据
        records = []
        for _, row in df.iterrows():
            records.append((
                str(row.get('代码', '')),
                str(row.get('简称', '')),
                str(row.get('基金经理', '')),
                str(row.get('基金公司', '')),
                int(row.get('5星评级家数', 0)),
                float(row.get('上海证券')) if row.get('上海证券') is not None else None,
                float(row.get('招商证券')) if row.get('招商证券') is not None else None,
                float(row.get('济安金信')) if row.get('济安金信') is not None else None,
                float(row.get('晨星评级')) if row.get('晨星评级') is not None else None,
                float(row.get('手续费', 0)),
                str(row.get('类型', ''))
            ))

        # 先清空旧数据
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute('DELETE FROM fund_rating_all')
        conn.commit()
        logger.info("[定时任务] 已清空旧评级数据")

        # 批量插入新数据
        query = '''
            INSERT INTO fund_rating_all
            (代码, 简称, 基金经理, 基金公司, "5星评级家数", 上海证券, 招商证券, 济安金信, 晨星评级, 手续费, 类型, 更新时间)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
        '''

        row_count = execute_many(query, records)

        elapsed = (datetime.now() - start_time).total_seconds()
        logger.info(f"[定时任务] 评级数据更新完成: {row_count} 条记录，耗时 {elapsed:.2f}秒")

    except Exception as e:
        logger.error(f"[定时任务] 评级数据更新失败: {str(e)}", exc_info=True)


def update_money_fund():
    """
    更新货币基金数据（每个交易日执行）
    """
    try:
        start_time = datetime.now()
        logger.info("[定时任务] 开始更新货币基金数据...")

        # 调用 AkShare API 获取货币基金数据
        df = ak.fund_money_fund_daily_em()

        if df is None or df.empty:
            logger.warning("[定时任务] 获取货币基金数据为空")
            return

        logger.info(f"[定时任务] 获取到 {len(df)} 条货币基金记录")

        # 解析动态字段名（日期格式：YYYY-MM-DD-字段名）
        date_columns = [col for col in df.columns if '-' in str(col) and str(col).count('-') >= 3]

        if not date_columns:
            logger.error("[定时任务] 未找到日期列")
            return

        # 提取日期部分并获取最新日期
        dates = sorted(set([str(col)[:10] for col in date_columns if len(str(col)) >= 10]), reverse=True)
        latest_date = dates[0] if dates else None

        logger.info(f"[定时任务] 使用最新日期: {latest_date}")

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

        # 准备批量插入的数据
        records = []
        for _, row in df.iterrows():
            try:
                # 解析数值
                wan_fen_shouyi = row.get(field_mapping.get('万份收益', ''), None)
                qi_ri_nianhua = row.get(field_mapping.get('七日年化', ''), None)

                # 转换万份收益为浮点数
                try:
                    wan_fen_shouyi = float(wan_fen_shouyi) if wan_fen_shouyi not in [None, '', '--'] else None
                except (ValueError, TypeError):
                    wan_fen_shouyi = None

                # 七日年化保持字符串格式
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
                logger.warning(f"[定时任务] 处理行数据失败: {row_error}")
                continue

        # 先清空旧数据
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute('DELETE FROM fund_money_cache')
        conn.commit()
        logger.info("[定时任务] 已清空旧货币基金数据")

        # 批量插入新数据
        if records:
            cursor.executemany('''
                INSERT OR REPLACE INTO fund_money_cache
                (基金代码, 基金简称, 万份收益, 七日年化, 单位净值, 日涨幅,
                 成立日期, 基金经理, 手续费, 可购全部, 更新时间)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
            ''', records)
            conn.commit()

            elapsed = (datetime.now() - start_time).total_seconds()
            logger.info(f"[定时任务] 货币基金数据更新完成: {len(records)} 条记录，耗时 {elapsed:.2f}秒")

    except Exception as e:
        logger.error(f"[定时任务] 货币基金数据更新失败: {str(e)}", exc_info=True)


def update_fund_purchase_status():
    """
    更新基金申购赎回状态数据（每日更新）
    """
    try:
        start_time = datetime.now()
        logger.info("[定时任务] 开始更新基金申购赎回状态...")

        # 调用 AkShare API 获取全量申购赎回数据
        df = ak.fund_purchase_em()

        if df is None or df.empty:
            logger.warning("[定时任务] 获取申购赎回数据为空")
            return

        logger.info(f"[定时任务] 获取到 {len(df)} 条申购赎回记录")

        # 准备批量插入的数据
        records = []
        for _, row in df.iterrows():
            records.append((
                int(row.get('序号', 0)),
                str(row.get('基金代码', '')),
                str(row.get('基金简称', '')),
                str(row.get('基金类型', '')),
                str(row.get('最新净值/万份收益', '')),
                str(row.get('最新净值/万份收益-报告时间', '')),
                str(row.get('申购状态', '')),
                str(row.get('赎回状态', '')),
                str(row.get('下一开放日', '')),
                str(row.get('购买起点', '')),
                str(row.get('日累计限定金额', '')),
                str(row.get('手续费', ''))
            ))

        # 先清空旧数据
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute('DELETE FROM fund_purchase_status')
        conn.commit()
        logger.info("[定时任务] 已清空旧申购赎回数据")

        # 批量插入新数据
        query = '''
            INSERT INTO fund_purchase_status
            (序号, 基金代码, 基金简称, 基金类型, 最新净值万份收益, 最新净值万份收益报告时间,
             申购状态, 赎回状态, 下一开放日, 购买起点, 日累计限定金额, 手续费, 更新时间)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
        '''

        row_count = execute_many(query, records)

        elapsed = (datetime.now() - start_time).total_seconds()
        logger.info(f"[定时任务] 申购赎回数据更新完成: {row_count} 条记录，耗时 {elapsed:.2f}秒")

    except Exception as e:
        logger.error(f"[定时任务] 申购赎回数据更新失败: {str(e)}", exc_info=True)


def update_fund_company_aum():
    """
    更新基金公司规模数据（每周更新）
    """
    try:
        start_time = datetime.now()
        logger.info("[定时任务] 开始更新基金公司规模数据...")

        # 调用 AkShare API 获取基金公司规模数据
        df = ak.fund_aum_em()

        if df is None or df.empty:
            logger.warning("[定时任务] 获取基金公司规模数据为空")
            return

        logger.info(f"[定时任务] 获取到 {len(df)} 家基金公司规模数据")

        # 准备批量插入的数据
        records = []
        for _, row in df.iterrows():
            records.append((
                int(row.get('序号', 0)),
                str(row.get('基金公司', '')),
                str(row.get('成立时间', '')),
                float(row.get('全部管理规模', 0)),
                int(row.get('全部基金数', 0)),
                int(row.get('全部经理数', 0)),
                str(row.get('更新日期', ''))
            ))

        # 先清空旧数据
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute('DELETE FROM fund_company_aum')
        conn.commit()

        # 批量插入新数据
        query = '''
            INSERT INTO fund_company_aum
            (序号, 基金公司, 成立时间, 全部管理规模, 全部基金数, 全部经理数, 更新日期, 更新时间)
            VALUES (?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
        '''

        row_count = execute_many(query, records)

        elapsed = (datetime.now() - start_time).total_seconds()
        logger.info(f"[定时任务] 基金公司规模数据更新完成: {row_count} 条记录，耗时 {elapsed:.2f}秒")

    except Exception as e:
        logger.error(f"[定时任务] 基金公司规模数据更新失败: {str(e)}", exc_info=True)


def update_fund_company_aum_hist(year: str = None):
    """
    更新基金公司规模历史数据（年度数据）

    Args:
        year: 年份，默认为当前年份
    """
    try:
        if year is None:
            year = str(datetime.now().year)

        start_time = datetime.now()
        logger.info(f"[定时任务] 开始更新 {year} 年基金公司规模历史数据...")

        # 调用 AkShare API
        df = ak.fund_aum_hist_em(year=year)

        if df is None or df.empty:
            logger.warning(f"[定时任务] 获取 {year} 年基金公司规模历史数据为空")
            return

        logger.info(f"[定时任务] 获取到 {len(df)} 家基金公司 {year} 年规模历史数据")

        # 准备批量插入的数据
        records = []
        for _, row in df.iterrows():
            records.append((
                int(row.get('序号', 0)),
                str(row.get('基金公司', '')),
                year,
                float(row.get('总规模', 0)),
                float(row.get('股票型', 0)),
                float(row.get('混合型', 0)),
                float(row.get('债券型', 0)),
                float(row.get('指数型', 0)),
                float(row.get('QDII', 0)),
                float(row.get('货币型', 0))
            ))

        # 使用 REPLACE INTO 自动覆盖旧数据
        query = '''
            REPLACE INTO fund_company_aum_hist
            (序号, 基金公司, 年份, 总规模, 股票型, 混合型, 债券型, 指数型, QDII, 货币型, 更新时间)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
        '''

        row_count = execute_many(query, records)

        elapsed = (datetime.now() - start_time).total_seconds()
        logger.info(f"[定时任务] {year} 年基金公司规模历史数据更新完成: {row_count} 条记录，耗时 {elapsed:.2f}秒")

    except Exception as e:
        logger.error(f"[定时任务] {year} 年基金公司规模历史数据更新失败: {str(e)}", exc_info=True)


def update_fund_market_trend():
    """
    更新基金市场规模趋势数据（季度数据）
    """
    try:
        start_time = datetime.now()
        logger.info("[定时任务] 开始更新基金市场规模趋势数据...")

        # 调用 AkShare API
        df = ak.fund_aum_trend_em()

        if df is None or df.empty:
            logger.warning("[定时任务] 获取基金市场规模趋势数据为空")
            return

        logger.info(f"[定时任务] 获取到 {len(df)} 条市场规模趋势数据")

        # 准备批量插入的数据
        records = []
        for _, row in df.iterrows():
            records.append((
                str(row.get('date', '')),
                float(row.get('value', 0))
            ))

        # 先清空旧数据
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute('DELETE FROM fund_market_aum_trend')
        conn.commit()

        # 批量插入新数据
        query = '''
            INSERT INTO fund_market_aum_trend
            (日期, 市场总规模, 更新时间)
            VALUES (?, ?, CURRENT_TIMESTAMP)
        '''

        row_count = execute_many(query, records)

        elapsed = (datetime.now() - start_time).total_seconds()
        logger.info(f"[定时任务] 基金市场规模趋势数据更新完成: {row_count} 条记录，耗时 {elapsed:.2f}秒")

    except Exception as e:
        logger.error(f"[定时任务] 基金市场规模趋势数据更新失败: {str(e)}", exc_info=True)


def update_fund_risk_indicators_single(fund_code: str) -> bool:
    """
    更新单个基金的雪球风险指标数据（按需调用）

    Args:
        fund_code: 基金代码

    Returns:
        bool: 是否成功
    """
    try:
        logger.info(f"[风险指标] 开始更新基金 {fund_code} 的风险指标...")

        # 调用 AkShare 雪球API
        df = ak.fund_individual_analysis_xq(symbol=fund_code)

        if df is None or df.empty:
            logger.warning(f"[风险指标] 基金 {fund_code} 无风险指标数据")
            return False

        # 准备批量插入的数据
        records = []
        for _, row in df.iterrows():
            records.append((
                fund_code,
                row.get('周期', ''),
                int(row.get('较同类风险收益比', 0)),
                int(row.get('较同类抗风险波动', 0)),
                float(row.get('年化波动率', 0)),
                float(row.get('年化夏普比率', 0)),
                float(row.get('最大回撤', 0))
            ))

        # 批量更新数据库（使用 REPLACE INTO 自动覆盖）
        query = '''
            REPLACE INTO fund_risk_indicators_xq
            (基金代码, 周期, 较同类风险收益比, 较同类抗风险波动, 年化波动率, 年化夏普比率, 最大回撤, 更新时间)
            VALUES (?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
        '''

        row_count = execute_many(query, records)
        logger.info(f"[风险指标] 基金 {fund_code} 风险指标更新完成: {row_count} 条记录")
        return True

    except Exception as e:
        logger.error(f"[风险指标] 基金 {fund_code} 风险指标更新失败: {str(e)}", exc_info=True)
        return False


def clear_expired_cache_job():
    """
    清理过期缓存任务（每30分钟执行一次）
    """
    try:
        logger.info("[定时任务] 开始清理过期缓存...")
        CacheHelper.clear_expired_cache()
        logger.info("[定时任务] 过期缓存清理完成")
    except Exception as e:
        logger.error(f"[定时任务] 清理过期缓存失败: {str(e)}", exc_info=True)


def start_scheduler():
    """
    启动定时任务调度器
    """
    global scheduler

    if scheduler is not None:
        logger.warning("[调度器] 调度器已运行")
        return

    scheduler = BackgroundScheduler(timezone='Asia/Shanghai')

    # 任务1: 每个交易日9:00-15:00，每30分钟更新一次实时估值
    # 时间点: 9:00, 9:30, 10:00, 10:30, 11:00, 11:30, 13:00, 13:30, 14:00, 14:30, 15:00
    scheduler.add_job(
        update_fund_estimation,
        CronTrigger(day_of_week='mon-fri', hour='9-11,13-15', minute='0,30'),
        id='update_estimation_trading_hours',
        replace_existing=True
    )

    # 任务2: 每周日凌晨3点更新分红数据
    scheduler.add_job(
        update_fund_dividend,
        CronTrigger(day_of_week='sun', hour=3, minute=0),
        id='update_dividend',
        replace_existing=True
    )

    # 任务3: 每周日凌晨4点更新评级数据
    scheduler.add_job(
        update_fund_rating,
        CronTrigger(day_of_week='sun', hour=4, minute=0),
        id='update_rating',
        replace_existing=True
    )

    # 任务4: 每个交易日上午9:30更新货币基金数据
    scheduler.add_job(
        update_money_fund,
        CronTrigger(day_of_week='mon-fri', hour=9, minute=30),
        id='update_money_fund',
        replace_existing=True
    )

    # 任务5: 每个交易日上午8:00更新申购赎回状态
    scheduler.add_job(
        update_fund_purchase_status,
        CronTrigger(day_of_week='mon-fri', hour=8, minute=0),
        id='update_purchase_status',
        replace_existing=True
    )

    # 任务6: 每30分钟清理一次过期缓存
    scheduler.add_job(
        clear_expired_cache_job,
        IntervalTrigger(minutes=30),
        id='clear_expired_cache',
        replace_existing=True
    )

    # 任务7: 每周日凌晨5:00更新基金公司规模数据
    scheduler.add_job(
        update_fund_company_aum,
        CronTrigger(day_of_week='sun', hour=5, minute=0),
        id='update_company_aum',
        replace_existing=True
    )

    # 任务8: 每周日凌晨5:30更新基金市场规模趋势数据
    scheduler.add_job(
        update_fund_market_trend,
        CronTrigger(day_of_week='sun', hour=5, minute=30),
        id='update_market_trend',
        replace_existing=True
    )

    # 任务9: 每季度更新基金公司规模历史数据（每年1月、4月、7月、10月的1号凌晨6点）
    scheduler.add_job(
        update_fund_company_aum_hist,
        CronTrigger(month='1,4,7,10', day=1, hour=6, minute=0),
        id='update_company_aum_hist',
        replace_existing=True
    )

    # 启动调度器
    scheduler.start()
    logger.info("[调度器] 定时任务调度器已启动")
    logger.info("[调度器] - 货币基金更新: 每个交易日 09:30")
    logger.info("[调度器] - 估值更新: 每个交易日 09:00-15:00 每30分钟（跳过12:00-12:30）")
    logger.info("[调度器] - 申购赎回状态更新: 每个交易日 08:00")
    logger.info("[调度器] - 分红更新: 每周日 03:00")
    logger.info("[调度器] - 评级更新: 每周日 04:00")
    logger.info("[调度器] - 基金公司规模更新: 每周日 05:00")
    logger.info("[调度器] - 市场规模趋势更新: 每周日 05:30")
    logger.info("[调度器] - 公司历史规模更新: 每季度首日 06:00")
    logger.info("[调度器] - 缓存清理: 每30分钟")


def stop_scheduler():
    """
    停止定时任务调度器
    """
    global scheduler

    if scheduler is not None:
        scheduler.shutdown()
        scheduler = None
        logger.info("[调度器] 定时任务调度器已停止")
