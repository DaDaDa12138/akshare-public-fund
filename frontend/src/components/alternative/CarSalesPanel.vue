<template>
  <div class="car-sales-panel">
    <!-- 市场总览卡片 -->
    <div class="card">
      <div class="card-header">
        <h3>📊 市场总览</h3>
        <div class="card-actions">
          <el-select v-model="totalMarket.symbol" size="small" style="width: 140px">
            <el-option label="狭义乘用车" value="狭义乘用车" />
            <el-option label="广义乘用车" value="广义乘用车" />
          </el-select>
          <el-select v-model="totalMarket.indicator" size="small" style="width: 100px">
            <el-option label="零售" value="零售" />
            <el-option label="批发" value="批发" />
            <el-option label="产量" value="产量" />
            <el-option label="出口" value="出口" />
          </el-select>
          <el-button size="small" @click="loadTotalMarket">刷新</el-button>
        </div>
      </div>
      <div v-loading="totalMarket.loading" class="chart-container">
        <div ref="totalChartRef" class="chart" style="height: 400px"></div>
      </div>
    </div>

    <!-- 厂商排名和车型分类并排 -->
    <el-row :gutter="16">
      <!-- 厂商排名卡片 -->
      <el-col :xs="24" :sm="24" :md="12">
        <div class="card">
          <div class="card-header">
            <h3>🏆 厂商排名 TOP10</h3>
            <div class="card-actions">
              <el-select v-model="manufacturerRank.symbol" size="small" style="width: 100px">
                <el-option label="单月" value="单月" />
                <el-option label="累计" value="累计" />
              </el-select>
              <el-select v-model="manufacturerRank.indicator" size="small" style="width: 100px">
                <el-option label="零售" value="零售" />
                <el-option label="批发" value="批发" />
              </el-select>
            </div>
          </div>
          <div v-loading="manufacturerRank.loading" class="chart-container">
            <div ref="manufacturerChartRef" class="chart" style="height: 450px"></div>
          </div>
        </div>
      </el-col>

      <!-- 车型分类卡片 -->
      <el-col :xs="24" :sm="24" :md="12">
        <div class="card">
          <div class="card-header">
            <h3>🚙 车型占比</h3>
            <div class="card-actions">
              <el-select v-model="categoryData.indicator" size="small" style="width: 100px">
                <el-option label="零售" value="零售" />
                <el-option label="批发" value="批发" />
              </el-select>
            </div>
          </div>
          <div v-loading="categoryData.loading" class="chart-container">
            <div v-if="categoryData.data.length === 0 && !categoryData.loading" class="empty-state">
              <p>暂无车型分类数据</p>
              <p class="text-secondary" style="font-size: 12px">该接口暂时不可用</p>
            </div>
            <div v-else ref="categoryChartRef" class="chart" style="height: 450px"></div>
          </div>
        </div>
      </el-col>
    </el-row>

    <!-- 新能源市场和国别分析 -->
    <el-row :gutter="16">
      <!-- 新能源市场卡片 -->
      <el-col :xs="24" :sm="24" :md="12">
        <div class="card">
          <div class="card-header">
            <h3>⚡ 新能源市场</h3>
            <div class="card-actions">
              <el-select v-model="fuelData.symbol" size="small" style="width: 120px">
                <el-option label="整体市场" value="整体市场" />
                <el-option label="销量占比" value="销量占比" />
              </el-select>
            </div>
          </div>
          <div v-loading="fuelData.loading" class="chart-container">
            <div ref="fuelChartRef" class="chart" style="height: 400px"></div>
          </div>
        </div>
      </el-col>

      <!-- 国别细分卡片 -->
      <el-col :xs="24" :sm="24" :md="12">
        <div class="card">
          <div class="card-header">
            <h3>🌍 国别细分市场</h3>
          </div>
          <div v-loading="countryData.loading" class="chart-container">
            <div ref="countryChartRef" class="chart" style="height: 400px"></div>
          </div>
        </div>
      </el-col>
    </el-row>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, watch, nextTick } from 'vue'
import { ElMessage } from 'element-plus'
import * as echarts from 'echarts'
import type { ECharts } from 'echarts'
import {
  getCarMarketTotal,
  getCarManufacturerRank,
  getCarCategoryData,
  getCarCountryData,
  getCarFuelData
} from '@/api/alternative'
import type { CarMarketTotal, CarManufacturerRank, CarCategoryData, CarCountryData, CarFuelData } from '@/types/alternative'

// 图表引用
const totalChartRef = ref<HTMLDivElement>()
const manufacturerChartRef = ref<HTMLDivElement>()
const categoryChartRef = ref<HTMLDivElement>()
const fuelChartRef = ref<HTMLDivElement>()
const countryChartRef = ref<HTMLDivElement>()

// ECharts 实例
let totalChart: ECharts | null = null
let manufacturerChart: ECharts | null = null
let categoryChart: ECharts | null = null
let fuelChart: ECharts | null = null
let countryChart: ECharts | null = null

// ========== 市场总览 ==========
const totalMarket = ref({
  symbol: '狭义乘用车',
  indicator: '零售',
  loading: false,
  data: [] as CarMarketTotal[]
})

const loadTotalMarket = async () => {
  totalMarket.value.loading = true
  try {
    const data = await getCarMarketTotal(totalMarket.value.symbol, totalMarket.value.indicator)
    totalMarket.value.data = data
    renderTotalChart()
  } catch (error: any) {
    ElMessage.error('加载市场总览数据失败')
    console.error(error)
  } finally {
    totalMarket.value.loading = false
  }
}

const renderTotalChart = () => {
  if (!totalChartRef.value || totalMarket.value.data.length === 0) return

  if (!totalChart) {
    totalChart = echarts.init(totalChartRef.value)
  }

  // 提取月份和年份数据
  const months = totalMarket.value.data.map(item => item.月份)
  const years = Object.keys(totalMarket.value.data[0]).filter(key => key !== '月份')

  const series = years.map(year => ({
    name: year,
    type: 'line',
    smooth: true,
    data: totalMarket.value.data.map(item => item[year]),
    emphasis: {
      focus: 'series'
    }
  }))

  const option = {
    title: {
      text: `${totalMarket.value.symbol} - ${totalMarket.value.indicator}趋势`,
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
          html += `${item.marker} ${item.seriesName}: <strong>${item.value || '-'}</strong> 万辆<br/>`
        })
        return html
      }
    },
    legend: {
      data: years,
      top: 30,
      type: 'scroll'
    },
    grid: {
      left: '3%',
      right: '4%',
      bottom: '10%',
      containLabel: true
    },
    xAxis: {
      type: 'category',
      data: months,
      boundaryGap: false,
      axisLabel: {
        rotate: 45
      }
    },
    yAxis: {
      type: 'value',
      name: '销量（万辆）',
      axisLabel: {
        formatter: '{value}'
      }
    },
    series: series,
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
    ]
  }

  totalChart.setOption(option)
}

// ========== 厂商排名 ==========
const manufacturerRank = ref({
  symbol: '单月',
  indicator: '零售',
  loading: false,
  data: [] as CarManufacturerRank[]
})

const loadManufacturerRank = async () => {
  manufacturerRank.value.loading = true
  try {
    const data = await getCarManufacturerRank(manufacturerRank.value.symbol, manufacturerRank.value.indicator)
    manufacturerRank.value.data = data.slice(0, 10)  // TOP10
    renderManufacturerChart()
  } catch (error: any) {
    ElMessage.error('加载厂商排名数据失败')
    console.error(error)
  } finally {
    manufacturerRank.value.loading = false
  }
}

const renderManufacturerChart = () => {
  if (!manufacturerChartRef.value || manufacturerRank.value.data.length === 0) return

  if (!manufacturerChart) {
    manufacturerChart = echarts.init(manufacturerChartRef.value)
  }

  const manufacturers = manufacturerRank.value.data.map(item => item.厂商)
  const latestYear = Object.keys(manufacturerRank.value.data[0]).filter(key => key !== '厂商')[0]
  const values = manufacturerRank.value.data.map(item => item[latestYear])

  const option = {
    title: {
      text: `厂商${manufacturerRank.value.indicator}排名 (${latestYear})`,
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
        return `<strong>${item.name}</strong><br/>${item.seriesName}: <strong>${item.value}</strong> 万辆`
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
      name: '销量（万辆）'
    },
    yAxis: {
      type: 'category',
      data: manufacturers,
      inverse: true,
      axisLabel: {
        fontSize: 12
      }
    },
    series: [
      {
        name: manufacturerRank.value.indicator,
        type: 'bar',
        data: values,
        itemStyle: {
          color: new echarts.graphic.LinearGradient(0, 0, 1, 0, [
            { offset: 0, color: '#667eea' },
            { offset: 1, color: '#764ba2' }
          ]),
          borderRadius: [0, 4, 4, 0]
        },
        label: {
          show: true,
          position: 'right',
          formatter: '{c} 万辆',
          fontSize: 11
        }
      }
    ]
  }

  manufacturerChart.setOption(option)
}

// ========== 车型分类 ==========
const categoryData = ref({
  indicator: '零售',
  loading: false,
  data: [] as any[]
})

const loadCategoryData = async () => {
  categoryData.value.loading = true
  try {
    // 获取三种车型的最新数据（使用 Promise.allSettled 以容错）
    const results = await Promise.allSettled([
      getCarCategoryData('轿车', categoryData.value.indicator),
      getCarCategoryData('MPV', categoryData.value.indicator),
      getCarCategoryData('SUV', categoryData.value.indicator)
    ])

    // 提取成功的数据
    const [sedanResult, mpvResult, suvResult] = results

    if (sedanResult.status === 'rejected' && mpvResult.status === 'rejected' && suvResult.status === 'rejected') {
      console.warn('车型分类接口暂时不可用，将隐藏此图表')
      categoryData.value.data = []
      return
    }

    const categoryList: Array<{ name: string; value: number }> = []

    if (sedanResult.status === 'fulfilled' && sedanResult.value.length > 0) {
      const sedan = sedanResult.value
      const latestMonth = sedan[sedan.length - 1]
      const latestYear = Object.keys(latestMonth).filter(key => key !== '月份')[0]
      categoryList.push({ name: '轿车', value: sedan[sedan.length - 1][latestYear] })
    }

    if (mpvResult.status === 'fulfilled' && mpvResult.value.length > 0) {
      const mpv = mpvResult.value
      const latestMonth = mpv[mpv.length - 1]
      const latestYear = Object.keys(latestMonth).filter(key => key !== '月份')[0]
      categoryList.push({ name: 'MPV', value: mpv[mpv.length - 1][latestYear] })
    }

    if (suvResult.status === 'fulfilled' && suvResult.value.length > 0) {
      const suv = suvResult.value
      const latestMonth = suv[suv.length - 1]
      const latestYear = Object.keys(latestMonth).filter(key => key !== '月份')[0]
      categoryList.push({ name: 'SUV', value: suv[suv.length - 1][latestYear] })
    }

    categoryData.value.data = categoryList

    if (categoryList.length > 0) {
      renderCategoryChart()
    }
  } catch (error: any) {
    console.error('加载车型分类数据失败:', error)
    categoryData.value.data = []
  } finally {
    categoryData.value.loading = false
  }
}

const renderCategoryChart = () => {
  if (!categoryChartRef.value || categoryData.value.data.length === 0) return

  if (!categoryChart) {
    categoryChart = echarts.init(categoryChartRef.value)
  }

  const option = {
    title: {
      text: '车型类别占比',
      left: 'center',
      textStyle: {
        fontSize: 16,
        fontWeight: 'bold'
      }
    },
    tooltip: {
      trigger: 'item',
      formatter: '{a} <br/>{b}: {c} 万辆 ({d}%)'
    },
    legend: {
      orient: 'vertical',
      left: 'left',
      top: 'center'
    },
    series: [
      {
        name: '车型',
        type: 'pie',
        radius: ['40%', '70%'],
        avoidLabelOverlap: false,
        itemStyle: {
          borderRadius: 10,
          borderColor: '#fff',
          borderWidth: 2
        },
        label: {
          show: true,
          formatter: '{b}\n{d}%',
          fontSize: 14,
          fontWeight: 'bold'
        },
        emphasis: {
          label: {
            show: true,
            fontSize: 16,
            fontWeight: 'bold'
          }
        },
        data: categoryData.value.data,
        color: ['#5470c6', '#91cc75', '#fac858']
      }
    ]
  }

  categoryChart.setOption(option)
}

// ========== 新能源市场 ==========
const fuelData = ref({
  symbol: '整体市场',
  loading: false,
  data: [] as CarFuelData[]
})

const loadFuelData = async () => {
  fuelData.value.loading = true
  try {
    const data = await getCarFuelData(fuelData.value.symbol)
    fuelData.value.data = data
    renderFuelChart()
  } catch (error: any) {
    ElMessage.error('加载新能源市场数据失败')
    console.error(error)
  } finally {
    fuelData.value.loading = false
  }
}

const renderFuelChart = () => {
  if (!fuelChartRef.value || fuelData.value.data.length === 0) return

  if (!fuelChart) {
    fuelChart = echarts.init(fuelChartRef.value)
  }

  const months = fuelData.value.data.map(item => item.月份)
  const years = Object.keys(fuelData.value.data[0]).filter(key => key !== '月份')

  const series = years.map(year => ({
    name: year,
    type: 'line',
    smooth: true,
    data: fuelData.value.data.map(item => item[year]),
    areaStyle: {
      opacity: 0.3
    }
  }))

  const option = {
    title: {
      text: `新能源汽车${fuelData.value.symbol}`,
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
      }
    },
    legend: {
      data: years,
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
      data: months,
      boundaryGap: false
    },
    yAxis: {
      type: 'value',
      name: fuelData.value.symbol === '销量占比' ? '占比（%）' : '销量（万辆）'
    },
    series: series,
    color: ['#30d158', '#ff9500', '#ff3b30']
  }

  fuelChart.setOption(option)
}

// ========== 国别细分 ==========
const countryData = ref({
  loading: false,
  data: [] as CarCountryData[]
})

const loadCountryData = async () => {
  countryData.value.loading = true
  try {
    const data = await getCarCountryData()
    countryData.value.data = data
    renderCountryChart()
  } catch (error: any) {
    ElMessage.error('加载国别细分数据失败')
    console.error(error)
  } finally {
    countryData.value.loading = false
  }
}

const renderCountryChart = () => {
  if (!countryChartRef.value || countryData.value.data.length === 0) return

  if (!countryChart) {
    countryChart = echarts.init(countryChartRef.value)
  }

  const months = countryData.value.data.map(item => item.月份)
  const countries = ['自主', '德系', '日系', '美系', '韩系', '法系', '其他欧系']

  const series = countries.map(country => ({
    name: country,
    type: 'line',
    stack: 'Total',
    areaStyle: {},
    emphasis: {
      focus: 'series'
    },
    data: countryData.value.data.map(item => item[country as keyof CarCountryData] || 0)
  }))

  const option = {
    title: {
      text: '国别细分市场趋势',
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
      }
    },
    legend: {
      data: countries,
      top: 30,
      type: 'scroll'
    },
    grid: {
      left: '3%',
      right: '4%',
      bottom: '3%',
      containLabel: true
    },
    xAxis: {
      type: 'category',
      data: months,
      boundaryGap: false
    },
    yAxis: {
      type: 'value',
      name: '销量（万辆）'
    },
    series: series
  }

  countryChart.setOption(option)
}

// ========== 响应式处理 ==========
const handleResize = () => {
  totalChart?.resize()
  manufacturerChart?.resize()
  categoryChart?.resize()
  fuelChart?.resize()
  countryChart?.resize()
}

// ========== 监听变化 ==========
watch(() => totalMarket.value.symbol, loadTotalMarket)
watch(() => totalMarket.value.indicator, loadTotalMarket)
watch(() => manufacturerRank.value.symbol, loadManufacturerRank)
watch(() => manufacturerRank.value.indicator, loadManufacturerRank)
watch(() => categoryData.value.indicator, loadCategoryData)
watch(() => fuelData.value.symbol, loadFuelData)

// ========== 生命周期 ==========
onMounted(async () => {
  // 初始化图表
  await nextTick()

  // 加载所有数据
  await Promise.all([
    loadTotalMarket(),
    loadManufacturerRank(),
    loadCategoryData(),
    loadFuelData(),
    loadCountryData()
  ])

  // 监听窗口大小变化
  window.addEventListener('resize', handleResize)
})

// 组件卸载时清理
import { onBeforeUnmount } from 'vue'
onBeforeUnmount(() => {
  window.removeEventListener('resize', handleResize)
  totalChart?.dispose()
  manufacturerChart?.dispose()
  categoryChart?.dispose()
  fuelChart?.dispose()
  countryChart?.dispose()
})
</script>

<style scoped>
.car-sales-panel {
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
}

.chart-container {
  min-height: 300px;
}

.chart {
  width: 100%;
}

.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 450px;
  color: var(--color-text-secondary);
  text-align: center;
}

.empty-state p {
  margin: var(--spacing-xs) 0;
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

  .chart {
    height: 300px !important;
  }

  .empty-state {
    height: 300px !important;
  }
}
</style>
