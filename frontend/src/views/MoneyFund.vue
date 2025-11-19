<template>
  <div class="container">
    <div class="page-header">
      <h1 class="page-title">货币基金排行</h1>
      <p class="page-description">按七日年化收益率排序</p>
    </div>

    <!-- 搜索栏 -->
    <div class="card search-card">
      <input
        v-model="searchQuery"
        type="text"
        class="search-input"
        placeholder="搜索基金代码或名称..."
      />
    </div>

    <!-- 加载状态 -->
    <div v-if="loading" class="card">
      <p class="text-secondary text-center">加载中...</p>
    </div>

    <!-- 错误状态 -->
    <div v-else-if="error" class="card">
      <p class="text-secondary text-center">{{ error }}</p>
    </div>

    <!-- 数据表格 -->
    <div v-else class="card table-card">
      <div class="table-header">
        <div class="table-info">
          <span class="text-secondary">共 {{ filteredFunds.length }} 只基金</span>
          <span v-if="dataSource" class="text-secondary">
            数据来源: {{ dataSource === 'cache' ? '缓存' : 'API' }}
          </span>
        </div>
      </div>

      <div class="table-wrapper">
        <table class="data-table">
          <thead>
            <tr>
              <th>排名</th>
              <th>基金代码</th>
              <th>基金简称</th>
              <th class="number-cell">万份收益</th>
              <th class="number-cell">七日年化</th>
              <th>成立日期</th>
              <th>基金经理</th>
              <th>手续费</th>
              <th>申购状态</th>
            </tr>
          </thead>
          <tbody>
            <tr
              v-for="(fund, index) in filteredFunds"
              :key="fund.基金代码"
              class="table-row"
            >
              <td class="rank-cell">
                <span class="rank-badge" :class="getRankClass(index)">
                  {{ index + 1 }}
                </span>
              </td>
              <td>
                <router-link :to="`/detail/${fund.基金代码}`" class="fund-link">
                  {{ fund.基金代码 }}
                </router-link>
              </td>
              <td>
                <router-link :to="`/detail/${fund.基金代码}`" class="fund-link">
                  {{ fund.基金简称 }}
                </router-link>
              </td>
              <td class="number-cell">
                <span class="positive-value">{{ formatNumber(fund.万份收益) }}</span>
              </td>
              <td class="number-cell">
                <span class="positive-value strong">{{ formatAnnualizedReturn(fund.七日年化) }}</span>
              </td>
              <td class="text-secondary">{{ fund.成立日期 || '-' }}</td>
              <td>{{ fund.基金经理 || '-' }}</td>
              <td>{{ fund.手续费 || '-' }}</td>
              <td>
                <span :class="getPurchaseStatusClass(fund.可购全部)">
                  {{ getPurchaseStatusText(fund.可购全部) }}
                </span>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { getMoneyFunds, type MoneyFundData } from '@/api/fund'

const loading = ref(true)
const error = ref('')
const funds = ref<MoneyFundData[]>([])
const searchQuery = ref('')
const dataSource = ref('')

// 筛选基金
const filteredFunds = computed(() => {
  if (!searchQuery.value.trim()) {
    return funds.value
  }

  const query = searchQuery.value.toLowerCase()
  return funds.value.filter(fund =>
    fund.基金代码.toLowerCase().includes(query) ||
    fund.基金简称.toLowerCase().includes(query)
  )
})

// 格式化数字
const formatNumber = (value: any): string => {
  if (value === null || value === undefined || value === '') return '-'
  const num = typeof value === 'number' ? value : parseFloat(value)
  if (isNaN(num)) return '-'
  return num.toFixed(4)
}

// 格式化年化收益率（去除多余的%）
const formatAnnualizedReturn = (value: string): string => {
  if (!value) return '-'
  // 去除所有%符号，然后添加一个%
  const cleanValue = value.replace(/%/g, '')
  const num = parseFloat(cleanValue)
  if (isNaN(num)) return value
  return `${num.toFixed(2)}%`
}

// 获取排名徽章样式
const getRankClass = (index: number): string => {
  if (index === 0) return 'rank-gold'
  if (index === 1) return 'rank-silver'
  if (index === 2) return 'rank-bronze'
  return ''
}

// 获取申购状态样式
const getPurchaseStatusClass = (status: string): string => {
  if (status === '开放申购') return 'status-available'
  if (status === '暂停申购') return 'status-unavailable'
  return 'text-secondary'
}

// 获取申购状态文本
const getPurchaseStatusText = (status: string): string => {
  return status || '-'
}

// 加载数据
const loadData = async () => {
  try {
    loading.value = true
    error.value = ''

    const response = await getMoneyFunds()

    if (!response.success) {
      error.value = response.error || '加载失败'
      return
    }

    funds.value = response.data
    dataSource.value = response.source
  } catch (err: any) {
    error.value = err.message || '加载失败'
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  loadData()
})
</script>

<style scoped>
.page-header {
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

.search-card {
  margin-bottom: var(--spacing-lg);
}

.search-input {
  width: 100%;
  padding: var(--spacing-md);
  font-size: 17px;
  border: 1px solid var(--color-border);
  border-radius: 8px;
  background: var(--color-bg-primary);
  color: var(--color-text-primary);
  transition: all var(--transition-base);
}

.search-input:focus {
  outline: none;
  border-color: var(--color-accent);
  box-shadow: 0 0 0 3px rgba(0, 113, 227, 0.1);
}

.table-card {
  overflow: hidden;
}

.table-header {
  padding: var(--spacing-lg);
  border-bottom: 1px solid var(--color-border);
}

.table-info {
  display: flex;
  gap: var(--spacing-lg);
  font-size: 15px;
}

.table-wrapper {
  overflow-x: auto;
}

.data-table {
  width: 100%;
  border-collapse: collapse;
}

.data-table thead {
  background: var(--color-bg-secondary);
  border-bottom: 1px solid var(--color-border);
}

.data-table th {
  padding: var(--spacing-md);
  text-align: left;
  font-weight: 600;
  font-size: 15px;
  color: var(--color-text-secondary);
  white-space: nowrap;
}

.data-table th.number-cell {
  text-align: right;
}

.data-table td {
  padding: var(--spacing-md);
  font-size: 15px;
  border-bottom: 1px solid var(--color-border);
  color: var(--color-text-primary);
}

.data-table td.number-cell {
  text-align: right;
  font-variant-numeric: tabular-nums;
}

.table-row {
  transition: background-color var(--transition-base);
}

.table-row:hover {
  background: var(--color-bg-secondary);
}

.table-row:last-child td {
  border-bottom: none;
}

.rank-cell {
  width: 60px;
}

.rank-badge {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 32px;
  height: 32px;
  border-radius: 50%;
  font-weight: 700;
  font-size: 13px;
  background: var(--color-bg-secondary);
  color: var(--color-text-secondary);
}

.rank-gold {
  background: linear-gradient(135deg, #ffd700, #ffed4e);
  color: #8b6914;
}

.rank-silver {
  background: linear-gradient(135deg, #c0c0c0, #e8e8e8);
  color: #5a5a5a;
}

.rank-bronze {
  background: linear-gradient(135deg, #cd7f32, #e8a87c);
  color: #5a3a1e;
}

.fund-link {
  color: var(--color-accent);
  text-decoration: none;
  transition: opacity var(--transition-base);
}

.fund-link:hover {
  opacity: 0.7;
}

.positive-value {
  color: var(--color-success);
  font-weight: 500;
}

.positive-value.strong {
  font-weight: 700;
  font-size: 17px;
}

.status-available {
  color: var(--color-success);
  font-weight: 500;
}

.status-unavailable {
  color: var(--color-danger);
}

@media (max-width: 734px) {
  .page-title {
    font-size: 24px;
  }

  .page-description {
    font-size: 15px;
  }

  .table-info {
    flex-direction: column;
    gap: var(--spacing-sm);
  }

  .data-table th,
  .data-table td {
    padding: var(--spacing-sm);
    font-size: 13px;
  }

  .rank-badge {
    width: 28px;
    height: 28px;
    font-size: 12px;
  }

  .positive-value.strong {
    font-size: 15px;
  }
}
</style>
