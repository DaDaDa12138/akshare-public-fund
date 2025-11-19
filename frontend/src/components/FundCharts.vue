<template>
  <div class="fund-charts">
    <el-row :gutter="20">
      <!-- 收益率分布图 -->
      <el-col :xs="24" :sm="24" :md="12">
        <div class="chart-card card">
          <h3 class="chart-title">收益率分布</h3>
          <div ref="returnChartRef" class="chart-container"></div>
        </div>
      </el-col>

      <!-- 基金类型占比图 -->
      <el-col :xs="24" :sm="24" :md="12">
        <div class="chart-card card">
          <h3 class="chart-title">基金类型占比</h3>
          <div ref="typeChartRef" class="chart-container"></div>
        </div>
      </el-col>
    </el-row>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, watch, onUnmounted } from 'vue'
import * as echarts from 'echarts'
import type { ECharts } from 'echarts'

interface Props {
  data: any[]
}

const props = defineProps<Props>()

const returnChartRef = ref<HTMLElement>()
const typeChartRef = ref<HTMLElement>()

let returnChart: ECharts | null = null
let typeChart: ECharts | null = null

// 解析收益率字符串为数字
const parseReturn = (value: any): number | null => {
  if (value === null || value === undefined || value === '' || value === '-' || value === '---') {
    return null
  }
  try {
    return parseFloat(value)
  } catch {
    return null
  }
}

// 初始化收益率分布图
const initReturnChart = () => {
  if (!returnChartRef.value) return

  returnChart = echarts.init(returnChartRef.value)

  // 统计收益率分布
  const ranges = [
    { label: '<-10%', min: -Infinity, max: -10, count: 0 },
    { label: '-10%~0%', min: -10, max: 0, count: 0 },
    { label: '0%~10%', min: 0, max: 10, count: 0 },
    { label: '10%~20%', min: 10, max: 20, count: 0 },
    { label: '20%~30%', min: 20, max: 30, count: 0 },
    { label: '>30%', min: 30, max: Infinity, count: 0 }
  ]

  props.data.forEach(item => {
    const ret = parseReturn(item['近1年'])
    if (ret !== null) {
      for (const range of ranges) {
        if (ret > range.min && ret <= range.max) {
          range.count++
          break
        }
      }
    }
  })

  const option = {
    tooltip: {
      trigger: 'axis',
      axisPointer: {
        type: 'shadow'
      }
    },
    grid: {
      left: '3%',
      right: '4%',
      bottom: '3%',
      containLabel: true
    },
    xAxis: {
      type: 'category',
      data: ranges.map(r => r.label),
      axisLabel: {
        fontSize: 12
      }
    },
    yAxis: {
      type: 'value',
      name: '基金数量',
      axisLabel: {
        fontSize: 12
      }
    },
    series: [
      {
        name: '基金数量',
        type: 'bar',
        data: ranges.map(r => r.count),
        itemStyle: {
          color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
            { offset: 0, color: '#667eea' },
            { offset: 1, color: '#764ba2' }
          ])
        },
        label: {
          show: true,
          position: 'top',
          fontSize: 11
        }
      }
    ]
  }

  returnChart.setOption(option)
}

// 初始化基金类型占比图
const initTypeChart = () => {
  if (!typeChartRef.value) return

  typeChart = echarts.init(typeChartRef.value)

  // 统计基金类型
  const typeCount: Record<string, number> = {}

  props.data.forEach(item => {
    const type = item['基金类型'] || item['类型'] || '未知'
    typeCount[type] = (typeCount[type] || 0) + 1
  })

  const data = Object.entries(typeCount).map(([name, value]) => ({
    name,
    value
  }))

  const option = {
    tooltip: {
      trigger: 'item',
      formatter: '{a} <br/>{b}: {c} ({d}%)'
    },
    legend: {
      orient: 'vertical',
      right: '10%',
      top: 'center',
      textStyle: {
        fontSize: 12
      }
    },
    series: [
      {
        name: '基金类型',
        type: 'pie',
        radius: ['40%', '70%'],
        center: ['40%', '50%'],
        avoidLabelOverlap: false,
        itemStyle: {
          borderRadius: 10,
          borderColor: '#fff',
          borderWidth: 2
        },
        label: {
          show: false,
          position: 'center'
        },
        emphasis: {
          label: {
            show: true,
            fontSize: 20,
            fontWeight: 'bold'
          }
        },
        labelLine: {
          show: false
        },
        data: data
      }
    ],
    color: ['#667eea', '#764ba2', '#f093fb', '#4facfe', '#43e97b', '#fa709a']
  }

  typeChart.setOption(option)
}

// 更新图表
const updateCharts = () => {
  if (props.data.length === 0) return

  initReturnChart()
  initTypeChart()
}

// 监听数据变化
watch(() => props.data, () => {
  updateCharts()
}, { deep: true })

// 窗口大小改变时重新调整图表
const handleResize = () => {
  returnChart?.resize()
  typeChart?.resize()
}

onMounted(() => {
  updateCharts()
  window.addEventListener('resize', handleResize)
})

onUnmounted(() => {
  returnChart?.dispose()
  typeChart?.dispose()
  window.removeEventListener('resize', handleResize)
})
</script>

<style scoped>
.fund-charts {
  margin-bottom: var(--spacing-lg);
}

.chart-card {
  padding: var(--spacing-lg);
  min-height: 350px;
}

.chart-title {
  font-size: 17px;
  font-weight: 600;
  margin: 0 0 var(--spacing-md) 0;
  padding-bottom: var(--spacing-sm);
  border-bottom: 2px solid var(--color-border);
}

.chart-container {
  width: 100%;
  height: 280px;
}

@media (max-width: 734px) {
  .chart-card {
    margin-bottom: var(--spacing-md);
  }

  .chart-container {
    height: 250px;
  }
}
</style>
