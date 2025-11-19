<template>
  <div class="wealth-rank-panel">
    <!-- 榜单选择卡片 -->
    <div class="card">
      <div class="card-header">
        <h3>💰 选择榜单</h3>
      </div>
      <div class="rank-selector">
        <el-radio-group v-model="selectedRank" size="large">
          <el-radio-button label="fortune">财富500强</el-radio-button>
          <el-radio-button label="forbes">福布斯中国榜</el-radio-button>
          <el-radio-button label="xincaifu">新财富榜</el-radio-button>
          <el-radio-button label="hurun">胡润百富榜</el-radio-button>
        </el-radio-group>
      </div>
    </div>

    <!-- 财富500强 -->
    <div v-if="selectedRank === 'fortune'" class="card">
      <div class="card-header">
        <h3>🌍 财富世界500强</h3>
        <div class="card-actions">
          <el-select v-model="fortune.year" size="small" style="width: 100px">
            <el-option
              v-for="year in availableYears"
              :key="year"
              :label="`${year}年`"
              :value="String(year)"
            />
          </el-select>
        </div>
      </div>
      <div v-loading="fortune.loading">
        <div ref="fortuneChartRef" class="chart" style="height: 400px; margin-bottom: 16px"></div>
        <el-table :data="fortune.data.slice(0, 20)" stripe style="width: 100%">
          <el-table-column prop="排名" label="排名" width="80" align="center" />
          <el-table-column prop="公司名称" label="公司名称" min-width="200" show-overflow-tooltip />
          <el-table-column label="营业收入" width="150" align="right">
            <template #default="{ row }">
              <span class="text-success">{{ formatRevenue(row.营业收入) }}</span>
            </template>
          </el-table-column>
          <el-table-column label="利润" width="150" align="right">
            <template #default="{ row }">
              <span :class="row.利润 >= 0 ? 'text-success' : 'text-danger'">
                {{ formatRevenue(row.利润) }}
              </span>
            </template>
          </el-table-column>
          <el-table-column prop="国家" label="国家" width="120" align="center" />
          <el-table-column prop="行业" label="行业" min-width="150" show-overflow-tooltip />
        </el-table>
      </div>
    </div>

    <!-- 福布斯中国榜 -->
    <div v-if="selectedRank === 'forbes'" class="card">
      <div class="card-header">
        <h3>📊 福布斯中国榜</h3>
        <div class="card-actions">
          <el-select v-model="forbes.symbol" size="small" style="width: 200px">
            <el-option label="中国400富豪榜" value="中国400富豪榜" />
            <el-option label="30岁以下精英榜" value="30岁以下精英榜" />
            <el-option label="最佳创业投资机构" value="中国最佳创业投资机构" />
          </el-select>
        </div>
      </div>
      <div v-loading="forbes.loading">
        <div ref="forbesChartRef" class="chart" style="height: 400px; margin-bottom: 16px"></div>
        <el-table :data="forbes.data.slice(0, 20)" stripe style="width: 100%">
          <el-table-column prop="排名" label="排名" width="80" align="center" />
          <el-table-column label="姓名/企业" min-width="150">
            <template #default="{ row }">
              {{ row.姓名 || row.企业名 || row.名称 }}
            </template>
          </el-table-column>
          <el-table-column label="财富/估值" width="150" align="right">
            <template #default="{ row }">
              <span class="text-accent">
                {{ formatWealth(row.财富 || row.估值) }}
              </span>
            </template>
          </el-table-column>
          <el-table-column prop="行业" label="行业" min-width="120" />
          <el-table-column prop="年龄" label="年龄" width="80" align="center">
            <template #default="{ row }">
              {{ row.年龄 || '-' }}
            </template>
          </el-table-column>
          <el-table-column prop="公司" label="公司" min-width="150" show-overflow-tooltip>
            <template #default="{ row }">
              {{ row.公司 || '-' }}
            </template>
          </el-table-column>
        </el-table>
      </div>
    </div>

    <!-- 新财富榜 -->
    <div v-if="selectedRank === 'xincaifu'" class="card">
      <div class="card-header">
        <h3>💎 新财富500富豪榜</h3>
        <div class="card-actions">
          <el-select v-model="xincaifu.year" size="small" style="width: 100px">
            <el-option
              v-for="year in availableYears"
              :key="year"
              :label="`${year}年`"
              :value="String(year)"
            />
          </el-select>
        </div>
      </div>
      <div v-loading="xincaifu.loading">
        <div ref="xincaifuChartRef" class="chart" style="height: 400px; margin-bottom: 16px"></div>
        <el-table :data="xincaifu.data.slice(0, 20)" stripe style="width: 100%">
          <el-table-column prop="排名" label="排名" width="80" align="center" />
          <el-table-column prop="姓名" label="姓名" width="120" />
          <el-table-column label="财富" width="150" align="right">
            <template #default="{ row }">
              <span class="text-success">{{ formatWealth(row.财富) }}</span>
            </template>
          </el-table-column>
          <el-table-column prop="公司" label="公司" min-width="150" show-overflow-tooltip />
          <el-table-column prop="行业" label="行业" width="120" />
          <el-table-column prop="年龄" label="年龄" width="80" align="center" />
          <el-table-column prop="财富变化" label="变化" width="100" align="center">
            <template #default="{ row }">
              <el-tag v-if="row.财富变化" size="small" :type="getChangeType(row.财富变化)">
                {{ row.财富变化 }}
              </el-tag>
            </template>
          </el-table-column>
        </el-table>
      </div>
    </div>

    <!-- 胡润百富榜 -->
    <div v-if="selectedRank === 'hurun'" class="card">
      <div class="card-header">
        <h3>🏆 胡润百富榜</h3>
        <div class="card-actions">
          <el-select v-model="hurun.indicator" size="small" style="width: 140px">
            <el-option label="富豪榜" value="富豪榜" />
            <el-option label="全球富豪榜" value="全球富豪榜" />
            <el-option label="独角兽榜" value="独角兽榜" />
            <el-option label="500强" value="500强" />
          </el-select>
          <el-select v-model="hurun.year" size="small" style="width: 140px">
            <el-option
              v-for="year in availableYears"
              :key="year"
              :label="`${year}年`"
              :value="String(year)"
            />
          </el-select>
        </div>
      </div>
      <div v-loading="hurun.loading">
        <div ref="hurunChartRef" class="chart" style="height: 400px; margin-bottom: 16px"></div>
        <el-table :data="hurun.data.slice(0, 20)" stripe style="width: 100%">
          <el-table-column prop="排名" label="排名" width="80" align="center" />
          <el-table-column label="姓名/企业" min-width="150">
            <template #default="{ row }">
              {{ row.姓名 || row.企业 || row.名称 }}
            </template>
          </el-table-column>
          <el-table-column label="财富/估值" width="150" align="right">
            <template #default="{ row }">
              <span class="text-accent">
                {{ formatWealth(row.财富 || row.估值) }}
              </span>
            </template>
          </el-table-column>
          <el-table-column prop="行业" label="行业" min-width="120" />
          <el-table-column prop="公司" label="公司" min-width="150" show-overflow-tooltip>
            <template #default="{ row }">
              {{ row.公司 || '-' }}
            </template>
          </el-table-column>
        </el-table>
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
  getFortuneRank,
  getForbesRank,
  getXincaifuRank,
  getHurunRank
} from '@/api/alternative'
import type { FortuneRank, ForbesRank, XincaifuRank, HurunRank } from '@/types/alternative'

// 图表引用
const fortuneChartRef = ref<HTMLDivElement>()
const forbesChartRef = ref<HTMLDivElement>()
const xincaifuChartRef = ref<HTMLDivElement>()
const hurunChartRef = ref<HTMLDivElement>()

// ECharts 实例
let fortuneChart: ECharts | null = null
let forbesChart: ECharts | null = null
let xincaifuChart: ECharts | null = null
let hurunChart: ECharts | null = null

// 选择的榜单类型
const selectedRank = ref<'fortune' | 'forbes' | 'xincaifu' | 'hurun'>('fortune')

// 可选年份
const availableYears = computed(() => {
  const currentYear = new Date().getFullYear()
  return Array.from({ length: 10 }, (_, i) => currentYear - 1 - i)
})

// ========== 财富500强 ==========
const fortune = ref({
  year: String(new Date().getFullYear() - 1),
  loading: false,
  data: [] as FortuneRank[]
})

const loadFortuneData = async () => {
  fortune.value.loading = true
  try {
    const data = await getFortuneRank(fortune.value.year)
    fortune.value.data = data
    await nextTick()
    renderFortuneChart()
  } catch (error: any) {
    ElMessage.error('加载财富500强数据失败')
    console.error(error)
  } finally {
    fortune.value.loading = false
  }
}

const renderFortuneChart = () => {
  if (!fortuneChartRef.value || fortune.value.data.length === 0) return

  if (!fortuneChart) {
    fortuneChart = echarts.init(fortuneChartRef.value)
  }

  // 按国家统计数量
  const countryCount: Record<string, number> = {}
  fortune.value.data.forEach(item => {
    countryCount[item.国家] = (countryCount[item.国家] || 0) + 1
  })

  const topCountries = Object.entries(countryCount)
    .sort((a, b) => b[1] - a[1])
    .slice(0, 10)

  const option = {
    title: {
      text: '财富500强 - 国家分布 TOP10',
      left: 'center',
      textStyle: { fontSize: 16, fontWeight: 'bold' }
    },
    tooltip: {
      trigger: 'item',
      formatter: '{b}: {c} 家 ({d}%)'
    },
    legend: {
      orient: 'vertical',
      left: 'left',
      top: 'center'
    },
    series: [
      {
        type: 'pie',
        radius: ['40%', '70%'],
        data: topCountries.map(([name, value]) => ({ name, value })),
        emphasis: {
          itemStyle: {
            shadowBlur: 10,
            shadowOffsetX: 0,
            shadowColor: 'rgba(0, 0, 0, 0.5)'
          }
        }
      }
    ]
  }

  fortuneChart.setOption(option)
}

// ========== 福布斯中国榜 ==========
const forbes = ref({
  symbol: '中国400富豪榜',
  loading: false,
  data: [] as ForbesRank[]
})

const loadForbesData = async () => {
  forbes.value.loading = true
  try {
    const data = await getForbesRank(forbes.value.symbol)
    forbes.value.data = data
    await nextTick()
    renderForbesChart()
  } catch (error: any) {
    ElMessage.error('加载福布斯榜单数据失败')
    console.error(error)
  } finally {
    forbes.value.loading = false
  }
}

const renderForbesChart = () => {
  if (!forbesChartRef.value || forbes.value.data.length === 0) return

  if (!forbesChart) {
    forbesChart = echarts.init(forbesChartRef.value)
  }

  const top10 = forbes.value.data.slice(0, 10)
  const names = top10.map(item => item.姓名 || item.企业名 || item.名称 || '')
  const wealth = top10.map(item => item.财富 || item.估值 || 0)

  const option = {
    title: {
      text: `${forbes.value.symbol} TOP10`,
      left: 'center',
      textStyle: { fontSize: 16, fontWeight: 'bold' }
    },
    tooltip: {
      trigger: 'axis',
      axisPointer: { type: 'shadow' },
      formatter: (params: any) => {
        const item = params[0]
        return `<strong>${item.name}</strong><br/>财富: <strong>${formatWealth(item.value)}</strong>`
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
      name: '财富（亿元）'
    },
    yAxis: {
      type: 'category',
      data: names,
      inverse: true
    },
    series: [
      {
        type: 'bar',
        data: wealth,
        itemStyle: {
          color: new echarts.graphic.LinearGradient(0, 0, 1, 0, [
            { offset: 0, color: '#667eea' },
            { offset: 1, color: '#764ba2' }
          ])
        },
        label: {
          show: true,
          position: 'right',
          formatter: (params: any) => formatWealth(params.value)
        }
      }
    ]
  }

  forbesChart.setOption(option)
}

// ========== 新财富榜 ==========
const xincaifu = ref({
  year: String(new Date().getFullYear() - 1),
  loading: false,
  data: [] as XincaifuRank[]
})

const loadXincaifuData = async () => {
  xincaifu.value.loading = true
  try {
    const data = await getXincaifuRank(xincaifu.value.year)
    xincaifu.value.data = data
    await nextTick()
    renderXincaifuChart()
  } catch (error: any) {
    ElMessage.error('加载新财富榜单数据失败')
    console.error(error)
  } finally {
    xincaifu.value.loading = false
  }
}

const renderXincaifuChart = () => {
  if (!xincaifuChartRef.value || xincaifu.value.data.length === 0) return

  if (!xincaifuChart) {
    xincaifuChart = echarts.init(xincaifuChartRef.value)
  }

  // 按行业统计财富总和
  const industryWealth: Record<string, number> = {}
  xincaifu.value.data.forEach(item => {
    industryWealth[item.行业] = (industryWealth[item.行业] || 0) + (item.财富 || 0)
  })

  const topIndustries = Object.entries(industryWealth)
    .sort((a, b) => b[1] - a[1])
    .slice(0, 10)

  const option = {
    title: {
      text: '新财富榜 - 行业财富分布 TOP10',
      left: 'center',
      textStyle: { fontSize: 16, fontWeight: 'bold' }
    },
    tooltip: {
      trigger: 'axis',
      axisPointer: { type: 'shadow' },
      formatter: (params: any) => {
        const item = params[0]
        return `<strong>${item.name}</strong><br/>总财富: <strong>${formatWealth(item.value)}</strong>`
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
      data: topIndustries.map(([name]) => name),
      axisLabel: {
        rotate: 45,
        formatter: (value: string) => value.length > 6 ? value.slice(0, 6) + '...' : value
      }
    },
    yAxis: {
      type: 'value',
      name: '总财富（亿元）'
    },
    series: [
      {
        type: 'bar',
        data: topIndustries.map(([, value]) => value),
        itemStyle: {
          color: new echarts.graphic.LinearGradient(0, 1, 0, 0, [
            { offset: 0, color: '#30d158' },
            { offset: 1, color: '#00d4aa' }
          ])
        },
        label: {
          show: true,
          position: 'top',
          formatter: (params: any) => formatWealth(params.value)
        }
      }
    ]
  }

  xincaifuChart.setOption(option)
}

// ========== 胡润百富榜 ==========
const hurun = ref({
  indicator: '富豪榜',
  year: String(new Date().getFullYear() - 1),
  loading: false,
  data: [] as HurunRank[]
})

const loadHurunData = async () => {
  hurun.value.loading = true
  try {
    const data = await getHurunRank(hurun.value.indicator, hurun.value.year)
    hurun.value.data = data
    await nextTick()
    renderHurunChart()
  } catch (error: any) {
    ElMessage.error('加载胡润榜单数据失败')
    console.error(error)
  } finally {
    hurun.value.loading = false
  }
}

const renderHurunChart = () => {
  if (!hurunChartRef.value || hurun.value.data.length === 0) return

  if (!hurunChart) {
    hurunChart = echarts.init(hurunChartRef.value)
  }

  const top10 = hurun.value.data.slice(0, 10)
  const names = top10.map(item => item.姓名 || item.企业 || item.名称 || '')
  const wealth = top10.map(item => item.财富 || item.估值 || 0)

  const option = {
    title: {
      text: `胡润${hurun.value.indicator} TOP10`,
      left: 'center',
      textStyle: { fontSize: 16, fontWeight: 'bold' }
    },
    tooltip: {
      trigger: 'axis',
      axisPointer: { type: 'shadow' }
    },
    grid: {
      left: '3%',
      right: '4%',
      bottom: '3%',
      containLabel: true
    },
    xAxis: {
      type: 'value'
    },
    yAxis: {
      type: 'category',
      data: names,
      inverse: true
    },
    series: [
      {
        type: 'bar',
        data: wealth,
        itemStyle: {
          color: new echarts.graphic.LinearGradient(0, 0, 1, 0, [
            { offset: 0, color: '#fa709a' },
            { offset: 1, color: '#fee140' }
          ])
        },
        label: {
          show: true,
          position: 'right',
          formatter: (params: any) => formatWealth(params.value)
        }
      }
    ]
  }

  hurunChart.setOption(option)
}

// ========== 工具函数 ==========
const formatRevenue = (value: number): string => {
  if (!value) return '-'
  if (value >= 1000) return `${(value / 1000).toFixed(1)}B`
  return `${value.toFixed(0)}M`
}

const formatWealth = (value: number): string => {
  if (!value) return '-'
  if (value >= 1000) return `${(value / 1000).toFixed(0)}千亿`
  return `${value.toFixed(0)}亿`
}

const getChangeType = (change: string): 'success' | 'danger' | 'info' => {
  if (change.includes('+') || change.includes('↑')) return 'success'
  if (change.includes('-') || change.includes('↓')) return 'danger'
  return 'info'
}

// ========== 响应式处理 ==========
const handleResize = () => {
  fortuneChart?.resize()
  forbesChart?.resize()
  xincaifuChart?.resize()
  hurunChart?.resize()
}

// ========== 监听变化 ==========
watch(() => fortune.value.year, loadFortuneData)
watch(() => forbes.value.symbol, loadForbesData)
watch(() => xincaifu.value.year, loadXincaifuData)
watch(() => hurun.value.indicator, loadHurunData)
watch(() => hurun.value.year, loadHurunData)

watch(selectedRank, async (newRank) => {
  await nextTick()
  // 加载对应榜单数据
  switch (newRank) {
    case 'fortune':
      await loadFortuneData()
      break
    case 'forbes':
      await loadForbesData()
      break
    case 'xincaifu':
      await loadXincaifuData()
      break
    case 'hurun':
      await loadHurunData()
      break
  }
})

// ========== 生命周期 ==========
onMounted(async () => {
  await nextTick()
  await loadFortuneData()  // 默认加载财富500强
  window.addEventListener('resize', handleResize)
})

// 组件卸载时清理
import { onBeforeUnmount } from 'vue'
onBeforeUnmount(() => {
  window.removeEventListener('resize', handleResize)
  fortuneChart?.dispose()
  forbesChart?.dispose()
  xincaifuChart?.dispose()
  hurunChart?.dispose()
})
</script>

<style scoped>
.wealth-rank-panel {
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

.rank-selector {
  display: flex;
  justify-content: center;
  padding: var(--spacing-md) 0;
}

.chart {
  width: 100%;
}

.text-success {
  color: var(--color-success);
  font-weight: 600;
}

.text-danger {
  color: var(--color-danger);
  font-weight: 600;
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

  .rank-selector :deep(.el-radio-group) {
    flex-direction: column;
    width: 100%;
  }

  .rank-selector :deep(.el-radio-button) {
    width: 100%;
  }

  .chart {
    height: 300px !important;
  }
}
</style>
