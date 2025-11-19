<template>
  <div class="news-cctv-panel">
    <el-card class="filter-card">
      <div class="filter-section">
        <el-date-picker
          v-model="selectedDate"
          type="date"
          placeholder="选择日期"
          format="YYYY-MM-DD"
          value-format="YYYYMMDD"
          :disabled-date="disabledDate"
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
          <span class="title">新闻联播文字稿</span>
          <el-tag v-if="newsList.length > 0" type="info">
            共 {{ newsList.length }} 条新闻
          </el-tag>
        </div>
      </template>

      <el-empty v-if="!loading && newsList.length === 0" description="暂无数据" />

      <div v-else class="news-list">
        <div v-for="(news, index) in newsList" :key="index" class="news-item">
          <div class="news-header">
            <span class="news-index">{{ index + 1 }}</span>
            <h3 class="news-title">{{ news.title }}</h3>
            <el-tag type="primary" size="small">{{ formatDate(news.date) }}</el-tag>
          </div>
          <div class="news-content">
            {{ news.content }}
          </div>
        </div>
      </div>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { getNewsCCTV, type NewsCCTV } from '@/api/alternative'
import { ElMessage } from 'element-plus'

const loading = ref(false)
const newsList = ref<NewsCCTV[]>([])
const selectedDate = ref<string>('')

// 禁用未来日期
const disabledDate = (time: Date) => {
  return time.getTime() > Date.now()
}

// 格式化日期显示
const formatDate = (dateStr: string) => {
  if (!dateStr || dateStr.length !== 8) return dateStr
  const year = dateStr.substring(0, 4)
  const month = dateStr.substring(4, 6)
  const day = dateStr.substring(6, 8)
  return `${year}年${month}月${day}日`
}

// 加载数据
const loadData = async () => {
  if (!selectedDate.value) {
    ElMessage.warning('请选择日期')
    return
  }

  loading.value = true
  try {
    const data = await getNewsCCTV(selectedDate.value)
    newsList.value = data || []

    if (newsList.value.length === 0) {
      ElMessage.info('该日期暂无新闻联播数据')
    }
  } catch (error) {
    console.error('加载新闻联播数据失败:', error)
    ElMessage.error('加载数据失败，请稍后重试')
    newsList.value = []
  } finally {
    loading.value = false
  }
}

// 初始化：加载昨天的数据
onMounted(() => {
  const yesterday = new Date()
  yesterday.setDate(yesterday.getDate() - 1)
  const year = yesterday.getFullYear()
  const month = String(yesterday.getMonth() + 1).padStart(2, '0')
  const day = String(yesterday.getDate()).padStart(2, '0')
  selectedDate.value = `${year}${month}${day}`

  loadData()
})
</script>

<style scoped>
.news-cctv-panel {
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
      display: flex;
      justify-content: space-between;
      align-items: center;

      .title {
        font-size: 16px;
        font-weight: 600;
      }
    }

    .news-list {
      display: flex;
      flex-direction: column;
      gap: 20px;

      .news-item {
        padding: 16px;
        background: #f5f7fa;
        border-radius: 8px;
        transition: all 0.3s;

        &:hover {
          background: #e8ecf1;
          box-shadow: 0 2px 12px rgba(0, 0, 0, 0.08);
        }

        .news-header {
          display: flex;
          align-items: center;
          gap: 12px;
          margin-bottom: 12px;

          .news-index {
            flex-shrink: 0;
            width: 28px;
            height: 28px;
            display: flex;
            align-items: center;
            justify-content: center;
            background: #409eff;
            color: white;
            border-radius: 50%;
            font-weight: 600;
            font-size: 14px;
          }

          .news-title {
            flex: 1;
            margin: 0;
            font-size: 16px;
            font-weight: 600;
            color: #303133;
            line-height: 1.5;
          }
        }

        .news-content {
          padding-left: 40px;
          font-size: 14px;
          line-height: 1.8;
          color: #606266;
          text-align: justify;
        }
      }
    }
  }
}
</style>
