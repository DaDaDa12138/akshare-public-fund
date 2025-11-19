<template>
  <div class="etf-kline-chart">
    <div class="chart-controls">
      <div class="control-group">
        <label>周期:</label>
        <select v-model="period" @change="loadChartData" class="select-input">
          <option value="daily">日K</option>
          <option value="weekly">周K</option>
          <option value="monthly">月K</option>
        </select>
      </div>
      <div class="control-group">
        <label>复权:</label>
        <select v-model="adjust" @change="loadChartData" class="select-input">
          <option value="qfq">前复权</option>
          <option value="hfq">后复权</option>
          <option value="">不复权</option>
        </select>
      </div>
    </div>

    <div v-if="loading" class="chart-loading">
      <p>加载中...</p>
    </div>

    <div v-else-if="error" class="chart-error">
      <p>{{ error }}</p>
    </div>

    <div v-else ref="chartContainer" class="chart-container"></div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, watch, onBeforeUnmount } from 'vue'
import * as echarts from 'echarts'
import { getFundETFHist, type ETFHistData } from '@/api/fund'

const props = defineProps<{
  symbol: string
  title?: string
}>()

const chartContainer = ref<HTMLElement>()
const chartInstance = ref<echarts.ECharts>()
const loading = ref(true)
const error = ref('')
const chartData = ref<ETFHistData[]>([])

// 控制参数
const period = ref('daily')
const adjust = ref('qfq')

// 加载图表数据
const loadChartData = async () => {
  try {
    loading.value = true
    error.value = ''

    const response = await getFundETFHist(props.symbol, period.value, adjust.value)

    if (!response.success) {
      error.value = response.error || '加载失败'
      return
    }

    chartData.value = response.data
    renderChart()
  } catch (err: any) {
    error.value = err.message || '加载失败'
  } finally {
    loading.value = false
  }
}

// 渲染图表
const renderChart = () => {
  if (!chartContainer.value || chartData.value.length === 0) return

  // 初始化图表实例
  if (!chartInstance.value) {
    chartInstance.value = echarts.init(chartContainer.value)
  }

  // 准备K线数据
  const dates = chartData.value.map(item => item.日期)
  const klineData = chartData.value.map(item => [
    item.开盘,
    item.收盘,
    item.最低,
    item.最高
  ])
  const volumes = chartData.value.map(item => item.成交量)

  // 配置图表
  const option: echarts.EChartsOption = {
    title: {
      text: props.title || `${props.symbol} K线图`,
      left: 'center',
      textStyle: {
        color: 'var(--color-text-primary)',
        fontSize: 18,
        fontWeight: 600
      }
    },
    tooltip: {
      trigger: 'axis',
      axisPointer: {
        type: 'cross'
      },
      backgroundColor: 'rgba(255, 255, 255, 0.95)',
      borderColor: 'var(--color-border)',
      textStyle: {
        color: 'var(--color-text-primary)'
      }
    },
    legend: {
      data: ['K线', '成交量'],
      top: 30,
      textStyle: {
        color: 'var(--color-text-secondary)'
      }
    },
    grid: [
      {
        left: '8%',
        right: '8%',
        top: '15%',
        height: '50%'
      },
      {
        left: '8%',
        right: '8%',
        top: '70%',
        height: '15%'
      }
    ],
    xAxis: [
      {
        type: 'category',
        data: dates,
        boundaryGap: true,
        axisLine: { onZero: false },
        splitLine: { show: false },
        min: 'dataMin',
        max: 'dataMax',
        axisLabel: {
          color: 'var(--color-text-secondary)'
        }
      },
      {
        type: 'category',
        gridIndex: 1,
        data: dates,
        boundaryGap: true,
        axisLine: { onZero: false },
        axisTick: { show: false },
        splitLine: { show: false },
        axisLabel: { show: false },
        min: 'dataMin',
        max: 'dataMax'
      }
    ],
    yAxis: [
      {
        scale: true,
        splitArea: {
          show: true
        },
        axisLabel: {
          color: 'var(--color-text-secondary)'
        }
      },
      {
        scale: true,
        gridIndex: 1,
        splitNumber: 2,
        axisLabel: { show: false },
        axisLine: { show: false },
        axisTick: { show: false },
        splitLine: { show: false }
      }
    ],
    dataZoom: [
      {
        type: 'inside',
        xAxisIndex: [0, 1],
        start: 80,
        end: 100
      },
      {
        show: true,
        xAxisIndex: [0, 1],
        type: 'slider',
        bottom: '5%',
        start: 80,
        end: 100
      }
    ],
    series: [
      {
        name: 'K线',
        type: 'candlestick',
        data: klineData,
        itemStyle: {
          color: '#ef5350',  // 阳线颜色(涨)
          color0: '#26a69a', // 阴线颜色(跌)
          borderColor: '#ef5350',
          borderColor0: '#26a69a'
        }
      },
      {
        name: '成交量',
        type: 'bar',
        xAxisIndex: 1,
        yAxisIndex: 1,
        data: volumes,
        itemStyle: {
          color: function(params) {
            const dataIndex = params.dataIndex
            if (dataIndex === 0) return '#ef5350'
            const current = chartData.value[dataIndex]
            const prev = chartData.value[dataIndex - 1]
            return current.收盘 >= prev.收盘 ? '#ef5350' : '#26a69a'
          }
        }
      }
    ]
  }

  chartInstance.value.setOption(option)
}

// 监听symbol变化
watch(() => props.symbol, () => {
  loadChartData()
})

// 窗口大小变化时重新调整图表
const handleResize = () => {
  chartInstance.value?.resize()
}

onMounted(() => {
  loadChartData()
  window.addEventListener('resize', handleResize)
})

onBeforeUnmount(() => {
  window.removeEventListener('resize', handleResize)
  chartInstance.value?.dispose()
})
</script>

<style scoped>
.etf-kline-chart {
  width: 100%;
}

.chart-controls {
  display: flex;
  gap: var(--spacing-lg);
  margin-bottom: var(--spacing-lg);
  padding: var(--spacing-md);
  background: var(--color-bg-secondary);
  border-radius: 8px;
}

.control-group {
  display: flex;
  align-items: center;
  gap: var(--spacing-sm);
}

.control-group label {
  font-size: 15px;
  color: var(--color-text-secondary);
  font-weight: 500;
}

.select-input {
  padding: var(--spacing-sm) var(--spacing-md);
  font-size: 15px;
  border: 1px solid var(--color-border);
  border-radius: 6px;
  background: var(--color-bg-primary);
  color: var(--color-text-primary);
  cursor: pointer;
  transition: all var(--transition-base);
}

.select-input:hover {
  border-color: var(--color-accent);
}

.select-input:focus {
  outline: none;
  border-color: var(--color-accent);
  box-shadow: 0 0 0 3px rgba(0, 113, 227, 0.1);
}

.chart-container {
  width: 100%;
  height: 500px;
}

.chart-loading,
.chart-error {
  height: 500px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--color-bg-secondary);
  border-radius: 12px;
}

.chart-loading p,
.chart-error p {
  font-size: 17px;
  color: var(--color-text-secondary);
}

.chart-error p {
  color: var(--color-danger);
}

@media (max-width: 734px) {
  .chart-controls {
    flex-direction: column;
    gap: var(--spacing-md);
  }

  .chart-container {
    height: 400px;
  }
}
</style>
