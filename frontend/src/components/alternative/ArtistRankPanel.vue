<template>
  <div class="artist-rank-panel">
    <el-card class="filter-card">
      <div class="filter-section">
        <el-radio-group v-model="rankType" @change="loadData">
          <el-radio-button value="business">商业价值榜</el-radio-button>
          <el-radio-button value="online">网络价值榜</el-radio-button>
        </el-radio-group>
        <el-tag type="info">
          更新时间: {{ updateDate }}
        </el-tag>
      </div>
    </el-card>

    <el-card v-loading="loading" class="data-card">
      <template #header>
        <div class="card-header">
          <span class="title">
            {{ rankType === 'business' ? '艺人商业价值榜 TOP100' : '艺人网络价值榜 TOP100' }}
          </span>
        </div>
      </template>

      <el-empty v-if="!loading && artistList.length === 0" description="暂无数据" />

      <div v-else class="content-wrapper">
        <!-- TOP 10 卡片展示 -->
        <div class="top10-cards">
          <div
            v-for="artist in artistList.slice(0, 10)"
            :key="artist.排名"
            class="artist-card"
            :class="getRankClass(artist.排名)"
          >
            <div class="rank-badge">{{ artist.排名 }}</div>
            <div class="artist-info">
              <div class="artist-name">{{ artist.艺人 }}</div>
              <div class="artist-score">
                {{ rankType === 'business' ? artist.商业价值 : artist.流量价值 }}
              </div>
            </div>
            <div class="artist-details">
              <div class="detail-item">
                <span class="label">专业热度</span>
                <el-progress
                  :percentage="artist.专业热度"
                  :stroke-width="6"
                  :show-text="false"
                  :color="getProgressColor(artist.专业热度)"
                />
              </div>
              <div class="detail-item">
                <span class="label">关注热度</span>
                <el-progress
                  :percentage="artist.关注热度"
                  :stroke-width="6"
                  :show-text="false"
                  :color="getProgressColor(artist.关注热度)"
                />
              </div>
              <div class="detail-item">
                <span class="label">预测热度</span>
                <el-progress
                  :percentage="artist.预测热度"
                  :stroke-width="6"
                  :show-text="false"
                  :color="getProgressColor(artist.预测热度)"
                />
              </div>
              <div class="detail-item">
                <span class="label">{{ rankType === 'business' ? '美誉度' : '带货力' }}</span>
                <el-progress
                  :percentage="rankType === 'business' ? artist.美誉度 : artist.带货力"
                  :stroke-width="6"
                  :show-text="false"
                  :color="getProgressColor(rankType === 'business' ? artist.美誉度 : artist.带货力)"
                />
              </div>
            </div>
          </div>
        </div>

        <!-- 完整榜单表格 -->
        <div class="full-table">
          <el-table :data="artistList" stripe style="width: 100%">
            <el-table-column prop="排名" label="排名" width="80" align="center">
              <template #default="{ row }">
                <el-tag :type="getTagType(row.排名)" size="small">
                  {{ row.排名 }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="艺人" label="艺人" width="120" />
            <el-table-column
              :prop="rankType === 'business' ? '商业价值' : '流量价值'"
              :label="rankType === 'business' ? '商业价值' : '流量价值'"
              width="120"
              align="center"
            >
              <template #default="{ row }">
                <span class="score-value">
                  {{ rankType === 'business' ? row.商业价值 : row.流量价值 }}
                </span>
              </template>
            </el-table-column>
            <el-table-column prop="专业热度" label="专业热度" width="140" align="center">
              <template #default="{ row }">
                <el-progress
                  :percentage="row.专业热度"
                  :stroke-width="8"
                  :color="getProgressColor(row.专业热度)"
                />
              </template>
            </el-table-column>
            <el-table-column prop="关注热度" label="关注热度" width="140" align="center">
              <template #default="{ row }">
                <el-progress
                  :percentage="row.关注热度"
                  :stroke-width="8"
                  :color="getProgressColor(row.关注热度)"
                />
              </template>
            </el-table-column>
            <el-table-column prop="预测热度" label="预测热度" width="140" align="center">
              <template #default="{ row }">
                <el-progress
                  :percentage="row.预测热度"
                  :stroke-width="8"
                  :color="getProgressColor(row.预测热度)"
                />
              </template>
            </el-table-column>
            <el-table-column
              :prop="rankType === 'business' ? '美誉度' : '带货力'"
              :label="rankType === 'business' ? '美誉度' : '带货力'"
              width="140"
              align="center"
            >
              <template #default="{ row }">
                <el-progress
                  :percentage="rankType === 'business' ? row.美誉度 : row.带货力"
                  :stroke-width="8"
                  :color="getProgressColor(rankType === 'business' ? row.美誉度 : row.带货力)"
                />
              </template>
            </el-table-column>
            <el-table-column prop="统计日期" label="统计日期" width="120" align="center" />
          </el-table>
        </div>
      </div>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import {
  getBusinessValueArtist,
  getOnlineValueArtist,
  type BusinessValueArtist,
  type OnlineValueArtist
} from '@/api/alternative'
import { ElMessage } from 'element-plus'

const loading = ref(false)
const rankType = ref<'business' | 'online'>('business')
const artistList = ref<(BusinessValueArtist | OnlineValueArtist)[]>([])

const updateDate = computed(() => {
  if (artistList.value.length > 0) {
    return artistList.value[0].统计日期
  }
  return '-'
})

// 获取排名样式类
const getRankClass = (rank: number) => {
  if (rank === 1) return 'rank-1'
  if (rank === 2) return 'rank-2'
  if (rank === 3) return 'rank-3'
  return ''
}

// 获取标签类型
const getTagType = (rank: number) => {
  if (rank <= 3) return 'danger'
  if (rank <= 10) return 'warning'
  return 'info'
}

// 获取进度条颜色
const getProgressColor = (value: number) => {
  if (value >= 80) return '#67c23a'
  if (value >= 60) return '#409eff'
  if (value >= 40) return '#e6a23c'
  return '#f56c6c'
}

// 加载数据
const loadData = async () => {
  loading.value = true
  try {
    if (rankType.value === 'business') {
      const data = await getBusinessValueArtist()
      artistList.value = data || []
    } else {
      const data = await getOnlineValueArtist()
      artistList.value = data || []
    }

    if (artistList.value.length === 0) {
      ElMessage.info('暂无艺人数据')
    }
  } catch (error) {
    console.error('加载艺人数据失败:', error)
    ElMessage.error('加载数据失败，请稍后重试')
    artistList.value = []
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  loadData()
})
</script>

<style scoped>
.artist-rank-panel {
  .filter-card {
    margin-bottom: 20px;

    .filter-section {
      display: flex;
      gap: 12px;
      align-items: center;
    }
  }

  .data-card {
    .card-header {
      .title {
        font-size: 16px;
        font-weight: 600;
      }
    }

    .content-wrapper {
      display: flex;
      flex-direction: column;
      gap: 24px;

      .top10-cards {
        display: grid;
        grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
        gap: 16px;

        .artist-card {
          position: relative;
          padding: 20px;
          background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
          border-radius: 12px;
          color: white;
          box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
          transition: all 0.3s;

          &:hover {
            transform: translateY(-4px);
            box-shadow: 0 6px 20px rgba(0, 0, 0, 0.2);
          }

          &.rank-1 {
            background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
          }

          &.rank-2 {
            background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
          }

          &.rank-3 {
            background: linear-gradient(135deg, #43e97b 0%, #38f9d7 100%);
          }

          .rank-badge {
            position: absolute;
            top: 12px;
            right: 12px;
            width: 36px;
            height: 36px;
            display: flex;
            align-items: center;
            justify-content: center;
            background: rgba(255, 255, 255, 0.3);
            border-radius: 50%;
            font-size: 18px;
            font-weight: bold;
          }

          .artist-info {
            margin-bottom: 16px;

            .artist-name {
              font-size: 20px;
              font-weight: bold;
              margin-bottom: 8px;
            }

            .artist-score {
              font-size: 32px;
              font-weight: bold;
              opacity: 0.9;
            }
          }

          .artist-details {
            display: flex;
            flex-direction: column;
            gap: 8px;

            .detail-item {
              display: flex;
              align-items: center;
              gap: 8px;

              .label {
                width: 70px;
                font-size: 12px;
                opacity: 0.9;
              }

              :deep(.el-progress) {
                flex: 1;

                .el-progress-bar__outer {
                  background-color: rgba(255, 255, 255, 0.3);
                }
              }
            }
          }
        }
      }

      .full-table {
        .score-value {
          font-size: 16px;
          font-weight: bold;
          color: #409eff;
        }
      }
    }
  }
}
</style>
