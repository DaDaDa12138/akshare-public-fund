<template>
  <div class="dividend-rank">
    <div class="container">
      <!-- 标题 -->
      <div class="ranking-header">
        <h1>📈 基金分红排行榜</h1>
        <p class="text-secondary">查看累计分红最多的基金</p>
      </div>

      <!-- 排序选择器 -->
      <div class="sort-panel card">
        <div class="left-controls">
          <div class="sort-options">
            <label>排序方式:</label>
            <el-radio-group v-model="sortBy" @change="loadData">
              <el-radio-button value="累计分红">按累计分红</el-radio-button>
              <el-radio-button value="累计次数">按分红次数</el-radio-button>
            </el-radio-group>
          </div>
          <div class="limit-selector">
            <label>显示数量:</label>
            <el-select v-model="limit" @change="loadData" style="width: 120px">
              <el-option label="前 50 名" :value="50" />
              <el-option label="前 100 名" :value="100" />
              <el-option label="前 200 名" :value="200" />
              <el-option label="全部" :value="10000" />
            </el-select>
          </div>
        </div>
        <div class="export-buttons">
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

      <!-- 加载状态 -->
      <div v-if="loading" class="loading-container card">
        <el-icon class="is-loading"><Loading /></el-icon>
        <p>加载中...</p>
      </div>

      <!-- 错误提示 -->
      <div v-else-if="error" class="error-container card">
        <el-icon><WarningFilled /></el-icon>
        <p>{{ error }}</p>
        <el-button type="primary" @click="loadData">重试</el-button>
      </div>

      <!-- 排行榜表格 -->
      <div v-else class="ranking-table card">
        <el-table
          :data="rankData"
          stripe
          style="width: 100%"
          :row-class-name="getRowClass"
          @row-click="handleRowClick"
        >
          <el-table-column prop="序号" label="排名" width="80" align="center">
            <template #default="{ row }">
              <div class="rank-badge" :class="getRankClass(row.序号)">
                {{ row.序号 }}
              </div>
            </template>
          </el-table-column>

          <el-table-column prop="基金代码" label="基金代码" width="100" align="center" />

          <el-table-column prop="基金简称" label="基金名称" min-width="200" show-overflow-tooltip>
            <template #default="{ row }">
              <router-link :to="`/detail/${row.基金代码}`" class="fund-link">
                {{ row.基金简称 }}
              </router-link>
            </template>
          </el-table-column>

          <el-table-column prop="累计分红" label="累计分红(元)" width="140" align="right" sortable>
            <template #default="{ row }">
              <span class="dividend-amount">{{ row.累计分红.toFixed(4) }}</span>
            </template>
          </el-table-column>

          <el-table-column prop="累计次数" label="分红次数" width="100" align="center" sortable />

          <el-table-column prop="成立日期" label="成立日期" width="120" align="center" />

          <el-table-column label="操作" width="100" align="center" fixed="right">
            <template #default="{ row }">
              <el-button
                type="primary"
                size="small"
                @click.stop="goToDetail(row.基金代码)"
              >
                详情
              </el-button>
            </template>
          </el-table-column>
        </el-table>

        <!-- 数据说明 -->
        <div class="data-info">
          <p>
            <el-icon><InfoFilled /></el-icon>
            数据来源: 东方财富网 | 共 {{ rankData.length }} 只基金 | 排序方式: {{ sortBy }}
          </p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { getFundDividendRank, exportDividendRank, type FundDividendRankData } from '@/api/fund'
import { Loading, WarningFilled, InfoFilled, Download, Document } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'

const router = useRouter()

// 响应式数据
const rankData = ref<FundDividendRankData[]>([])
const loading = ref(true)
const error = ref('')
const sortBy = ref('累计分红')
const limit = ref(100)
const exporting = ref(false)

// 加载数据
const loadData = async () => {
  try {
    loading.value = true
    error.value = ''

    const response = await getFundDividendRank(limit.value, sortBy.value)

    if (!response.success) {
      error.value = response.error || '加载失败'
      return
    }

    rankData.value = response.data

    console.log(`[分红排行] 成功加载 ${rankData.value.length} 条数据`)
  } catch (err: any) {
    error.value = err.message || '网络错误'
    console.error('[分红排行] 加载失败:', err)
  } finally {
    loading.value = false
  }
}

// 获取排名样式
const getRankClass = (rank: number) => {
  if (rank === 1) return 'rank-1'
  if (rank === 2) return 'rank-2'
  if (rank === 3) return 'rank-3'
  return ''
}

// 获取行样式
const getRowClass = ({ row }: { row: FundDividendRankData }) => {
  return row.序号 <= 3 ? 'top-three-row' : ''
}

// 行点击事件
const handleRowClick = (row: FundDividendRankData) => {
  router.push(`/detail/${row.基金代码}`)
}

// 跳转详情
const goToDetail = (code: string) => {
  router.push(`/detail/${code}`)
}

// 导出数据
const handleExport = async (format: 'csv' | 'excel') => {
  try {
    exporting.value = true
    const result = await exportDividendRank(format)
    if (result.success) {
      ElMessage.success('导出成功')
    } else {
      ElMessage.error(result.message || '导出失败')
    }
  } catch (err: any) {
    console.error('[分红排行] 导出失败:', err)
    ElMessage.error(err.message || '导出失败')
  } finally {
    exporting.value = false
  }
}

// 初始化
onMounted(() => {
  loadData()
})
</script>

<style scoped>
.dividend-rank {
  min-height: calc(100vh - 200px);
}

.ranking-header {
  text-align: center;
  margin-bottom: var(--spacing-2xl);
}

.ranking-header h1 {
  font-size: 32px;
  font-weight: 600;
  margin-bottom: var(--spacing-sm);
  background: linear-gradient(90deg, var(--color-text-primary), var(--color-accent));
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.sort-panel {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: var(--spacing-lg);
  margin-bottom: var(--spacing-lg);
  gap: var(--spacing-lg);
}

.left-controls {
  display: flex;
  align-items: center;
  gap: var(--spacing-xl);
  flex-wrap: wrap;
}

.export-buttons {
  display: flex;
  align-items: center;
}

.sort-options,
.limit-selector {
  display: flex;
  align-items: center;
  gap: var(--spacing-md);
}

.sort-options label,
.limit-selector label {
  font-size: 15px;
  font-weight: 500;
  color: var(--color-text-secondary);
}

.loading-container,
.error-container {
  padding: var(--spacing-3xl);
  text-align: center;
}

.loading-container .el-icon,
.error-container .el-icon {
  font-size: 48px;
  color: var(--color-accent);
  margin-bottom: var(--spacing-md);
}

.error-container .el-icon {
  color: var(--color-danger);
}

.ranking-table {
  padding: var(--spacing-lg);
}

/* 排名徽章 */
.rank-badge {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 36px;
  height: 36px;
  border-radius: 50%;
  font-weight: 600;
  font-size: 15px;
  background: var(--color-bg-secondary);
  color: var(--color-text-primary);
}

.rank-badge.rank-1 {
  background: linear-gradient(135deg, #FFD700, #FFA500);
  color: #fff;
  box-shadow: 0 2px 8px rgba(255, 215, 0, 0.3);
}

.rank-badge.rank-2 {
  background: linear-gradient(135deg, #C0C0C0, #A8A8A8);
  color: #fff;
  box-shadow: 0 2px 8px rgba(192, 192, 192, 0.3);
}

.rank-badge.rank-3 {
  background: linear-gradient(135deg, #CD7F32, #A85A32);
  color: #fff;
  box-shadow: 0 2px 8px rgba(205, 127, 50, 0.3);
}

/* 前三名行高亮 */
:deep(.top-three-row) {
  background-color: var(--color-bg-secondary);
  font-weight: 500;
}

/* 基金链接 */
.fund-link {
  color: var(--color-text-primary);
  text-decoration: none;
  transition: color var(--transition-base);
}

.fund-link:hover {
  color: var(--color-accent);
}

/* 分红金额 */
.dividend-amount {
  font-weight: 600;
  color: var(--color-success);
}

/* 数据说明 */
.data-info {
  margin-top: var(--spacing-lg);
  padding-top: var(--spacing-lg);
  border-top: 1px solid var(--color-border);
  text-align: center;
}

.data-info p {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: var(--spacing-sm);
  color: var(--color-text-secondary);
  font-size: 15px;
}

/* 表格行可点击样式 */
:deep(.el-table__row) {
  cursor: pointer;
  transition: background-color var(--transition-base);
}

:deep(.el-table__row:hover) {
  background-color: var(--color-bg-secondary) !important;
}

/* 移动端适配 */
@media (max-width: 734px) {
  .ranking-header h1 {
    font-size: 24px;
  }

  .sort-panel {
    flex-direction: column;
    align-items: stretch;
  }

  .left-controls {
    flex-direction: column;
    align-items: stretch;
    gap: var(--spacing-lg);
  }

  .export-buttons {
    width: 100%;
  }

  .export-buttons .el-dropdown {
    width: 100%;
  }

  .export-buttons .el-button {
    width: 100%;
  }

  .sort-options,
  .limit-selector {
    flex-direction: column;
    align-items: flex-start;
  }

  .el-table {
    font-size: 14px;
  }
}
</style>
