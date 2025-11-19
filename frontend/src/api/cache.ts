/**
 * API 缓存模块
 * 混合缓存策略：
 * - 小数据（< 1MB）: 使用 localStorage 持久化缓存
 * - 大数据（>= 1MB）: 自动降级到内存缓存（防止配额超限）
 * - 配额超限时: 自动降级到内存缓存
 *
 * 优点：
 * - 小数据跨页面刷新保留（localStorage）
 * - 大数据不受 localStorage 5-10MB 配额限制（内存缓存）
 * - 自动降级保证服务可用性
 */

interface CacheItem<T> {
  data: T
  timestamp: number
  ttl: number // 缓存有效期（毫秒）
}

class APICache {
  private prefix = 'akshare_cache_'
  private memoryCache = new Map<string, CacheItem<any>>()

  /**
   * 获取缓存数据
   * @param key 缓存键
   * @returns 缓存的数据，如果缓存不存在或已过期则返回 null
   */
  get<T>(key: string): T | null {
    try {
      const cacheKey = this.prefix + key
      const now = Date.now()

      // 1. 先尝试从内存缓存获取
      const memCached = this.memoryCache.get(cacheKey)
      if (memCached) {
        if (now - memCached.timestamp <= memCached.ttl) {
          return memCached.data as T
        } else {
          // 内存缓存过期，删除
          this.memoryCache.delete(cacheKey)
        }
      }

      // 2. 再尝试从 localStorage 获取
      const cached = localStorage.getItem(cacheKey)

      if (!cached) {
        return null
      }

      const item: CacheItem<T> = JSON.parse(cached)

      // 检查是否过期
      if (now - item.timestamp > item.ttl) {
        this.remove(key)
        return null
      }

      return item.data
    } catch (error) {
      console.error('Cache get error:', error)
      return null
    }
  }

  /**
   * 设置缓存数据
   * @param key 缓存键
   * @param data 要缓存的数据
   * @param ttl 缓存有效期（毫秒），默认 5 分钟
   */
  set<T>(key: string, data: T, ttl: number = 5 * 60 * 1000): void {
    try {
      const cacheKey = this.prefix + key
      const item: CacheItem<T> = {
        data,
        timestamp: Date.now(),
        ttl
      }

      const serialized = JSON.stringify(item)

      // 检查数据大小（超过 1MB 不缓存到 localStorage）
      const sizeInMB = new Blob([serialized]).size / 1024 / 1024
      if (sizeInMB > 1) {
        console.warn(`[Cache Skip] ${key} - Size too large (${sizeInMB.toFixed(2)}MB), using memory cache instead`)
        this.memoryCache.set(cacheKey, item)
        return
      }

      localStorage.setItem(cacheKey, serialized)
    } catch (error) {
      // localStorage 配额超限或其他错误，使用内存缓存降级
      if (error instanceof DOMException && error.name === 'QuotaExceededError') {
        console.warn(`[Cache Quota Exceeded] ${key} - Falling back to memory cache`)
        this.cleanup() // 清理过期缓存

        // 降级到内存缓存
        const cacheKey = this.prefix + key
        const item: CacheItem<T> = {
          data,
          timestamp: Date.now(),
          ttl
        }
        this.memoryCache.set(cacheKey, item)
      } else {
        console.error('Cache set error:', error)
      }
    }
  }

  /**
   * 移除指定缓存
   * @param key 缓存键
   */
  remove(key: string): void {
    const cacheKey = this.prefix + key
    localStorage.removeItem(cacheKey)
  }

  /**
   * 清理所有缓存
   */
  clear(): void {
    // 清理 localStorage
    const keys = Object.keys(localStorage)
    keys.forEach(key => {
      if (key.startsWith(this.prefix)) {
        localStorage.removeItem(key)
      }
    })

    // 清理内存缓存
    this.memoryCache.clear()
  }

  /**
   * 清理过期缓存
   */
  cleanup(): void {
    const now = Date.now()

    // 清理 localStorage 过期缓存
    const keys = Object.keys(localStorage)
    keys.forEach(key => {
      if (!key.startsWith(this.prefix)) {
        return
      }

      try {
        const cached = localStorage.getItem(key)
        if (!cached) return

        const item: CacheItem<any> = JSON.parse(cached)
        if (now - item.timestamp > item.ttl) {
          localStorage.removeItem(key)
        }
      } catch (error) {
        // 解析失败，直接删除
        localStorage.removeItem(key)
      }
    })

    // 清理内存缓存过期项
    for (const [key, item] of this.memoryCache.entries()) {
      if (now - item.timestamp > item.ttl) {
        this.memoryCache.delete(key)
      }
    }
  }

  /**
   * 包装 API 请求，自动处理缓存
   * @param key 缓存键
   * @param fetcher API 请求函数
   * @param ttl 缓存有效期（毫秒）
   * @returns 数据（来自缓存或 API）
   */
  async wrap<T>(
    key: string,
    fetcher: () => Promise<T>,
    ttl: number = 5 * 60 * 1000
  ): Promise<T> {
    // 尝试从缓存获取
    const cached = this.get<T>(key)
    if (cached !== null) {
      console.log(`[Cache Hit] ${key}`)
      return cached
    }

    // 缓存未命中，调用 API
    console.log(`[Cache Miss] ${key}`)
    const data = await fetcher()

    // 存入缓存
    this.set(key, data, ttl)

    return data
  }
}

// 导出单例
export const apiCache = new APICache()

// 定期清理过期缓存（每 10 分钟）
setInterval(() => {
  apiCache.cleanup()
}, 10 * 60 * 1000)
