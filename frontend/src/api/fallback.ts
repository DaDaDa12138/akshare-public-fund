/**
 * API降级配置和策略
 * 当主接口失败时，自动切换到备用接口或组合查询
 */

import type { AxiosError } from 'axios'

/**
 * API降级策略配置
 */
interface FallbackStrategy {
  primary: string              // 主接口
  fallbacks: string[]          // 备用接口列表（按优先级）
  combineStrategy?: string     // 组合查询策略名称
  defaultValue?: any           // 默认返回值
}

/**
 * API降级映射表
 */
export const API_FALLBACK_MAP: Record<string, FallbackStrategy> = {
  // 基金历史净值：主接口fund_open_fund_info_em，备用fund_etf_fund_info_em
  'fund_open_fund_info_em': {
    primary: '/fund_open_fund_info_em',
    fallbacks: ['/fund_etf_fund_info_em'],
    defaultValue: []
  },

  // 基金概况：已废弃，使用组合查询
  'fund_overview_em': {
    primary: '/fund_overview_em',
    fallbacks: [],
    combineStrategy: 'fund_basic_info',
    defaultValue: null
  },

  // 基金持仓：无备用，返回空数组
  'fund_portfolio_hold_em': {
    primary: '/fund_portfolio_hold_em',
    fallbacks: [],
    defaultValue: []
  }
}

/**
 * 判断是否为可忽略的错误（404、500等）
 */
export function isIgnorableError(error: AxiosError): boolean {
  if (!error.response) return false
  const status = error.response.status
  return status === 404 || status === 500 || status === 502 || status === 503
}

/**
 * 获取降级策略
 */
export function getFallbackStrategy(apiPath: string): FallbackStrategy | null {
  const apiName = apiPath.replace('/api/public/', '').split('?')[0]
  return API_FALLBACK_MAP[apiName] || null
}

/**
 * 错误日志收集
 */
interface ErrorLog {
  api: string
  params: any
  error: string
  timestamp: number
  retryCount: number
}

class ErrorLogCollector {
  private logs: ErrorLog[] = []
  private maxLogs = 100

  add(api: string, params: any, error: AxiosError, retryCount: number = 0) {
    const log: ErrorLog = {
      api,
      params,
      error: error.message,
      timestamp: Date.now(),
      retryCount
    }

    this.logs.unshift(log)

    // 保持最多100条日志
    if (this.logs.length > this.maxLogs) {
      this.logs = this.logs.slice(0, this.maxLogs)
    }

    // 开发环境下输出到控制台
    if (import.meta.env.DEV) {
      console.warn(`[API Error] ${api}`, {
        params,
        error: error.message,
        status: error.response?.status
      })
    }
  }

  get() {
    return this.logs
  }

  clear() {
    this.logs = []
  }

  // 获取API错误统计
  getStats() {
    const stats: Record<string, number> = {}
    this.logs.forEach(log => {
      stats[log.api] = (stats[log.api] || 0) + 1
    })
    return stats
  }
}

export const errorLogger = new ErrorLogCollector()

/**
 * API健康状态监控
 */
interface ApiHealthStatus {
  api: string
  status: 'healthy' | 'degraded' | 'down'
  lastCheck: number
  errorRate: number          // 错误率 (0-1)
  avgResponseTime: number    // 平均响应时间(ms)
}

class ApiHealthMonitor {
  private health: Map<string, ApiHealthStatus> = new Map()
  private checkInterval = 5 * 60 * 1000 // 5分钟

  update(api: string, success: boolean, responseTime: number) {
    const current = this.health.get(api) || {
      api,
      status: 'healthy' as const,
      lastCheck: Date.now(),
      errorRate: 0,
      avgResponseTime: 0
    }

    // 计算新的错误率（使用移动平均）
    const newErrorRate = success ? current.errorRate * 0.9 : current.errorRate * 0.9 + 0.1

    // 计算新的平均响应时间（使用移动平均）
    const newAvgResponseTime = current.avgResponseTime * 0.9 + responseTime * 0.1

    // 确定健康状态
    let status: ApiHealthStatus['status'] = 'healthy'
    if (newErrorRate > 0.5) {
      status = 'down'
    } else if (newErrorRate > 0.2 || newAvgResponseTime > 5000) {
      status = 'degraded'
    }

    this.health.set(api, {
      api,
      status,
      lastCheck: Date.now(),
      errorRate: newErrorRate,
      avgResponseTime: newAvgResponseTime
    })
  }

  getStatus(api: string): ApiHealthStatus | null {
    return this.health.get(api) || null
  }

  getAllStatus(): ApiHealthStatus[] {
    return Array.from(this.health.values())
  }

  // 判断API是否应该使用降级策略
  shouldFallback(api: string): boolean {
    const status = this.health.get(api)
    if (!status) return false
    return status.status === 'down' || status.status === 'degraded'
  }
}

export const healthMonitor = new ApiHealthMonitor()
