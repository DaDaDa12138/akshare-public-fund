/**
 * 另类数据 API 封装
 * 包含汽车销量、空气质量、电影票房、财富排行榜等25个接口
 */
import axios from 'axios'
import { apiCache } from './cache'
import type {
  CarMarketTotal,
  CarManufacturerRank,
  CarCategoryData,
  CarCountryData,
  CarSegmentData,
  CarFuelData,
  CarSaleRankGasgoo,
  AirQualityCity,
  AirQualityHistory,
  AirQualityRank,
  AirQualityWatchPoint,
  MovieBoxOfficeRealtime,
  MovieBoxOfficeDaily,
  MovieBoxOfficeWeekly,
  MovieBoxOfficeMonthly,
  MovieBoxOfficeYearly,
  MovieCinemaBoxOffice,
  FortuneRank,
  ForbesRank,
  XincaifuRank,
  HurunRank,
  ForbesInvestor,
  AlternativeDataResponse
} from '@/types/alternative'

// 创建 axios 实例
const request = axios.create({
  baseURL: '/api/public',
  timeout: 30000  // 30秒超时
})

// 响应拦截器 - 提取 response.data
request.interceptors.response.use(
  response => response.data,
  error => {
    console.error('另类数据API请求失败:', error)
    return Promise.reject(error)
  }
)

// 缓存时间：10分钟
const CACHE_TTL = 10 * 60 * 1000

// 缓存版本（修改此值会使所有旧缓存失效）
const CACHE_VERSION = 'v5'

// ==================== 汽车销量数据 API ====================

/**
 * 获取乘联会总体市场数据
 * @param symbol 市场类型：狭义乘用车 | 广义乘用车
 * @param indicator 指标类型：产量 | 批发 | 零售 | 出口
 */
export const getCarMarketTotal = (
  symbol: string = "狭义乘用车",
  indicator: string = "零售"
): Promise<CarMarketTotal[]> => {
  return apiCache.wrap(
    `${CACHE_VERSION}_alternative_car_total_${symbol}_${indicator}`,
    () => request.get('/car_market_total_cpca', { params: { symbol, indicator } }),
    CACHE_TTL
  )
}

/**
 * 获取厂商销售排名数据
 * @param symbol 统计周期：单月 | 累计
 * @param indicator 销售类型：批发 | 零售
 */
export const getCarManufacturerRank = (
  symbol: string = "单月",
  indicator: string = "零售"
): Promise<CarManufacturerRank[]> => {
  return apiCache.wrap(
    `${CACHE_VERSION}_alternative_car_man_${symbol}_${indicator}`,
    () => request.get('/car_market_man_rank_cpca', { params: { symbol, indicator } }),
    CACHE_TTL
  )
}

/**
 * 获取车型大类细分市场数据
 * @param symbol 车型类别：轿车 | MPV | SUV | 占比
 * @param indicator 销售类型：批发 | 零售
 */
export const getCarCategoryData = (
  symbol: string = "轿车",
  indicator: string = "零售"
): Promise<CarCategoryData[]> => {
  return apiCache.wrap(
    `${CACHE_VERSION}_alternative_car_cate_${symbol}_${indicator}`,
    () => request.get('/car_market_cate_cpca', { params: { symbol, indicator } }),
    CACHE_TTL
  )
}

/**
 * 获取国别细分市场数据
 */
export const getCarCountryData = (): Promise<CarCountryData[]> => {
  return apiCache.wrap(
    `${CACHE_VERSION}_alternative_car_country`,
    () => request.get('/car_market_country_cpca'),
    CACHE_TTL
  )
}

/**
 * 获取级别细分市场数据（A00/A0/A/B/C级）
 * @param symbol 车型类别：轿车 | MPV | SUV
 */
export const getCarSegmentData = (symbol: string = "轿车"): Promise<CarSegmentData[]> => {
  return apiCache.wrap(
    `${CACHE_VERSION}_alternative_car_segment_${symbol}`,
    () => request.get('/car_market_segment_cpca', { params: { symbol } }),
    CACHE_TTL
  )
}

/**
 * 获取新能源细分市场数据
 * @param symbol 数据类型：整体市场 | 销量占比
 */
export const getCarFuelData = (symbol: string = "整体市场"): Promise<CarFuelData[]> => {
  return apiCache.wrap(
    `${CACHE_VERSION}_alternative_car_fuel_${symbol}`,
    () => request.get('/car_market_fuel_cpca', { params: { symbol } }),
    CACHE_TTL
  )
}

/**
 * 获取盖世汽车销量排行榜
 * @param symbol 榜单类型：车企榜 | 品牌榜 | 车型榜
 * @param date 查询年月（格式：YYYYMM，如"202401"）
 */
export const getCarSaleRank = (
  symbol: string = "车企榜",
  date: string
): Promise<CarSaleRankGasgoo[]> => {
  return apiCache.wrap(
    `${CACHE_VERSION}_alternative_car_sale_${symbol}_${date}`,
    () => request.get('/car_sale_rank_gasgoo', { params: { symbol, date } }),
    CACHE_TTL
  )
}

// ==================== 空气质量数据 API ====================

/**
 * 获取全国城市空气质量实时表
 */
export const getAirCityTable = (): Promise<AirQualityCity[]> => {
  return apiCache.wrap(
    `${CACHE_VERSION}_alternative_air_city_table`,
    () => request.get('/air_city_table'),
    CACHE_TTL
  )
}

/**
 * 获取空气质量排名
 * @param date 查询日期（可选，格式：YYYY-MM-DD）
 */
export const getAirQualityRank = (date?: string): Promise<AirQualityRank[]> => {
  const params = date ? { date } : {}
  const cacheKey = date ? `${CACHE_VERSION}_alternative_air_rank_${date}` : `${CACHE_VERSION}_alternative_air_rank`
  return apiCache.wrap(
    cacheKey,
    () => request.get('/air_quality_rank', { params }),
    CACHE_TTL
  )
}

/**
 * 获取指定城市历史空气质量数据
 * @param city 城市名称（如"北京"）
 * @param period 时间粒度：小时 | 天 | 月
 * @param startDate 开始日期（格式：YYYY-MM-DD）
 * @param endDate 结束日期（格式：YYYY-MM-DD）
 */
export const getAirQualityHistory = (
  city: string,
  period: string = "天",
  startDate: string,
  endDate: string
): Promise<AirQualityHistory[]> => {
  // 参数转换：将中文转为英文
  const periodMap: Record<string, string> = {
    '天': 'day',
    '小时': 'hour',
    '月': 'month'
  }
  const periodEn = periodMap[period] || period

  // 日期格式转换：YYYY-MM-DD → YYYYMMDD
  const formatDate = (date: string) => date.replace(/-/g, '')
  const startDateFormatted = formatDate(startDate)
  const endDateFormatted = formatDate(endDate)

  return apiCache.wrap(
    `${CACHE_VERSION}_alternative_air_hist_${city}_${period}_${startDate}_${endDate}`,
    () => request.get('/air_quality_hist', {
      params: {
        city,
        period: periodEn,
        start_date: startDateFormatted,
        end_date: endDateFormatted
      }
    }),
    CACHE_TTL
  )
}

/**
 * 获取城市监测点空气质量数据
 * @param city 城市名称
 * @param startDate 开始日期
 * @param endDate 结束日期
 */
export const getAirQualityWatchPoint = (
  city: string,
  startDate: string,
  endDate: string
): Promise<AirQualityWatchPoint[]> => {
  return apiCache.wrap(
    `${CACHE_VERSION}_alternative_air_watch_${city}_${startDate}_${endDate}`,
    () => request.get('/air_quality_watch_point', {
      params: { city, start_date: startDate, end_date: endDate }
    }),
    CACHE_TTL
  )
}

/**
 * 获取河北省实时空气质量
 */
export const getAirQualityHebei = (): Promise<AirQualityCity[]> => {
  return apiCache.wrap(
    `${CACHE_VERSION}_alternative_air_hebei`,
    () => request.get('/air_quality_hebei'),
    CACHE_TTL
  )
}

// ==================== 电影票房数据 API ====================

/**
 * 电影票房字段映射辅助函数
 * API返回的字段名与组件期望的字段名不一致，需要映射
 */
const mapMovieFields = (item: any) => ({
  排名: item.排序 || item.排名,
  影片名: item.影片名称 || item.影片名,
  实时票房: item.实时票房,
  实时占比: item.票房占比 || item.实时占比,
  单日票房: item.单日票房,
  单日占比: item.单日占比,
  周票房: item.周票房,
  周占比: item.周占比,
  月票房: item.月票房,
  月占比: item.月占比,
  年度票房: item.年度票房,
  年度占比: item.年度占比,
  累计票房: item.累计票房,
  上映天数: item.上映天数,
  票房占比: item.票房占比,
  场均人次: item.场均人次,
  平均票价: item.平均票价,
  环比: item.环比变化 || item.环比,
  类型: item.类型,
  上映日期: item.上映日期
})

/**
 * 获取实时电影票房数据
 */
export const getMovieBoxOfficeRealtime = (): Promise<MovieBoxOfficeRealtime[]> => {
  return apiCache.wrap(
    `${CACHE_VERSION}_alternative_movie_realtime`,
    async () => {
      const data = await request.get('/movie_boxoffice_realtime')
      return data.map(mapMovieFields)
    },
    5 * 60 * 1000  // 实时数据缓存5分钟
  )
}

/**
 * 获取单日电影票房数据
 * @param date 日期（格式：YYYYMMDD，如"20240115"）
 */
export const getMovieBoxOfficeDaily = (date: string): Promise<MovieBoxOfficeDaily[]> => {
  return apiCache.wrap(
    `${CACHE_VERSION}_alternative_movie_daily_${date}`,
    async () => {
      const data = await request.get('/movie_boxoffice_daily', { params: { date } })
      return data.map(mapMovieFields)
    },
    CACHE_TTL
  )
}

/**
 * 获取周电影票房数据
 * 注意：AKShare 的周票房接口暂不支持 date 参数（会报错），只能获取最新一周的数据
 */
export const getMovieBoxOfficeWeekly = (): Promise<MovieBoxOfficeWeekly[]> => {
  return apiCache.wrap(
    `${CACHE_VERSION}_alternative_movie_weekly`,
    async () => {
      const data = await request.get('/movie_boxoffice_weekly')
      return data.map(mapMovieFields)
    },
    CACHE_TTL
  )
}

/**
 * 获取月电影票房数据
 * @param date 年月（格式：YYYYMM，如"202401"）
 */
export const getMovieBoxOfficeMonthly = (date: string): Promise<MovieBoxOfficeMonthly[]> => {
  return apiCache.wrap(
    `${CACHE_VERSION}_alternative_movie_monthly_${date}`,
    async () => {
      const data = await request.get('/movie_boxoffice_monthly', { params: { date } })
      return data.map(mapMovieFields)
    },
    CACHE_TTL
  )
}

/**
 * 获取年度电影票房数据
 * @param date 年份（格式：YYYY，如"2023"）
 */
export const getMovieBoxOfficeYearly = (date: string): Promise<MovieBoxOfficeYearly[]> => {
  return apiCache.wrap(
    `${CACHE_VERSION}_alternative_movie_yearly_${date}`,
    async () => {
      const data = await request.get('/movie_boxoffice_yearly', { params: { date } })
      return data.map(mapMovieFields)
    },
    CACHE_TTL
  )
}

/**
 * 获取年度首周票房数据
 * @param date 年份（格式：YYYY）
 */
export const getMovieBoxOfficeYearlyFirstWeek = (date: string): Promise<MovieBoxOfficeYearly[]> => {
  return apiCache.wrap(
    `${CACHE_VERSION}_alternative_movie_yearly_first_${date}`,
    () => request.get('/movie_boxoffice_yearly_first_week', { params: { date } }),
    CACHE_TTL
  )
}

/**
 * 获取影院日票房排行
 * @param date 日期（格式：YYYYMMDD）
 */
export const getMovieCinemaDaily = (date: string): Promise<MovieCinemaBoxOffice[]> => {
  return apiCache.wrap(
    `${CACHE_VERSION}_alternative_movie_cinema_daily_${date}`,
    () => request.get('/movie_boxoffice_cinema_daily', { params: { date } }),
    CACHE_TTL
  )
}

/**
 * 获取影院周票房排行
 * @param date 周起始日期（格式：YYYY-MM-DD）
 */
export const getMovieCinemaWeekly = (date: string): Promise<MovieCinemaBoxOffice[]> => {
  return apiCache.wrap(
    `${CACHE_VERSION}_alternative_movie_cinema_weekly_${date}`,
    () => request.get('/movie_boxoffice_cinema_weekly', { params: { date } }),
    CACHE_TTL
  )
}

// ==================== 财富排行榜数据 API ====================

/**
 * 获取财富世界500强公司排行
 * @param year 年份（如"2023"）
 */
export const getFortuneRank = (year: string = "2023"): Promise<FortuneRank[]> => {
  return apiCache.wrap(
    `${CACHE_VERSION}_alternative_fortune_${year}`,
    () => request.get('/fortune_rank', { params: { year } }),
    CACHE_TTL
  )
}

/**
 * 获取福布斯中国榜单
 * @param symbol 榜单名称（如"中国400富豪榜"）
 */
export const getForbesRank = (symbol: string = "中国400富豪榜"): Promise<ForbesRank[]> => {
  return apiCache.wrap(
    `${CACHE_VERSION}_alternative_forbes_${symbol}`,
    () => request.get('/forbes_rank', { params: { symbol } }),
    CACHE_TTL
  )
}

/**
 * 获取新财富500富豪榜
 * @param year 年份（如"2023"）
 */
export const getXincaifuRank = (year: string = "2023"): Promise<XincaifuRank[]> => {
  return apiCache.wrap(
    `${CACHE_VERSION}_alternative_xincaifu_${year}`,
    () => request.get('/xincaifu_rank', { params: { year } }),
    CACHE_TTL
  )
}

/**
 * 获取胡润百富榜单
 * @param indicator 榜单类型：富豪榜 | 全球富豪榜 | 独角兽榜 | 500强 | 艺术榜
 * @param year 年份（如"2023"）
 */
export const getHurunRank = (
  indicator: string = "富豪榜",
  year: string = "2023"
): Promise<HurunRank[]> => {
  return apiCache.wrap(
    `${CACHE_VERSION}_alternative_hurun_${indicator}_${year}`,
    () => request.get('/hurun_rank', { params: { indicator, year } }),
    CACHE_TTL
  )
}

// ==================== 新闻数据 ====================

/**
 * 新闻联播文字稿
 * 字段：date, title, content
 */
export interface NewsCCTV {
  date: string          // 日期 20241101
  title: string         // 标题
  content: string       // 内容
}

/**
 * 获取新闻联播文字稿
 * @param date 日期（YYYYMMDD格式，如"20241101"）
 */
export const getNewsCCTV = (date: string): Promise<NewsCCTV[]> => {
  return apiCache.wrap(
    `${CACHE_VERSION}_alternative_news_cctv_${date}`,
    () => request.get('/news_cctv', { params: { date } }),
    CACHE_TTL
  )
}

// ==================== 艺人数据 ====================

/**
 * 艺人商业价值榜
 * 字段：排名, 艺人, 商业价值, 专业热度, 关注热度, 预测热度, 美誉度, 统计日期
 */
export interface BusinessValueArtist {
  排名: number
  艺人: string
  商业价值: number
  专业热度: number
  关注热度: number
  预测热度: number
  美誉度: number
  统计日期: string
}

/**
 * 艺人网络价值榜
 * 字段：排名, 艺人, 流量价值, 专业热度, 关注热度, 预测热度, 带货力, 统计日期
 */
export interface OnlineValueArtist {
  排名: number
  艺人: string
  流量价值: number
  专业热度: number
  关注热度: number
  预测热度: number
  带货力: number
  统计日期: string
}

/**
 * 获取艺人商业价值榜 TOP100
 */
export const getBusinessValueArtist = (): Promise<BusinessValueArtist[]> => {
  return apiCache.wrap(
    `${CACHE_VERSION}_alternative_business_value_artist`,
    () => request.get('/business_value_artist'),
    CACHE_TTL
  )
}

/**
 * 获取艺人网络价值榜 TOP100
 */
export const getOnlineValueArtist = (): Promise<OnlineValueArtist[]> => {
  return apiCache.wrap(
    `${CACHE_VERSION}_alternative_online_value_artist`,
    () => request.get('/online_value_artist'),
    CACHE_TTL
  )
}

// ==================== 日出日落数据 ====================

/**
 * 日出日落数据
 * 字段：date, Sunrise, Sunset, Length等
 */
export interface SunriseData {
  date: string
  Sunrise: string       // 日出时间
  Sunset: string        // 日落时间
  Length: string        // 日照时长
  [key: string]: any    // 其他字段
}

/**
 * 获取每日日出日落时间
 * @param date 日期（YYYYMMDD格式）
 */
export const getSunriseDaily = (date: string): Promise<SunriseData[]> => {
  return apiCache.wrap(
    `${CACHE_VERSION}_alternative_sunrise_daily_${date}`,
    () => request.get('/sunrise_daily', { params: { date } }),
    CACHE_TTL
  )
}

/**
 * 获取每月日出日落时间
 * @param date 月份（YYYYMM格式）
 */
export const getSunriseMonthly = (date: string): Promise<SunriseData[]> => {
  return apiCache.wrap(
    `${CACHE_VERSION}_alternative_sunrise_monthly_${date}`,
    () => request.get('/sunrise_monthly', { params: { date } }),
    CACHE_TTL
  )
}

/**
 * 获取电视剧播映数据
 */
export const getVideoTV = (): Promise<VideoData[]> => {
  return apiCache.wrap(
    `${CACHE_VERSION}_alternative_video_tv`,
    () => request.get('/video_tv'),
    CACHE_TTL
  )
}

/**
 * 获取综艺节目播映数据
 */
export const getVideoVarietyShow = (): Promise<VideoData[]> => {
  return apiCache.wrap(
    `${CACHE_VERSION}_alternative_video_variety`,
    () => request.get('/video_variety_show'),
    CACHE_TTL
  )
}

/**
 * 获取微博舆情股票报告
 */
export const getWeiboStockReport = (): Promise<WeiboStockReport[]> => {
  return apiCache.wrap(
    `${CACHE_VERSION}_alternative_weibo_stock`,
    () => request.get('/stock_js_weibo_report'),
    CACHE_TTL
  )
}

/**
 * 获取福布斯中国最佳创投人榜
 * 注意：API返回的列名是第一行数据，需要进行字段映射
 */
export const getForbesChineseInvestors = async (): Promise<ForbesInvestor[]> => {
  return apiCache.wrap(
    `${CACHE_VERSION}_alternative_forbes_investors`,
    async () => {
      const rawData: any[] = await request.get('/forbes_rank')

      if (rawData.length === 0) {
        return []
      }

      // API返回的列名格式: ['1', '沈南鹏', '男', '53', '红杉中国', '创始及执行合伙人']
      // 这些实际上是第一行数据（排名1的投资人），被pandas用作列名了
      //
      // ⚠️ 重要：JavaScript的Object.keys()会将数字字符串键按数字顺序排在前面！
      // 实际顺序是：['1', '53', '沈南鹏', '男', '红杉中国', '创始及执行合伙人']
      //                排名  年龄   姓名    性别

      const keys = Object.keys(rawData[0])

      // 手动添加第一行数据（从列名中恢复排名1的投资人）
      // 修正：考虑Object.keys()的排序规则
      const firstRow: ForbesInvestor = {
        排名: Number(keys[0]),        // '1' -> 1 (第一个数字键)
        年龄: keys[1],                 // '53' (第二个数字键)
        姓名: keys[2],                 // '沈南鹏' (第一个字符串键)
        性别: keys[3],                 // '男' (第二个字符串键)
        机构: keys[4],                 // '红杉中国'
        职位: keys[5]                  // '创始及执行合伙人'
      }

      // 映射剩余的数据（排名2-99）
      const restData: ForbesInvestor[] = rawData.map(item => ({
        排名: Number(item[keys[0]]),  // 排名 (第一个数字键)
        年龄: item[keys[1]],           // 年龄 (第二个数字键)
        姓名: item[keys[2]],           // 姓名 (第一个字符串键)
        性别: item[keys[3]],           // 性别 (第二个字符串键)
        机构: item[keys[4]],           // 机构
        职位: item[keys[5]]            // 职位
      }))

      // 合并第一行和其他行，返回完整的99条数据
      return [firstRow, ...restData]
    },
    CACHE_TTL
  )
}

// ==================== 工具函数 ====================

/**
 * 获取AQI等级和颜色
 * @param aqi AQI值
 * @returns 等级名称和对应颜色
 */
export const getAQILevel = (aqi: number): { level: string; color: string } => {
  if (aqi <= 50) return { level: '优', color: '#30d158' }
  if (aqi <= 100) return { level: '良', color: '#ffd60a' }
  if (aqi <= 150) return { level: '轻度污染', color: '#ff9500' }
  if (aqi <= 200) return { level: '中度污染', color: '#ff3b30' }
  if (aqi <= 300) return { level: '重度污染', color: '#bf5af2' }
  return { level: '严重污染', color: '#ac8e68' }
}

/**
 * 格式化票房数据（万元转亿元）
 * @param value 票房值（万元）
 * @returns 格式化字符串
 */
export const formatBoxOffice = (value: number): string => {
  if (value >= 10000) {
    return `${(value / 10000).toFixed(2)}亿`
  }
  return `${value.toFixed(0)}万`
}

/**
 * 格式化增长率
 * @param value 增长率字符串（如"+15.3%"）
 * @returns { value: number, isPositive: boolean }
 */
export const parseGrowthRate = (value: string): { value: number; isPositive: boolean } => {
  const match = value.match(/([+-]?[\d.]+)%?/)
  if (match) {
    const num = parseFloat(match[1])
    return { value: Math.abs(num), isPositive: num >= 0 }
  }
  return { value: 0, isPositive: true }
}

/**
 * 获取当前年月（YYYYMM格式）
 */
export const getCurrentYearMonth = (): string => {
  const now = new Date()
  const year = now.getFullYear()
  const month = String(now.getMonth() + 1).padStart(2, '0')
  return `${year}${month}`
}

/**
 * 获取昨天日期（YYYYMMDD格式）
 */
export const getYesterday = (): string => {
  const yesterday = new Date()
  yesterday.setDate(yesterday.getDate() - 1)
  const year = yesterday.getFullYear()
  const month = String(yesterday.getMonth() + 1).padStart(2, '0')
  const day = String(yesterday.getDate()).padStart(2, '0')
  return `${year}${month}${day}`
}

/**
 * 获取上周日期（YYYY-MM-DD格式）
 */
export const getLastWeek = (): string => {
  const lastWeek = new Date()
  lastWeek.setDate(lastWeek.getDate() - 7)
  return lastWeek.toISOString().split('T')[0]
}

/**
 * 获取去年年份
 */
export const getLastYear = (): string => {
  return String(new Date().getFullYear() - 1)
}
