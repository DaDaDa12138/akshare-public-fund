<template>
  <div class="fund-chart">
    <div class="container">
      <!-- 标题 -->
      <div class="chart-header">
        <h1>净值走势</h1>
        <p class="text-secondary">查看基金历史净值和收益率走势</p>
      </div>

      <!-- 基金选择和控制面板 -->
      <div class="control-panel card">
        <el-row :gutter="16">
          <el-col :xs="24" :sm="24" :md="12">
            <div class="control-item">
              <label>选择基金：</label>
              <el-select-v2
                v-model="selectedFund"
                :options="fundOptions"
                filterable
                placeholder="请输入基金代码或名称"
                size="large"
                style="width: 100%"
                @change="handleFundChange"
              />
            </div>
          </el-col>

          <el-col :xs="24" :sm="12" :md="6">
            <div class="control-item">
              <label>指标类型：</label>
              <el-select
                v-model="indicator"
                size="large"
                style="width: 100%"
                @change="loadChartData"
              >
                <el-option label="单位净值走势" value="单位净值走势" />
                <el-option label="累计净值走势" value="累计净值走势" />
                <el-option label="累计收益率走势" value="累计收益率走势" />
              </el-select>
            </div>
          </el-col>

          <el-col :xs="24" :sm="12" :md="6">
            <div class="control-item">
              <label>&nbsp;</label>
              <el-button
                type="primary"
                size="large"
                :loading="loading"
                :disabled="!selectedFund"
                @click="loadChartData"
                style="width: 100%"
              >
                查询
              </el-button>
            </div>
          </el-col>
        </el-row>
      </div>

      <!-- 图表容器 -->
      <div class="chart-container card" v-loading="loading">
        <div ref="chartRef" class="chart"></div>
        <div v-if="!selectedFund" class="empty-state">
          <p>请选择一个基金查看净值走势</p>
        </div>
      </div>

      <!-- 数据统计 -->
      <div class="stats-panel" v-if="stats">
        <el-row :gutter="16">
          <el-col :xs="12" :sm="6">
            <div class="stat-card card">
              <div class="stat-label">最新净值</div>
              <div class="stat-value">{{ stats.latest }}</div>
            </div>
          </el-col>
          <el-col :xs="12" :sm="6">
            <div class="stat-card card">
              <div class="stat-label">累计增长</div>
              <div class="stat-value" :class="stats.change >= 0 ? 'positive' : 'negative'">
                {{ stats.change >= 0 ? '+' : '' }}{{ stats.change }}%
              </div>
            </div>
          </el-col>
          <el-col :xs="12" :sm="6">
            <div class="stat-card card">
              <div class="stat-label">最高净值</div>
              <div class="stat-value">{{ stats.max }}</div>
            </div>
          </el-col>
          <el-col :xs="12" :sm="6">
            <div class="stat-card card">
              <div class="stat-label">最低净值</div>
              <div class="stat-value">{{ stats.min }}</div>
            </div>
          </el-col>
        </el-row>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onBeforeUnmount, nextTick } from 'vue'
import { useFundStore } from '@/stores/fund'
import { getFundHistData } from '@/api/fund'
import * as echarts from 'echarts'
import type { ECharts } from 'echarts'
import type { FundHistData } from '@/types/fund'

const fundStore = useFundStore()

// 状态
const selectedFund = ref(fundStore.selectedFund || '')
const indicator = ref('单位净值走势')
const loading = ref(false)
const chartRef = ref<HTMLElement>()
let chartInstance: ECharts | null = null
let resizeHandler: (() => void) | null = null

// el-select-v2 需要的数据格式
const fundOptions = computed(() =>
  fundStore.fundList.map(fund => ({
    value: fund.基金代码,
    label: `${fund.基金代码} - ${fund.基金简称}`
  }))
)

// 统计数据
const stats = ref<{
  latest: string
  change: number
  max: string
  min: string
} | null>(null)

// 加载基金列表
onMounted(async () => {
  await fundStore.loadFundList()

  // 如果有选中的基金，自动加载
  if (selectedFund.value) {
    await loadChartData()
  }
})

// 清理
onBeforeUnmount(() => {
  // 清理图表实例
  if (chartInstance) {
    chartInstance.dispose()
    chartInstance = null
  }
  // 清理 resize 事件监听器
  if (resizeHandler) {
    window.removeEventListener('resize', resizeHandler)
    resizeHandler = null
  }
})

// 基金变更
const handleFundChange = () => {
  fundStore.selectedFund = selectedFund.value
  loadChartData()
}

// 加载图表数据
const loadChartData = async () => {
  if (!selectedFund.value) return

  loading.value = true
  try {
    const data = await getFundHistData(selectedFund.value, indicator.value)

    if (data && data.length > 0) {
      renderChart(data)
      calculateStats(data)
    }
  } catch (error) {
    console.error('Failed to load chart data:', error)
  } finally {
    loading.value = false
  }
}

// 计算统计数据
const calculateStats = (data: FundHistData[]) => {
  if (!data || data.length === 0) {
    stats.value = null
    return
  }

  const values = data.map(item => parseFloat(item.单位净值 || item.累计净值 || '0'))
  const latest = values[values.length - 1]
  const first = values[0]
  const max = Math.max(...values)
  const min = Math.min(...values)
  const change = ((latest - first) / first * 100).toFixed(2)

  stats.value = {
    latest: latest.toFixed(4),
    change: parseFloat(change),
    max: max.toFixed(4),
    min: min.toFixed(4)
  }
}

// 渲染图表
const renderChart = async (data: FundHistData[]) => {
  await nextTick()

  if (!chartRef.value) return

  // 初始化或获取图表实例
  if (!chartInstance) {
    chartInstance = echarts.init(chartRef.value)
  }

  // 准备数据
  const dates = data.map(item => item.净值日期)
  const values = data.map(item => {
    const value = item.单位净值 || item.累计净值 || item.累计收益率
    return parseFloat(value || '0')
  })

  // 配置选项
  const option = {
    title: {
      text: `${selectedFund.value} ${indicator.value}`,
      left: 'center',
      textStyle: {
        color: '#1d1d1f',
        fontSize: 18,
        fontWeight: 600
      }
    },
    tooltip: {
      trigger: 'axis',
      backgroundColor: 'rgba(255, 255, 255, 0.9)',
      borderColor: '#d2d2d7',
      borderWidth: 1,
      textStyle: {
        color: '#1d1d1f'
      },
      formatter: (params: any) => {
        const param = params[0]
        return `
          <div style="padding: 4px;">
            <div>${param.name}</div>
            <div style="margin-top: 4px;">
              <strong style="color: #0071e3;">${param.value.toFixed(4)}</strong>
            </div>
          </div>
        `
      }
    },
    grid: {
      left: '3%',
      right: '4%',
      bottom: '3%',
      top: '15%',
      containLabel: true
    },
    xAxis: {
      type: 'category',
      data: dates,
      boundaryGap: false,
      axisLine: {
        lineStyle: {
          color: '#d2d2d7'
        }
      },
      axisLabel: {
        color: '#86868b'
      }
    },
    yAxis: {
      type: 'value',
      scale: true,
      axisLine: {
        lineStyle: {
          color: '#d2d2d7'
        }
      },
      axisLabel: {
        color: '#86868b',
        formatter: (value: number) => value.toFixed(4)
      },
      splitLine: {
        lineStyle: {
          color: '#f5f5f7'
        }
      }
    },
    series: [
      {
        name: indicator.value,
        type: 'line',
        data: values,
        smooth: true,
        symbol: 'none',
        lineStyle: {
          color: '#0071e3',
          width: 2
        },
        areaStyle: {
          color: {
            type: 'linear',
            x: 0,
            y: 0,
            x2: 0,
            y2: 1,
            colorStops: [
              { offset: 0, color: 'rgba(0, 113, 227, 0.3)' },
              { offset: 1, color: 'rgba(0, 113, 227, 0.05)' }
            ]
          }
        }
      }
    ]
  }

  chartInstance.setOption(option)

  // 清理旧的 resize 监听器
  if (resizeHandler) {
    window.removeEventListener('resize', resizeHandler)
  }

  // 添加新的 resize 监听器
  resizeHandler = () => {
    chartInstance?.resize()
  }
  window.addEventListener('resize', resizeHandler)
}

// 防抖函数
const debounce = <T extends (...args: any[]) => any>(fn: T, delay: number) => {
  let timeoutId: number | null = null
  return (...args: Parameters<T>) => {
    if (timeoutId) {
      clearTimeout(timeoutId)
    }
    timeoutId = window.setTimeout(() => {
      fn(...args)
    }, delay)
  }
}

// 添加防抖的加载函数（300ms延迟）
const debouncedLoadChartData = debounce(loadChartData, 300)
</script>

<style scoped>
.fund-chart {
  min-height: 100vh;
}

.chart-header {
  text-align: center;
  margin-bottom: var(--spacing-xl);
}

.chart-header h1 {
  margin-bottom: var(--spacing-sm);
}

.control-panel {
  margin-bottom: var(--spacing-lg);
}

.control-item {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-sm);
}

.control-item label {
  font-size: 14px;
  font-weight: 500;
  color: var(--color-text-primary);
}

.chart-container {
  margin-bottom: var(--spacing-lg);
  min-height: 500px;
  position: relative;
}

.chart {
  width: 100%;
  height: 500px;
}

.empty-state {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  text-align: center;
  color: var(--color-text-secondary);
}

.stats-panel {
  margin-top: var(--spacing-lg);
}

.stat-card {
  text-align: center;
  padding: var(--spacing-lg);
  transition: all var(--transition-base);
}

.stat-card:hover {
  transform: translateY(-4px);
  box-shadow: var(--shadow-lg);
}

.stat-label {
  font-size: 14px;
  color: var(--color-text-secondary);
  margin-bottom: var(--spacing-sm);
}

.stat-value {
  font-size: 24px;
  font-weight: 600;
  color: var(--color-text-primary);
}

.stat-value.positive {
  color: var(--color-success);
}

.stat-value.negative {
  color: var(--color-danger);
}

@media (max-width: 734px) {
  .chart {
    height: 350px;
  }

  .stat-value {
    font-size: 20px;
  }
}
</style>
