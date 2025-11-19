// 基金基本信息
export interface FundInfo {
  基金代码: string
  基金简称: string
  拼音缩写?: string
  基金类型?: string
  拼音全称?: string
}

// 开放式基金实时净值
export interface FundDailyData {
  基金代码: string
  基金简称: string
  '2025-11-14-单位净值'?: string
  '2025-11-14-累计净值'?: string
  '2025-11-13-单位净值'?: string
  '2025-11-13-累计净值'?: string
  日增长值?: string
  日增长率?: string
  申购状态?: string
  赎回状态?: string
  手续费?: string
  [key: string]: any
}

// 基金排行数据
export interface FundRankData {
  序号?: number
  基金代码: string
  基金简称: string
  类型?: string
  '单位净值-日期'?: string
  '单位净值-单位净值'?: string
  '累计净值'?: string
  '日增长率'?: string
  '近1周'?: string
  '近1月'?: string
  '近3月'?: string
  '近6月'?: string
  '近1年'?: string
  '近2年'?: string
  '近3年'?: string
  '今年来'?: string
  '成立来'?: string
  手续费?: string
  [key: string]: any
}

// 基金历史净值
export interface FundHistData {
  净值日期: string
  单位净值: string
  累计净值?: string
  日增长率?: string
  申购状态?: string
  赎回状态?: string
  [key: string]: any
}

// 基金概况
export interface FundOverview {
  基金全称?: string
  基金简称?: string
  基金代码?: string
  基金类型?: string
  发行日期?: string
  成立日期?: string
  资产规模?: string
  份额规模?: string
  基金管理人?: string
  基金托管人?: string
  基金经理人?: string
  成立来分红?: string
  管理费率?: string
  托管费率?: string
  销售服务费率?: string
  最高认购费率?: string
  最高申购费率?: string
  最高赎回费率?: string
  业绩比较基准?: string
  跟踪标的?: string
  [key: string]: any
}

// 基金持仓
export interface FundHolding {
  序号?: number
  股票代码?: string
  股票名称?: string
  '占净值比例%'?: string
  持股数?: string
  持仓市值?: string
  季度?: string
  [key: string]: any
}

// 雪球 - 基金基本信息（返回 key-value 对数组）
export interface FundBasicInfoXQ {
  item: string  // 信息项名称，如 "基金代码"、"基金经理"、"基金公司"、"最新规模"、"成立时间"
  value: string  // 信息项值
}

// 雪球 - 基金分析数据（风险指标）
export interface FundAnalysisXQ {
  周期?: string                // 如：近1年、近3年、近5年
  较同类风险收益比?: number      // 较同类排名百分比
  较同类抗风险波动?: number      // 较同类排名百分比
  年化波动率?: number           // 百分比值，如 19.64
  年化夏普比率?: number         // 如 0.59
  最大回撤?: number             // 百分比值，如 14.05
  [key: string]: any
}

// 行业分布（东方财富）
export interface IndustryAllocation {
  序号?: number
  行业类别?: string  // ⚠️ 注意：字段名是 "行业类别" 而非 "行业名称"
  市值?: number
  占净值比例?: number
  截止时间?: string
  [key: string]: any
}

// 雪球 - 资产配置
export interface AssetAllocationXQ {
  资产类型?: string  // 如 "股票"、"债券"、"现金"、"其他"
  仓位占比?: number  // ⚠️ 注意：字段名是 "仓位占比" 而非 "占比"
  [key: string]: any
}

// 实时估值（来自数据库）
export interface FundValueEstimation {
  基金代码: string
  基金名称?: string
  估算时间?: string
  估算值?: string
  估算增长率?: string
  单位净值?: string
  日增长率?: string
  估算偏差?: string
  更新时间?: string
  [key: string]: any
}

// 基金评级
export interface FundRating {
  代码: string
  简称?: string
  基金经理?: string
  基金公司?: string
  '5星评级家数'?: number
  上海证券?: number | null  // 1-5星，null表示无评级
  招商证券?: number | null
  济安金信?: number | null
  晨星评级?: number | null
  手续费?: number
  类型?: string
  [key: string]: any
}

// 基金分红记录
export interface FundDividend {
  基金代码: string
  基金简称?: string
  权益登记日?: string
  除息日期?: string
  分红?: number
  分红发放日?: string
  [key: string]: any
}

// 基金对比 - 基础信息
export interface FundCompareBasicInfo {
  基金全称?: string
  基金简称?: string
  基金类型?: string
  成立日期?: string
  基金经理人?: string
  基金管理人?: string
  资产规模?: string
  管理费率?: string
  托管费率?: string
}

// 基金对比 - 收益率
export interface FundCompareReturn {
  单位净值?: string
  累计净值?: string
  日增长率?: string
  近1周?: string
  近1月?: string
  近3月?: string
  近6月?: string
  近1年?: string
  近2年?: string
  近3年?: string
  今年来?: string
  成立来?: string
}

// 基金对比 - 风险指标
export interface FundCompareRisk {
  年化波动率?: string | number
  年化夏普比率?: string | number
  最大回撤?: string | number
}

// 基金对比 - 评级
export interface FundCompareRating {
  上海证券?: number | null
  招商证券?: number | null
  济安金信?: number | null
  晨星评级?: number | null
  "5星评级家数"?: number
}

// 基金对比 - 分红统计
export interface FundCompareDividend {
  分红次数?: number
  累计分红?: number
}

// 基金对比 - 单个基金完整数据
export interface FundCompareData {
  基金代码: string
  基础信息: FundCompareBasicInfo
  收益率: FundCompareReturn
  风险指标: FundCompareRisk
  评级: FundCompareRating
  分红统计: FundCompareDividend
}

// 基金对比 - API 响应
export interface FundCompareResponse {
  success: boolean
  count: number
  data: FundCompareData[]
}

// API 响应类型
export interface ApiResponse<T> {
  code?: number
  data: T
  message?: string
}

// 基金历史净值 - 单条记录
export interface FundNetValueHistoryRecord {
  净值日期: string
  单位净值?: number
  累计净值?: number
  日增长率?: number
  同类排名?: number
  同类排名百分比?: number
  累计收益率?: number
}

// 基金历史净值 - API 响应
export interface FundNetValueHistoryResponse {
  success: boolean
  symbol: string
  indicator: string
  total: number
  data: FundNetValueHistoryRecord[]
  source: string
  message?: string
}

// 基金风险指标 - 单条记录
export interface FundRiskIndicator {
  周期: string                // 如：近1年、近3年、近5年
  较同类风险收益比: number      // 较同类排名百分比 (0-100)
  较同类抗风险波动: number      // 较同类排名百分比 (0-100)
  年化波动率: number           // 百分比值，如 19.64
  年化夏普比率: number         // 如 0.59
  最大回撤: number             // 百分比值，如 14.05
}

// 基金风险指标 - API 响应
export interface FundRiskIndicatorResponse {
  success: boolean
  data: FundRiskIndicator[]
  count: number
  source: string              // "database" 或 "xueqiu"
  message?: string
}
