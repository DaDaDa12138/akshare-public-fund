<template>
  <div class="weibo-stock-panel">
    <el-card v-loading="loading" class="data-card">
      <template #header>
        <div class="card-header">
          <span class="title">📊 微博舆情股票热度 TOP50</span>
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

      <el-empty v-if="!loading && stockList.length === 0" description="暂无数据" />

      <div v-else class="content-wrapper">
        <!-- 统计概览 -->
        <div class="stats-overview">
          <div class="stat-item">
            <div class="stat-label">上涨股票</div>
            <div class="stat-value up">{{ upCount }}</div>
          </div>
          <div class="stat-item">
            <div class="stat-label">下跌股票</div>
            <div class="stat-value down">{{ downCount }}</div>
          </div>
          <div class="stat-item">
            <div class="stat-label">平盘股票</div>
            <div class="stat-value flat">{{ flatCount }}</div>
          </div>
        </div>

        <!-- 股票列表 -->
        <div class="stock-grid">
          <div
            v-for="(stock, index) in stockList"
            :key="index"
            class="stock-card"
            :class="getStockClass(stock.rate)"
          >
            <div class="rank-badge">{{ index + 1 }}</div>
            <div class="stock-info">
              <div class="stock-name">{{ stock.name }}</div>
              <div class="stock-rate">
                <span class="rate-icon">{{ getRateIcon(stock.rate) }}</span>
                <span class="rate-value">{{ formatRate(stock.rate) }}</span>
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
import { getWeiboStockReport, type WeiboStockReport } from '@/api/alternative'
import { ElMessage } from 'element-plus'
import { Refresh as RefreshIcon } from '@element-plus/icons-vue'

const loading = ref(false)
const stockList = ref<WeiboStockReport[]>([])

// 统计数据
const upCount = computed(() =>
  stockList.value.filter(s => s.rate > 0).length
)

const downCount = computed(() =>
  stockList.value.filter(s => s.rate < 0).length
)

const flatCount = computed(() =>
  stockList.value.filter(s => s.rate === 0).length
)

// 获取股票样式类
const getStockClass = (rate: number) => {
  if (rate > 0) return 'stock-up'
  if (rate < 0) return 'stock-down'
  return 'stock-flat'
}

// 获取涨跌图标
const getRateIcon = (rate: number) => {
  if (rate > 0) return '↑'
  if (rate < 0) return '↓'
  return '━'
}

// 格式化涨跌幅
const formatRate = (rate: number) => {
  const formatted = Math.abs(rate).toFixed(2)
  if (rate > 0) return `+${formatted}%`
  if (rate < 0) return `-${formatted}%`
  return `${formatted}%`
}

// 加载数据
const loadData = async () => {
  loading.value = true
  try {
    const data = await getWeiboStockReport()
    stockList.value = data || []

    if (stockList.value.length === 0) {
      ElMessage.info('暂无微博舆情股票数据')
    }
  } catch (error) {
    console.error('加载微博舆情股票数据失败:', error)
    ElMessage.error('加载数据失败，请稍后重试')
    stockList.value = []
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  loadData()
})
</script>

<style scoped>
.weibo-stock-panel {
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
      .stats-overview {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
        gap: 16px;
        margin-bottom: 24px;

        .stat-item {
          padding: 16px;
          background: var(--color-bg-secondary);
          border-radius: 8px;
          text-align: center;

          .stat-label {
            font-size: 13px;
            color: var(--color-text-secondary);
            margin-bottom: 8px;
          }

          .stat-value {
            font-size: 28px;
            font-weight: bold;

            &.up {
              color: #f56c6c;
            }

            &.down {
              color: #67c23a;
            }

            &.flat {
              color: #909399;
            }
          }
        }
      }

      .stock-grid {
        display: grid;
        grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
        gap: 12px;

        .stock-card {
          position: relative;
          padding: 12px 12px 12px 44px;
          background: var(--color-bg-secondary);
          border-radius: 8px;
          border-left: 4px solid #909399;
          transition: all 0.3s;

          &:hover {
            transform: translateY(-2px);
            box-shadow: var(--shadow-md);
          }

          &.stock-up {
            border-left-color: #f56c6c;
            background: linear-gradient(135deg, #fff5f7 0%, #ffffff 100%);
          }

          &.stock-down {
            border-left-color: #67c23a;
            background: linear-gradient(135deg, #f0fdf4 0%, #ffffff 100%);
          }

          &.stock-flat {
            border-left-color: #909399;
          }

          .rank-badge {
            position: absolute;
            top: 8px;
            left: 8px;
            width: 28px;
            height: 28px;
            display: flex;
            align-items: center;
            justify-content: center;
            background: var(--color-accent);
            color: white;
            border-radius: 4px;
            font-size: 12px;
            font-weight: bold;
          }

          .stock-info {
            .stock-name {
              font-size: 14px;
              font-weight: 600;
              color: var(--color-text-primary);
              margin-bottom: 6px;
              white-space: nowrap;
              overflow: hidden;
              text-overflow: ellipsis;
            }

            .stock-rate {
              display: flex;
              align-items: baseline;
              gap: 4px;

              .rate-icon {
                font-size: 16px;
                font-weight: bold;
              }

              .rate-value {
                font-size: 16px;
                font-weight: bold;
              }
            }

            &:has(.stock-card.stock-up) .stock-rate {
              color: #f56c6c;
            }

            &:has(.stock-card.stock-down) .stock-rate {
              color: #67c23a;
            }
          }

          &.stock-up .stock-rate {
            color: #f56c6c;
          }

          &.stock-down .stock-rate {
            color: #67c23a;
          }

          &.stock-flat .stock-rate {
            color: #909399;
          }
        }
      }
    }
  }
}

@media (max-width: 768px) {
  .weibo-stock-panel {
    .stock-grid {
      grid-template-columns: 1fr !important;
    }
  }
}
</style>
