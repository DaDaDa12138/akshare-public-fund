import axios from 'axios'
import type {
  FundInfo,
  FundDailyData,
  FundRankData,
  FundHistData,
  FundOverview,
  FundHolding,
  FundBasicInfoXQ,
  FundAnalysisXQ,
  IndustryAllocation,
  AssetAllocationXQ,
  FundValueEstimation,
  FundRating,
  FundDividend,
  FundCompareResponse,
  FundRiskIndicatorResponse
} from '@/types/fund'
import {
  errorLogger,
  healthMonitor,
  isIgnorableError,
  getFallbackStrategy
} from './fallback'
import { apiCache } from './cache'

// 创建 axios 实例
const request = axios.create({
  baseURL: '/api/public',
  timeout: 30000
})

// 请求开始时间记录
const requestStartTimes = new Map<any, number>()

// 请求拦截器
request.interceptors.request.use(
  config => {
    // 记录请求开始时间，用于计算响应时间
    requestStartTimes.set(config, Date.now())
    return config
  },
  error => {
    return Promise.reject(error)
  }
)

// 响应拦截器
request.interceptors.response.use(
  response => {
    // 计算响应时间并更新健康监控
    const startTime = requestStartTimes.get(response.config) || Date.now()
    const responseTime = Date.now() - startTime
    requestStartTimes.delete(response.config)

    const apiPath = response.config.url || ''
    healthMonitor.update(apiPath, true, responseTime)

    return response.data
  },
  error => {
    // 计算响应时间
    const startTime = requestStartTimes.get(error.config) || Date.now()
    const responseTime = Date.now() - startTime
    requestStartTimes.delete(error.config)

    const apiPath = error.config?.url || ''

    // 记录错误日志
    if (isIgnorableError(error)) {
      errorLogger.add(apiPath, error.config?.params, error)
      healthMonitor.update(apiPath, false, responseTime)
    }

    // Silent fail for expected API errors (404, 500)
    // These are handled by individual components
    return Promise.reject(error)
  }
)

/**
 * 获取所有基金列表
 * 缓存 30 分钟（基金列表变化不频繁）
 */
export const getFundList = () => {
  return apiCache.wrap(
    'fund_list',
    () => request.get<any, FundInfo[]>('/fund_name_em'),
    30 * 60 * 1000 // 30 分钟
  )
}

/**
 * 获取开放式基金实时净值
 * 缓存 1 分钟（实时数据，极短缓存）
 */
export const getFundDailyData = () => {
  return apiCache.wrap(
    'fund_daily_data',
    () => request.get<any, FundDailyData[]>('/fund_open_fund_daily_em'),
    1 * 60 * 1000 // 1 分钟
  )
}

/**
 * 获取基金排行榜
 * @param symbol 基金类型：全部、股票型、混合型、债券型、指数型、QDII、LOF、FOF
 * 缓存 10 分钟（排行数据，根据类型缓存）
 */
export const getFundRank = (symbol: string = '全部') => {
  const cacheKey = `fund_rank_${symbol}`

  return apiCache.wrap(
    cacheKey,
    () => request.get<any, FundRankData[]>('/fund_open_fund_rank_em', {
      params: { symbol }
    }),
    10 * 60 * 1000 // 10 分钟
  )
}

/**
 * 获取基金历史净值
 * @param symbol 基金代码
 * @param indicator 指标类型：单位净值走势、累计净值走势、累计收益率走势等
 * @param period 时间周期（仅用于累计收益率走势）：1月、3月、6月、1年、3年、5年、今年来、成立来
 * 缓存 60 分钟（历史数据极少变化，长期缓存减少API调用）
 */
export const getFundHistData = (symbol: string, indicator: string = '单位净值走势', period?: string) => {
  const params: any = { symbol, indicator }  // AKTools 0.0.91 使用 symbol 参数
  if (period) {
    params.period = period
  }

  // 根据参数生成缓存键
  const cacheKey = `fund_hist_${symbol}_${indicator}${period ? '_' + period : ''}`

  return apiCache.wrap(
    cacheKey,
    () => request.get<any, FundHistData[]>('/fund_open_fund_info_em', { params }),
    60 * 60 * 1000 // 60 分钟（历史数据极少变化，长期缓存）
  )
}

/**
 * 获取基金概况信息
 * @param symbol 基金代码
 */
export const getFundOverview = (symbol: string) => {
  return request.get<any, FundOverview>('/fund_overview_em', {
    params: { symbol }
  })
}

/**
 * 获取基金持仓明细
 * @param symbol 基金代码
 * @param date 年份，如 "2024"
 * 缓存 30 分钟（持仓数据更新不频繁）
 */
export const getFundHoldings = (symbol: string, date: string = '2024') => {
  const cacheKey = `fund_holdings_${symbol}_${date}`

  return apiCache.wrap(
    cacheKey,
    () => request.get<any, FundHolding[]>('/fund_portfolio_hold_em', {
      params: { symbol, date }
    }),
    30 * 60 * 1000 // 30 分钟
  )
}

/**
 * 获取场内基金实时数据
 * 缓存 1 分钟（实时数据，极短缓存）
 */
export const getETFFundDaily = () => {
  return apiCache.wrap(
    'etf_fund_daily',
    () => request.get<any, FundDailyData[]>('/fund_etf_fund_daily_em'),
    1 * 60 * 1000 // 1 分钟
  )
}

/**
 * 获取货币基金排行
 */
export const getMoneyFundRank = () => {
  return request.get<any, any[]>('/fund_money_rank_em')
}

/**
 * 获取基金分红记录
 * @param symbol 基金代码
 * 缓存 24 小时（分红数据变化不频繁）
 */
export const getFundDividend = (symbol: string) => {
  const cacheKey = `fund_dividend_${symbol}`

  // 使用 axios 创建一个临时实例，baseURL 为相对路径
  const customRequest = axios.create({
    baseURL: '/',
    timeout: 30000
  })

  return apiCache.wrap(
    cacheKey,
    () => customRequest.get<FundDividend[]>(`/api/fund_dividend/${symbol}`)
      .then(res => res.data)
      .catch(error => {
        // 404 或无数据是预期情况（基金可能没有分红），返回空数组
        if (error.response?.status === 404 || !error.response) {
          return []
        }
        // 其他错误继续抛出
        throw error
      }),
    24 * 60 * 60 * 1000 // 24 小时
  )
}

/**
 * 雪球 - 获取基金基本信息（基金经理、公司、规模）
 * @param symbol 基金代码
 * 缓存 30 分钟（基本信息变化不频繁）
 */
export const getFundBasicInfoXQ = (symbol: string) => {
  const cacheKey = `fund_basic_info_xq_${symbol}`

  return apiCache.wrap(
    cacheKey,
    () => request.get<any, FundBasicInfoXQ>('/fund_individual_basic_info_xq', {
      params: { symbol }
    }),
    30 * 60 * 1000 // 30 分钟
  )
}

/**
 * 雪球 - 获取基金分析数据（风险指标）
 * @param symbol 基金代码
 * 缓存 30 分钟（风险指标更新不频繁）
 * 返回多个周期的数据：近1年、近3年、近5年
 */
export const getFundAnalysisXQ = (symbol: string) => {
  const cacheKey = `fund_analysis_xq_${symbol}`

  return apiCache.wrap(
    cacheKey,
    () => request.get<any, FundAnalysisXQ[]>('/fund_individual_analysis_xq', {
      params: { symbol }
    }),
    30 * 60 * 1000 // 30 分钟（风险指标更新不频繁）
  )
}

/**
 * 获取基金行业分布
 * @param symbol 基金代码
 * 缓存 30 分钟
 */
export const getFundIndustryAllocation = (symbol: string) => {
  const cacheKey = `fund_industry_allocation_${symbol}`

  return apiCache.wrap(
    cacheKey,
    async () => {
      // 使用自定义端点（带错误处理）
      const response = await axios.get(`/api/fund_industry_allocation/${symbol}`)
      if (response.data && response.data.success) {
        return response.data.data as IndustryAllocation[]
      }
      return []
    },
    30 * 60 * 1000 // 30 分钟
  )
}

/**
 * 雪球 - 获取基金资产配置详情
 * @param symbol 基金代码
 * 缓存 30 分钟
 */
export const getFundAssetAllocationXQ = (symbol: string) => {
  const cacheKey = `fund_asset_allocation_xq_${symbol}`

  return apiCache.wrap(
    cacheKey,
    () => request.get<any, AssetAllocationXQ[]>('/fund_individual_detail_hold_xq', {
      params: { symbol }
    }),
    30 * 60 * 1000 // 30 分钟
  )
}

/**
 * 获取基金实时估值（来自本地数据库）
 * @param symbol 基金代码
 * 缓存 1 分钟（实时数据，短期缓存）
 * 注意：此API不在 /api/public 路径下，而是在 /api 根路径
 *
 * 注意：不是所有基金都有实时估值数据，404 错误是正常现象
 */
export const getFundValueEstimation = (symbol: string) => {
  const cacheKey = `fund_value_estimation_${symbol}`

  // 使用 axios 创建一个临时实例，baseURL 为相对路径
  const customRequest = axios.create({
    baseURL: '/',
    timeout: 30000
  })

  return apiCache.wrap(
    cacheKey,
    () => customRequest.get<FundValueEstimation>(`/api/fund_estimation/${symbol}`)
      .then(res => res.data)
      .catch(error => {
        // 404 是预期错误（基金无估值数据），静默处理
        if (error.response?.status === 404) {
          return null
        }
        // 其他错误继续抛出
        throw error
      }),
    1 * 60 * 1000 // 1 分钟（实时估值数据）
  )
}

/**
 * 基金对比
 * @param symbols 基金代码数组（2-5个）
 * 缓存 10 分钟（对比数据更新不频繁）
 */
export const compareFunds = (symbols: string[]) => {
  const cacheKey = `fund_compare_${symbols.sort().join('_')}`

  // 使用 axios 创建一个临时实例，baseURL 为相对路径
  const customRequest = axios.create({
    baseURL: '/',
    timeout: 60000 // 对比API可能耗时较长，设置60秒超时
  })

  return apiCache.wrap(
    cacheKey,
    () => customRequest.post<FundCompareResponse>('/api/fund_compare', { symbols })
      .then(res => res.data)
      .catch(error => {
        // 处理错误
        throw error
      }),
    10 * 60 * 1000 // 10 分钟
  )
}

/**
 * 获取基金完整历史净值数据
 * @param symbol 基金代码
 * @param indicator 数据类型（默认"单位净值走势"）
 * 缓存 10 分钟（历史数据更新不频繁）
 */
export const getFundNetValueHistory = (
  symbol: string,
  indicator: string = '单位净值走势'
) => {
  const cacheKey = `fund_net_value_history_${symbol}_${indicator}`

  // 使用 axios 创建一个临时实例，baseURL 为相对路径
  const customRequest = axios.create({
    baseURL: '/',
    timeout: 30000
  })

  return apiCache.wrap(
    cacheKey,
    () => customRequest.get<FundNetValueHistoryResponse>(
      `/api/fund_net_value_history/${symbol}`,
      { params: { indicator } }
    )
      .then(res => res.data)
      .catch(error => {
        // 404 或 500 都返回空数据
        if (error.response?.status === 404 || error.response?.status === 500) {
          return {
            success: true,
            symbol,
            indicator,
            total: 0,
            data: [],
            source: 'eastmoney',
            message: '暂无历史净值数据'
          }
        }
        throw error
      }),
    10 * 60 * 1000 // 10 分钟
  )
}

/**
 * 获取基金债券持仓数据
 * @param symbol 基金代码
 * @param quarter 可选，指定季度（如 "2023年4季度"）
 * 缓存 30 分钟（持仓数据更新不频繁）
 */
export interface FundBondHoldingResponse {
  success: boolean
  data: Array<{
    序号: number
    债券代码: string
    债券名称: string
    占净值比例: number
    持仓市值: number
    季度: string
  }>
  quarters: string[]
  source: string
  error?: string
}

export const getFundBondHoldings = (symbol: string, quarter?: string) => {
  const cacheKey = `fund_bond_holdings_${symbol}${quarter ? '_' + quarter : ''}`

  // 使用 axios 创建一个临时实例，baseURL 为相对路径
  const customRequest = axios.create({
    baseURL: '/',
    timeout: 30000
  })

  const params: any = {}
  if (quarter) {
    params.quarter = quarter
  }

  return apiCache.wrap(
    cacheKey,
    () => customRequest.get<FundBondHoldingResponse>(`/api/fund_bond_holdings/${symbol}`, { params })
      .then(res => res.data)
      .catch(error => {
        // 404 或无数据是预期情况，返回空结果
        if (error.response?.status === 404 || !error.response) {
          return {
            success: true,
            data: [],
            quarters: [],
            source: 'error'
          }
        }
        // 其他错误继续抛出
        throw error
      }),
    30 * 60 * 1000 // 30 分钟
  )
}

/**
 * 获取货币基金数据
 * 缓存 10 分钟（货币基金数据更新频繁）
 */
export interface MoneyFundData {
  基金代码: string
  基金简称: string
  万份收益: number
  七日年化: string
  单位净值: string
  日涨幅: string
  成立日期: string
  基金经理: string
  手续费: string
  可购全部: string
  更新时间?: string
}

export interface MoneyFundResponse {
  success: boolean
  data: MoneyFundData[]
  source: string
  total?: number
  last_update?: string
  error?: string
}

export const getMoneyFunds = () => {
  const cacheKey = 'money_funds'

  // 使用 axios 创建一个临时实例，baseURL 为相对路径
  const customRequest = axios.create({
    baseURL: '/',
    timeout: 30000
  })

  return apiCache.wrap(
    cacheKey,
    () => customRequest.get<MoneyFundResponse>('/api/fund_money')
      .then(res => res.data)
      .catch(error => {
        // 返回空结果
        if (!error.response) {
          return {
            success: false,
            data: [],
            source: 'error',
            error: error.message
          }
        }
        throw error
      }),
    10 * 60 * 1000 // 10 分钟
  )
}

/**
 * 获取ETF历史行情数据
 * @param symbol 基金代码
 * @param period 时间周期 - daily(日k), weekly(周k), monthly(月k)
 * @param adjust 复权类型 - 空(不复权), qfq(前复权), hfq(后复权)
 * @param startDate 起始日期 (YYYY-MM-DD)，可选
 * @param endDate 结束日期 (YYYY-MM-DD)，可选
 * 缓存10分钟（K线数据较稳定）
 */
export interface ETFHistData {
  日期: string
  开盘: number
  收盘: number
  最高: number
  最低: number
  成交量: number
  成交额: number
  振幅: number
  涨跌幅: number
  涨跌额: number
  换手率: number
}

export interface ETFHistResponse {
  success: boolean
  data: ETFHistData[]
  source: string
  total: number
  symbol: string
  period: string
  adjust: string
  error?: string
}

export const getFundETFHist = (
  symbol: string,
  period: string = 'daily',
  adjust: string = 'qfq',
  startDate?: string,
  endDate?: string
) => {
  const cacheKey = `etf_hist_${symbol}_${period}_${adjust}`

  // 使用 axios 创建一个临时实例，baseURL 为相对路径
  const customRequest = axios.create({
    baseURL: '/',
    timeout: 60000 // ETF历史数据可能较大，设置60秒超时
  })

  const params: any = { period, adjust }
  if (startDate) params.start_date = startDate
  if (endDate) params.end_date = endDate

  return apiCache.wrap(
    cacheKey,
    () => customRequest.get<ETFHistResponse>(`/api/fund_etf_hist/${symbol}`, { params })
      .then(res => res.data)
      .catch(error => {
        // 返回空结果
        if (!error.response) {
          return {
            success: false,
            data: [],
            source: 'error',
            total: 0,
            symbol,
            period,
            adjust,
            error: error.message
          }
        }
        throw error
      }),
    10 * 60 * 1000 // 10 分钟
  )
}

/**
 * 获取基金评级信息
 * @param symbol 基金代码
 * 缓存30分钟（评级数据更新不频繁）
 */
export interface FundRatingData {
  代码: string
  简称: string
  基金经理: string
  基金公司: string
  '5星评级家数': number
  上海证券: number | null
  招商证券: number | null
  济安金信: number | null
  晨星评级: number | null
  手续费: number
  类型: string
  更新时间: string
}

export interface FundRatingResponse {
  success: boolean
  data: FundRatingData | null
  source: string
  message?: string
  error?: string
}

export const getFundRating = (symbol: string) => {
  const cacheKey = `fund_rating_${symbol}`

  const customRequest = axios.create({
    baseURL: '/',
    timeout: 30000
  })

  return apiCache.wrap(
    cacheKey,
    () => customRequest.get<FundRatingResponse>(`/api/fund_rating/${symbol}`)
      .then(res => res.data)
      .catch(error => {
        if (!error.response) {
          return {
            success: false,
            data: null,
            source: 'error',
            error: error.message
          }
        }
        throw error
      }),
    30 * 60 * 1000 // 30 分钟
  )
}

/**
 * 基金分红排行数据接口
 */
export interface FundDividendRankData {
  序号: number
  基金代码: string
  基金简称: string
  累计分红: number
  累计次数: number
  成立日期: string
}

export interface FundDividendRankResponse {
  success: boolean
  count: number
  data: FundDividendRankData[]
  sort_by: string
  source: string
  error?: string
}

/**
 * 获取基金分红排行榜
 * @param limit 返回数量限制 (默认100)
 * @param sortBy 排序字段: 累计分红 或 累计次数
 * 缓存5分钟（排行榜数据相对稳定）
 */
export const getFundDividendRank = (limit: number = 100, sortBy: string = '累计分红') => {
  const cacheKey = `fund_dividend_rank_${limit}_${sortBy}`

  const customRequest = axios.create({
    baseURL: '/',
    timeout: 60000  // 排行榜数据量大，超时时间60秒
  })

  return apiCache.wrap(
    cacheKey,
    () => customRequest.get<FundDividendRankResponse>('/api/fund_dividend_rank', {
      params: { limit, sort_by: sortBy }
    })
      .then(res => res.data)
      .catch(error => {
        if (!error.response) {
          return {
            success: false,
            count: 0,
            data: [],
            sort_by: sortBy,
            source: 'error',
            error: error.message
          }
        }
        throw error
      }),
    5 * 60 * 1000 // 5 分钟
  )
}

/**
 * 基金持仓数据接口
 */
export interface FundPortfolioHoldData {
  序号: number
  股票代码: string
  股票名称: string
  占净值比例: number
  持股数: number
  持仓市值: number
  季度: string
}

export interface FundPortfolioHoldResponse {
  success: boolean
  count: number
  data: FundPortfolioHoldData[]
  fund_code: string
  date: string
  source: string
  error?: string
}

/**
 * 获取基金重仓股票持仓明细
 * @param symbol 基金代码
 * @param date 季度日期 (格式: YYYYMMDD，例如: 20231231)
 * 缓存10分钟（持仓数据更新不频繁）
 */
export const getFundPortfolioHold = (symbol: string, date: string = '20231231') => {
  const cacheKey = `fund_portfolio_hold_${symbol}_${date}`

  const customRequest = axios.create({
    baseURL: '/',
    timeout: 30000
  })

  return apiCache.wrap(
    cacheKey,
    () => customRequest.get<FundPortfolioHoldResponse>('/api/fund_portfolio_hold', {
      params: { symbol, date }
    })
      .then(res => res.data)
      .catch(error => {
        if (!error.response) {
          return {
            success: false,
            count: 0,
            data: [],
            fund_code: symbol,
            date,
            source: 'error',
            error: error.message
          }
        }
        throw error
      }),
    10 * 60 * 1000 // 10 分钟
  )
}

/**
 * 基金持仓变动数据接口
 */
export interface FundPortfolioChangeData {
  序号: number
  股票代码: string
  股票名称: string
  本期累计买入金额: number
  占期初基金资产净值比例: number
  季度: string
}

export interface FundPortfolioChangeResponse {
  success: boolean
  count: number
  data: FundPortfolioChangeData[]
  fund_code: string
  date: string
  source: string
  error?: string
}

/**
 * 获取基金持仓变动明细(累计买入)
 * @param symbol 基金代码
 * @param date 季度日期 (格式: YYYYMMDD，例如: 20231231)
 * 缓存10分钟（持仓变动数据更新不频繁）
 */
export const getFundPortfolioChange = (symbol: string, date: string = '20231231') => {
  const cacheKey = `fund_portfolio_change_${symbol}_${date}`

  const customRequest = axios.create({
    baseURL: '/',
    timeout: 30000
  })

  return apiCache.wrap(
    cacheKey,
    () => customRequest.get<FundPortfolioChangeResponse>('/api/fund_portfolio_change', {
      params: { symbol, date }
    })
      .then(res => res.data)
      .catch(error => {
        if (!error.response) {
          return {
            success: false,
            count: 0,
            data: [],
            fund_code: symbol,
            date,
            source: 'error',
            error: error.message
          }
        }
        throw error
      }),
    10 * 60 * 1000 // 10 分钟
  )
}

/**
 * 获取基金风险指标数据（来自雪球）
 * @param symbol 基金代码
 * @param forceUpdate 是否强制更新（默认使用缓存）
 * 缓存10分钟（风险指标更新不频繁）
 *
 * 返回数据包含3个周期：近1年、近3年、近5年
 * 每个周期包含5个风险指标：
 * - 较同类风险收益比（百分比排名）
 * - 较同类抗风险波动（百分比排名）
 * - 年化波动率
 * - 年化夏普比率
 * - 最大回撤
 */
export const getFundRiskIndicators = (symbol: string, forceUpdate: boolean = false) => {
  const cacheKey = `fund_risk_indicators_${symbol}`

  const customRequest = axios.create({
    baseURL: '/',
    timeout: 30000
  })

  return apiCache.wrap(
    cacheKey,
    () => customRequest.get<FundRiskIndicatorResponse>(`/api/fund_risk_indicators/${symbol}`, {
      params: { force_update: forceUpdate }
    })
      .then(res => res.data)
      .catch(error => {
        // 404 或无数据是预期情况（基金可能没有风险指标数据），返回空结果
        if (error.response?.status === 404 || !error.response) {
          return {
            success: false,
            data: [],
            count: 0,
            source: 'error',
            message: error.response?.data?.message || '暂无风险指标数据'
          }
        }
        // 其他错误继续抛出
        throw error
      }),
    10 * 60 * 1000 // 10 分钟
  )
}

/**
 * 导出相关API
 * 不使用缓存，每次都是实时导出
 */

/**
 * 导出基金排行数据
 * @param filters 筛选条件
 * @param format 导出格式: csv 或 excel
 */
export const exportFundRanking = async (filters: any, format: 'csv' | 'excel' = 'csv') => {
  const customRequest = axios.create({
    baseURL: '/',
    timeout: 120000, // 导出可能需要较长时间，设置2分钟超时
    responseType: 'blob' // 重要：设置响应类型为blob
  })

  try {
    const response = await customRequest.post('/api/export/ranking', {
      filters,
      format
    })

    // 从响应头获取文件名
    const contentDisposition = response.headers['content-disposition']
    let fileName = `基金排行_${new Date().toISOString().slice(0, 10)}.${format === 'csv' ? 'csv' : 'xlsx'}`

    if (contentDisposition) {
      // 尝试从Content-Disposition头中提取文件名
      const matches = /filename\*=UTF-8''(.+)/.exec(contentDisposition)
      if (matches && matches[1]) {
        fileName = decodeURIComponent(matches[1])
      }
    }

    // 创建下载链接并触发下载
    const url = window.URL.createObjectURL(new Blob([response.data]))
    const link = document.createElement('a')
    link.href = url
    link.setAttribute('download', fileName)
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    window.URL.revokeObjectURL(url)

    return { success: true, message: '导出成功' }
  } catch (error: any) {
    console.error('导出基金排行失败:', error)
    return { success: false, message: error.message || '导出失败' }
  }
}

/**
 * 导出基金公司规模排行数据
 * @param format 导出格式: csv 或 excel
 */
export const exportCompanyRanking = async (format: 'csv' | 'excel' = 'csv') => {
  const customRequest = axios.create({
    baseURL: '/',
    timeout: 120000,
    responseType: 'blob'
  })

  try {
    const response = await customRequest.get(`/api/export/company_ranking/${format}`)

    const contentDisposition = response.headers['content-disposition']
    let fileName = `基金公司规模排行_${new Date().toISOString().slice(0, 10)}.${format === 'csv' ? 'csv' : 'xlsx'}`

    if (contentDisposition) {
      const matches = /filename\*=UTF-8''(.+)/.exec(contentDisposition)
      if (matches && matches[1]) {
        fileName = decodeURIComponent(matches[1])
      }
    }

    const url = window.URL.createObjectURL(new Blob([response.data]))
    const link = document.createElement('a')
    link.href = url
    link.setAttribute('download', fileName)
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    window.URL.revokeObjectURL(url)

    return { success: true, message: '导出成功' }
  } catch (error: any) {
    console.error('导出公司排行失败:', error)
    return { success: false, message: error.message || '导出失败' }
  }
}

/**
 * 导出基金分红排行数据
 * @param format 导出格式: csv 或 excel
 */
export const exportDividendRank = async (format: 'csv' | 'excel' = 'csv') => {
  const customRequest = axios.create({
    baseURL: '/',
    timeout: 120000,
    responseType: 'blob'
  })

  try {
    const response = await customRequest.get(`/api/export/dividend_rank/${format}`)

    const contentDisposition = response.headers['content-disposition']
    let fileName = `基金分红排行_${new Date().toISOString().slice(0, 10)}.${format === 'csv' ? 'csv' : 'xlsx'}`

    if (contentDisposition) {
      const matches = /filename\*=UTF-8''(.+)/.exec(contentDisposition)
      if (matches && matches[1]) {
        fileName = decodeURIComponent(matches[1])
      }
    }

    const url = window.URL.createObjectURL(new Blob([response.data]))
    const link = document.createElement('a')
    link.href = url
    link.setAttribute('download', fileName)
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    window.URL.revokeObjectURL(url)

    return { success: true, message: '导出成功' }
  } catch (error: any) {
    console.error('导出分红排行失败:', error)
    return { success: false, message: error.message || '导出失败' }
  }
}
