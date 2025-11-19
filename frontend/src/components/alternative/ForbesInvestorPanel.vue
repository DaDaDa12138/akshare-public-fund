<template>
  <div class="forbes-investor-panel">
    <el-card v-loading="loading" class="data-card">
      <template #header>
        <div class="card-header">
          <span class="title">💼 福布斯中国最佳创投人榜 TOP99</span>
          <el-button
            type="primary"
            size="small"
            :icon="RefreshIcon"
            @click="loadData"
          >
            刷新数据
          </el-button>
        </div>
      </template>

      <el-empty v-if="!loading && investorList.length === 0" description="暂无数据" />

      <div v-else class="content-wrapper">
        <!-- 搜索框 -->
        <div class="search-section">
          <el-input
            v-model="searchKeyword"
            placeholder="搜索投资人姓名或机构"
            clearable
            size="default"
            style="max-width: 400px"
          >
            <template #prefix>
              <el-icon><Search /></el-icon>
            </template>
          </el-input>
        </div>

        <!-- 统计信息 -->
        <div class="stats-info">
          <el-tag type="info">共 {{ filteredList.length }} 位投资人</el-tag>
          <el-tag type="success">{{ maleCount }} 位男性</el-tag>
          <el-tag type="warning">{{ femaleCount }} 位女性</el-tag>
        </div>

        <!-- 投资人列表 -->
        <div class="investor-grid">
          <div
            v-for="investor in filteredList"
            :key="investor.排名"
            class="investor-card"
            :class="getRankClass(investor.排名)"
          >
            <div class="rank-badge">{{ investor.排名 }}</div>
            <div class="investor-info">
              <div class="investor-header">
                <span class="investor-name">{{ investor.姓名 }}</span>
                <el-tag size="small" :type="investor.性别 === '男' ? 'primary' : 'danger'">
                  {{ investor.性别 }}
                </el-tag>
              </div>
              <div class="investor-details">
                <div class="detail-item">
                  <span class="label">年龄</span>
                  <span class="value">{{ investor.年龄 }}岁</span>
                </div>
                <div class="detail-item">
                  <span class="label">机构</span>
                  <span class="value institution">{{ investor.机构 }}</span>
                </div>
                <div class="detail-item">
                  <span class="label">职位</span>
                  <span class="value">{{ investor.职位 }}</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { getForbesChineseInvestors, type ForbesInvestor } from '@/api/alternative'
import { ElMessage } from 'element-plus'
import { Refresh as RefreshIcon, Search } from '@element-plus/icons-vue'

const loading = ref(false)
const investorList = ref<ForbesInvestor[]>([])
const searchKeyword = ref('')

// 筛选后的列表
const filteredList = computed(() => {
  if (!searchKeyword.value.trim()) {
    return investorList.value
  }
  const keyword = searchKeyword.value.toLowerCase()
  return investorList.value.filter(investor =>
    investor.姓名.toLowerCase().includes(keyword) ||
    investor.机构.toLowerCase().includes(keyword)
  )
})

// 统计数据
const maleCount = computed(() =>
  investorList.value.filter(i => i.性别 === '男').length
)

const femaleCount = computed(() =>
  investorList.value.filter(i => i.性别 === '女').length
)

// 获取排名样式类
const getRankClass = (rank: number) => {
  if (rank === 1) return 'rank-1'
  if (rank === 2) return 'rank-2'
  if (rank === 3) return 'rank-3'
  if (rank <= 10) return 'rank-top10'
  return ''
}

// 加载数据
const loadData = async () => {
  loading.value = true
  try {
    const data = await getForbesChineseInvestors()
    investorList.value = data || []

    if (investorList.value.length === 0) {
      ElMessage.info('暂无福布斯投资人数据')
    }
  } catch (error) {
    console.error('加载福布斯投资人数据失败:', error)
    ElMessage.error('加载数据失败，请稍后重试')
    investorList.value = []
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  loadData()
})
</script>

<style scoped>
.forbes-investor-panel {
  .data-card {
    .card-header {
      display: flex;
      justify-content: space-between;
      align-items: center;

      .title {
        font-size: 16px;
        font-weight: 600;
      }
    }

    .content-wrapper {
      .search-section {
        margin-bottom: 20px;
      }

      .stats-info {
        display: flex;
        gap: 12px;
        margin-bottom: 24px;
      }

      .investor-grid {
        display: grid;
        grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
        gap: 16px;

        .investor-card {
          position: relative;
          padding: 16px 16px 16px 56px;
          background: var(--color-bg-secondary);
          border-radius: 12px;
          border-left: 4px solid #909399;
          transition: all 0.3s;

          &:hover {
            transform: translateY(-4px);
            box-shadow: var(--shadow-md);
          }

          &.rank-1 {
            border-left-color: #f5576c;
            background: linear-gradient(135deg, #fff5f7 0%, #ffe5e9 100%);
          }

          &.rank-2 {
            border-left-color: #4facfe;
            background: linear-gradient(135deg, #f0f9ff 0%, #e0f2fe 100%);
          }

          &.rank-3 {
            border-left-color: #43e97b;
            background: linear-gradient(135deg, #f0fdf4 0%, #dcfce7 100%);
          }

          &.rank-top10 {
            border-left-color: #ffc107;
          }

          .rank-badge {
            position: absolute;
            top: 12px;
            left: 12px;
            width: 36px;
            height: 36px;
            display: flex;
            align-items: center;
            justify-content: center;
            background: var(--color-accent);
            color: white;
            border-radius: 8px;
            font-size: 16px;
            font-weight: bold;
            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.15);
          }

          .investor-info {
            .investor-header {
              display: flex;
              align-items: center;
              justify-content: space-between;
              margin-bottom: 12px;

              .investor-name {
                font-size: 18px;
                font-weight: 600;
                color: var(--color-text-primary);
              }
            }

            .investor-details {
              display: flex;
              flex-direction: column;
              gap: 8px;

              .detail-item {
                display: flex;
                align-items: center;
                gap: 8px;

                .label {
                  font-size: 13px;
                  color: var(--color-text-secondary);
                  min-width: 40px;
                }

                .value {
                  font-size: 14px;
                  color: var(--color-text-primary);
                  flex: 1;

                  &.institution {
                    font-weight: 500;
                    color: var(--color-accent);
                  }
                }
              }
            }
          }
        }
      }
    }
  }
}

@media (max-width: 768px) {
  .forbes-investor-panel {
    .investor-grid {
      grid-template-columns: 1fr !important;
    }
  }
}
</style>
