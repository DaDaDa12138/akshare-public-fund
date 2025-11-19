<template>
  <div class="company-detail">
    <div class="container">
      <!-- 返回按钮 -->
      <div class="back-button">
        <el-button @click="goBack" :icon="ArrowLeft">返回列表</el-button>
      </div>

      <!-- 加载状态 -->
      <div v-if="loading" class="loading-card card">
        <el-skeleton :rows="6" animated />
      </div>

      <!-- 错误状态 -->
      <EmptyState
        v-else-if="!loading && !companyInfo"
        title="未找到公司信息"
        description="该基金公司不存在或数据加载失败"
      >
        <template #action>
          <el-button type="primary" @click="goBack">返回列表</el-button>
        </template>
      </EmptyState>

      <!-- 公司详情内容 -->
      <div v-else>
        <!-- 公司基本信息 -->
        <div class="company-header card">
          <div class="company-title">
            <h1>{{ companyName }}</h1>
            <el-tag v-if="companyInfo.成立时间" type="info" size="large">
              成立于 {{ companyInfo.成立时间 }}
            </el-tag>
          </div>
          <div class="company-stats-grid">
            <div class="stat-item">
              <div class="stat-label">管理规模</div>
              <div class="stat-value primary">{{ formatScale(companyInfo.全部管理规模) }}亿元</div>
            </div>
            <div class="stat-item">
              <div class="stat-label">基金数量</div>
              <div class="stat-value">{{ companyInfo.全部基金数 || 0 }}只</div>
            </div>
            <div class="stat-item">
              <div class="stat-label">基金经理</div>
              <div class="stat-value">{{ companyInfo.全部经理数 || 0 }}人</div>
            </div>
            <div class="stat-item">
              <div class="stat-label">更新日期</div>
              <div class="stat-value">{{ companyInfo.更新日期 || '-' }}</div>
            </div>
          </div>
        </div>

        <!-- 历史规模趋势 -->
        <div v-if="historyData && historyData.length > 0" class="history-card card">
          <div class="card-header">
            <h2>
              <el-icon><TrendCharts /></el-icon>
              历史规模趋势
            </h2>
          </div>
          <div class="history-table">
            <el-table :data="historyData" stripe style="width: 100%">
              <el-table-column prop="年份" label="年份" width="120" />
              <el-table-column
                prop="总规模"
                label="总规模（亿元）"
                width="150"
                align="right"
              >
                <template #default="{ row }">
                  <span class="scale-value">{{ formatScale(row.总规模) }}</span>
                </template>
              </el-table-column>
              <el-table-column
                prop="股票型"
                label="股票型（亿元）"
                width="150"
                align="right"
              >
                <template #default="{ row }">
                  {{ formatScale(row.股票型) }}
                </template>
              </el-table-column>
              <el-table-column
                prop="混合型"
                label="混合型（亿元）"
                width="150"
                align="right"
              >
                <template #default="{ row }">
                  {{ formatScale(row.混合型) }}
                </template>
              </el-table-column>
              <el-table-column
                prop="债券型"
                label="债券型（亿元）"
                width="150"
                align="right"
              >
                <template #default="{ row }">
                  {{ formatScale(row.债券型) }}
                </template>
              </el-table-column>
              <el-table-column
                prop="指数型"
                label="指数型（亿元）"
                width="150"
                align="right"
              >
                <template #default="{ row }">
                  {{ formatScale(row.指数型) }}
                </template>
              </el-table-column>
              <el-table-column
                prop="QDII"
                label="QDII（亿元）"
                width="150"
                align="right"
              >
                <template #default="{ row }">
                  {{ formatScale(row.QDII) }}
                </template>
              </el-table-column>
              <el-table-column
                prop="货币型"
                label="货币型（亿元）"
                width="150"
                align="right"
              >
                <template #default="{ row }">
                  {{ formatScale(row.货币型) }}
                </template>
              </el-table-column>
            </el-table>
          </div>
        </div>

        <!-- 无历史数据提示 -->
        <div v-else-if="!loading" class="empty-history card">
          <EmptyState
            title="暂无历史数据"
            description="该基金公司暂无历史规模数据"
          />
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ArrowLeft, TrendCharts } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import axios from 'axios'
import EmptyState from '@/components/EmptyState.vue'

const route = useRoute()
const router = useRouter()

// 数据状态
const loading = ref(false)
const companyInfo = ref<any>(null)
const historyData = ref<any[]>([])

// 公司名称
const companyName = computed(() => {
  return decodeURIComponent(route.params.name as string)
})

// 加载数据
onMounted(() => {
  loadCompanyInfo()
  loadHistoryData()
})

// 加载公司基本信息
const loadCompanyInfo = async () => {
  loading.value = true
  try {
    const response = await axios.get(`/api/fund_company_aum/${companyName.value}`)

    if (response.data.success) {
      companyInfo.value = response.data.data
    } else {
      ElMessage.error(response.data.message || '加载公司信息失败')
    }
  } catch (error: any) {
    console.error('Failed to load company info:', error)
    ElMessage.error('加载公司信息失败: ' + (error.response?.data?.detail || error.message))
  } finally {
    loading.value = false
  }
}

// 加载历史数据
const loadHistoryData = async () => {
  try {
    const response = await axios.get(`/api/fund_company_aum_hist/${companyName.value}`)

    if (response.data.success) {
      historyData.value = response.data.data || []
    }
  } catch (error: any) {
    console.error('Failed to load history data:', error)
  }
}

// 格式化规模
const formatScale = (value: any): string => {
  if (!value || value === 'NaN') return '0.00'
  const num = parseFloat(value)
  if (isNaN(num)) return '0.00'
  return num.toFixed(2)
}

// 返回
const goBack = () => {
  router.push('/company-ranking')
}
</script>

<style scoped>
.company-detail {
  min-height: 100vh;
}

.back-button {
  margin-bottom: var(--spacing-lg);
}

.loading-card {
  padding: var(--spacing-2xl);
}

.company-header {
  padding: var(--spacing-2xl);
  margin-bottom: var(--spacing-lg);
}

.company-title {
  display: flex;
  align-items: center;
  gap: var(--spacing-md);
  margin-bottom: var(--spacing-xl);
  flex-wrap: wrap;
}

.company-title h1 {
  margin: 0;
  font-size: 32px;
  font-weight: 700;
  color: var(--color-text-primary);
}

.company-stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: var(--spacing-xl);
}

.stat-item {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-sm);
}

.stat-label {
  font-size: 14px;
  color: var(--color-text-secondary);
}

.stat-value {
  font-size: 24px;
  font-weight: 700;
  color: var(--color-text-primary);
}

.stat-value.primary {
  color: var(--color-primary);
  font-size: 28px;
}

.history-card,
.empty-history {
  padding: var(--spacing-xl);
}

.card-header {
  margin-bottom: var(--spacing-lg);
}

.card-header h2 {
  display: flex;
  align-items: center;
  gap: var(--spacing-sm);
  margin: 0;
  font-size: 24px;
  font-weight: 700;
}

.history-table {
  overflow-x: auto;
}

.scale-value {
  font-weight: 600;
  color: var(--color-primary);
}

@media (max-width: 734px) {
  .company-title h1 {
    font-size: 24px;
  }

  .company-stats-grid {
    grid-template-columns: 1fr 1fr;
  }

  .stat-value {
    font-size: 20px;
  }

  .stat-value.primary {
    font-size: 24px;
  }

  .card-header h2 {
    font-size: 20px;
  }
}
</style>
