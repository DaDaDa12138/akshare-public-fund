<template>
  <div class="sunrise-sunset-panel">
    <el-card class="filter-card">
      <div class="filter-section">
        <el-radio-group v-model="viewType" @change="loadData">
          <el-radio-button value="daily">每日查询</el-radio-button>
          <el-radio-button value="monthly">每月查询</el-radio-button>
        </el-radio-group>

        <el-date-picker
          v-if="viewType === 'daily'"
          v-model="selectedDate"
          type="date"
          placeholder="选择日期"
          format="YYYY-MM-DD"
          value-format="YYYYMMDD"
          @change="loadData"
        />

        <el-date-picker
          v-else
          v-model="selectedMonth"
          type="month"
          placeholder="选择月份"
          format="YYYY-MM"
          value-format="YYYYMM"
          @change="loadData"
        />

        <el-button type="primary" :loading="loading" @click="loadData">
          查询
        </el-button>
      </div>
    </el-card>

    <el-card v-loading="loading" class="data-card">
      <template #header>
        <div class="card-header">
          <span class="title">
            {{ viewType === 'daily' ? '每日日出日落时间' : '月度日出日落数据' }}
          </span>
          <el-tag v-if="sunriseData.length > 0" type="info">
            {{ viewType === 'daily' ? '1天数据' : `${sunriseData.length}天数据` }}
          </el-tag>
        </div>
      </template>

      <el-empty v-if="!loading && sunriseData.length === 0" description="暂无数据" />

      <div v-else class="content-wrapper">
        <!-- 单日数据卡片 -->
        <div v-if="viewType === 'daily' && sunriseData.length > 0" class="daily-card">
          <div class="info-grid">
            <div class="info-item sunrise">
              <div class="icon">🌅</div>
              <div class="content">
                <div class="label">日出时间</div>
                <div class="value">{{ sunriseData[0].Sunrise }}</div>
              </div>
            </div>

            <div class="info-item sunset">
              <div class="icon">🌇</div>
              <div class="content">
                <div class="label">日落时间</div>
                <div class="value">{{ sunriseData[0].Sunset }}</div>
              </div>
            </div>

            <div class="info-item length">
              <div class="icon">⏱️</div>
              <div class="content">
                <div class="label">日照时长</div>
                <div class="value">{{ sunriseData[0].Length }}</div>
              </div>
            </div>

            <div class="info-item solar">
              <div class="icon">☀️</div>
              <div class="content">
                <div class="label">太阳位置</div>
                <div class="value">{{ sunriseData[0].Time }}</div>
              </div>
            </div>
          </div>
        </div>

        <!-- 月度数据表格 -->
        <div v-else-if="viewType === 'monthly'" class="monthly-table">
          <el-table :data="sunriseData" stripe style="width: 100%">
            <el-table-column prop="date" label="日期" width="100" align="center">
              <template #default="{ row }">
                <span>{{ formatMonthDay(row) }}</span>
              </template>
            </el-table-column>
            <el-table-column prop="Sunrise" label="日出时间 🌅" width="140" align="center" />
            <el-table-column prop="Sunset" label="日落时间 🌇" width="140" align="center" />
            <el-table-column prop="Length" label="日照时长 ⏱️" width="140" align="center">
              <template #default="{ row }">
                <el-tag type="success">{{ row.Length }}</el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="Time" label="太阳中天时间" width="160" align="center" />
            <el-table-column label="昼夜长度变化" align="center">
              <template #default="{ row }">
                <span :class="getDiffClass(row.Diff)">
                  {{ row.Diff || '-' }}
                </span>
              </template>
            </el-table-column>
          </el-table>
        </div>
      </div>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { getSunriseDaily, getSunriseMonthly, type SunriseData } from '@/api/alternative'
import { ElMessage } from 'element-plus'

const loading = ref(false)
const viewType = ref<'daily' | 'monthly'>('daily')
const sunriseData = ref<SunriseData[]>([])
const selectedDate = ref<string>('')
const selectedMonth = ref<string>('')

// 格式化月日显示
const formatMonthDay = (row: SunriseData) => {
  if (row['11月']) {
    return `11月${row['11月']}日`
  }
  return row.date || '-'
}

// 获取昼夜长度变化样式
const getDiffClass = (diff: string) => {
  if (!diff) return ''
  if (diff.includes('+') || diff.includes('↑')) return 'text-success'
  if (diff.includes('-') || diff.includes('↓')) return 'text-danger'
  return ''
}

// 加载数据
const loadData = async () => {
  if (viewType.value === 'daily' && !selectedDate.value) {
    ElMessage.warning('请选择日期')
    return
  }

  if (viewType.value === 'monthly' && !selectedMonth.value) {
    ElMessage.warning('请选择月份')
    return
  }

  loading.value = true
  try {
    if (viewType.value === 'daily') {
      const data = await getSunriseDaily(selectedDate.value)
      sunriseData.value = data || []
    } else {
      const data = await getSunriseMonthly(selectedMonth.value)
      sunriseData.value = data || []
    }

    if (sunriseData.value.length === 0) {
      ElMessage.info('该时间暂无数据')
    }
  } catch (error) {
    console.error('加载日出日落数据失败:', error)
    ElMessage.error('加载数据失败，请稍后重试')
    sunriseData.value = []
  } finally {
    loading.value = false
  }
}

// 初始化：默认今天和本月
onMounted(() => {
  const today = new Date()
  const year = today.getFullYear()
  const month = String(today.getMonth() + 1).padStart(2, '0')
  const day = String(today.getDate()).padStart(2, '0')

  selectedDate.value = `${year}${month}${day}`
  selectedMonth.value = `${year}${month}`

  loadData()
})
</script>

<style scoped>
.sunrise-sunset-panel {
  .filter-card {
    margin-bottom: 20px;

    .filter-section {
      display: flex;
      gap: 12px;
      align-items: center;
      flex-wrap: wrap;
    }
  }

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
      .daily-card {
        .info-grid {
          display: grid;
          grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
          gap: 20px;

          .info-item {
            padding: 24px;
            border-radius: 12px;
            display: flex;
            align-items: center;
            gap: 16px;
            transition: all 0.3s;

            &:hover {
              transform: translateY(-4px);
              box-shadow: 0 8px 24px rgba(0, 0, 0, 0.12);
            }

            &.sunrise {
              background: linear-gradient(135deg, #fff5e6 0%, #ffe0b2 100%);
            }

            &.sunset {
              background: linear-gradient(135deg, #ffe6f0 0%, #ffcce0 100%);
            }

            &.length {
              background: linear-gradient(135deg, #e6f7ff 0%, #bae7ff 100%);
            }

            &.solar {
              background: linear-gradient(135deg, #fff7e6 0%, #ffd591 100%);
            }

            .icon {
              font-size: 48px;
              flex-shrink: 0;
            }

            .content {
              flex: 1;

              .label {
                font-size: 13px;
                color: #666;
                margin-bottom: 6px;
              }

              .value {
                font-size: 24px;
                font-weight: bold;
                color: #333;
              }
            }
          }
        }
      }

      .monthly-table {
        .text-success {
          color: #67c23a;
          font-weight: 500;
        }

        .text-danger {
          color: #f56c6c;
          font-weight: 500;
        }
      }
    }
  }
}

@media (max-width: 768px) {
  .sunrise-sunset-panel {
    .filter-section {
      flex-direction: column;
      align-items: stretch;
    }

    .daily-card .info-grid {
      grid-template-columns: 1fr;
    }
  }
}
</style>
