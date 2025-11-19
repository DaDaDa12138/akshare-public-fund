<template>
  <div class="fund-search">
    <div class="container">
      <!-- 标题和搜索 -->
      <div class="search-header">
        <h1>基金搜索</h1>
        <p class="text-secondary">搜索并筛选超过10000+公募基金</p>
      </div>

      <!-- 搜索框 -->
      <div class="search-box card">
        <el-input
          v-model="searchKeyword"
          size="large"
          placeholder="输入基金代码、名称或拼音缩写..."
          clearable
          @input="handleSearch"
        >
          <template #prefix>
            <el-icon><Search /></el-icon>
          </template>
        </el-input>
      </div>

      <!-- 筛选器 -->
      <div class="filter-box card">
        <el-space wrap>
          <span class="filter-label">基金类型：</span>
          <el-radio-group v-model="selectedType" @change="handleFilter">
            <el-radio-button value="">全部</el-radio-button>
            <el-radio-button value="股票型">股票型</el-radio-button>
            <el-radio-button value="混合型">混合型</el-radio-button>
            <el-radio-button value="债券型">债券型</el-radio-button>
            <el-radio-button value="指数型">指数型</el-radio-button>
            <el-radio-button value="QDII">QDII</el-radio-button>
          </el-radio-group>
        </el-space>
      </div>

      <!-- 数据表格 -->
      <div class="table-container card">
        <el-table
          :data="displayData"
          v-loading="loading"
          stripe
          style="width: 100%"
          max-height="600"
          @row-click="handleRowClick"
        >
          <el-table-column prop="基金代码" label="基金代码" width="120" fixed />
          <el-table-column prop="基金简称" label="基金名称" min-width="200" />
          <el-table-column prop="基金类型" label="类型" width="150">
            <template #default="{ row }">
              <el-tag>{{ row.基金类型 || '-' }}</el-tag>
            </template>
          </el-table-column>
          <el-table-column label="操作" width="260" fixed="right">
            <template #default="{ row }">
              <el-button
                :type="favoritesStore.isFavorite(row.基金代码) ? 'warning' : 'default'"
                :icon="favoritesStore.isFavorite(row.基金代码) ? 'StarFilled' : 'Star'"
                size="small"
                @click.stop="toggleFavorite(row)"
                circle
              />
              <el-button
                type="primary"
                size="small"
                @click.stop="viewDetail(row.基金代码)"
              >
                查看详情
              </el-button>
              <el-button
                type="default"
                size="small"
                @click.stop="viewChart(row.基金代码)"
              >
                走势图
              </el-button>
            </template>
          </el-table-column>
        </el-table>

        <!-- 分页 -->
        <div class="pagination">
          <el-pagination
            v-model:current-page="currentPage"
            v-model:page-size="pageSize"
            :page-sizes="[20, 50, 100, 200]"
            :total="filteredData.length"
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
import { useFundStore } from '@/stores/fund'
import { useFavoritesStore } from '@/stores/favorites'
import { Search } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import type { FundInfo } from '@/types/fund'

const router = useRouter()
const fundStore = useFundStore()
const favoritesStore = useFavoritesStore()

// 搜索和筛选
const searchKeyword = ref('')
const selectedType = ref('')
const loading = ref(false)

// 分页
const currentPage = ref(1)
const pageSize = ref(50)

// 加载基金列表
onMounted(async () => {
  loading.value = true
  await fundStore.loadFundList()
  loading.value = false
})

// 筛选后的数据
const filteredData = computed(() => {
  let data = fundStore.fundList

  // 搜索过滤
  if (searchKeyword.value) {
    const keyword = searchKeyword.value.toLowerCase()
    data = data.filter(fund =>
      fund.基金代码.includes(keyword) ||
      fund.基金简称.toLowerCase().includes(keyword) ||
      (fund.拼音缩写 && fund.拼音缩写.toLowerCase().includes(keyword))
    )
  }

  // 类型过滤
  if (selectedType.value) {
    data = data.filter(fund =>
      fund.基金类型 && fund.基金类型.includes(selectedType.value)
    )
  }

  return data
})

// 分页显示的数据
const displayData = computed(() => {
  const start = (currentPage.value - 1) * pageSize.value
  const end = start + pageSize.value
  return filteredData.value.slice(start, end)
})

// 搜索处理
const handleSearch = () => {
  currentPage.value = 1
}

// 筛选处理
const handleFilter = () => {
  currentPage.value = 1
}

// 分页处理
const handleSizeChange = () => {
  currentPage.value = 1
}

const handleCurrentChange = () => {
  // 页码改变时滚动到顶部
  window.scrollTo({ top: 0, behavior: 'smooth' })
}

// 行点击
const handleRowClick = (row: FundInfo) => {
  viewDetail(row.基金代码)
}

// 查看详情
const viewDetail = (code: string) => {
  router.push(`/detail/${code}`)
}

// 查看走势图
const viewChart = (code: string) => {
  fundStore.selectedFund = code
  router.push('/chart')
}

// 切换收藏状态
const toggleFavorite = (fund: FundInfo) => {
  const success = favoritesStore.toggleFavorite(fund.基金代码, fund.基金简称)
  if (success) {
    if (favoritesStore.isFavorite(fund.基金代码)) {
      ElMessage.success(`已添加收藏：${fund.基金简称}`)
    } else {
      ElMessage.info(`已取消收藏：${fund.基金简称}`)
    }
  }
}
</script>

<style scoped>
.fund-search {
  min-height: 100vh;
}

.search-header {
  text-align: center;
  margin-bottom: var(--spacing-xl);
}

.search-header h1 {
  margin-bottom: var(--spacing-sm);
}

.search-box {
  margin-bottom: var(--spacing-lg);
}

.filter-box {
  margin-bottom: var(--spacing-lg);
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: var(--spacing-md);
}

.filter-label {
  font-weight: 500;
  color: var(--color-text-primary);
}

.table-container {
  overflow: hidden;
}

.pagination {
  display: flex;
  justify-content: center;
  padding: var(--spacing-lg) 0;
}

/* 表格行悬停效果 */
:deep(.el-table__row) {
  cursor: pointer;
  transition: all var(--transition-base);
}

:deep(.el-table__row:hover) {
  transform: scale(1.002);
}

@media (max-width: 734px) {
  .search-header h1 {
    font-size: 28px;
  }

  .filter-box {
    flex-direction: column;
    align-items: flex-start;
  }
}
</style>
