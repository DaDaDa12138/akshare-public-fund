<template>
  <div class="data-admin">
    <div class="container">
      <!-- 页面标题 -->
      <div class="page-header">
        <h1>数据管理</h1>
        <p class="text-secondary">查看数据状态并手动触发更新</p>
      </div>

      <!-- 数据统计卡片 -->
      <div class="stats-section">
        <h3 class="section-title">数据统计</h3>
        <el-row :gutter="20" v-loading="loading">
          <!-- 估值数据 -->
          <el-col :xs="24" :sm="8">
            <div class="stat-card card">
              <div class="card-icon estimation">
                <el-icon :size="32"><TrendCharts /></el-icon>
              </div>
              <div class="card-content">
                <div class="card-title">实时估值</div>
                <div class="card-value">{{ dataStatus.estimation?.total || 0 }} 条</div>
                <div class="card-footer text-secondary">
                  最后更新: {{ formatTime(dataStatus.estimation?.last_update) }}
                </div>
              </div>
              <el-button
                type="primary"
                :loading="updating.estimation"
                @click="updateEstimation"
                class="update-btn"
              >
                {{ updating.estimation ? '更新中...' : '立即更新' }}
              </el-button>
            </div>
          </el-col>

          <!-- 分红数据 -->
          <el-col :xs="24" :sm="8">
            <div class="stat-card card">
              <div class="card-icon dividend">
                <el-icon :size="32"><Money /></el-icon>
              </div>
              <div class="card-content">
                <div class="card-title">基金分红</div>
                <div class="card-value">{{ dataStatus.dividend?.total || 0 }} 条</div>
                <div class="card-subtitle">
                  覆盖 {{ dataStatus.dividend?.fund_count || 0 }} 个基金
                </div>
                <div class="card-footer text-secondary">
                  最后更新: {{ formatTime(dataStatus.dividend?.last_update) }}
                </div>
              </div>
              <el-button
                type="success"
                :loading="updating.dividend"
                @click="updateDividend"
                class="update-btn"
              >
                {{ updating.dividend ? '更新中...' : '立即更新' }}
              </el-button>
            </div>
          </el-col>

          <!-- 评级数据 -->
          <el-col :xs="24" :sm="8">
            <div class="stat-card card">
              <div class="card-icon rating">
                <el-icon :size="32"><Star /></el-icon>
              </div>
              <div class="card-content">
                <div class="card-title">基金评级</div>
                <div class="card-value">{{ dataStatus.rating?.total || 0 }} 条</div>
                <div class="card-footer text-secondary">
                  最后更新: {{ formatTime(dataStatus.rating?.last_update) }}
                </div>
              </div>
              <el-button
                type="warning"
                :loading="updating.rating"
                @click="updateRating"
                class="update-btn"
              >
                {{ updating.rating ? '更新中...' : '立即更新' }}
              </el-button>
            </div>
          </el-col>
        </el-row>
      </div>

      <!-- 定时任务状态 -->
      <div class="scheduler-section">
        <h3 class="section-title">定时任务状态</h3>
        <div class="scheduler-card card" v-loading="schedulerLoading">
          <div v-if="schedulerStatus.running" class="scheduler-running">
            <el-tag type="success" size="large">
              <el-icon><CircleCheck /></el-icon>
              调度器运行中
            </el-tag>
          </div>
          <div v-else class="scheduler-stopped">
            <el-tag type="danger" size="large">
              <el-icon><CircleClose /></el-icon>
              调度器已停止
            </el-tag>
          </div>

          <el-table
            v-if="schedulerStatus.jobs && schedulerStatus.jobs.length > 0"
            :data="schedulerStatus.jobs"
            stripe
            style="width: 100%; margin-top: 20px"
          >
            <el-table-column prop="name" label="任务名称" width="250">
              <template #default="{ row }">
                <span class="job-name">{{ getJobDisplayName(row.name) }}</span>
              </template>
            </el-table-column>
            <el-table-column prop="trigger" label="触发规则" min-width="300" />
            <el-table-column label="下次执行时间" width="200">
              <template #default="{ row }">
                <el-tag v-if="row.next_run_time" type="info">
                  {{ formatScheduledTime(row.next_run_time) }}
                </el-tag>
                <el-tag v-else type="warning">未调度</el-tag>
              </template>
            </el-table-column>
          </el-table>

          <div v-else class="no-jobs text-secondary">
            暂无定时任务
          </div>
        </div>
      </div>

      <!-- 缓存管理 -->
      <div class="cache-section">
        <h3 class="section-title">缓存管理</h3>
        <div class="cache-card card" v-loading="cacheLoading">
          <div class="cache-header">
            <div class="cache-info">
              <el-icon :size="24" color="#409EFF"><DataAnalysis /></el-icon>
              <div>
                <div class="cache-title">内存缓存</div>
                <div class="cache-subtitle text-secondary">
                  缓存有效期: 10分钟 | 当前缓存项: {{ cacheStatus.total_entries || 0 }}
                </div>
              </div>
            </div>
            <el-button type="danger" plain @click="clearCache" :loading="clearingCache">
              清空缓存
            </el-button>
          </div>

          <el-table
            v-if="cacheStatus.entries && cacheStatus.entries.length > 0"
            :data="cacheStatus.entries"
            stripe
            style="width: 100%; margin-top: 20px"
          >
            <el-table-column prop="key" label="缓存键" width="200" />
            <el-table-column label="数据量" width="120">
              <template #default="{ row }">
                {{ row.data_size }} 条
              </template>
            </el-table-column>
            <el-table-column label="创建时间" width="180">
              <template #default="{ row }">
                {{ formatCacheTime(row.created_at) }}
              </template>
            </el-table-column>
            <el-table-column label="过期时间" width="180">
              <template #default="{ row }">
                <el-tag :type="getCacheExpiryType(row.expires_at)">
                  {{ formatCacheTime(row.expires_at) }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column label="剩余时间">
              <template #default="{ row }">
                {{ getRemainingTime(row.expires_at) }}
              </template>
            </el-table-column>
          </el-table>

          <div v-else class="no-cache text-secondary">
            暂无缓存数据
          </div>
        </div>
      </div>

      <!-- 操作说明 -->
      <div class="tips-section card">
        <h3 class="section-title">使用说明</h3>
        <el-timeline>
          <el-timeline-item timestamp="提示 1" placement="top">
            <strong>实时估值</strong>数据每个交易日自动更新2次（10:00和15:00）
          </el-timeline-item>
          <el-timeline-item timestamp="提示 2" placement="top">
            <strong>基金分红</strong>和<strong>基金评级</strong>数据每周日凌晨自动更新
          </el-timeline-item>
          <el-timeline-item timestamp="提示 3" placement="top">
            点击"立即更新"按钮可手动触发数据更新，更新过程在后台执行，请稍后刷新查看结果
          </el-timeline-item>
          <el-timeline-item timestamp="提示 4" placement="top">
            分红和评级数据更新可能需要1-2分钟，请耐心等待
          </el-timeline-item>
          <el-timeline-item timestamp="提示 5" placement="top">
            <strong>内存缓存</strong>用于优化基金排行数据查询性能，自动过期后会重新从API获取最新数据
          </el-timeline-item>
        </el-timeline>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { TrendCharts, Money, Star, CircleCheck, CircleClose, DataAnalysis } from '@element-plus/icons-vue'
import axios from 'axios'

// 数据状态
const loading = ref(false)
const schedulerLoading = ref(false)
const dataStatus = ref<any>({
  estimation: null,
  dividend: null,
  rating: null
})

// 定时任务状态
const schedulerStatus = ref<any>({
  running: false,
  jobs: []
})

// 缓存状态
const cacheLoading = ref(false)
const clearingCache = ref(false)
const cacheStatus = ref<any>({
  total_entries: 0,
  entries: []
})

// 更新状态
const updating = ref({
  estimation: false,
  dividend: false,
  rating: false
})

// 加载数据状态
const loadDataStatus = async () => {
  loading.value = true
  try {
    const response = await axios.get('/api/admin/data_status')
    if (response.data.success) {
      dataStatus.value = response.data.data
    }
  } catch (error: any) {
    console.error('获取数据状态失败:', error)
    ElMessage.error('获取数据状态失败: ' + (error.response?.data?.detail || error.message))
  } finally {
    loading.value = false
  }
}

// 加载调度器状态
const loadSchedulerStatus = async () => {
  schedulerLoading.value = true
  try {
    const response = await axios.get('/api/admin/scheduler_status')
    if (response.data.success) {
      schedulerStatus.value = response.data.data
    }
  } catch (error: any) {
    console.error('获取调度器状态失败:', error)
    ElMessage.error('获取调度器状态失败: ' + (error.response?.data?.detail || error.message))
  } finally {
    schedulerLoading.value = false
  }
}

// 手动更新估值数据
const updateEstimation = async () => {
  updating.value.estimation = true
  try {
    const response = await axios.post('/api/admin/update_estimation')
    if (response.data.success) {
      ElMessage.success(response.data.message)
      // 10秒后刷新数据状态
      setTimeout(() => {
        loadDataStatus()
      }, 10000)
    }
  } catch (error: any) {
    console.error('更新估值数据失败:', error)
    ElMessage.error('更新失败: ' + (error.response?.data?.detail || error.message))
  } finally {
    updating.value.estimation = false
  }
}

// 手动更新分红数据
const updateDividend = async () => {
  updating.value.dividend = true
  try {
    const response = await axios.post('/api/admin/update_dividend')
    if (response.data.success) {
      ElMessage.success(response.data.message)
      // 60秒后刷新数据状态（分红数据更新需要较长时间）
      setTimeout(() => {
        loadDataStatus()
      }, 60000)
    }
  } catch (error: any) {
    console.error('更新分红数据失败:', error)
    ElMessage.error('更新失败: ' + (error.response?.data?.detail || error.message))
  } finally {
    updating.value.dividend = false
  }
}

// 手动更新评级数据
const updateRating = async () => {
  updating.value.rating = true
  try {
    const response = await axios.post('/api/admin/update_rating')
    if (response.data.success) {
      ElMessage.success(response.data.message)
      // 60秒后刷新数据状态（评级数据更新需要较长时间）
      setTimeout(() => {
        loadDataStatus()
      }, 60000)
    }
  } catch (error: any) {
    console.error('更新评级数据失败:', error)
    ElMessage.error('更新失败: ' + (error.response?.data?.detail || error.message))
  } finally {
    updating.value.rating = false
  }
}

// 格式化时间
const formatTime = (timeStr: string | null) => {
  if (!timeStr) return '暂无数据'
  return timeStr.replace('T', ' ').substring(0, 19)
}

// 格式化调度时间
const formatScheduledTime = (isoStr: string | null) => {
  if (!isoStr) return '-'
  const date = new Date(isoStr)
  return date.toLocaleString('zh-CN', {
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit'
  })
}

// 获取任务显示名称
const getJobDisplayName = (funcName: string) => {
  const nameMap: Record<string, string> = {
    'update_fund_estimation': '更新基金实时估值',
    'update_fund_dividend': '更新基金分红数据',
    'update_fund_rating': '更新基金评级数据'
  }
  return nameMap[funcName] || funcName
}

// 加载缓存状态
const loadCacheStatus = async () => {
  cacheLoading.value = true
  try {
    const response = await axios.get('/api/admin/cache_status')
    if (response.data.success) {
      cacheStatus.value = response.data.data
    }
  } catch (error: any) {
    console.error('获取缓存状态失败:', error)
    ElMessage.error('获取缓存状态失败: ' + (error.response?.data?.detail || error.message))
  } finally {
    cacheLoading.value = false
  }
}

// 清空缓存
const clearCache = async () => {
  clearingCache.value = true
  try {
    const response = await axios.post('/api/admin/clear_cache')
    if (response.data.success) {
      ElMessage.success(response.data.message)
      loadCacheStatus() // 刷新缓存状态
    }
  } catch (error: any) {
    console.error('清空缓存失败:', error)
    ElMessage.error('清空缓存失败: ' + (error.response?.data?.detail || error.message))
  } finally {
    clearingCache.value = false
  }
}

// 格式化缓存时间
const formatCacheTime = (isoStr: string | null) => {
  if (!isoStr) return '-'
  const date = new Date(isoStr)
  return date.toLocaleString('zh-CN', {
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit'
  })
}

// 获取缓存过期状态标签类型
const getCacheExpiryType = (expiresAt: string) => {
  const now = new Date()
  const expiry = new Date(expiresAt)
  const diff = expiry.getTime() - now.getTime()
  const minutes = diff / 1000 / 60

  if (minutes < 2) return 'danger'
  if (minutes < 5) return 'warning'
  return 'success'
}

// 获取剩余时间
const getRemainingTime = (expiresAt: string) => {
  const now = new Date()
  const expiry = new Date(expiresAt)
  const diff = expiry.getTime() - now.getTime()

  if (diff < 0) return '已过期'

  const minutes = Math.floor(diff / 1000 / 60)
  const seconds = Math.floor((diff / 1000) % 60)

  return `${minutes}分${seconds}秒`
}

// 页面加载时获取数据
onMounted(() => {
  loadDataStatus()
  loadSchedulerStatus()
  loadCacheStatus()
})
</script>

<style scoped>
.data-admin {
  min-height: 100vh;
  padding: var(--spacing-lg);
}

.page-header {
  text-align: center;
  margin-bottom: var(--spacing-xl);
}

.page-header h1 {
  font-size: 28px;
  font-weight: 600;
  color: var(--color-text-primary);
  margin-bottom: var(--spacing-sm);
}

.section-title {
  font-size: 20px;
  font-weight: 600;
  margin-bottom: var(--spacing-lg);
  padding-bottom: var(--spacing-sm);
  border-bottom: 2px solid var(--color-border);
}

.stats-section {
  margin-bottom: var(--spacing-xl);
}

.stat-card {
  padding: var(--spacing-lg);
  position: relative;
  display: flex;
  flex-direction: column;
  gap: var(--spacing-md);
  min-height: 220px;
  transition: transform var(--transition-base);
}

.stat-card:hover {
  transform: translateY(-4px);
}

.card-icon {
  width: 60px;
  height: 60px;
  border-radius: var(--radius-lg);
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
}

.card-icon.estimation {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.card-icon.dividend {
  background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
}

.card-icon.rating {
  background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
}

.card-content {
  flex: 1;
}

.card-title {
  font-size: 15px;
  color: var(--color-text-secondary);
  margin-bottom: var(--spacing-xs);
}

.card-value {
  font-size: 32px;
  font-weight: 700;
  color: var(--color-text-primary);
  margin-bottom: var(--spacing-xs);
  font-family: 'SF Mono', Monaco, 'Cascadia Code', 'Roboto Mono', Consolas, 'Courier New', monospace;
}

.card-subtitle {
  font-size: 13px;
  color: var(--color-text-tertiary);
  margin-bottom: var(--spacing-sm);
}

.card-footer {
  font-size: 13px;
}

.update-btn {
  width: 100%;
}

.scheduler-section {
  margin-bottom: var(--spacing-xl);
}

.scheduler-card {
  padding: var(--spacing-lg);
}

.scheduler-running,
.scheduler-stopped {
  margin-bottom: var(--spacing-md);
}

.job-name {
  font-weight: 500;
}

.no-jobs {
  text-align: center;
  padding: var(--spacing-xl);
}

.cache-section {
  margin-bottom: var(--spacing-xl);
}

.cache-card {
  padding: var(--spacing-lg);
}

.cache-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding-bottom: var(--spacing-md);
  border-bottom: 1px solid var(--color-border);
}

.cache-info {
  display: flex;
  align-items: center;
  gap: var(--spacing-md);
}

.cache-title {
  font-size: 17px;
  font-weight: 600;
  color: var(--color-text-primary);
  margin-bottom: var(--spacing-xs);
}

.cache-subtitle {
  font-size: 13px;
}

.no-cache {
  text-align: center;
  padding: var(--spacing-xl);
  margin-top: var(--spacing-md);
}

.tips-section {
  padding: var(--spacing-lg);
}

@media (max-width: 734px) {
  .page-header h1 {
    font-size: 24px;
  }

  .stat-card {
    margin-bottom: var(--spacing-md);
    min-height: auto;
  }

  .card-value {
    font-size: 28px;
  }

  .cache-header {
    flex-direction: column;
    align-items: flex-start;
    gap: var(--spacing-md);
  }

  .cache-info {
    width: 100%;
  }
}
</style>
