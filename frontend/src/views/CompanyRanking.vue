<template>
  <div class="company-ranking">
    <div class="container">
      <!-- 页面标题 -->
      <div class="page-header">
        <h1 class="page-title">基金公司规模排行榜</h1>
        <p class="page-description">查看全国基金公司管理规模、基金数量及基金经理数量</p>
      </div>

      <!-- 统计卡片 -->
      <div v-if="!loading && stats" class="stats-grid">
        <div class="stat-card card">
          <div class="stat-icon">
            <el-icon :size="32"><Grid /></el-icon>
          </div>
          <div class="stat-content">
            <div class="stat-value">{{ stats.total_companies?.toLocaleString() || 0 }}</div>
            <div class="stat-label">基金公司总数</div>
          </div>
        </div>

        <div class="stat-card card highlight">
          <div class="stat-icon primary">
            <el-icon :size="32"><TrendCharts /></el-icon>
          </div>
          <div class="stat-content">
            <div class="stat-value">{{ formatScale(getTotalScale()) }}亿</div>
            <div class="stat-label">市场总规模</div>
          </div>
        </div>

        <div class="stat-card card">
          <div class="stat-icon success">
            <el-icon :size="32"><Trophy /></el-icon>
          </div>
          <div class="stat-content">
            <div class="stat-value">{{ getTopCompanyScale() }}亿</div>
            <div class="stat-label">TOP1公司规模</div>
          </div>
        </div>

        <div class="stat-card card">
          <div class="stat-icon warning">
            <el-icon :size="32"><Medal /></el-icon>
          </div>
          <div class="stat-content">
            <div class="stat-value">{{ getTop10Ratio() }}%</div>
            <div class="stat-label">TOP10占比</div>
          </div>
        </div>
      </div>

      <!-- 规模分布图表 -->
      <div v-if="!loading && stats && stats.scale_distribution" class="chart-card card">
        <div class="chart-header">
          <h3>
            <el-icon><PieChart /></el-icon>
            基金公司规模分布
          </h3>
        </div>
        <div class="chart-content">
          <div class="distribution-grid">
            <div
              v-for="item in stats.scale_distribution"
              :key="item.scale_level"
              class="distribution-item"
            >
              <div class="distribution-bar">
                <div
                  class="distribution-fill"
                  :style="{ width: getDistributionPercent(item.count) + '%' }"
                ></div>
              </div>
              <div class="distribution-info">
                <span class="distribution-label">{{ item.scale_level }}</span>
                <span class="distribution-value">{{ item.count }} 家</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- TOP 10 公司卡片 -->
      <div v-if="!loading && stats && stats.top_10_companies" class="top10-section">
        <h2 class="section-title">
          <el-icon><Star /></el-icon>
          TOP 10 基金公司
        </h2>
        <div class="top10-grid">
          <div
            v-for="(company, index) in stats.top_10_companies"
            :key="company.基金公司"
            class="top10-card card"
            :class="{ highlight: index < 3 }"
            @click="viewCompanyDetail(company.基金公司)"
          >
            <div class="top10-rank" :class="getRankClass(index)">
              {{ index + 1 }}
            </div>
            <div class="top10-content">
              <div class="top10-name">{{ company.基金公司 }}</div>
              <div class="top10-stats">
                <div class="top10-stat">
                  <span class="stat-label">管理规模</span>
                  <span class="stat-value primary">{{ formatScale(company.全部管理规模) }}亿</span>
                </div>
                <div class="top10-stat">
                  <span class="stat-label">基金数</span>
                  <span class="stat-value">{{ company.全部基金数 }}只</span>
                </div>
                <div class="top10-stat">
                  <span class="stat-label">基金经理</span>
                  <span class="stat-value">{{ company.全部经理数 }}人</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- 筛选工具栏 -->
      <div v-if="companyData.length > 0" class="toolbar card">
        <div class="toolbar-left">
          <span class="data-stats">
            共 <strong>{{ totalRecords }}</strong> 家基金公司
          </span>
          <el-select v-model="sortBy" placeholder="排序方式" style="width: 180px">
            <el-option label="管理规模" value="全部管理规模" />
            <el-option label="基金数量" value="全部基金数" />
            <el-option label="基金经理数" value="全部经理数" />
            <el-option label="成立时间" value="成立时间" />
          </el-select>
        </div>
        <div class="toolbar-right">
          <el-input
            v-model="searchQuery"
            placeholder="搜索基金公司名称"
            style="width: 280px"
            clearable
            :prefix-icon="Search"
          />
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
      <div class="table-card card" v-loading="loading">
        <EmptyState
          v-if="!loading && displayData.length === 0"
          title="暂无数据"
          description="没有找到符合条件的基金公司"
        />

        <el-table
          v-else
          :data="displayData"
          stripe
          style="width: 100%"
          max-height="700"
          @row-click="handleRowClick"
          :default-sort="{ prop: sortBy, order: 'descending' }"
        >
          <el-table-column
            type="index"
            label="排名"
            width="80"
            fixed
            align="center"
            :index="indexMethod"
          >
            <template #default="{ $index }">
              <div class="rank-badge" :class="getRankBadgeClass($index)">
                {{ $index + 1 }}
              </div>
            </template>
          </el-table-column>

          <el-table-column prop="基金公司" label="基金公司" min-width="200" fixed>
            <template #default="{ row }">
              <div class="company-cell">
                <span class="company-name">{{ row.基金公司 }}</span>
                <el-tag v-if="row.成立时间" size="small" type="info" class="company-tag">
                  {{ row.成立时间 }}
                </el-tag>
              </div>
            </template>
          </el-table-column>

          <el-table-column
            prop="全部管理规模"
            label="管理规模（亿元）"
            width="180"
            sortable
            align="right"
          >
            <template #default="{ row }">
              <span class="scale-value">{{ formatScale(row.全部管理规模) }}</span>
            </template>
          </el-table-column>

          <el-table-column
            prop="全部基金数"
            label="基金数量（只）"
            width="150"
            sortable
            align="right"
          >
            <template #default="{ row }">
              <span class="fund-count">{{ row.全部基金数 || 0 }}</span>
            </template>
          </el-table-column>

          <el-table-column
            prop="全部经理数"
            label="基金经理（人）"
            width="150"
            sortable
            align="right"
          >
            <template #default="{ row }">
              <span class="manager-count">{{ row.全部经理数 || 0 }}</span>
            </template>
          </el-table-column>

          <el-table-column prop="更新日期" label="更新日期" width="120" />

          <el-table-column label="操作" width="120" fixed="right">
            <template #default="{ row }">
              <el-button
                type="primary"
                size="small"
                @click.stop="viewCompanyDetail(row.基金公司)"
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
            :page-sizes="[20, 50, 100, 200]"
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
  Grid,
  TrendCharts,
  Trophy,
  Medal,
  PieChart,
  Star,
  Search,
  Download,
  Document
} from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import axios from 'axios'
import EmptyState from '@/components/EmptyState.vue'
import { exportCompanyRanking } from '@/api/fund'

const router = useRouter()

// 数据状态
const loading = ref(false)
const exporting = ref(false)
const companyData = ref<any[]>([])
const stats = ref<any>(null)
const totalRecords = ref(0)

// 筛选排序
const sortBy = ref('全部管理规模')
const searchQuery = ref('')

// 分页
const currentPage = ref(1)
const pageSize = ref(50)

// 筛选和搜索后的数据
const filteredData = computed(() => {
  let data = [...companyData.value]

  // 搜索过滤
  if (searchQuery.value.trim()) {
    const query = searchQuery.value.toLowerCase()
    data = data.filter(item =>
      item.基金公司?.toLowerCase().includes(query)
    )
  }

  // 排序
  data.sort((a, b) => {
    const valueA = a[sortBy.value]
    const valueB = b[sortBy.value]

    if (sortBy.value === '成立时间') {
      // 日期排序（从旧到新）
      return valueA < valueB ? -1 : 1
    } else {
      // 数值排序（从大到小）
      return (valueB || 0) - (valueA || 0)
    }
  })

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

// 加载基金公司列表
const loadData = async () => {
  loading.value = true
  try {
    const response = await axios.get('/api/fund_company_aum', {
      params: {
        limit: 1000,
        offset: 0,
        sort_by: sortBy.value
      }
    })

    if (response.data.success) {
      companyData.value = response.data.data || []
      totalRecords.value = response.data.total || 0
    } else {
      ElMessage.error(response.data.message || '加载失败')
    }
  } catch (error: any) {
    console.error('Failed to load company ranking data:', error)
    ElMessage.error('加载数据失败: ' + (error.response?.data?.detail || error.message))
  } finally {
    loading.value = false
  }
}

// 加载统计数据
const loadStats = async () => {
  try {
    const response = await axios.get('/api/fund_company_stats')
    if (response.data.success) {
      stats.value = response.data.data
    }
  } catch (error: any) {
    console.error('Failed to load stats:', error)
  }
}

// 计算市场总规模
const getTotalScale = (): number => {
  if (!stats.value?.top_10_companies) return 0
  return companyData.value.reduce((sum, item) => sum + (item.全部管理规模 || 0), 0)
}

// 获取TOP1公司规模
const getTopCompanyScale = (): string => {
  if (!stats.value?.top_10_companies || stats.value.top_10_companies.length === 0) return '0'
  return formatScale(stats.value.top_10_companies[0].全部管理规模)
}

// 计算TOP10占比
const getTop10Ratio = (): string => {
  if (!stats.value?.top_10_companies) return '0.00'
  const top10Total = stats.value.top_10_companies.reduce(
    (sum: number, item: any) => sum + (item.全部管理规模 || 0),
    0
  )
  const total = getTotalScale()
  if (total === 0) return '0.00'
  return ((top10Total / total) * 100).toFixed(2)
}

// 获取分布百分比
const getDistributionPercent = (count: number): number => {
  if (!stats.value?.total_companies) return 0
  return (count / stats.value.total_companies) * 100
}

// 格式化规模
const formatScale = (value: any): string => {
  if (!value || value === 'NaN') return '0.00'
  const num = parseFloat(value)
  if (isNaN(num)) return '0.00'
  return num.toFixed(2)
}

// 获取排名样式类
const getRankClass = (index: number): string => {
  if (index === 0) return 'rank-gold'
  if (index === 1) return 'rank-silver'
  if (index === 2) return 'rank-bronze'
  return ''
}

// 获取表格排名徽章样式
const getRankBadgeClass = (index: number): string => {
  const globalIndex = (currentPage.value - 1) * pageSize.value + index
  if (globalIndex === 0) return 'rank-1'
  if (globalIndex === 1) return 'rank-2'
  if (globalIndex === 2) return 'rank-3'
  return ''
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
  viewCompanyDetail(row.基金公司)
}

// 查看公司详情
const viewCompanyDetail = (companyName: string) => {
  router.push(`/company/${encodeURIComponent(companyName)}`)
}

// 导出数据
const handleExport = async (format: 'csv' | 'excel') => {
  if (companyData.value.length === 0) {
    ElMessage.warning('暂无数据可导出')
    return
  }

  try {
    exporting.value = true
    const result = await exportCompanyRanking(format)
    if (result.success) {
      ElMessage.success('导出成功')
    } else {
      ElMessage.error(result.message || '导出失败')
    }
  } catch (err: any) {
    console.error('[公司排行] 导出失败:', err)
    ElMessage.error(err.message || '导出失败')
  } finally {
    exporting.value = false
  }
}
</script>

<style scoped>
.company-ranking {
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
  transition: transform var(--transition-base), box-shadow var(--transition-base);
}

.stat-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.stat-card.highlight {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
}

.stat-card.highlight .stat-label,
.stat-card.highlight .stat-value {
  color: white;
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

.stat-icon.primary {
  background: rgba(255, 255, 255, 0.2);
  color: white;
}

.stat-icon.success {
  background: rgba(103, 194, 58, 0.1);
  color: var(--color-success);
}

.stat-icon.warning {
  background: rgba(230, 162, 60, 0.1);
  color: var(--color-warning);
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

/* 规模分布图表 */
.chart-card {
  margin-bottom: var(--spacing-xl);
}

.chart-header {
  padding: var(--spacing-lg);
  border-bottom: 1px solid var(--color-border);
}

.chart-header h3 {
  display: flex;
  align-items: center;
  gap: var(--spacing-sm);
  margin: 0;
  font-size: 18px;
  font-weight: 600;
}

.chart-content {
  padding: var(--spacing-lg);
}

.distribution-grid {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-md);
}

.distribution-item {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-xs);
}

.distribution-bar {
  height: 32px;
  background: var(--color-bg-secondary);
  border-radius: 16px;
  overflow: hidden;
}

.distribution-fill {
  height: 100%;
  background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
  transition: width 0.6s ease;
}

.distribution-info {
  display: flex;
  justify-content: space-between;
  font-size: 14px;
}

.distribution-label {
  color: var(--color-text-secondary);
}

.distribution-value {
  color: var(--color-primary);
  font-weight: 600;
}

/* TOP 10 区域 */
.top10-section {
  margin-bottom: var(--spacing-xl);
}

.section-title {
  display: flex;
  align-items: center;
  gap: var(--spacing-sm);
  font-size: 24px;
  font-weight: 700;
  margin-bottom: var(--spacing-lg);
}

.top10-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
  gap: var(--spacing-lg);
}

.top10-card {
  display: flex;
  gap: var(--spacing-md);
  padding: var(--spacing-lg);
  cursor: pointer;
  transition: transform var(--transition-base), box-shadow var(--transition-base);
}

.top10-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 6px 16px rgba(0, 0, 0, 0.12);
}

.top10-card.highlight {
  background: linear-gradient(135deg, rgba(102, 126, 234, 0.05) 0%, rgba(118, 75, 162, 0.05) 100%);
  border: 2px solid rgba(102, 126, 234, 0.3);
}

.top10-rank {
  width: 48px;
  height: 48px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 50%;
  font-size: 20px;
  font-weight: 700;
  background: var(--color-bg-secondary);
  color: var(--color-text-secondary);
  flex-shrink: 0;
}

.top10-rank.rank-gold {
  background: linear-gradient(135deg, #ffd700, #ffed4e);
  color: #8b6914;
}

.top10-rank.rank-silver {
  background: linear-gradient(135deg, #c0c0c0, #e8e8e8);
  color: #5a5a5a;
}

.top10-rank.rank-bronze {
  background: linear-gradient(135deg, #cd7f32, #e8a87c);
  color: #5a3a1e;
}

.top10-content {
  flex: 1;
  min-width: 0;
}

.top10-name {
  font-size: 16px;
  font-weight: 600;
  color: var(--color-text-primary);
  margin-bottom: var(--spacing-sm);
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.top10-stats {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-xs);
}

.top10-stat {
  display: flex;
  justify-content: space-between;
  font-size: 13px;
}

.top10-stat .stat-label {
  color: var(--color-text-tertiary);
}

.top10-stat .stat-value {
  font-weight: 600;
  color: var(--color-text-primary);
}

.top10-stat .stat-value.primary {
  color: var(--color-primary);
  font-size: 14px;
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
  gap: var(--spacing-md);
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

.toolbar-right {
  display: flex;
  gap: var(--spacing-sm);
}

/* 表格 */
.table-card {
  overflow: hidden;
}

.company-cell {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-xs);
}

.company-name {
  font-weight: 600;
  color: var(--color-text-primary);
}

.company-tag {
  align-self: flex-start;
}

.scale-value {
  font-weight: 600;
  color: var(--color-primary);
  font-size: 16px;
}

.fund-count,
.manager-count {
  font-weight: 500;
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

  .top10-grid {
    grid-template-columns: 1fr;
  }

  .section-title {
    font-size: 20px;
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

  .toolbar-right :deep(.el-select) {
    width: 100% !important;
  }
}
</style>
