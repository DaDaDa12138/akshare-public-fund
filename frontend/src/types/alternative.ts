/**
 * 另类数据 TypeScript 类型定义
 * 包含汽车销量、空气质量、电影票房、财富排行榜等数据类型
 */

// ==================== 汽车销量数据类型 ====================

/**
 * 汽车市场总体数据（按月份）
 */
export interface CarMarketTotal {
  月份: string
  [year: string]: string | number  // 动态年份列（如"2024年"、"2023年"）
}

/**
 * 厂商销售排名数据
 */
export interface CarManufacturerRank {
  厂商: string
  [year: string]: string | number  // 动态年份列
}

/**
 * 车型分类数据
 */
export interface CarCategoryData {
  月份: string
  [year: string]: string | number
}

/**
 * 国别细分市场数据
 */
export interface CarCountryData {
  月份: string
  自主: number
  德系: number
  日系: number
  法系?: number
  美系: number
  韩系: number
  其他欧系?: number
}

/**
 * 级别细分市场数据（A00/A0/A/B/C级）
 */
export interface CarSegmentData {
  月份: string
  A00级?: number
  A0级?: number
  A级: number
  B级: number
  C级?: number
}

/**
 * 新能源细分市场数据
 */
export interface CarFuelData {
  月份: string
  [year: string]: string | number
}

/**
 * 盖世汽车销量排行
 */
export interface CarSaleRankGasgoo {
  排名: number
  车企?: string
  品牌?: string
  车型?: string
  销量: number
  同比: string
  环比: string
}

// ==================== 空气质量数据类型 ====================

/**
 * 城市空气质量实时数据
 */
export interface AirQualityCity {
  城市: string
  AQI: number
  'PM2.5浓度'?: number
  PM2_5?: number  // 兼容不同字段名
  首要污染物: string
  质量等级: string
  PM10?: number
  SO2?: number
  NO2?: number
  CO?: number
  O3?: number
}

/**
 * 空气质量历史数据
 */
export interface AirQualityHistory {
  时间: string
  日期?: string  // 兼容不同字段名
  AQI: number
  PM2_5: number
  PM10?: number
  SO2?: number
  NO2?: number
  CO?: number
  O3?: number
  质量等级: string
}

/**
 * 空气质量排名数据
 */
export interface AirQualityRank {
  排名: number
  城市: string
  AQI: number
  PM2_5?: number
  质量等级: string
}

/**
 * 监测点空气质量数据
 */
export interface AirQualityWatchPoint {
  监测点名称: string
  监测点?: string  // 兼容字段名
  时间: string
  AQI: number
  PM2_5: number
  PM10: number
  SO2?: number
  NO2?: number
  CO?: number
  O3?: number
}

// ==================== 电影票房数据类型 ====================

/**
 * 实时电影票房数据
 */
export interface MovieBoxOfficeRealtime {
  排名: number
  影片名: string
  实时票房: number  // 万元
  实时占比: number  // 百分比
  累计票房: number  // 万元
  上映天数: number
  票房占比?: number
}

/**
 * 单日电影票房数据
 */
export interface MovieBoxOfficeDaily {
  排名: number
  影片名: string
  单日票房: number  // 万元
  单日占比: number  // 百分比
  场均人次?: number
  平均票价?: number  // 元
  环比?: string
  累计票房?: number
}

/**
 * 周电影票房数据
 */
export interface MovieBoxOfficeWeekly {
  排名: number
  影片名: string
  周票房: number  // 万元
  周占比: number  // 百分比
  环比?: string
  场均人次?: number
}

/**
 * 月电影票房数据
 */
export interface MovieBoxOfficeMonthly {
  排名: number
  影片名: string
  月票房: number  // 万元
  月占比: number  // 百分比
  累计票房?: number
  上映日期?: string
}

/**
 * 年度电影票房数据
 */
export interface MovieBoxOfficeYearly {
  排名: number
  影片名: string
  年度票房: number  // 万元
  年度占比: number  // 百分比
  平均票价?: number
  类型?: string
  上映日期?: string
}

/**
 * 影院票房排行数据
 */
export interface MovieCinemaBoxOffice {
  排名: number
  影院名称: string
  单日票房?: number  // 元（日榜）
  周票房?: number  // 万元（周榜）
  场次?: number
  人次?: number
  上座率?: number  // 百分比
  城市: string
  单银幕票房?: number
  场均人次?: number
}

// ==================== 财富排行榜数据类型 ====================

/**
 * 财富500强数据
 */
export interface FortuneRank {
  排名: number
  公司名称: string
  营业收入: number  // 百万美元
  利润?: number  // 百万美元
  国家: string
  行业?: string
}

/**
 * 福布斯榜单数据（通用结构）
 */
export interface ForbesRank {
  排名: number
  姓名?: string
  企业名?: string
  名称?: string  // 兼容字段
  财富?: number  // 亿元
  估值?: number  // 亿元
  行业: string
  年龄?: number
  公司?: string
  [key: string]: any  // 支持87个不同榜单的特殊字段
}

/**
 * 新财富500富豪榜数据
 */
export interface XincaifuRank {
  排名: number
  姓名: string
  财富: number  // 亿元
  公司?: string
  行业: string
  年龄?: number
  财富变化?: string
}

/**
 * 胡润百富榜数据
 */
export interface HurunRank {
  排名: number
  姓名?: string
  企业?: string
  名称?: string  // 兼容字段
  财富?: number  // 亿元
  估值?: number  // 亿元（独角兽榜）
  行业: string
  公司?: string
  年龄?: number
  财富变化?: string
}

// ==================== 其他数据类型 ====================

/**
 * 新闻联播文字稿数据
 */
export interface NewsCCTV {
  新闻日期: string
  新闻标题: string
  新闻内容: string
}

/**
 * 日出日落数据
 */
export interface SunriseData {
  日期?: string
  日出: string  // 时间格式 "HH:MM"
  日落: string
  日长: string
}

/**
 * 视频播映数据（电视剧/综艺）- 实际字段名
 */
export interface VideoData {
  排序: number  // 排名
  名称: string  // 电视剧名或综艺名
  类型: string
  播映指数: number
  媒体热度: number
  用户热度: number
  好评度: number
  观看度: number
  统计日期: string
}

/**
 * 艺人商业价值数据
 */
export interface ArtistBusinessValue {
  排名: number
  艺人名: string
  商业价值指数: number
  专业热度: number
  关注热度: number
  预测热度: number
  美誉度: number
}

/**
 * 艺人流量价值数据
 */
export interface ArtistOnlineValue {
  排名: number
  艺人名: string
  流量价值: number
  专业热度: number
  关注热度: number
  预测热度: number
  带货力: number
}

/**
 * 生活成本排名数据
 */
export interface CostLiving {
  排名: number
  城市: string
  生活成本指数: number
  租金指数?: number
  购买力指数?: number
}

/**
 * 微博舆情股票数据 - 实际字段名
 */
export interface WeiboStockReport {
  name: string  // 股票名称
  rate: number  // 涨跌幅
}

/**
 * 福布斯中国最佳创投人榜数据
 */
export interface ForbesInvestor {
  排名: number  // 排名
  姓名: string  // 投资人姓名
  性别: string  // 性别
  年龄: string  // 年龄
  机构: string  // 投资机构
  职位: string  // 职务
}

/**
 * 彭博亿万富豪指数
 */
export interface BloombergBillionaires {
  排名: number
  姓名: string
  净资产: number  // 十亿美元
  国家: string
  行业: string
  年龄?: number
}

// ==================== API 响应类型 ====================

/**
 * 通用API响应结构
 */
export interface AlternativeDataResponse<T = any> {
  success: boolean
  data: T[]
  message?: string
  total?: number
}

/**
 * 图表数据格式（ECharts使用）
 */
export interface ChartData {
  xAxis: string[]  // X轴数据（如月份、排名）
  series: ChartSeries[]  // 系列数据
}

export interface ChartSeries {
  name: string  // 系列名称
  type: 'line' | 'bar' | 'pie' | 'scatter' | 'radar' | 'heatmap'  // 图表类型
  data: (number | { value: number; name?: string })[]  // 数据点
  [key: string]: any  // 其他ECharts配置
}

/**
 * 标签页类型
 */
export type AlternativeTab = 'car' | 'air' | 'movie' | 'wealth' | 'news' | 'artist' | 'sunrise' | 'video' | 'weibo' | 'forbes'

/**
 * 加载状态
 */
export interface LoadingState {
  isLoading: boolean
  error: string | null
}
