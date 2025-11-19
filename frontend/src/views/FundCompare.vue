<template>
  <div class="fund-compare-container">
    <h1 class="page-title">基金对比</h1>

    <!-- 基金选择器 -->
    <div class="fund-selector-section card">
      <h3>选择对比基金 (2-5个)</h3>
      <div class="selector-row">
        <el-select
          v-for="(item, index) in selectedFunds"
          :key="index"
          v-model="selectedFunds[index]"
          filterable
          remote
          :remote-method="(query) => handleSearch(query, index)"
          :loading="searchLoading[index]"
          placeholder="输入基金代码或名称搜索"
          clearable
          style="width: 240px; margin-right: 10px;"
          @change="handleFundChange"
        >
          <el-option
            v-for="fund in searchResults[index] || []"
            :key="fund.基金代码"
            :label="`${fund.基金代码} - ${fund.基金简称}`"
            :value="fund.基金代码"
          />
        </el-select>

        <el-button
          v-if="selectedFunds.length < 5"
          @click="addFundSelector"
          type="primary"
          plain
        >
          + 添加基金
        </el-button>

        <el-button
          @click="compareNow"
          type="primary"
          :disabled="validFundCount < 2"
          :loading="comparing"
        >
          开始对比
        </el-button>
      </div>

      <div class="hint-text">
        已选择 {{ validFundCount }} 个基金（需要至少2个）
      </div>
    </div>

    <!-- 对比结果 -->
    <div v-if="compareData.length > 0" class="compare-results">
      <!-- 基础信息对比 -->
      <div class="compare-section card">
        <h3 class="section-title">基础信息</h3>
        <el-table :data="basicInfoTableData" stripe border>
          <el-table-column prop="label" label="项目" width="150" fixed />
          <el-table-column
            v-for="(fund, index) in compareData"
            :key="index"
            :label="fund.基金代码"
            min-width="180"
          >
            <template #default="scope">
              {{ scope.row[`value${index}`] || '-' }}
            </template>
          </el-table-column>
        </el-table>
      </div>

      <!-- 收益率对比 -->
      <div class="compare-section card">
        <h3 class="section-title">收益率对比 (%)</h3>
        <el-table :data="returnTableData" stripe border>
          <el-table-column prop="label" label="时间周期" width="150" fixed />
          <el-table-column
            v-for="(fund, index) in compareData"
            :key="index"
            :label="fund.基金代码"
            min-width="120"
          >
            <template #default="scope">
              <span :class="getReturnClass(scope.row[`value${index}`])">
                {{ formatReturn(scope.row[`value${index}`]) }}
              </span>
            </template>
          </el-table-column>
        </el-table>
      </div>

      <!-- 风险指标对比 -->
      <div class="compare-section card">
        <h3 class="section-title">风险指标</h3>
        <el-table :data="riskTableData" stripe border>
          <el-table-column prop="label" label="指标" width="150" fixed />
          <el-table-column
            v-for="(fund, index) in compareData"
            :key="index"
            :label="fund.基金代码"
            min-width="120"
          >
            <template #default="scope">
              {{ formatDecimal(scope.row[`value${index}`]) }}
            </template>
          </el-table-column>
        </el-table>
      </div>

      <!-- 分红统计对比 -->
      <div class="compare-section card">
        <h3 class="section-title">分红统计</h3>
        <el-table :data="dividendTableData" stripe border>
          <el-table-column prop="label" label="项目" width="150" fixed />
          <el-table-column
            v-for="(fund, index) in compareData"
            :key="index"
            :label="fund.基金代码"
            min-width="120"
          >
            <template #default="scope">
              <span v-if="scope.row.label === '分红次数'">
                {{ formatInteger(scope.row[`value${index}`]) }}
              </span>
              <span v-else-if="scope.row.label === '累计分红 (元)'">
                {{ formatDecimal(scope.row[`value${index}`], 4) }}
              </span>
              <span v-else>
                {{ scope.row[`value${index}`] || '-' }}
              </span>
            </template>
          </el-table-column>
        </el-table>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { getFundList, compareFunds } from '@/api/fund'
import type { FundInfo, FundCompareData } from '@/types/fund'
import { ElMessage } from 'element-plus'

// 基金列表缓存
let fullFundList: FundInfo[] = []

// 搜索结果和加载状态
const searchResults = ref<FundInfo[][]>([[], []])
const searchLoading = ref<boolean[]>([false, false])
const selectedFunds = ref<string[]>(['', ''])
const compareData = ref<FundCompareData[]>([])
const comparing = ref(false)

// 有效基金数量
const validFundCount = computed(() => {
  return selectedFunds.value.filter(code => code && code.trim() !== '').length
})

// 远程搜索基金
const handleSearch = async (query: string, index: number) => {
  if (!query || query.trim() === '') {
    searchResults.value[index] = []
    return
  }

  searchLoading.value[index] = true

  try {
    // 首次搜索时加载完整列表到内存
    if (fullFundList.length === 0) {
      fullFundList = await getFundList()
      console.log('[基金对比] 基金列表加载成功:', fullFundList.length)
    }

    // 在本地搜索
    const queryLower = query.toLowerCase()
    const results = fullFundList.filter(fund => {
      return (
        fund.基金代码.includes(queryLower) ||
        fund.基金简称.toLowerCase().includes(queryLower) ||
        fund.拼音缩写?.toLowerCase().includes(queryLower)
      )
    }).slice(0, 50) // 限制最多显示50条结果

    searchResults.value[index] = results
  } catch (error) {
    console.error('[基金对比] 搜索失败:', error)
    ElMessage.error('搜索失败，请稍后重试')
  } finally {
    searchLoading.value[index] = false
  }
}

// 添加基金选择器
const addFundSelector = () => {
  if (selectedFunds.value.length < 5) {
    selectedFunds.value.push('')
    searchResults.value.push([])
    searchLoading.value.push(false)
  }
}

// 基金变更
const handleFundChange = () => {
  // 移除空选项（除了最后两个）
  const validFunds = selectedFunds.value.filter(code => code && code.trim() !== '')
  const emptyCount = selectedFunds.value.length - validFunds.length

  if (emptyCount > 2) {
    selectedFunds.value = [...validFunds, '', '']
  }
}

// 开始对比
const compareNow = async () => {
  const validCodes = selectedFunds.value.filter(code => code && code.trim() !== '')

  if (validCodes.length < 2) {
    ElMessage.warning('请至少选择2个基金')
    return
  }

  comparing.value = true
  try {
    const result = await compareFunds(validCodes)
    compareData.value = result.data
    ElMessage.success(`成功对比 ${result.count} 个基金`)
  } catch (error) {
    console.error('[基金对比] 对比失败:', error)
    ElMessage.error('对比失败，请稍后重试')
  } finally {
    comparing.value = false
  }
}

// 基础信息表格数据
const basicInfoTableData = computed(() => {
  if (compareData.value.length === 0) return []

  const rows = [
    { label: '基金简称' },
    { label: '基金类型' },
    { label: '基金经理' },
    { label: '基金公司' },
    { label: '成立日期' },
    { label: '资产规模' },
    { label: '管理费率' },
    { label: '托管费率' }
  ]

  const keys = ['基金简称', '基金类型', '基金经理人', '基金管理人', '成立日期', '资产规模', '管理费率', '托管费率']

  rows.forEach((row, rowIndex) => {
    compareData.value.forEach((fund, fundIndex) => {
      row[`value${fundIndex}`] = fund.基础信息[keys[rowIndex]] || '-'
    })
  })

  return rows
})

// 收益率表格数据
const returnTableData = computed(() => {
  if (compareData.value.length === 0) return []

  const rows = [
    { label: '日增长率' },
    { label: '近1周' },
    { label: '近1月' },
    { label: '近3月' },
    { label: '近6月' },
    { label: '近1年' },
    { label: '近3年' },
    { label: '今年来' },
    { label: '成立来' }
  ]

  const keys = ['日增长率', '近1周', '近1月', '近3月', '近6月', '近1年', '近3年', '今年来', '成立来']

  rows.forEach((row, rowIndex) => {
    compareData.value.forEach((fund, fundIndex) => {
      row[`value${fundIndex}`] = fund.收益率[keys[rowIndex]]
    })
  })

  return rows
})

// 风险指标表格数据
const riskTableData = computed(() => {
  if (compareData.value.length === 0) return []

  const rows = [
    { label: '年化波动率 (%)' },
    { label: '夏普比率' },
    { label: '最大回撤 (%)' }
  ]

  const keys = ['年化波动率', '年化夏普比率', '最大回撤']

  rows.forEach((row, rowIndex) => {
    compareData.value.forEach((fund, fundIndex) => {
      row[`value${fundIndex}`] = fund.风险指标[keys[rowIndex]]
    })
  })

  return rows
})

// 分红统计表格数据
const dividendTableData = computed(() => {
  if (compareData.value.length === 0) return []

  const rows = [
    { label: '分红次数' },
    { label: '累计分红 (元)' }
  ]

  const keys = ['分红次数', '累计分红']

  rows.forEach((row, rowIndex) => {
    compareData.value.forEach((fund, fundIndex) => {
      const value = fund.分红统计[keys[rowIndex]]
      row[`value${fundIndex}`] = value !== null && value !== undefined ? value : '-'
    })
  })

  return rows
})

// 格式化收益率
const formatReturn = (value: any) => {
  if (value === null || value === undefined || value === '') return '-'
  const num = parseFloat(value)
  if (isNaN(num)) return '-'
  return num > 0 ? `+${num.toFixed(2)}%` : `${num.toFixed(2)}%`
}

// 格式化百分比（不带符号）
const formatPercent = (value: any) => {
  if (value === null || value === undefined || value === '') return '-'
  const num = parseFloat(value)
  if (isNaN(num)) return '-'
  return `${num.toFixed(2)}%`
}

// 格式化小数（2位）
const formatDecimal = (value: any, digits: number = 2) => {
  if (value === null || value === undefined || value === '') return '-'
  const num = parseFloat(value)
  if (isNaN(num)) return '-'
  return num.toFixed(digits)
}

// 格式化整数
const formatInteger = (value: any) => {
  if (value === null || value === undefined || value === '') return '-'
  const num = parseInt(value)
  if (isNaN(num)) return '-'
  return num.toString()
}

// 收益率样式
const getReturnClass = (value: any) => {
  if (value === null || value === undefined || value === '') return ''
  const num = parseFloat(value)
  if (isNaN(num)) return ''
  return num > 0 ? 'positive-return' : num < 0 ? 'negative-return' : ''
}
</script>

<style scoped>
.fund-compare-container {
  padding: var(--spacing-lg);
  max-width: 1400px;
  margin: 0 auto;
}

.page-title {
  font-size: 28px;
  font-weight: 600;
  color: var(--color-text-primary);
  margin-bottom: var(--spacing-lg);
}

.card {
  background: var(--color-bg-card);
  border-radius: var(--border-radius);
  padding: var(--spacing-lg);
  box-shadow: var(--shadow-card);
  margin-bottom: var(--spacing-lg);
}

.fund-selector-section h3 {
  margin: 0 0 var(--spacing-md) 0;
  font-size: 18px;
  font-weight: 600;
  color: var(--color-text-primary);
}

.selector-row {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  align-items: center;
  margin-bottom: var(--spacing-md);
}

.hint-text {
  color: var(--color-text-secondary);
  font-size: 14px;
}

.compare-section {
  overflow-x: auto;
}

.section-title {
  margin: 0 0 var(--spacing-md) 0;
  font-size: 18px;
  font-weight: 600;
  color: var(--color-text-primary);
}

.positive-return {
  color: #f56c6c;
  font-weight: 600;
}

.negative-return {
  color: #67c23a;
  font-weight: 600;
}
</style>
