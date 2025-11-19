/**
 * 基金收藏管理工具类
 * 使用 LocalStorage 持久化存储收藏列表
 */

const STORAGE_KEY = 'fund_favorites'

export interface FavoriteFund {
  基金代码: string
  基金简称: string
  addedTime: number  // 添加时间戳
}

/**
 * 获取所有收藏的基金
 */
export const getFavorites = (): FavoriteFund[] => {
  try {
    const data = localStorage.getItem(STORAGE_KEY)
    if (!data) return []
    return JSON.parse(data) as FavoriteFund[]
  } catch (error) {
    console.error('[收藏管理] 读取收藏列表失败:', error)
    return []
  }
}

/**
 * 添加收藏
 */
export const addFavorite = (code: string, name: string): boolean => {
  try {
    const favorites = getFavorites()

    // 检查是否已收藏
    if (favorites.some(f => f.基金代码 === code)) {
      console.warn('[收藏管理] 基金已在收藏列表中:', code)
      return false
    }

    const newFavorite: FavoriteFund = {
      基金代码: code,
      基金简称: name,
      addedTime: Date.now()
    }

    favorites.unshift(newFavorite) // 添加到开头
    localStorage.setItem(STORAGE_KEY, JSON.stringify(favorites))
    console.log('[收藏管理] 添加收藏成功:', code, name)
    return true
  } catch (error) {
    console.error('[收藏管理] 添加收藏失败:', error)
    return false
  }
}

/**
 * 取消收藏
 */
export const removeFavorite = (code: string): boolean => {
  try {
    const favorites = getFavorites()
    const newFavorites = favorites.filter(f => f.基金代码 !== code)

    if (newFavorites.length === favorites.length) {
      console.warn('[收藏管理] 基金不在收藏列表中:', code)
      return false
    }

    localStorage.setItem(STORAGE_KEY, JSON.stringify(newFavorites))
    console.log('[收藏管理] 取消收藏成功:', code)
    return true
  } catch (error) {
    console.error('[收藏管理] 取消收藏失败:', error)
    return false
  }
}

/**
 * 检查是否已收藏
 */
export const isFavorite = (code: string): boolean => {
  const favorites = getFavorites()
  return favorites.some(f => f.基金代码 === code)
}

/**
 * 获取收藏数量
 */
export const getFavoriteCount = (): number => {
  return getFavorites().length
}

/**
 * 清空所有收藏
 */
export const clearFavorites = (): boolean => {
  try {
    localStorage.removeItem(STORAGE_KEY)
    console.log('[收藏管理] 清空收藏列表成功')
    return true
  } catch (error) {
    console.error('[收藏管理] 清空收藏列表失败:', error)
    return false
  }
}
