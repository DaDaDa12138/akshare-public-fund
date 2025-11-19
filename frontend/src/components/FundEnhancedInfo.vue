<template>
  <div class="fund-enhanced-info">
    <!-- 申购赎回状态 -->
    <div v-if="purchaseStatus" class="info-card card">
      <div class="card-header">
        <h3>
          <el-icon><ShoppingCart /></el-icon>
          申购赎回状态
        </h3>
      </div>
      <div class="card-body">
        <div class="status-grid">
          <div class="status-item">
            <div class="status-label">申购状态</div>
            <div class="status-value">
              <el-tag :type="getStatusType(purchaseStatus.申购状态)" size="large">
                {{ purchaseStatus.申购状态 }}
              </el-tag>
            </div>
          </div>
          <div class="status-item">
            <div class="status-label">赎回状态</div>
            <div class="status-value">
              <el-tag :type="getStatusType(purchaseStatus.赎回状态)" size="large">
                {{ purchaseStatus.赎回状态 }}
              </el-tag>
            </div>
          </div>
          <div class="status-item">
            <div class="status-label">购买起点</div>
            <div class="status-value">{{ formatAmount(purchaseStatus.购买起点) }}</div>
          </div>
          <div class="status-item">
            <div class="status-label">手续费率</div>
            <div class="status-value">{{ formatFeeRate(purchaseStatus.手续费) }}</div>
          </div>
        </div>
      </div>
    </div>

    <!-- 基金评级 -->
    <div v-if="rating" class="info-card card">
      <div class="card-header">
        <h3>
          <el-icon><Medal /></el-icon>
          基金评级
        </h3>
      </div>
      <div class="card-body">
        <div class="rating-grid">
          <div class="rating-item" v-if="rating.晨星评级">
            <div class="rating-label">晨星评级</div>
            <div class="rating-stars">
              <el-rate
                v-model="rating.晨星评级"
                disabled
                show-score
                text-color="#ff9900"
              />
            </div>
          </div>
          <div class="rating-item" v-if="rating.上海证券">
            <div class="rating-label">上海证券</div>
            <div class="rating-stars">
              <el-rate
                v-model="rating.上海证券"
                disabled
                show-score
                text-color="#ff9900"
              />
            </div>
          </div>
          <div class="rating-item" v-if="rating.招商证券">
            <div class="rating-label">招商证券</div>
            <div class="rating-stars">
              <el-rate
                v-model="rating.招商证券"
                disabled
                show-score
                text-color="#ff9900"
              />
            </div>
          </div>
          <div class="rating-item" v-if="rating.济安金信">
            <div class="rating-label">济安金信</div>
            <div class="rating-stars">
              <el-rate
                v-model="rating.济安金信"
                disabled
                show-score
                text-color="#ff9900"
              />
            </div>
          </div>
        </div>
        <div class="rating-summary" v-if="rating['5星评级家数']">
          <el-icon><Trophy /></el-icon>
          共有 <strong>{{ rating['5星评级家数'] }}</strong> 家机构给予5星评级
        </div>
      </div>
    </div>

    <!-- 分红历史 -->
    <div v-if="dividends && dividends.length > 0" class="info-card card">
      <div class="card-header">
        <h3>
          <el-icon><Money /></el-icon>
          分红历史（近{{ dividends.length }}次）
        </h3>
      </div>
      <div class="card-body">
        <el-table :data="dividends" stripe style="width: 100%">
          <el-table-column prop="权益登记日" label="权益登记日" width="120" />
          <el-table-column prop="除息日期" label="除息日期" width="120" />
          <el-table-column prop="分红" label="分红金额" width="120" align="right">
            <template #default="{ row }">
              <span class="dividend-amount">¥{{ row.分红 }}</span>
            </template>
          </el-table-column>
          <el-table-column prop="分红发放日" label="分红发放日" width="120" />
        </el-table>
      </div>
    </div>

    <!-- 没有数据的提示 -->
    <div v-if="!hasAnyData" class="no-data-hint">
      <el-empty description="暂无增强信息"></el-empty>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { ShoppingCart, Medal, Money, Trophy } from '@element-plus/icons-vue'
import axios from 'axios'

// Props
const props = defineProps<{
  fundCode: string
}>()

// 数据
const purchaseStatus = ref<any>(null)
const rating = ref<any>(null)
const dividends = ref<any[]>([])

// 计算是否有任何数据
const hasAnyData = computed(() => {
  return purchaseStatus.value || rating.value || (dividends.value && dividends.value.length > 0)
})

// 加载数据
onMounted(() => {
  loadPurchaseStatus()
  loadRating()
  loadDividends()
})

// 加载申购赎回状态
const loadPurchaseStatus = async () => {
  try {
    const response = await axios.get(`/api/fund_purchase_status/${props.fundCode}`)
    if (response.data.success && response.data.data) {
      purchaseStatus.value = response.data.data
    }
  } catch (error) {
    console.error('加载申购赎回状态失败:', error)
  }
}

// 加载基金评级
const loadRating = async () => {
  try {
    const response = await axios.get(`/api/fund_rating/${props.fundCode}`)
    if (response.data.success && response.data.data) {
      rating.value = response.data.data
    }
  } catch (error) {
    console.error('加载基金评级失败:', error)
  }
}

// 加载分红历史
const loadDividends = async () => {
  try {
    const response = await axios.get(`/api/fund_dividend/${props.fundCode}`)
    if (response.data.success && response.data.data) {
      dividends.value = response.data.data.slice(0, 10) // 只显示最近10次
    }
  } catch (error) {
    console.error('加载分红历史失败:', error)
  }
}

// 获取状态标签类型
const getStatusType = (status: string): string => {
  if (status?.includes('开放')) return 'success'
  if (status?.includes('暂停')) return 'danger'
  if (status?.includes('限')) return 'warning'
  return 'info'
}

// 格式化金额
const formatAmount = (amount: any): string => {
  if (!amount || amount === 'NaN') return '-'
  const num = parseFloat(amount)
  if (isNaN(num)) return '-'
  if (num < 10000) return `¥${num.toFixed(2)}`
  return `¥${(num / 10000).toFixed(2)}万`
}

// 格式化费率
const formatFeeRate = (rate: any): string => {
  if (!rate || rate === 'NaN') return '-'
  const num = parseFloat(rate)
  if (isNaN(num)) return '-'
  return `${(num * 100).toFixed(2)}%`
}
</script>

<style scoped>
.fund-enhanced-info {
  margin-top: var(--spacing-lg);
}

.info-card {
  margin-bottom: var(--spacing-lg);
}

.card-header {
  padding: var(--spacing-lg);
  border-bottom: 1px solid var(--color-border);
}

.card-header h3 {
  display: flex;
  align-items: center;
  gap: var(--spacing-sm);
  margin: 0;
  font-size: 20px;
  font-weight: 600;
  color: var(--color-text-primary);
}

.card-body {
  padding: var(--spacing-xl);
}

/* 申购赎回状态 */
.status-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: var(--spacing-lg);
}

.status-item {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-sm);
}

.status-label {
  font-size: 14px;
  color: var(--color-text-secondary);
}

.status-value {
  font-size: 18px;
  font-weight: 600;
  color: var(--color-text-primary);
}

/* 基金评级 */
.rating-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: var(--spacing-lg);
  margin-bottom: var(--spacing-lg);
}

.rating-item {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-sm);
  padding: var(--spacing-md);
  background: var(--color-bg-secondary);
  border-radius: 8px;
}

.rating-label {
  font-size: 14px;
  color: var(--color-text-secondary);
  font-weight: 500;
}

.rating-stars {
  display: flex;
  align-items: center;
}

.rating-summary {
  display: flex;
  align-items: center;
  gap: var(--spacing-sm);
  padding: var(--spacing-md);
  background: linear-gradient(135deg, rgba(255, 153, 0, 0.1) 0%, rgba(255, 153, 0, 0.05) 100%);
  border-radius: 8px;
  border-left: 4px solid #ff9900;
  font-size: 15px;
  color: var(--color-text-primary);
}

.rating-summary strong {
  color: #ff9900;
  font-size: 18px;
}

/* 分红历史 */
.dividend-amount {
  color: var(--color-success);
  font-weight: 600;
  font-size: 16px;
}

/* 无数据提示 */
.no-data-hint {
  padding: var(--spacing-2xl);
  text-align: center;
}

@media (max-width: 734px) {
  .status-grid,
  .rating-grid {
    grid-template-columns: 1fr;
  }

  .card-header h3 {
    font-size: 18px;
  }
}
</style>
