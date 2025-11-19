<template>
  <div class="movie-boxoffice-panel">
    <!-- 实时票房卡片 -->
    <div class="card">
      <div class="card-header">
        <h3>🎬 实时票房 TOP10</h3>
        <div class="card-actions">
          <el-tag type="info" effect="plain">
            <el-icon><Clock /></el-icon>
            5分钟更新
          </el-tag>
          <el-button size="small" @click="loadRealtimeData">刷新</el-button>
        </div>
      </div>
      <div v-loading="realtime.loading" class="table-container">
        <el-table :data="realtime.data.slice(0, 10)" stripe style="width: 100%">
          <el-table-column prop="排名" label="排名" width="80" align="center">
            <template #default="{ row }">
              <div class="rank-badge" :class="`rank-${row.排名}`">
                {{ row.排名 }}
              </div>
            </template>
          </el-table-column>
          <el-table-column prop="影片名" label="影片名" min-width="150" show-overflow-tooltip />
          <el-table-column label="实时票房" width="120" align="right">
            <template #default="{ row }">
              <span class="text-accent">{{ formatBoxOffice(row.实时票房) }}</span>
            </template>
          </el-table-column>
          <el-table-column prop="实时占比" label="占比" width="100" align="center">
            <template #default="{ row }">
              <el-progress
                :percentage="parseFloat(row.实时占比)"
                :stroke-width="16"
                :show-text="true"
                :format="() => `${row.实时占比}%`"
              />
            </template>
          </el-table-column>
          <el-table-column label="累计票房" width="120" align="right">
            <template #default="{ row }">
              {{ formatBoxOffice(row.累计票房) }}
            </template>
          </el-table-column>
          <el-table-column prop="上映天数" label="上映天数" width="100" align="center">
            <template #default="{ row }">
              <el-tag size="small">{{ row.上映天数 }}天</el-tag>
            </template>
          </el-table-column>
        </el-table>
      </div>
    </div>

    <!-- 票房排行和年度趋势 -->
    <el-row :gutter="16">
      <!-- 票房排行卡片 -->
      <el-col :xs="24" :sm="24" :md="12">
        <div class="card">
          <div class="card-header">
            <h3>📊 票房排行</h3>
            <div class="card-actions">
              <el-select v-model="ranking.period" size="small" style="width: 100px">
                <el-option label="单日" value="daily" />
                <el-option label="周榜" value="weekly" />
                <el-option label="月榜" value="monthly" />
                <el-option label="年榜" value="yearly" />
              </el-select>
              <el-date-picker
                v-if="ranking.period === 'daily' || ranking.period === 'monthly'"
                v-model="ranking.date"
                type="date"
                placeholder="选择日期"
                size="small"
                :disabled-date="disabledDate"
                value-format="YYYYMMDD"
                style="width: 150px"
              />
              <el-tag v-else-if="ranking.period === 'weekly'" type="info" size="small">最近一周</el-tag>
              <el-select
                v-else-if="ranking.period === 'yearly'"
                v-model="ranking.year"
                size="small"
                style="width: 100px"
              >
                <el-option
                  v-for="year in availableYears"
                  :key="year"
                  :label="`${year}年`"
                  :value="year"
                />
              </el-select>
            </div>
          </div>
          <div v-loading="ranking.loading" class="chart-container">
            <div ref="rankingChartRef" class="chart" style="height: 450px"></div>
          </div>
        </div>
      </el-col>

      <!-- 年度趋势卡片 -->
      <el-col :xs="24" :sm="24" :md="12">
        <div class="card">
          <div class="card-header">
            <h3>📈 年度票房趋势</h3>
            <div class="card-actions">
              <el-select v-model="yearlyCompare.years" multiple size="small" style="width: 200px">
                <el-option
                  v-for="year in availableYears"
                  :key="year"
                  :label="`${year}年`"
                  :value="year"
                />
              </el-select>
            </div>
          </div>
          <div v-loading="yearlyCompare.loading" class="chart-container">
            <div ref="yearlyChartRef" class="chart" style="height: 450px"></div>
          </div>
        </div>
      </el-col>
    </el-row>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, watch, nextTick } from 'vue'
import { ElMessage } from 'element-plus'
import { Clock } from '@element-plus/icons-vue'
import * as echarts from 'echarts'
import type { ECharts } from 'echarts'
import {
  getMovieBoxOfficeRealtime,
  getMovieBoxOfficeDaily,
  getMovieBoxOfficeWeekly,
  getMovieBoxOfficeMonthly,
  getMovieBoxOfficeYearly,
  getYesterday,
  getLastYear,
  formatBoxOffice
} from '@/api/alternative'
import type {
  MovieBoxOfficeRealtime,
  MovieBoxOfficeDaily,
  MovieBoxOfficeYearly
} from '@/types/alternative'

// 图表引用
const rankingChartRef = ref<HTMLDivElement>()
const yearlyChartRef = ref<HTMLDivElement>()

// ECharts 实例
let rankingChart: ECharts | null = null
let yearlyChart: ECharts | null = null

// ========== 实时票房 ==========
const realtime = ref({
  loading: false,
  data: [] as MovieBoxOfficeRealtime[]
})

const loadRealtimeData = async () => {
  realtime.value.loading = true
  try {
    const data = await getMovieBoxOfficeRealtime()
    realtime.value.data = data
  } catch (error: any) {
    ElMessage.error('加载实时票房数据失败')
    console.error(error)
  } finally {
    realtime.value.loading = false
  }
}

// ========== 票房排行 ==========
const ranking = ref({
  period: 'daily' as 'daily' | 'weekly' | 'monthly' | 'yearly',
  date: getYesterday(),
  year: getLastYear(),
  loading: false,
  data: [] as any[]
})

const availableYears = computed(() => {
  const currentYear = new Date().getFullYear()
  return Array.from({ length: 10 }, (_, i) => currentYear - i)
})

const disabledDate = (time: Date) => {
  return time.getTime() > Date.now()
}

const loadRankingData = async () => {
  ranking.value.loading = true
  try {
    let data: any[] = []

    switch (ranking.value.period) {
      case 'daily':
        data = await getMovieBoxOfficeDaily(ranking.value.date)
        break
      case 'weekly':
        data = await getMovieBoxOfficeWeekly()
        break
      case 'monthly':
        data = await getMovieBoxOfficeMonthly(ranking.value.date.slice(0, 6))
        break
      case 'yearly':
        data = await getMovieBoxOfficeYearly(ranking.value.year)
        break
    }

    ranking.value.data = data.slice(0, 10)  // TOP10
    renderRankingChart()
  } catch (error: any) {
    ElMessage.error('加载票房排行数据失败')
    console.error(error)
  } finally {
    ranking.value.loading = false
  }
}

const renderRankingChart = () => {
  if (!rankingChartRef.value || ranking.value.data.length === 0) return

  if (!rankingChart) {
    rankingChart = echarts.init(rankingChartRef.value)
  }

  const movies = ranking.value.data.map(item => item.影片名)
  const boxOffice = ranking.value.data.map((item: any) => {
    return item.单日票房 || item.周票房 || item.月票房 || item.年度票房 || 0
  })

  const periodName = {
    daily: '单日票房',
    weekly: '周票房',
    monthly: '月票房',
    yearly: '年度票房'
  }[ranking.value.period]

  const option = {
    title: {
      text: `${periodName} TOP10`,
      left: 'center',
      textStyle: {
        fontSize: 16,
        fontWeight: 'bold'
      }
    },
    tooltip: {
      trigger: 'axis',
      axisPointer: {
        type: 'shadow'
      },
      formatter: (params: any) => {
        const item = params[0]
        return `<strong>${item.name}</strong><br/>${periodName}: <strong>${formatBoxOffice(item.value)}</strong>`
      }
    },
    grid: {
      left: '3%',
      right: '4%',
      bottom: '3%',
      containLabel: true
    },
    xAxis: {
      type: 'value',
      name: '票房（万元）',
      axisLabel: {
        formatter: (value: number) => {
          if (value >= 10000) return `${(value / 10000).toFixed(0)}亿`
          return value
        }
      }
    },
    yAxis: {
      type: 'category',
      data: movies,
      inverse: true,
      axisLabel: {
        fontSize: 12,
        formatter: (value: string) => {
          return value.length > 10 ? value.slice(0, 10) + '...' : value
        }
      }
    },
    series: [
      {
        name: periodName,
        type: 'bar',
        data: boxOffice,
        itemStyle: {
          color: new echarts.graphic.LinearGradient(0, 0, 1, 0, [
            { offset: 0, color: '#fa709a' },
            { offset: 1, color: '#fee140' }
          ]),
          borderRadius: [0, 4, 4, 0]
        },
        label: {
          show: true,
          position: 'right',
          formatter: (params: any) => formatBoxOffice(params.value),
          fontSize: 11
        }
      }
    ]
  }

  rankingChart.setOption(option)
}

// ========== 年度趋势对比 ==========
const yearlyCompare = ref({
  years: [String(new Date().getFullYear() - 1)],
  loading: false,
  data: {} as Record<string, MovieBoxOfficeYearly[]>
})

const loadYearlyCompare = async () => {
  if (yearlyCompare.value.years.length === 0) {
    ElMessage.warning('请至少选择一个年份')
    return
  }

  yearlyCompare.value.loading = true
  try {
    const dataPromises = yearlyCompare.value.years.map(year =>
      getMovieBoxOfficeYearly(year).then(data => ({ year, data: data.slice(0, 10) }))
    )

    const results = await Promise.all(dataPromises)
    yearlyCompare.value.data = {}
    results.forEach(({ year, data }) => {
      yearlyCompare.value.data[year] = data
    })

    renderYearlyChart()
  } catch (error: any) {
    ElMessage.error('加载年度趋势数据失败')
    console.error(error)
  } finally {
    yearlyCompare.value.loading = false
  }
}

const renderYearlyChart = () => {
  if (!yearlyChartRef.value || Object.keys(yearlyCompare.value.data).length === 0) return

  if (!yearlyChart) {
    yearlyChart = echarts.init(yearlyChartRef.value)
  }

  // 获取所有年份的TOP10影片排名
  const allMovies = new Set<string>()
  Object.values(yearlyCompare.value.data).forEach(yearData => {
    yearData.forEach(item => allMovies.add(item.影片名))
  })

  const movieArray = Array.from(allMovies).slice(0, 10)

  const series = yearlyCompare.value.years.map(year => ({
    name: `${year}年`,
    type: 'bar',
    data: movieArray.map(movie => {
      const item = yearlyCompare.value.data[year]?.find(d => d.影片名 === movie)
      return item ? item.年度票房 : 0
    })
  }))

  const option = {
    title: {
      text: '年度票房对比',
      left: 'center',
      textStyle: {
        fontSize: 16,
        fontWeight: 'bold'
      }
    },
    tooltip: {
      trigger: 'axis',
      axisPointer: {
        type: 'shadow'
      },
      formatter: (params: any) => {
        let html = `<strong>${params[0].axisValue}</strong><br/>`
        params.forEach((item: any) => {
          if (item.value > 0) {
            html += `${item.marker} ${item.seriesName}: <strong>${formatBoxOffice(item.value)}</strong><br/>`
          }
        })
        return html
      }
    },
    legend: {
      data: yearlyCompare.value.years.map(y => `${y}年`),
      top: 30
    },
    grid: {
      left: '3%',
      right: '4%',
      bottom: '3%',
      containLabel: true
    },
    xAxis: {
      type: 'category',
      data: movieArray,
      axisLabel: {
        rotate: 45,
        formatter: (value: string) => {
          return value.length > 6 ? value.slice(0, 6) + '...' : value
        }
      }
    },
    yAxis: {
      type: 'value',
      name: '票房（万元）',
      axisLabel: {
        formatter: (value: number) => {
          if (value >= 10000) return `${(value / 10000).toFixed(0)}亿`
          return value
        }
      }
    },
    series: series
  }

  yearlyChart.setOption(option)
}

// ========== 响应式处理 ==========
const handleResize = () => {
  rankingChart?.resize()
  yearlyChart?.resize()
}

// ========== 监听变化 ==========
watch(() => ranking.value.period, loadRankingData)
watch(() => ranking.value.date, loadRankingData)
watch(() => ranking.value.year, loadRankingData)
watch(() => yearlyCompare.value.years, loadYearlyCompare, { deep: true })

// ========== 生命周期 ==========
onMounted(async () => {
  await nextTick()

  // 加载初始数据
  await Promise.all([
    loadRealtimeData(),
    loadRankingData(),
    loadYearlyCompare()
  ])

  // 自动刷新实时票房（5分钟）
  setInterval(() => {
    loadRealtimeData()
  }, 5 * 60 * 1000)

  // 监听窗口大小变化
  window.addEventListener('resize', handleResize)
})

// 组件卸载时清理
import { onBeforeUnmount } from 'vue'
onBeforeUnmount(() => {
  window.removeEventListener('resize', handleResize)
  rankingChart?.dispose()
  yearlyChart?.dispose()
})
</script>

<style scoped>
.movie-boxoffice-panel {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-lg);
}

.card {
  background: var(--color-bg-secondary);
  border-radius: var(--radius-lg);
  padding: var(--spacing-lg);
  box-shadow: var(--shadow-sm);
  transition: all 250ms ease;
}

.card:hover {
  box-shadow: var(--shadow-md);
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: var(--spacing-md);
  flex-wrap: wrap;
  gap: var(--spacing-sm);
}

.card-header h3 {
  margin: 0;
  font-size: 18px;
  font-weight: 600;
}

.card-actions {
  display: flex;
  gap: var(--spacing-sm);
  flex-wrap: wrap;
  align-items: center;
}

.table-container {
  overflow-x: auto;
}

.chart-container {
  min-height: 300px;
}

.chart {
  width: 100%;
}

/* 排名徽章 */
.rank-badge {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 32px;
  height: 32px;
  border-radius: 50%;
  font-weight: bold;
  font-size: 14px;
  color: #fff;
}

.rank-badge.rank-1 {
  background: linear-gradient(135deg, #FFD700, #FFA500);
  box-shadow: 0 2px 8px rgba(255, 215, 0, 0.3);
}

.rank-badge.rank-2 {
  background: linear-gradient(135deg, #C0C0C0, #A9A9A9);
  box-shadow: 0 2px 8px rgba(192, 192, 192, 0.3);
}

.rank-badge.rank-3 {
  background: linear-gradient(135deg, #CD7F32, #B87333);
  box-shadow: 0 2px 8px rgba(205, 127, 50, 0.3);
}

.rank-badge:not(.rank-1):not(.rank-2):not(.rank-3) {
  background: var(--color-bg-tertiary);
  color: var(--color-text-primary);
  border: 1px solid var(--color-border-light);
}

.text-accent {
  color: var(--color-accent);
  font-weight: 600;
}

/* 响应式设计 */
@media (max-width: 734px) {
  .card {
    padding: var(--spacing-md);
  }

  .card-header {
    flex-direction: column;
    align-items: flex-start;
  }

  .card-header h3 {
    font-size: 16px;
  }

  .card-actions {
    width: 100%;
  }

  .card-actions .el-select,
  .card-actions .el-date-picker {
    width: 100% !important;
  }

  .chart {
    height: 350px !important;
  }
}
</style>
