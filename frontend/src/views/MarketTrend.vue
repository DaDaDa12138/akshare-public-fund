<template>
  <div class="market-trend">
    <div class="container">
      <!-- 页面标题 -->
      <div class="page-header">
        <h1 class="page-title">基金市场规模趋势</h1>
        <p class="page-description">查看全国基金市场总规模的季度变化趋势</p>
      </div>

      <!-- 加载状态 -->
      <div v-if="loading" class="loading-card card">
        <el-skeleton :rows="8" animated />
      </div>

      <!-- 数据展示 -->
      <div v-else-if="trendData.length > 0">
        <!-- 统计卡片 -->
        <div class="stats-grid">
          <div class="stat-card card">
            <div class="stat-icon">
              <el-icon :size="32"><TrendCharts /></el-icon>
            </div>
            <div class="stat-content">
              <div class="stat-value">{{ formatScale(getLatestScale()) }}亿</div>
              <div class="stat-label">最新市场规模</div>
            </div>
          </div>

          <div class="stat-card card">
            <div class="stat-icon success">
              <el-icon :size="32"><DataLine /></el-icon>
            </div>
            <div class="stat-content">
              <div class="stat-value">{{ trendData.length }}个</div>
              <div class="stat-label">季度数据点</div>
            </div>
          </div>

          <div class="stat-card card" :class="{ positive: getGrowthRate() > 0, negative: getGrowthRate() < 0 }">
            <div class="stat-icon" :class="{ success: getGrowthRate() > 0, danger: getGrowthRate() < 0 }">
              <el-icon :size="32">
                <component :is="getGrowthRate() >= 0 ? 'Top' : 'Bottom'" />
              </el-icon>
            </div>
            <div class="stat-content">
              <div class="stat-value">{{ getGrowthRate() }}%</div>
              <div class="stat-label">同比增长率</div>
            </div>
          </div>

          <div class="stat-card card">
            <div class="stat-icon warning">
              <el-icon :size="32"><Calendar /></el-icon>
            </div>
            <div class="stat-content">
              <div class="stat-value">{{ getLatestDate() }}</div>
              <div class="stat-label">最新更新</div>
            </div>
          </div>
        </div>

        <!-- 趋势图表 -->
        <div class="chart-card card">
          <div class="chart-header">
            <h2>
              <el-icon><DataAnalysis /></el-icon>
              市场规模趋势图
            </h2>
          </div>
          <div class="chart-content">
            <div class="simple-chart">
              <div
                v-for="(item, index) in trendData"
                :key="item.日期"
                class="chart-bar"
                :style="{ height: getBarHeight(item.市场总规模) + '%' }"
              >
                <div class="bar-label">
                  {{ formatScale(item.市场总规模) }}
                </div>
                <div class="bar-date">{{ formatDate(item.日期) }}</div>
              </div>
            </div>
          </div>
        </div>

        <!-- 数据表格 -->
        <div class="table-card card">
          <div class="table-header">
            <h2>
              <el-icon><Grid /></el-icon>
              历史数据详情
            </h2>
          </div>
          <el-table :data="displayData" stripe style="width: 100%">
            <el-table-column
              type="index"
              label="序号"
              width="80"
              align="center"
              :index="indexMethod"
            />

            <el-table-column prop="日期" label="日期" width="150" />

            <el-table-column
              prop="市场总规模"
              label="市场总规模（亿元）"
              width="180"
              align="right"
            >
              <template #default="{ row }">
                <span class="scale-value">{{ formatScale(row.市场总规模) }}</span>
              </template>
            </el-table-column>

            <el-table-column label="季度环比" width="150" align="right">
              <template #default="{ row, $index }">
                <span v-if="$index < trendData.length - 1" :class="getGrowthClass(row, $index)">
                  {{ calculateGrowth(row, $index) }}%
                </span>
                <span v-else class="text-secondary">-</span>
              </template>
            </el-table-column>

            <el-table-column prop="更新时间" label="更新时间" width="180" />
          </el-table>

          <!-- 分页 -->
          <div class="pagination">
            <el-pagination
              v-model:current-page="currentPage"
              v-model:page-size="pageSize"
              :page-sizes="[10, 20, 50]"
              :total="totalCount"
              layout="total, sizes, prev, pager, next"
              @size-change="handleSizeChange"
              @current-change="handleCurrentChange"
            />
          </div>
        </div>
      </div>

      <!-- 空状态 -->
      <EmptyState
        v-else-if="!loading"
        title="暂无数据"
        description="市场趋势数据暂未加载，请稍后再试"
      />
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import {
  TrendCharts,
  DataLine,
  Top,
  Bottom,
  Calendar,
  DataAnalysis,
  Grid
} from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import axios from 'axios'
import EmptyState from '@/components/EmptyState.vue'

// 数据状态
const loading = ref(false)
const trendData = ref<any[]>([])

// 分页
const currentPage = ref(1)
const pageSize = ref(10)

// 分页后的数据
const totalCount = computed(() => trendData.value.length)
const displayData = computed(() => {
  const start = (currentPage.value - 1) * pageSize.value
  const end = start + pageSize.value
  return trendData.value.slice(start, end)
})

// 序号计算
const indexMethod = (index: number) => {
  return (currentPage.value - 1) * pageSize.value + index + 1
}

// 加载数据
onMounted(() => {
  loadData()
})

// 加载市场趋势数据
const loadData = async () => {
  loading.value = true
  try {
    const response = await axios.get('/api/fund_market_trend')

    if (response.data.success) {
      trendData.value = response.data.data || []
      if (trendData.value.length === 0) {
        ElMessage.warning('暂无市场趋势数据')
      }
    } else {
      ElMessage.error(response.data.message || '加载失败')
    }
  } catch (error: any) {
    console.error('Failed to load market trend data:', error)
    ElMessage.error('加载数据失败: ' + (error.response?.data?.detail || error.message))
  } finally {
    loading.value = false
  }
}

// 获取最新规模
const getLatestScale = (): number => {
  if (trendData.value.length === 0) return 0
  return trendData.value[0].市场总规模 || 0
}

// 获取最新日期
const getLatestDate = (): string => {
  if (trendData.value.length === 0) return '-'
  return formatDate(trendData.value[0].日期)
}

// 计算增长率（同比）
const getGrowthRate = (): string => {
  if (trendData.value.length < 5) return '0.00'
  const latest = trendData.value[0].市场总规模 || 0
  const yearAgo = trendData.value[4].市场总规模 || 0
  if (yearAgo === 0) return '0.00'
  const growth = ((latest - yearAgo) / yearAgo) * 100
  return growth >= 0 ? `+${growth.toFixed(2)}` : growth.toFixed(2)
}

// 计算季度环比增长
const calculateGrowth = (row: any, index: number): string => {
  if (index >= trendData.value.length - 1) return '0.00'
  const current = row.市场总规模 || 0
  const previous = trendData.value[index + 1].市场总规模 || 0
  if (previous === 0) return '0.00'
  const growth = ((current - previous) / previous) * 100
  return growth >= 0 ? `+${growth.toFixed(2)}` : growth.toFixed(2)
}

// 获取增长样式类
const getGrowthClass = (row: any, index: number): string => {
  const growth = calculateGrowth(row, index)
  if (growth.startsWith('+')) return 'text-success'
  if (growth.startsWith('-')) return 'text-danger'
  return ''
}

// 获取柱状图高度
const getBarHeight = (value: number): number => {
  if (trendData.value.length === 0) return 0
  const max = Math.max(...trendData.value.map(item => item.市场总规模 || 0))
  if (max === 0) return 0
  return (value / max) * 100
}

// 格式化规模
const formatScale = (value: any): string => {
  if (!value || value === 'NaN') return '0.00'
  const num = parseFloat(value)
  if (isNaN(num)) return '0.00'
  return num.toFixed(2)
}

// 格式化日期
const formatDate = (value: string): string => {
  if (!value) return '-'
  // 将 2024-09-30 格式转换为 2024年Q3
  const parts = value.split('-')
  if (parts.length !== 3) return value
  const year = parts[0]
  const month = parseInt(parts[1])
  const quarter = Math.ceil(month / 3)
  return `${year}年Q${quarter}`
}

// 分页处理
const handleSizeChange = () => {
  currentPage.value = 1
}

const handleCurrentChange = () => {
  window.scrollTo({ top: 0, behavior: 'smooth' })
}
</script>

<style scoped>
.market-trend {
  min-height: 100vh;
}

.page-header {
  text-align: center;
  margin-bottom: var(--spacing-2xl);
}

.page-title {
  font-size: 32px;
  font-weight: 700;
  margin: 0 0 var(--spacing-sm) 0;
  color: var(--color-text-primary);
}

.page-description {
  font-size: 17px;
  color: var(--color-text-secondary);
  margin: 0;
}

.loading-card {
  padding: var(--spacing-2xl);
}

/* 统计卡片 */
.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: var(--spacing-lg);
  margin-bottom: var(--spacing-xl);
}

.stat-card {
  display: flex;
  align-items: center;
  gap: var(--spacing-lg);
  padding: var(--spacing-lg);
  transition: transform var(--transition-base);
}

.stat-card:hover {
  transform: translateY(-2px);
}

.stat-card.positive {
  background: linear-gradient(135deg, rgba(103, 194, 58, 0.1) 0%, rgba(103, 194, 58, 0.05) 100%);
  border-left: 4px solid var(--color-success);
}

.stat-card.negative {
  background: linear-gradient(135deg, rgba(245, 108, 108, 0.1) 0%, rgba(245, 108, 108, 0.05) 100%);
  border-left: 4px solid var(--color-danger);
}

.stat-icon {
  width: 64px;
  height: 64px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 12px;
  background: var(--color-bg-secondary);
  color: var(--color-primary);
}

.stat-icon.success {
  background: rgba(103, 194, 58, 0.1);
  color: var(--color-success);
}

.stat-icon.warning {
  background: rgba(230, 162, 60, 0.1);
  color: var(--color-warning);
}

.stat-icon.danger {
  background: rgba(245, 108, 108, 0.1);
  color: var(--color-danger);
}

.stat-content {
  flex: 1;
}

.stat-value {
  font-size: 28px;
  font-weight: 700;
  color: var(--color-text-primary);
  line-height: 1.2;
}

.stat-label {
  font-size: 14px;
  color: var(--color-text-secondary);
  margin-top: var(--spacing-xs);
}

/* 图表卡片 */
.chart-card,
.table-card {
  margin-bottom: var(--spacing-lg);
}

.chart-header,
.table-header {
  padding: var(--spacing-lg);
  border-bottom: 1px solid var(--color-border);
}

.chart-header h2,
.table-header h2 {
  display: flex;
  align-items: center;
  gap: var(--spacing-sm);
  margin: 0;
  font-size: 20px;
  font-weight: 600;
}

.chart-content {
  padding: var(--spacing-xl);
}

.simple-chart {
  display: flex;
  align-items: flex-end;
  justify-content: space-between;
  height: 300px;
  gap: var(--spacing-sm);
  padding-bottom: 40px;
  position: relative;
}

.chart-bar {
  flex: 1;
  min-height: 40px;
  background: linear-gradient(180deg, #667eea 0%, #764ba2 100%);
  border-radius: 4px 4px 0 0;
  position: relative;
  transition: all var(--transition-base);
  cursor: pointer;
}

.chart-bar:hover {
  transform: translateY(-4px);
  filter: brightness(1.1);
}

.bar-label {
  position: absolute;
  top: -28px;
  left: 50%;
  transform: translateX(-50%);
  font-size: 12px;
  font-weight: 600;
  color: var(--color-primary);
  white-space: nowrap;
}

.bar-date {
  position: absolute;
  bottom: -32px;
  left: 50%;
  transform: translateX(-50%) rotate(-45deg);
  font-size: 11px;
  color: var(--color-text-secondary);
  white-space: nowrap;
  transform-origin: top left;
}

.scale-value {
  font-weight: 600;
  color: var(--color-primary);
  font-size: 16px;
}

.text-success {
  color: var(--color-success);
  font-weight: 600;
}

.text-danger {
  color: var(--color-danger);
  font-weight: 600;
}

.pagination {
  display: flex;
  justify-content: center;
  padding: var(--spacing-lg) 0;
}

@media (max-width: 734px) {
  .page-title {
    font-size: 24px;
  }

  .page-description {
    font-size: 15px;
  }

  .stats-grid {
    grid-template-columns: 1fr;
  }

  .stat-value {
    font-size: 24px;
  }

  .simple-chart {
    height: 250px;
    overflow-x: auto;
  }

  .chart-bar {
    min-width: 40px;
  }

  .bar-label {
    font-size: 10px;
  }

  .bar-date {
    font-size: 9px;
  }
}
</style>
