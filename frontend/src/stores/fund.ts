import { defineStore } from 'pinia'
import { ref } from 'vue'
import type { FundInfo, FundDailyData, FundRankData } from '@/types/fund'
import { getFundList, getFundDailyData, getFundRank } from '@/api/fund'

export const useFundStore = defineStore('fund', () => {
  // 基金列表
  const fundList = ref<FundInfo[]>([])
  const fundListLoading = ref(false)

  // 实时净值数据
  const fundDailyData = ref<FundDailyData[]>([])
  const fundDailyLoading = ref(false)

  // 基金排行数据
  const fundRankData = ref<FundRankData[]>([])
  const fundRankLoading = ref(false)

  // 当前选中的基金
  const selectedFund = ref<string>('')

  /**
   * 加载基金列表
   */
  const loadFundList = async () => {
    if (fundList.value.length > 0) {
      return fundList.value
    }

    fundListLoading.value = true
    try {
      const data = await getFundList()
      fundList.value = data
      return data
    } catch (error) {
      console.error('Failed to load fund list:', error)
      return []
    } finally {
      fundListLoading.value = false
    }
  }

  /**
   * 加载实时净值数据
   */
  const loadFundDailyData = async () => {
    fundDailyLoading.value = true
    try {
      const data = await getFundDailyData()
      fundDailyData.value = data
      return data
    } catch (error) {
      console.error('Failed to load fund daily data:', error)
      return []
    } finally {
      fundDailyLoading.value = false
    }
  }

  /**
   * 加载基金排行数据
   */
  const loadFundRank = async (symbol: string = '全部') => {
    fundRankLoading.value = true
    try {
      const data = await getFundRank(symbol)
      fundRankData.value = data
      return data
    } catch (error) {
      console.error('Failed to load fund rank:', error)
      return []
    } finally {
      fundRankLoading.value = false
    }
  }

  /**
   * 搜索基金
   */
  const searchFund = (keyword: string) => {
    if (!keyword) return fundList.value

    const key = keyword.toLowerCase()
    return fundList.value.filter(fund =>
      fund.基金代码.includes(key) ||
      fund.基金简称.toLowerCase().includes(key) ||
      (fund.拼音缩写 && fund.拼音缩写.toLowerCase().includes(key))
    )
  }

  return {
    fundList,
    fundListLoading,
    fundDailyData,
    fundDailyLoading,
    fundRankData,
    fundRankLoading,
    selectedFund,
    loadFundList,
    loadFundDailyData,
    loadFundRank,
    searchFund
  }
})
