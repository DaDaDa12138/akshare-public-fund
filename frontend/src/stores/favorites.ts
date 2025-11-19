import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import {
  getFavorites,
  addFavorite as addFavoriteToStorage,
  removeFavorite as removeFavoriteFromStorage,
  isFavorite as checkIsFavorite,
  clearFavorites as clearFavoritesFromStorage,
  type FavoriteFund
} from '@/utils/favorites'

export const useFavoritesStore = defineStore('favorites', () => {
  // 状态
  const favorites = ref<FavoriteFund[]>([])

  // 计算属性
  const favoriteCount = computed(() => favorites.value.length)
  const favoriteCodes = computed(() => favorites.value.map(f => f.基金代码))

  // 初始化：从LocalStorage加载收藏列表
  const loadFavorites = () => {
    favorites.value = getFavorites()
    console.log('[收藏Store] 加载收藏列表:', favorites.value.length, '个')
  }

  // 添加收藏
  const addFavorite = (code: string, name: string) => {
    const success = addFavoriteToStorage(code, name)
    if (success) {
      loadFavorites() // 重新加载
    }
    return success
  }

  // 取消收藏
  const removeFavorite = (code: string) => {
    const success = removeFavoriteFromStorage(code)
    if (success) {
      loadFavorites() // 重新加载
    }
    return success
  }

  // 切换收藏状态
  const toggleFavorite = (code: string, name: string) => {
    if (isFavorite(code)) {
      return removeFavorite(code)
    } else {
      return addFavorite(code, name)
    }
  }

  // 检查是否已收藏
  const isFavorite = (code: string) => {
    return checkIsFavorite(code)
  }

  // 清空所有收藏
  const clearFavorites = () => {
    const success = clearFavoritesFromStorage()
    if (success) {
      favorites.value = []
    }
    return success
  }

  return {
    favorites,
    favoriteCount,
    favoriteCodes,
    loadFavorites,
    addFavorite,
    removeFavorite,
    toggleFavorite,
    isFavorite,
    clearFavorites
  }
})
