<template>
  <div class="fund-purchase-status">
    <div class="container">
      <!-- 页面标题 -->
      <div class="page-header">
        <h1 class="page-title">基金申购赎回状态</h1>
        <p class="page-description">查询全市场基金的申购赎回状态，支持多条件筛选</p>
      </div>

      <!-- 统计卡片 -->
      <div v-if="!loading && stats" class="stats-grid">
        <div class="stat-card card">
          <div class="stat-icon">
            <el-icon :size="32"><Grid /></el-icon>
          </div>
          <div class="stat-content">
            <div class="stat-value">{{ stats.total_funds?.toLocaleString() || 0 }}</div>
            <div class="stat-label">总基金数</div>
          </div>
        </div>

        <div class="stat-card card">
          <div class="stat-icon success">
            <el-icon :size="32"><Select /></el-icon>
          </div>
          <div class="stat-content">
            <div class="stat-value">{{ getStatusCount('开放申购') }}</div>
            <div class="stat-label">开放申购</div>
          </div>
        </div>

        <div class="stat-card card">
          <div class="stat-icon warning">
            <el-icon :size="32"><Warning /></el-icon>
          </div>
          <div class="stat-content">
            <div class="stat-value">{{ getStatusCount('限大额') }}</div>
            <div class="stat-label">限大额申购</div>
          </div>
        </div>

        <div class="stat-card card">
          <div class="stat-icon danger">
            <el-icon :size="32"><CircleClose /></el-icon>
          </div>
          <div class="stat-content">
            <div class="stat-value">{{ getStatusCount('暂停申购') }}</div>
            <div class="stat-label">暂停申购</div>
          </div>
        </div>
      </div>

      <!-- 筛选面板 -->
      <div class="filter-panel card">
        <div class="filter-header" @click="filterExpanded = !filterExpanded">
          <h3>
            <el-icon><Filter /></el-icon>
            高级筛选
            <el-tag v-if="activeFiltersCount > 0" type="primary" size="small" round>
              {{ activeFiltersCount }} 个条件
            </el-tag>
          </h3>
          <el-icon class="expand-icon" :class="{ expanded: filterExpanded }">
            <ArrowDown />
          </el-icon>
        </div>

        <transition name="filter-expand">
          <div v-show="filterExpanded" class="filter-content">
            <el-form :model="filterForm" label-position="left" label-width="100px">
              <el-row :gutter="20">
                <!-- 申购状态筛选 -->
                <el-col :xs="24" :sm="12" :md="8">
                  <el-form-item label="申购状态">
                    <el-select v-model="filterForm.purchaseStatus" placeholder="选择申购状态" clearable>
                      <el-option label="全部" value="" />
                      <el-option label="开放申购" value="开放申购" />
                      <el-option label="限大额" value="限大额" />
                      <el-option label="暂停申购" value="暂停申购" />
                    </el-select>
                  </el-form-item>
                </el-col>

                <!-- 赎回状态筛选 -->
                <el-col :xs="24" :sm="12" :md="8">
                  <el-form-item label="赎回状态">
                    <el-select v-model="filterForm.redeemStatus" placeholder="选择赎回状态" clearable>
                      <el-option label="全部" value="" />
                      <el-option label="开放赎回" value="开放赎回" />
                      <el-option label="暂停赎回" value="暂停赎回" />
                    </el-select>
                  </el-form-item>
                </el-col>

                <!-- 基金类型筛选 -->
                <el-col :xs="24" :sm="12" :md="8">
                  <el-form-item label="基金类型">
                    <el-select v-model="filterForm.fundType" placeholder="选择基金类型" clearable filterable>
                      <el-option label="全部" value="" />
                      <el-option
                        v-for="type in fundTypes"
                        :key="type"
                        :label="type"
                        :value="type"
                      />
                    </el-select>
                  </el-form-item>
                </el-col>
              </el-row>

              <div class="filter-actions">
                <el-button @click="handleResetFilter">重置</el-button>
                <el-button type="primary" @click="handleApplyFilter">应用筛选</el-button>
              </div>
            </el-form>
          </div>
        </transition>
      </div>

      <!-- 工具栏 -->
      <div v-if="purchaseData.length > 0" class="toolbar card">
        <div class="toolbar-left">
          <span class="data-stats">
            共 <strong>{{ totalRecords }}</strong> 条记录
            <span v-if="activeFiltersCount > 0">
              ，当前显示 <strong>{{ purchaseData.length }}</strong> 条
            </span>
          </span>
          <span v-if="dataSource" class="data-source">
            数据来源: {{ dataSource === 'database' ? '数据库' : 'API' }}
          </span>
        </div>
        <div class="toolbar-right">
          <el-input
            v-model="searchQuery"
            placeholder="搜索基金代码或名称"
            style="width: 280px"
            clearable
            :prefix-icon="Search"
          />
        </div>
      </div>

      <!-- 数据表格 -->
      <div class="table-card card" v-loading="loading">
        <EmptyState
          v-if="!loading && displayData.length === 0"
          title="暂无数据"
          description="没有找到符合条件的基金，请尝试调整筛选条件"
        />

        <el-table
          v-else
          :data="displayData"
          stripe
          style="width: 100%"
          max-height="700"
          @row-click="handleRowClick"
        >
          <el-table-column
            type="index"
            label="序号"
            width="80"
            fixed
            align="center"
            :index="indexMethod"
          />

          <el-table-column prop="基金代码" label="基金代码" width="120" fixed>
            <template #default="{ row }">
              <router-link :to="`/detail/${row.基金代码}`" class="fund-link">
                {{ row.基金代码 }}
              </router-link>
            </template>
          </el-table-column>

          <el-table-column prop="基金简称" label="基金名称" min-width="200" fixed>
            <template #default="{ row }">
              <router-link :to="`/detail/${row.基金代码}`" class="fund-link">
                {{ row.基金简称 }}
              </router-link>
            </template>
          </el-table-column>

          <el-table-column prop="基金类型" label="基金类型" width="150" />

          <el-table-column label="最新净值/万份收益" width="180">
            <template #default="{ row }">
              <div>
                <div class="net-value">{{ row.最新净值万份收益 || '-' }}</div>
                <div class="net-date text-secondary">{{ row.最新净值万份收益报告时间 || '-' }}</div>
              </div>
            </template>
          </el-table-column>

          <el-table-column prop="申购状态" label="申购状态" width="120" align="center">
            <template #default="{ row }">
              <el-tag :type="getPurchaseStatusType(row.申购状态)" size="small">
                {{ row.申购状态 || '-' }}
              </el-tag>
            </template>
          </el-table-column>

          <el-table-column prop="赎回状态" label="赎回状态" width="120" align="center">
            <template #default="{ row }">
              <el-tag :type="getRedeemStatusType(row.赎回状态)" size="small">
                {{ row.赎回状态 || '-' }}
              </el-tag>
            </template>
          </el-table-column>

          <el-table-column prop="购买起点" label="购买起点" width="120" align="right">
            <template #default="{ row }">
              <span v-if="row.购买起点 && row.购买起点 !== 'NaN'">
                {{ formatAmount(row.购买起点) }}
              </span>
              <span v-else class="text-secondary">-</span>
            </template>
          </el-table-column>

          <el-table-column prop="日累计限定金额" label="日累计限额" width="150" align="right">
            <template #default="{ row }">
              <span v-if="row.日累计限定金额 && row.日累计限定金额 !== 'NaN'">
                {{ formatAmount(row.日累计限定金额) }}
              </span>
              <span v-else class="text-secondary">-</span>
            </template>
          </el-table-column>

          <el-table-column prop="手续费" label="手续费" width="100" align="right">
            <template #default="{ row }">
              <span v-if="row.手续费 && row.手续费 !== 'NaN'">
                {{ row.手续费 }}%
              </span>
              <span v-else class="text-secondary">-</span>
            </template>
          </el-table-column>

          <el-table-column prop="下一开放日" label="下一开放日" width="120">
            <template #default="{ row }">
              <span v-if="row.下一开放日 && row.下一开放日 !== 'NaT'">
                {{ row.下一开放日 }}
              </span>
              <span v-else class="text-secondary">-</span>
            </template>
          </el-table-column>

          <el-table-column label="操作" width="120" fixed="right">
            <template #default="{ row }">
              <el-button
                type="primary"
                size="small"
                @click.stop="viewDetail(row.基金代码)"
              >
                查看详情
              </el-button>
            </template>
          </el-table-column>
        </el-table>

        <!-- 分页 -->
        <div v-if="displayData.length > 0" class="pagination">
          <el-pagination
            v-model:current-page="currentPage"
            v-model:page-size="pageSize"
            :page-sizes="[50, 100, 200, 500]"
            :total="totalCount"
            layout="total, sizes, prev, pager, next, jumper"
            @size-change="handleSizeChange"
            @current-change="handleCurrentChange"
          />
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import {
  Filter,
  ArrowDown,
  Grid,
  Select,
  Warning,
  CircleClose,
  Search
} from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import axios from 'axios'
import EmptyState from '@/components/EmptyState.vue'

const router = useRouter()

// 数据状态
const loading = ref(false)
const purchaseData = ref<any[]>([])
const stats = ref<any>(null)
const dataSource = ref('')
const totalRecords = ref(0)

// 筛选器状态
const filterExpanded = ref(false)
const filterForm = ref({
  purchaseStatus: '',
  redeemStatus: '',
  fundType: ''
})

// 基金类型列表（从统计数据中提取）
const fundTypes = ref<string[]>([])

// 搜索
const searchQuery = ref('')

// 分页
const currentPage = ref(1)
const pageSize = ref(100)

// 计算活跃筛选条件数量
const activeFiltersCount = computed(() => {
  let count = 0
  if (filterForm.value.purchaseStatus) count++
  if (filterForm.value.redeemStatus) count++
  if (filterForm.value.fundType) count++
  return count
})

// 筛选和搜索后的数据
const filteredData = computed(() => {
  let data = purchaseData.value

  // 搜索过滤
  if (searchQuery.value.trim()) {
    const query = searchQuery.value.toLowerCase()
    data = data.filter(item =>
      item.基金代码?.toLowerCase().includes(query) ||
      item.基金简称?.toLowerCase().includes(query)
    )
  }

  return data
})

// 分页后的数据
const totalCount = computed(() => filteredData.value.length)
const displayData = computed(() => {
  const start = (currentPage.value - 1) * pageSize.value
  const end = start + pageSize.value
  return filteredData.value.slice(start, end)
})

// 序号计算（考虑分页）
const indexMethod = (index: number) => {
  return (currentPage.value - 1) * pageSize.value + index + 1
}

// 加载数据
onMounted(() => {
  loadData()
  loadStats()
})

// 加载申购赎回状态列表
const loadData = async () => {
  loading.value = true
  try {
    const params: any = {
      limit: 10000, // 加载所有数据，前端分页
      offset: 0
    }

    if (filterForm.value.purchaseStatus) {
      params.purchase_status = filterForm.value.purchaseStatus
    }
    if (filterForm.value.redeemStatus) {
      params.redeem_status = filterForm.value.redeemStatus
    }
    if (filterForm.value.fundType) {
      params.fund_type = filterForm.value.fundType
    }

    const response = await axios.get('/api/fund_purchase_status', { params })

    if (response.data.success) {
      purchaseData.value = response.data.data || []
      totalRecords.value = response.data.total || 0
      dataSource.value = response.data.source || ''

      if (activeFiltersCount.value > 0) {
        ElMessage.success(`筛选完成: 找到 ${purchaseData.value.length} 条符合条件的记录`)
      }
    } else {
      ElMessage.error(response.data.message || '加载失败')
    }
  } catch (error: any) {
    console.error('Failed to load purchase status data:', error)
    ElMessage.error('加载数据失败: ' + (error.response?.data?.detail || error.message))
  } finally {
    loading.value = false
  }
}

// 加载统计数据
const loadStats = async () => {
  try {
    const response = await axios.get('/api/fund_purchase_status_stats')
    if (response.data.success) {
      stats.value = response.data.data

      // 提取基金类型列表
      if (stats.value.fund_type_distribution) {
        fundTypes.value = stats.value.fund_type_distribution
          .map((item: any) => item.基金类型)
          .filter((type: string) => type && type !== 'null')
      }
    }
  } catch (error: any) {
    console.error('Failed to load stats:', error)
  }
}

// 获取特定状态的统计数量
const getStatusCount = (status: string): number => {
  if (!stats.value?.purchase_status_distribution) return 0
  const item = stats.value.purchase_status_distribution.find(
    (s: any) => s.申购状态 === status
  )
  return item?.count || 0
}

// 应用筛选
const handleApplyFilter = () => {
  currentPage.value = 1
  loadData()
}

// 重置筛选
const handleResetFilter = () => {
  filterForm.value = {
    purchaseStatus: '',
    redeemStatus: '',
    fundType: ''
  }
  currentPage.value = 1
  loadData()
}

// 分页处理
const handleSizeChange = () => {
  currentPage.value = 1
}

const handleCurrentChange = () => {
  window.scrollTo({ top: 0, behavior: 'smooth' })
}

// 行点击
const handleRowClick = (row: any) => {
  viewDetail(row.基金代码)
}

// 查看详情
const viewDetail = (code: string) => {
  router.push(`/detail/${code}`)
}

// 获取申购状态类型
const getPurchaseStatusType = (status: string) => {
  if (status === '开放申购') return 'success'
  if (status === '限大额') return 'warning'
  if (status === '暂停申购') return 'danger'
  return 'info'
}

// 获取赎回状态类型
const getRedeemStatusType = (status: string) => {
  if (status === '开放赎回') return 'success'
  if (status === '暂停赎回') return 'danger'
  return 'info'
}

// 格式化金额
const formatAmount = (value: any): string => {
  if (!value || value === 'NaN') return '-'
  const num = parseFloat(value)
  if (isNaN(num)) return '-'

  if (num >= 100000000) {
    return `${(num / 100000000).toFixed(2)}亿`
  } else if (num >= 10000) {
    return `${(num / 10000).toFixed(2)}万`
  } else {
    return num.toFixed(2)
  }
}
</script>

<style scoped>
.fund-purchase-status {
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

/* 筛选面板 */
.filter-panel {
  margin-bottom: var(--spacing-lg);
}

.filter-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: var(--spacing-md);
  cursor: pointer;
  user-select: none;
  transition: background-color var(--transition-base);
}

.filter-header:hover {
  background-color: var(--color-bg-tertiary);
}

.filter-header h3 {
  display: flex;
  align-items: center;
  gap: var(--spacing-sm);
  margin: 0;
  font-size: 17px;
  font-weight: 600;
}

.expand-icon {
  transition: transform var(--transition-base);
}

.expand-icon.expanded {
  transform: rotate(180deg);
}

.filter-content {
  padding: var(--spacing-lg);
  border-top: 1px solid var(--color-border);
}

.filter-actions {
  display: flex;
  justify-content: flex-end;
  gap: var(--spacing-md);
  margin-top: var(--spacing-lg);
  padding-top: var(--spacing-lg);
  border-top: 1px solid var(--color-border);
}

/* 工具栏 */
.toolbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: var(--spacing-md) var(--spacing-lg);
  margin-bottom: var(--spacing-lg);
  gap: var(--spacing-md);
  flex-wrap: wrap;
}

.toolbar-left {
  display: flex;
  align-items: center;
  gap: var(--spacing-lg);
  flex-wrap: wrap;
}

.data-stats {
  color: var(--color-text-secondary);
  font-size: 14px;
}

.data-stats strong {
  color: var(--color-primary);
  font-weight: 600;
  margin: 0 4px;
}

.data-source {
  color: var(--color-text-tertiary);
  font-size: 13px;
}

.toolbar-right {
  display: flex;
  gap: var(--spacing-sm);
}

/* 表格 */
.table-card {
  overflow: hidden;
}

.fund-link {
  color: var(--color-accent);
  text-decoration: none;
  transition: opacity var(--transition-base);
}

.fund-link:hover {
  opacity: 0.7;
}

.net-value {
  font-weight: 600;
  color: var(--color-text-primary);
}

.net-date {
  font-size: 12px;
  margin-top: 2px;
}

.pagination {
  display: flex;
  justify-content: center;
  padding: var(--spacing-lg) 0;
}

:deep(.el-table__row) {
  cursor: pointer;
  transition: all var(--transition-base);
}

:deep(.el-table__row:hover) {
  transform: scale(1.001);
}

/* 筛选展开动画 */
.filter-expand-enter-active,
.filter-expand-leave-active {
  transition: all 0.3s ease;
  max-height: 500px;
  overflow: hidden;
}

.filter-expand-enter-from,
.filter-expand-leave-to {
  max-height: 0;
  opacity: 0;
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

  .stat-card {
    padding: var(--spacing-md);
  }

  .stat-value {
    font-size: 24px;
  }

  .toolbar {
    flex-direction: column;
    align-items: stretch;
  }

  .toolbar-left {
    flex-direction: column;
    align-items: flex-start;
    gap: var(--spacing-sm);
  }

  .toolbar-right {
    width: 100%;
  }

  .toolbar-right :deep(.el-input) {
    width: 100% !important;
  }
}
</style>
