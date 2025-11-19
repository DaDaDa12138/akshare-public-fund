<template>
  <div class="fund-favorites">
    <div class="container">
      <!-- 标题 -->
      <div class="page-header">
        <h1>自选基金</h1>
        <p class="text-secondary">快速访问您关注的基金</p>
      </div>

      <!-- 空状态 -->
      <div v-if="favoritesStore.favoriteCount === 0" class="empty-state card">
        <el-empty description="您还没有收藏任何基金">
          <el-button type="primary" @click="goToSearch">去搜索基金</el-button>
        </el-empty>
      </div>

      <!-- 收藏列表 -->
      <div v-else>
        <!-- 统计信息 -->
        <div class="stats-bar card">
          <div class="stat-item">
            <span class="stat-label">收藏总数：</span>
            <span class="stat-value">{{ favoritesStore.favoriteCount }}</span>
          </div>
          <div class="actions">
            <el-button
              type="primary"
              plain
              size="small"
              @click="loadFundData"
              :loading="loading"
            >
              {{ loading ? '加载中...' : '刷新数据' }}
            </el-button>
            <el-button
              type="danger"
              plain
              size="small"
              @click="confirmClearAll"
            >
              清空全部收藏
            </el-button>
          </div>
        </div>

        <!-- 基金表格 -->
        <div class="favorites-table card">
          <el-table
            :data="enrichedFavorites"
            v-loading="loading"
            stripe
            style="width: 100%"
            @row-click="handleRowClick"
          >
            <el-table-column prop="基金代码" label="基金代码" width="100" fixed />
            <el-table-column prop="基金简称" label="基金名称" min-width="180" />

            <!-- 实时估值 -->
            <el-table-column label="实时估值增长率" width="140" align="right">
              <template #default="{ row }">
                <span v-if="row.估算增长率 !== undefined" :class="getRateClass(row.估算增长率)">
                  {{ formatPercent(row.估算增长率) }}
                </span>
                <span v-else class="text-secondary">-</span>
              </template>
            </el-table-column>

            <!-- 近期收益率 -->
            <el-table-column label="近1周" width="100" align="right">
              <template #default="{ row }">
                <span v-if="row.近1周 !== undefined" :class="getRateClass(row.近1周)">
                  {{ formatPercent(row.近1周) }}
                </span>
                <span v-else class="text-secondary">-</span>
              </template>
            </el-table-column>

            <el-table-column label="近1月" width="100" align="right">
              <template #default="{ row }">
                <span v-if="row.近1月 !== undefined" :class="getRateClass(row.近1月)">
                  {{ formatPercent(row.近1月) }}
                </span>
                <span v-else class="text-secondary">-</span>
              </template>
            </el-table-column>

            <el-table-column label="近3月" width="100" align="right">
              <template #default="{ row }">
                <span v-if="row.近3月 !== undefined" :class="getRateClass(row.近3月)">
                  {{ formatPercent(row.近3月) }}
                </span>
                <span v-else class="text-secondary">-</span>
              </template>
            </el-table-column>

            <el-table-column label="近6月" width="100" align="right">
              <template #default="{ row }">
                <span v-if="row.近6月 !== undefined" :class="getRateClass(row.近6月)">
                  {{ formatPercent(row.近6月) }}
                </span>
                <span v-else class="text-secondary">-</span>
              </template>
            </el-table-column>

            <el-table-column label="近1年" width="100" align="right">
              <template #default="{ row }">
                <span v-if="row.近1年 !== undefined" :class="getRateClass(row.近1年)">
                  {{ formatPercent(row.近1年) }}
                </span>
                <span v-else class="text-secondary">-</span>
              </template>
            </el-table-column>

            <el-table-column label="操作" width="260" fixed="right">
              <template #default="{ row }">
                <el-button
                  type="danger"
                  size="small"
                  @click.stop="removeFavorite(row)"
                >
                  取消收藏
                </el-button>
                <el-button
                  type="primary"
                  size="small"
                  @click.stop="viewDetail(row.基金代码)"
                >
                  查看详情
                </el-button>
                <el-button
                  type="default"
                  size="small"
                  @click.stop="viewChart(row.基金代码)"
                >
                  走势图
                </el-button>
              </template>
            </el-table-column>
          </el-table>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useFavoritesStore } from '@/stores/favorites'
import { useFundStore } from '@/stores/fund'
import { ElMessage, ElMessageBox } from 'element-plus'
import type { FavoriteFund } from '@/utils/favorites'
import axios from 'axios'

const router = useRouter()
const favoritesStore = useFavoritesStore()
const fundStore = useFundStore()

// 数据状态
const loading = ref(false)
const fundDataMap = ref<Map<string, any>>(new Map())

// 合并收藏数据和实时数据
const enrichedFavorites = computed(() => {
  return favoritesStore.favorites.map(fav => {
    const data = fundDataMap.value.get(fav.基金代码) || {}
    return {
      ...fav,
      ...data
    }
  })
})

// 加载基金实时数据
const loadFundData = async () => {
  if (favoritesStore.favoriteCount === 0) return

  loading.value = true
  const newDataMap = new Map()

  try {
    const symbols = favoritesStore.favorites.map(f => f.基金代码)
    console.log('[自选基金] 开始加载数据，基金数量:', symbols.length, '代码:', symbols)

    // 批量获取基金对比数据（包含收益率）
    try {
      const response = await axios.post('/api/fund_compare', {
        symbols: symbols
      })

      console.log('[自选基金] 收益率数据响应:', response.data)

      if (response.data && response.data.success && response.data.data) {
        response.data.data.forEach((fund: any) => {
          const code = fund.基金代码
          const fundInfo: any = {
            基金代码: code
          }

          // 提取收益率数据
          if (fund.收益率) {
            const returns = fund.收益率
            fundInfo.近1周 = returns.近1周 ? parseFloat(returns.近1周) : undefined
            fundInfo.近1月 = returns.近1月 ? parseFloat(returns.近1月) : undefined
            fundInfo.近3月 = returns.近3月 ? parseFloat(returns.近3月) : undefined
            fundInfo.近6月 = returns.近6月 ? parseFloat(returns.近6月) : undefined
            fundInfo.近1年 = returns.近1年 ? parseFloat(returns.近1年) : undefined
            console.log(`[自选基金] ${code} 收益率:`, fundInfo)
          }

          newDataMap.set(code, fundInfo)
        })
      }
    } catch (error: any) {
      console.error('[自选基金] 获取收益率失败:', error)
      ElMessage.warning('收益率数据加载失败: ' + (error.response?.data?.detail || error.message))
    }

    // 获取实时估值数据
    try {
      const estimationSymbols = symbols.join(',')
      const estResponse = await axios.get(`/api/fund_estimation/batch?symbols=${estimationSymbols}`)

      console.log('[自选基金] 估值数据响应:', estResponse.data)

      if (estResponse.data && Array.isArray(estResponse.data)) {
        estResponse.data.forEach((est: any) => {
          const code = est.基金代码
          const existing = newDataMap.get(code) || {}
          const rate = est.估算增长率 ? parseFloat(est.估算增长率) : undefined
          newDataMap.set(code, {
            ...existing,
            估算增长率: rate
          })
          console.log(`[自选基金] ${code} 估值增长率: ${rate}`)
        })
      }
    } catch (error: any) {
      console.error('[自选基金] 获取实时估值失败:', error)
      ElMessage.warning('实时估值数据加载失败: ' + (error.response?.data?.detail || error.message))
    }

    fundDataMap.value = newDataMap
    console.log('[自选基金] 最终数据映射:', fundDataMap.value)

    if (newDataMap.size > 0) {
      ElMessage.success('数据刷新成功')
    } else {
      ElMessage.warning('未能获取到基金数据，请稍后重试')
    }
  } catch (error: any) {
    console.error('[自选基金] 加载基金数据失败:', error)
    ElMessage.error('数据加载失败: ' + (error.response?.data?.detail || error.message))
  } finally {
    loading.value = false
  }
}

// 格式化百分比
const formatPercent = (value: number | string | undefined) => {
  if (value === undefined || value === null || value === '') return '-'
  const num = typeof value === 'string' ? parseFloat(value) : value
  if (isNaN(num)) return '-'
  return num > 0 ? `+${num.toFixed(2)}%` : `${num.toFixed(2)}%`
}

// 获取涨跌样式类
const getRateClass = (value: number | string | undefined) => {
  if (value === undefined || value === null || value === '') return ''
  const num = typeof value === 'string' ? parseFloat(value) : value
  if (isNaN(num)) return ''
  if (num > 0) return 'rate-up'
  if (num < 0) return 'rate-down'
  return ''
}

// 行点击
const handleRowClick = (row: FavoriteFund) => {
  viewDetail(row.基金代码)
}

// 查看详情
const viewDetail = (code: string) => {
  router.push(`/detail/${code}`)
}

// 查看走势图
const viewChart = (code: string) => {
  fundStore.selectedFund = code
  router.push('/chart')
}

// 取消收藏
const removeFavorite = (fund: FavoriteFund) => {
  ElMessageBox.confirm(
    `确定要取消收藏「${fund.基金简称}」吗？`,
    '确认取消',
    {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    }
  ).then(() => {
    const success = favoritesStore.removeFavorite(fund.基金代码)
    if (success) {
      ElMessage.success(`已取消收藏：${fund.基金简称}`)
      // 从数据映射中移除
      fundDataMap.value.delete(fund.基金代码)
    }
  }).catch(() => {
    // 用户取消
  })
}

// 清空全部收藏
const confirmClearAll = () => {
  ElMessageBox.confirm(
    `确定要清空全部 ${favoritesStore.favoriteCount} 个收藏吗？此操作不可撤销！`,
    '确认清空',
    {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    }
  ).then(() => {
    const success = favoritesStore.clearFavorites()
    if (success) {
      ElMessage.success('已清空全部收藏')
      fundDataMap.value.clear()
    }
  }).catch(() => {
    // 用户取消
  })
}

// 去搜索页面
const goToSearch = () => {
  router.push('/')
}

// 页面加载时自动获取数据
onMounted(() => {
  if (favoritesStore.favoriteCount > 0) {
    loadFundData()
  }
})
</script>

<style scoped>
.fund-favorites {
  min-height: 100vh;
  padding: var(--spacing-lg);
}

.page-header {
  text-align: center;
  margin-bottom: var(--spacing-xl);
}

.page-header h1 {
  font-size: 28px;
  font-weight: 600;
  color: var(--color-text-primary);
  margin-bottom: var(--spacing-sm);
}

.empty-state {
  padding: var(--spacing-3xl);
  text-align: center;
}

.stats-bar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: var(--spacing-lg);
  margin-bottom: var(--spacing-lg);
}

.stat-item {
  display: flex;
  align-items: center;
  gap: var(--spacing-sm);
}

.stat-label {
  color: var(--color-text-secondary);
  font-size: 15px;
}

.stat-value {
  color: var(--color-accent);
  font-size: 21px;
  font-weight: 600;
}

.actions {
  display: flex;
  gap: var(--spacing-sm);
}

.favorites-table {
  overflow: hidden;
}

/* 涨跌样式 */
.rate-up {
  color: #f56c6c;
  font-weight: 500;
}

.rate-down {
  color: #67c23a;
  font-weight: 500;
}

/* 表格行悬停效果 */
:deep(.el-table__row) {
  cursor: pointer;
  transition: all var(--transition-base);
}

:deep(.el-table__row:hover) {
  transform: scale(1.002);
}

@media (max-width: 734px) {
  .page-header h1 {
    font-size: 24px;
  }

  .stats-bar {
    flex-direction: column;
    gap: var(--spacing-md);
    align-items: flex-start;
  }

  .actions {
    width: 100%;
    justify-content: flex-start;
  }
}
</style>
