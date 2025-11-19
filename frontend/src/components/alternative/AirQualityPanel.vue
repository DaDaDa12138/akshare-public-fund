<template>
  <div class="air-quality-panel">
    <!-- 城市排名卡片 -->
    <div class="card">
      <div class="card-header">
        <h3>🏆 城市空气质量排名</h3>
        <div class="card-actions">
          <el-button-group>
            <el-button
              :type="rankType === 'best' ? 'primary' : ''"
              size="small"
              @click="rankType = 'best'"
            >
              最佳 TOP10
            </el-button>
            <el-button
              :type="rankType === 'worst' ? 'primary' : ''"
              size="small"
              @click="rankType = 'worst'"
            >
              最差 TOP10
            </el-button>
          </el-button-group>
          <el-button size="small" @click="loadCityTable">刷新</el-button>
        </div>
      </div>
      <div v-loading="cityTable.loading" class="table-container">
        <el-table :data="displayedRankData" stripe style="width: 100%">
          <el-table-column prop="排名" label="排名" width="80" align="center">
            <template #default="{ row }">
              <el-tag
                v-if="row.排名 <= 3"
                :type="getRankTagType(row.排名)"
                effect="dark"
                round
              >
                {{ row.排名 }}
              </el-tag>
              <span v-else>{{ row.排名 }}</span>
            </template>
          </el-table-column>
          <el-table-column prop="城市" label="城市" min-width="120" />
          <el-table-column prop="AQI" label="AQI" width="100" align="center">
            <template #default="{ row }">
              <el-tag :color="getAQILevel(row.AQI).color" style="color: #fff; border: none">
                {{ row.AQI }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column label="PM2.5" width="100" align="center">
            <template #default="{ row }">
              {{ row.PM2_5浓度 || row.PM2_5 || '-' }}
            </template>
          </el-table-column>
          <el-table-column prop="首要污染物" label="首要污染物" width="120" align="center" />
          <el-table-column prop="质量等级" label="质量等级" width="120" align="center">
            <template #default="{ row }">
              <el-tag :color="getAQILevel(row.AQI).color" style="color: #fff; border: none">
                {{ row.质量等级 }}
              </el-tag>
            </template>
          </el-table-column>
        </el-table>
      </div>
    </div>

    <!-- 历史趋势和城市选择器 -->
    <div class="card">
      <div class="card-header">
        <h3>📈 历史空气质量趋势</h3>
        <div class="card-actions">
          <el-select v-model="historyCity" size="small" style="width: 120px" placeholder="选择城市">
            <el-option
              v-for="city in popularCities"
              :key="city"
              :label="city"
              :value="city"
            />
          </el-select>
          <el-select v-model="historyPeriod" size="small" style="width: 100px">
            <el-option label="按天" value="天" />
            <el-option label="按小时" value="小时" />
          </el-select>
          <el-date-picker
            v-model="historyDateRange"
            type="daterange"
            range-separator="至"
            start-placeholder="开始日期"
            end-placeholder="结束日期"
            size="small"
            :disabled-date="disabledDate"
            :shortcuts="dateShortcuts"
            style="width: 240px"
          />
          <el-button size="small" type="primary" @click="loadHistoryData">查询</el-button>
        </div>
      </div>
      <div v-loading="history.loading" class="chart-container">
        <div ref="historyChartRef" class="chart" style="height: 400px"></div>
      </div>
    </div>

    <!-- AQI分布热力图 -->
    <div class="card">
      <div class="card-header">
        <h3>🗺️ AQI等级分布</h3>
      </div>
      <div v-loading="cityTable.loading" class="chart-container">
        <div ref="aqiDistChartRef" class="chart" style="height: 350px"></div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, watch, nextTick } from 'vue'
import { ElMessage } from 'element-plus'
import * as echarts from 'echarts'
import type { ECharts } from 'echarts'
import {
  getAirCityTable,
  getAirQualityHistory,
  getAQILevel
} from '@/api/alternative'
import type { AirQualityCity, AirQualityHistory } from '@/types/alternative'

// 图表引用
const historyChartRef = ref<HTMLDivElement>()
const aqiDistChartRef = ref<HTMLDivElement>()

// ECharts 实例
let historyChart: ECharts | null = null
let aqiDistChart: ECharts | null = null

// ========== 城市空气质量表 ==========
const cityTable = ref({
  loading: false,
  data: [] as AirQualityCity[]
})

const rankType = ref<'best' | 'worst'>('best')

const displayedRankData = computed(() => {
  const sorted = [...cityTable.value.data].sort((a, b) => {
    return rankType.value === 'best' ? a.AQI - b.AQI : b.AQI - a.AQI
  })
  return sorted.slice(0, 10).map((item, index) => ({
    ...item,
    排名: index + 1
  }))
})

const loadCityTable = async () => {
  cityTable.value.loading = true
  try {
    const data = await getAirCityTable()
    cityTable.value.data = data
    renderAQIDistChart()
  } catch (error: any) {
    ElMessage.error('加载城市空气质量数据失败')
    console.error(error)
  } finally {
    cityTable.value.loading = false
  }
}

const getRankTagType = (rank: number): 'success' | 'warning' | 'danger' => {
  if (rank === 1) return 'success'
  if (rank === 2) return 'warning'
  return 'danger'
}

// ========== 历史趋势 ==========
const history = ref({
  loading: false,
  data: [] as AirQualityHistory[]
})

const historyCity = ref('北京')
const historyPeriod = ref('天')
const historyDateRange = ref<[Date, Date]>([
  new Date(Date.now() - 7 * 24 * 60 * 60 * 1000),  // 7天前
  new Date()
])

const popularCities = [
  '北京', '上海', '广州', '深圳', '成都',
  '杭州', '武汉', '西安', '南京', '天津',
  '重庆', '苏州', '长沙', '郑州', '沈阳'
]

const disabledDate = (time: Date) => {
  // 禁止选择未来日期
  return time.getTime() > Date.now()
}

const dateShortcuts = [
  {
    text: '最近1周',
    value: () => {
      const end = new Date()
      const start = new Date()
      start.setTime(start.getTime() - 7 * 24 * 3600 * 1000)
      return [start, end]
    }
  },
  {
    text: '最近1个月',
    value: () => {
      const end = new Date()
      const start = new Date()
      start.setTime(start.getTime() - 30 * 24 * 3600 * 1000)
      return [start, end]
    }
  },
  {
    text: '最近3个月',
    value: () => {
      const end = new Date()
      const start = new Date()
      start.setTime(start.getTime() - 90 * 24 * 3600 * 1000)
      return [start, end]
    }
  }
]

const loadHistoryData = async () => {
  if (!historyDateRange.value || historyDateRange.value.length !== 2) {
    ElMessage.warning('请选择日期范围')
    return
  }

  history.value.loading = true
  try {
    const [start, end] = historyDateRange.value
    const startDate = start.toISOString().split('T')[0]
    const endDate = end.toISOString().split('T')[0]

    const data = await getAirQualityHistory(
      historyCity.value,
      historyPeriod.value,
      startDate,
      endDate
    )
    history.value.data = data
    renderHistoryChart()
  } catch (error: any) {
    ElMessage.error(`加载${historyCity.value}历史数据失败`)
    console.error(error)
  } finally {
    history.value.loading = false
  }
}

const renderHistoryChart = () => {
  if (!historyChartRef.value || history.value.data.length === 0) return

  if (!historyChart) {
    historyChart = echarts.init(historyChartRef.value)
  }

  const times = history.value.data.map(item => item.时间 || item.日期)
  const aqiData = history.value.data.map(item => item.AQI)
  const pm25Data = history.value.data.map(item => item.PM2_5)
  const pm10Data = history.value.data.map(item => item.PM10 || null)

  const option = {
    title: {
      text: `${historyCity.value} - 空气质量历史趋势`,
      left: 'center',
      textStyle: {
        fontSize: 16,
        fontWeight: 'bold'
      }
    },
    tooltip: {
      trigger: 'axis',
      axisPointer: {
        type: 'cross'
      },
      formatter: (params: any) => {
        let html = `<strong>${params[0].axisValue}</strong><br/>`
        params.forEach((item: any) => {
          if (item.value !== null && item.value !== undefined) {
            html += `${item.marker} ${item.seriesName}: <strong>${item.value}</strong><br/>`
          }
        })
        return html
      }
    },
    legend: {
      data: ['AQI', 'PM2.5', 'PM10'],
      top: 30
    },
    grid: {
      left: '3%',
      right: '4%',
      bottom: '10%',
      containLabel: true
    },
    xAxis: {
      type: 'category',
      data: times,
      boundaryGap: false,
      axisLabel: {
        rotate: 45,
        formatter: (value: string) => {
          // 简化日期显示
          return value.split(' ')[0].slice(5)  // MM-DD
        }
      }
    },
    yAxis: {
      type: 'value',
      name: '浓度'
    },
    series: [
      {
        name: 'AQI',
        type: 'line',
        smooth: true,
        data: aqiData,
        itemStyle: {
          color: '#ff3b30'
        },
        areaStyle: {
          color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
            { offset: 0, color: 'rgba(255, 59, 48, 0.3)' },
            { offset: 1, color: 'rgba(255, 59, 48, 0.05)' }
          ])
        }
      },
      {
        name: 'PM2.5',
        type: 'line',
        smooth: true,
        data: pm25Data,
        itemStyle: {
          color: '#ff9500'
        }
      },
      {
        name: 'PM10',
        type: 'line',
        smooth: true,
        data: pm10Data,
        itemStyle: {
          color: '#ffd60a'
        }
      }
    ],
    dataZoom: [
      {
        type: 'inside',
        start: 0,
        end: 100
      },
      {
        type: 'slider',
        start: 0,
        end: 100
      }
    ],
    visualMap: {
      show: false,
      pieces: [
        { lte: 50, color: '#30d158' },
        { gt: 50, lte: 100, color: '#ffd60a' },
        { gt: 100, lte: 150, color: '#ff9500' },
        { gt: 150, lte: 200, color: '#ff3b30' },
        { gt: 200, color: '#bf5af2' }
      ],
      seriesIndex: 0  // 只应用到AQI系列
    }
  }

  historyChart.setOption(option)
}

// ========== AQI等级分布 ==========
const renderAQIDistChart = () => {
  if (!aqiDistChartRef.value || cityTable.value.data.length === 0) return

  if (!aqiDistChart) {
    aqiDistChart = echarts.init(aqiDistChartRef.value)
  }

  // 统计AQI等级分布
  const distribution: Record<string, number> = {
    '优': 0,
    '良': 0,
    '轻度污染': 0,
    '中度污染': 0,
    '重度污染': 0,
    '严重污染': 0
  }

  cityTable.value.data.forEach(item => {
    const level = getAQILevel(item.AQI).level
    if (level in distribution) {
      distribution[level]++
    }
  })

  const data = Object.entries(distribution).map(([name, value]) => ({
    name,
    value,
    itemStyle: {
      color: getAQILevel(
        name === '优' ? 25 :
        name === '良' ? 75 :
        name === '轻度污染' ? 125 :
        name === '中度污染' ? 175 :
        name === '重度污染' ? 250 : 350
      ).color
    }
  }))

  const option = {
    title: {
      text: 'AQI等级分布统计',
      left: 'center',
      textStyle: {
        fontSize: 16,
        fontWeight: 'bold'
      }
    },
    tooltip: {
      trigger: 'item',
      formatter: '{a} <br/>{b}: {c} 个城市 ({d}%)'
    },
    legend: {
      orient: 'vertical',
      left: 'left',
      top: 'center'
    },
    series: [
      {
        name: 'AQI等级',
        type: 'pie',
        radius: ['40%', '70%'],
        avoidLabelOverlap: false,
        padAngle: 3,
        itemStyle: {
          borderRadius: 10,
          borderColor: '#fff',
          borderWidth: 2
        },
        label: {
          show: true,
          formatter: '{b}\n{d}%',
          fontSize: 13,
          fontWeight: 'bold'
        },
        emphasis: {
          label: {
            show: true,
            fontSize: 15,
            fontWeight: 'bold'
          }
        },
        data: data
      }
    ]
  }

  aqiDistChart.setOption(option)
}

// ========== 响应式处理 ==========
const handleResize = () => {
  historyChart?.resize()
  aqiDistChart?.resize()
}

// ========== 生命周期 ==========
onMounted(async () => {
  await nextTick()

  // 加载初始数据
  await loadCityTable()
  await loadHistoryData()

  // 监听窗口大小变化
  window.addEventListener('resize', handleResize)
})

// 组件卸载时清理
import { onBeforeUnmount } from 'vue'
onBeforeUnmount(() => {
  window.removeEventListener('resize', handleResize)
  historyChart?.dispose()
  aqiDistChart?.dispose()
})
</script>

<style scoped>
.air-quality-panel {
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
    height: 300px !important;
  }
}
</style>
