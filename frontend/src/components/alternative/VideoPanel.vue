<template>
  <div class="video-panel">
    <el-card class="filter-card">
      <div class="filter-section">
        <el-radio-group v-model="videoType" @change="loadData">
          <el-radio-button value="tv">电视剧</el-radio-button>
          <el-radio-button value="variety">综艺节目</el-radio-button>
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
            {{ videoType === 'tv' ? '电视剧播映指数 TOP10' : '综艺节目播映指数 TOP10' }}
          </span>
        </div>
      </template>

      <el-empty v-if="!loading && videoList.length === 0" description="暂无数据" />

      <div v-else class="content-wrapper">
        <!-- TOP10 排行榜 -->
        <div class="video-list">
          <div
            v-for="video in videoList"
            :key="video.排序"
            class="video-item"
            :class="getRankClass(video.排序)"
          >
            <div class="rank-badge">{{ video.排序 }}</div>
            <div class="video-info">
              <div class="video-header">
                <span class="video-name">{{ video.名称 }}</span>
                <el-tag size="small" type="primary">{{ video.类型 }}</el-tag>
              </div>
              <div class="score-display">
                <div class="main-score">
                  <span class="score-label">播映指数</span>
                  <span class="score-value">{{ video.播映指数.toFixed(2) }}</span>
                </div>
              </div>
              <div class="metrics-grid">
                <div class="metric-item">
                  <span class="metric-label">媒体热度</span>
                  <el-progress
                    :percentage="video.媒体热度"
                    :stroke-width="6"
                    :show-text="false"
                    :color="getProgressColor(video.媒体热度)"
                  />
                  <span class="metric-value">{{ video.媒体热度 }}</span>
                </div>
                <div class="metric-item">
                  <span class="metric-label">用户热度</span>
                  <el-progress
                    :percentage="video.用户热度"
                    :stroke-width="6"
                    :show-text="false"
                    :color="getProgressColor(video.用户热度)"
                  />
                  <span class="metric-value">{{ video.用户热度 }}</span>
                </div>
                <div class="metric-item">
                  <span class="metric-label">好评度</span>
                  <el-progress
                    :percentage="video.好评度"
                    :stroke-width="6"
                    :show-text="false"
                    :color="getProgressColor(video.好评度)"
                  />
                  <span class="metric-value">{{ video.好评度 }}</span>
                </div>
                <div class="metric-item">
                  <span class="metric-label">观看度</span>
                  <el-progress
                    :percentage="video.观看度"
                    :stroke-width="6"
                    :show-text="false"
                    :color="getProgressColor(video.观看度)"
                  />
                  <span class="metric-value">{{ video.观看度 }}</span>
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
import { getVideoTV, getVideoVarietyShow, type VideoData } from '@/api/alternative'
import { ElMessage } from 'element-plus'

const loading = ref(false)
const videoType = ref<'tv' | 'variety'>('tv')
const videoList = ref<VideoData[]>([])

const updateDate = computed(() => {
  if (videoList.value.length > 0) {
    return videoList.value[0].统计日期
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
    if (videoType.value === 'tv') {
      const data = await getVideoTV()
      videoList.value = data || []
    } else {
      const data = await getVideoVarietyShow()
      videoList.value = data || []
    }

    if (videoList.value.length === 0) {
      ElMessage.info('暂无视频播映数据')
    }
  } catch (error) {
    console.error('加载视频播映数据失败:', error)
    ElMessage.error('加载数据失败，请稍后重试')
    videoList.value = []
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  loadData()
})
</script>

<style scoped>
.video-panel {
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
      .video-list {
        display: flex;
        flex-direction: column;
        gap: 16px;

        .video-item {
          position: relative;
          padding: 20px;
          background: var(--color-bg-secondary);
          border-radius: 12px;
          border: 2px solid transparent;
          transition: all 0.3s;

          &:hover {
            transform: translateY(-2px);
            box-shadow: var(--shadow-md);
          }

          &.rank-1 {
            border-color: #f5576c;
            background: linear-gradient(135deg, #fff5f7 0%, #ffe5e9 100%);
          }

          &.rank-2 {
            border-color: #4facfe;
            background: linear-gradient(135deg, #f0f9ff 0%, #e0f2fe 100%);
          }

          &.rank-3 {
            border-color: #43e97b;
            background: linear-gradient(135deg, #f0fdf4 0%, #dcfce7 100%);
          }

          .rank-badge {
            position: absolute;
            top: 16px;
            left: 16px;
            width: 32px;
            height: 32px;
            display: flex;
            align-items: center;
            justify-content: center;
            background: var(--color-accent);
            color: white;
            border-radius: 50%;
            font-size: 16px;
            font-weight: bold;
            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.15);
          }

          .video-info {
            margin-left: 48px;

            .video-header {
              display: flex;
              align-items: center;
              gap: 12px;
              margin-bottom: 12px;

              .video-name {
                font-size: 18px;
                font-weight: 600;
                color: var(--color-text-primary);
              }
            }

            .score-display {
              margin-bottom: 16px;

              .main-score {
                display: inline-flex;
                align-items: baseline;
                gap: 8px;
                padding: 8px 16px;
                background: rgba(64, 158, 255, 0.1);
                border-radius: 8px;

                .score-label {
                  font-size: 14px;
                  color: var(--color-text-secondary);
                }

                .score-value {
                  font-size: 28px;
                  font-weight: bold;
                  color: #409eff;
                }
              }
            }

            .metrics-grid {
              display: grid;
              grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
              gap: 12px;

              .metric-item {
                display: flex;
                flex-direction: column;
                gap: 4px;

                .metric-label {
                  font-size: 12px;
                  color: var(--color-text-secondary);
                }

                .metric-value {
                  font-size: 12px;
                  font-weight: 500;
                  color: var(--color-text-primary);
                  text-align: right;
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
  .video-panel {
    .video-item {
      .video-info {
        .metrics-grid {
          grid-template-columns: 1fr !important;
        }
      }
    }
  }
}
</style>
