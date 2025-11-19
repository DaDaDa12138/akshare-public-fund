<template>
  <div class="fund-ranking">
    <div class="container">
      <!-- 标题 -->
      <div class="ranking-header">
        <h1>基金排行榜</h1>
        <p class="text-secondary">按不同时期收益率查看基金排名</p>
      </div>

      <!-- 分类标签 -->
      <div class="category-tabs card">
        <el-radio-group v-model="category" size="large" @change="handleCategoryChange">
          <el-radio-button value="全部">全部基金</el-radio-button>
          <el-radio-button value="股票型">股票型</el-radio-button>
          <el-radio-button value="混合型">混合型</el-radio-button>
          <el-radio-button value="债券型">债券型</el-radio-button>
          <el-radio-button value="指数型">指数型</el-radio-button>
          <el-radio-button value="QDII">QDII</el-radio-button>
        </el-radio-group>
      </div>

      <!-- 高级筛选器 -->
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
            <el-form :model="filterForm" label-position="left" label-width="80px">
              <el-row :gutter="20">
                <!-- 晨星评级筛选 -->
                <el-col :xs="24" :sm="12" :md="8">
                  <el-form-item label="晨星评级">
                    <el-select v-model="filterForm.ratingMin" placeholder="最低评级" clearable>
                      <el-option label="不限" :value="null" />
                      <el-option label="★★★★★ 5星" :value="5" />
                      <el-option label="★★★★ 4星" :value="4" />
                      <el-option label="★★★ 3星" :value="3" />
                      <el-option label="★★ 2星" :value="2" />
                      <el-option label="★ 1星" :value="1" />
                    </el-select>
                  </el-form-item>
                </el-col>

                <!-- 近1月收益率 -->
                <el-col :xs="24" :sm="12" :md="8">
                  <el-form-item label="近1月">
                    <div class="range-input">
                      <el-input-number
                        v-model="filterForm.return1mMin"
                        :controls="false"
                        placeholder="最低%"
                        :precision="2"
                        size="default"
                      />
                      <span class="range-separator">~</span>
                      <el-input-number
                        v-model="filterForm.return1mMax"
                        :controls="false"
                        placeholder="最高%"
                        :precision="2"
                        size="default"
                      />
                    </div>
                  </el-form-item>
                </el-col>

                <!-- 近3月收益率 -->
                <el-col :xs="24" :sm="12" :md="8">
                  <el-form-item label="近3月">
                    <div class="range-input">
                      <el-input-number
                        v-model="filterForm.return3mMin"
                        :controls="false"
                        placeholder="最低%"
                        :precision="2"
                        size="default"
                      />
                      <span class="range-separator">~</span>
                      <el-input-number
                        v-model="filterForm.return3mMax"
                        :controls="false"
                        placeholder="最高%"
                        :precision="2"
                        size="default"
                      />
                    </div>
                  </el-form-item>
                </el-col>

                <!-- 近6月收益率 -->
                <el-col :xs="24" :sm="12" :md="8">
                  <el-form-item label="近6月">
                    <div class="range-input">
                      <el-input-number
                        v-model="filterForm.return6mMin"
                        :controls="false"
                        placeholder="最低%"
                        :precision="2"
                        size="default"
                      />
                      <span class="range-separator">~</span>
                      <el-input-number
                        v-model="filterForm.return6mMax"
                        :controls="false"
                        placeholder="最高%"
                        :precision="2"
                        size="default"
                      />
                    </div>
                  </el-form-item>
                </el-col>

                <!-- 近1年收益率 -->
                <el-col :xs="24" :sm="12" :md="8">
                  <el-form-item label="近1年">
                    <div class="range-input">
                      <el-input-number
                        v-model="filterForm.return1yMin"
                        :controls="false"
                        placeholder="最低%"
                        :precision="2"
                        size="default"
                      />
                      <span class="range-separator">~</span>
                      <el-input-number
                        v-model="filterForm.return1yMax"
                        :controls="false"
                        placeholder="最高%"
                        :precision="2"
                        size="default"
                      />
                    </div>
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

      <!-- 数据可视化 -->
      <FundCharts v-if="rankData.length > 0" :data="rankData" />

      <!-- 工具栏 -->
      <div v-if="rankData.length > 0" class="toolbar card">
        <div class="toolbar-left">
          <span class="data-stats">
            共 <strong>{{ totalFunds }}</strong> 个基金
            <span v-if="activeFiltersCount > 0">
              ，筛选后 <strong>{{ filteredCount }}</strong> 个
            </span>
          </span>
        </div>
        <div class="toolbar-right">
          <el-dropdown @command="handleExport">
            <el-button type="primary" :loading="exporting">
              <el-icon class="el-icon--left"><Download /></el-icon>
              导出数据
            </el-button>
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item command="csv">
                  <el-icon><Document /></el-icon>
                  导出为 CSV
                </el-dropdown-item>
                <el-dropdown-item command="excel">
                  <el-icon><Document /></el-icon>
                  导出为 Excel
                </el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
        </div>
      </div>

      <!-- 数据表格 -->
      <div class="ranking-table card" v-loading="loading">
        <el-table
          :data="displayData"
          stripe
          style="width: 100%"
          max-height="700"
          @row-click="handleRowClick"
          :default-sort="{ prop: '近1月', order: 'descending' }"
        >
          <el-table-column
            type="index"
            label="排名"
            width="80"
            fixed
            align="center"
          >
            <template #default="{ $index }">
              <div class="rank-badge" :class="getRankClass($index)">
                {{ $index + 1 }}
              </div>
            </template>
          </el-table-column>

          <el-table-column prop="基金代码" label="基金代码" width="120" fixed />
          <el-table-column prop="基金简称" label="基金名称" min-width="200" fixed />

          <el-table-column label="单位净值" width="180">
            <template #default="{ row }">
              <div>
                <div class="net-value">{{ getNetValue(row) }}</div>
                <div class="net-date text-secondary">{{ getNetDate(row) }}</div>
              </div>
            </template>
          </el-table-column>

          <el-table-column
            prop="日增长率"
            label="日涨幅"
            width="100"
            sortable
            align="right"
          >
            <template #default="{ row }">
              <span :class="getChangeClass(row.日增长率)">
                {{ formatPercent(row.日增长率) }}
              </span>
            </template>
          </el-table-column>

          <el-table-column
            prop="近1周"
            label="近1周"
            width="100"
            sortable
            align="right"
          >
            <template #default="{ row }">
              <span :class="getChangeClass(row.近1周)">
                {{ formatPercent(row.近1周) }}
              </span>
            </template>
          </el-table-column>

          <el-table-column
            prop="近1月"
            label="近1月"
            width="100"
            sortable
            align="right"
          >
            <template #default="{ row }">
              <span :class="getChangeClass(row.近1月)">
                {{ formatPercent(row.近1月) }}
              </span>
            </template>
          </el-table-column>

          <el-table-column
            prop="近3月"
            label="近3月"
            width="100"
            sortable
            align="right"
          >
            <template #default="{ row }">
              <span :class="getChangeClass(row.近3月)">
                {{ formatPercent(row.近3月) }}
              </span>
            </template>
          </el-table-column>

          <el-table-column
            prop="近6月"
            label="近6月"
            width="100"
            sortable
            align="right"
          >
            <template #default="{ row }">
              <span :class="getChangeClass(row.近6月)">
                {{ formatPercent(row.近6月) }}
              </span>
            </template>
          </el-table-column>

          <el-table-column
            prop="近1年"
            label="近1年"
            width="100"
            sortable
            align="right"
          >
            <template #default="{ row }">
              <span :class="getChangeClass(row.近1年)">
                {{ formatPercent(row.近1年) }}
              </span>
            </template>
          </el-table-column>

          <el-table-column
            prop="今年来"
            label="今年来"
            width="100"
            sortable
            align="right"
          >
            <template #default="{ row }">
              <span :class="getChangeClass(row.今年来)">
                {{ formatPercent(row.今年来) }}
              </span>
            </template>
          </el-table-column>

          <el-table-column
            prop="成立来"
            label="成立来"
            width="100"
            sortable
            align="right"
          >
            <template #default="{ row }">
              <span :class="getChangeClass(row.成立来)">
                {{ formatPercent(row.成立来) }}
              </span>
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
        <div class="pagination">
          <el-pagination
            v-model:current-page="currentPage"
            v-model:page-size="pageSize"
            :page-sizes="[50, 100, 200]"
            :total="totalCount"
            layout="total, sizes, prev, pager, next"
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
import { Filter, ArrowDown, Download, Document } from '@element-plus/icons-vue'
import { getFundRank, exportFundRanking } from '@/api/fund'
import { ElMessage } from 'element-plus'
import axios from 'axios'
import type { FundRankData } from '@/types/fund'
import FundCharts from '@/components/FundCharts.vue'

const router = useRouter()

// 状态
const category = ref('全部')
const loading = ref(false)
const exporting = ref(false)
const rankData = ref<FundRankData[]>([])

// 筛选器状态
const filterExpanded = ref(false)
const filterForm = ref({
  ratingMin: null as number | null,
  return1mMin: null as number | null,
  return1mMax: null as number | null,
  return3mMin: null as number | null,
  return3mMax: null as number | null,
  return6mMin: null as number | null,
  return6mMax: null as number | null,
  return1yMin: null as number | null,
  return1yMax: null as number | null
})

// 统计信息
const totalFunds = ref(0) // 原始数据总数
const filteredCount = ref(0) // 筛选后数量

// 计算活跃筛选条件数量
const activeFiltersCount = computed(() => {
  let count = 0
  if (filterForm.value.ratingMin !== null) count++
  if (filterForm.value.return1mMin !== null || filterForm.value.return1mMax !== null) count++
  if (filterForm.value.return3mMin !== null || filterForm.value.return3mMax !== null) count++
  if (filterForm.value.return6mMin !== null || filterForm.value.return6mMax !== null) count++
  if (filterForm.value.return1yMin !== null || filterForm.value.return1yMax !== null) count++
  return count
})

// 分页
const currentPage = ref(1)
const pageSize = ref(50)

const totalCount = computed(() => rankData.value.length)
const displayData = computed(() => {
  const start = (currentPage.value - 1) * pageSize.value
  const end = start + pageSize.value
  return rankData.value.slice(start, end)
})

// 加载数据
onMounted(() => {
  loadRankData()
})

// 加载排行数据(带筛选)
const loadRankData = async () => {
  loading.value = true
  try {
    // 统一使用筛选API（即使没有筛选条件，也能获取基金类型字段）
    const response = await axios.post('/api/fund_rank_filtered', {
      symbol: category.value,
      rating_min: filterForm.value.ratingMin,
      return_1m_min: filterForm.value.return1mMin,
      return_1m_max: filterForm.value.return1mMax,
      return_3m_min: filterForm.value.return3mMin,
      return_3m_max: filterForm.value.return3mMax,
      return_6m_min: filterForm.value.return6mMin,
      return_6m_max: filterForm.value.return6mMax,
      return_1y_min: filterForm.value.return1yMin,
      return_1y_max: filterForm.value.return1yMax
    })

    if (response.data.success) {
      rankData.value = response.data.data
      totalFunds.value = response.data.total
      filteredCount.value = response.data.filtered

      // 如果有筛选条件，显示筛选结果消息
      if (activeFiltersCount.value > 0) {
        ElMessage.success(`筛选完成: 从 ${totalFunds.value} 个基金中筛选出 ${filteredCount.value} 个`)
      }
    }
  } catch (error: any) {
    console.error('Failed to load ranking data:', error)
    ElMessage.error('加载数据失败: ' + (error.response?.data?.detail || error.message))
  } finally {
    loading.value = false
  }
}

// 分类切换
const handleCategoryChange = () => {
  currentPage.value = 1
  loadRankData()
}

// 应用筛选
const handleApplyFilter = () => {
  currentPage.value = 1
  loadRankData()
}

// 重置筛选
const handleResetFilter = () => {
  filterForm.value = {
    ratingMin: null,
    return1mMin: null,
    return1mMax: null,
    return3mMin: null,
    return3mMax: null,
    return6mMin: null,
    return6mMax: null,
    return1yMin: null,
    return1yMax: null
  }
  currentPage.value = 1
  loadRankData()
}

// 分页处理
const handleSizeChange = () => {
  currentPage.value = 1
}

const handleCurrentChange = () => {
  window.scrollTo({ top: 0, behavior: 'smooth' })
}

// 行点击
const handleRowClick = (row: FundRankData) => {
  viewDetail(row.基金代码)
}

// 查看详情
const viewDetail = (code: string) => {
  router.push(`/detail/${code}`)
}

// 获取净值
const getNetValue = (row: FundRankData) => {
  return row['单位净值'] || row['单位净值-单位净值'] || '-'
}

// 获取净值日期
const getNetDate = (row: FundRankData) => {
  return row['日期'] || row['单位净值-日期'] || ''
}

// 格式化百分比
const formatPercent = (value: any) => {
  if (!value || value === '-' || value === '---') return '-'
  const num = parseFloat(value)
  if (isNaN(num)) return '-'
  return num >= 0 ? `+${num}%` : `${num}%`
}

// 获取涨跌颜色类
const getChangeClass = (value: any) => {
  if (!value || value === '-' || value === '---') return ''
  const num = parseFloat(value)
  if (isNaN(num)) return ''
  return num >= 0 ? 'text-success' : 'text-danger'
}

// 获取排名样式类
const getRankClass = (index: number) => {
  if (index === 0) return 'rank-1'
  if (index === 1) return 'rank-2'
  if (index === 2) return 'rank-3'
  return ''
}

// 导出数据
const handleExport = async (format: 'csv' | 'excel') => {
  if (rankData.value.length === 0) {
    ElMessage.warning('暂无数据可导出')
    return
  }

  try {
    exporting.value = true

    // 构建筛选条件对象
    const filters: any = {
      symbol: category.value
    }

    // 添加评级筛选
    if (filterForm.value.ratingMin !== null) {
      filters.rating_min = filterForm.value.ratingMin
    }

    // 添加收益率范围筛选
    if (filterForm.value.return1mMin !== null) filters.return_1m_min = filterForm.value.return1mMin
    if (filterForm.value.return1mMax !== null) filters.return_1m_max = filterForm.value.return1mMax
    if (filterForm.value.return3mMin !== null) filters.return_3m_min = filterForm.value.return3mMin
    if (filterForm.value.return3mMax !== null) filters.return_3m_max = filterForm.value.return3mMax
    if (filterForm.value.return6mMin !== null) filters.return_6m_min = filterForm.value.return6mMin
    if (filterForm.value.return6mMax !== null) filters.return_6m_max = filterForm.value.return6mMax
    if (filterForm.value.return1yMin !== null) filters.return_1y_min = filterForm.value.return1yMin
    if (filterForm.value.return1yMax !== null) filters.return_1y_max = filterForm.value.return1yMax

    const result = await exportFundRanking(filters, format)
    if (result.success) {
      ElMessage.success('导出成功')
    } else {
      ElMessage.error(result.message || '导出失败')
    }
  } catch (err: any) {
    console.error('[基金排行] 导出失败:', err)
    ElMessage.error(err.message || '导出失败')
  } finally {
    exporting.value = false
  }
}
</script>

<style scoped>
.fund-ranking {
  min-height: 100vh;
}

.ranking-header {
  text-align: center;
  margin-bottom: var(--spacing-xl);
}

.ranking-header h1 {
  margin-bottom: var(--spacing-sm);
}

.category-tabs {
  margin-bottom: var(--spacing-lg);
  display: flex;
  justify-content: center;
}

.ranking-table {
  overflow: hidden;
}

.rank-badge {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 32px;
  height: 32px;
  border-radius: 50%;
  font-weight: 600;
  font-size: 14px;
  background-color: var(--color-bg-tertiary);
  color: var(--color-text-secondary);
}

.rank-badge.rank-1 {
  background: linear-gradient(135deg, #FFD700, #FFA500);
  color: white;
  box-shadow: 0 2px 8px rgba(255, 215, 0, 0.3);
}

.rank-badge.rank-2 {
  background: linear-gradient(135deg, #C0C0C0, #A9A9A9);
  color: white;
  box-shadow: 0 2px 8px rgba(192, 192, 192, 0.3);
}

.rank-badge.rank-3 {
  background: linear-gradient(135deg, #CD7F32, #B87333);
  color: white;
  box-shadow: 0 2px 8px rgba(205, 127, 50, 0.3);
}

.net-value {
  font-weight: 600;
  color: var(--color-text-primary);
}

.net-date {
  font-size: 12px;
  margin-top: 2px;
}

.text-success {
  color: var(--color-success);
  font-weight: 500;
}

.text-danger {
  color: var(--color-danger);
  font-weight: 500;
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

/* 筛选面板样式 */
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

.range-input {
  display: flex;
  align-items: center;
  gap: var(--spacing-sm);
}

.range-input :deep(.el-input-number) {
  flex: 1;
}

.range-separator {
  color: var(--color-text-secondary);
  font-weight: 500;
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
}

.toolbar-left {
  display: flex;
  align-items: center;
  gap: var(--spacing-md);
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

.toolbar-right {
  display: flex;
  gap: var(--spacing-sm);
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
  .category-tabs {
    overflow-x: auto;
  }

  .ranking-header h1 {
    font-size: 28px;
  }

  .filter-content {
    padding: var(--spacing-md);
  }

  .range-input {
    flex-direction: column;
    align-items: stretch;
  }

  .range-separator {
    text-align: center;
  }
}
</style>
