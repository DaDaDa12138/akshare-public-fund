<template>
  <div class="alternative-data-page">
    <div class="container">
      <!-- 页面标题 -->
      <div class="page-header">
        <h1>另类数据</h1>
        <p class="text-secondary">
          汽车销量、空气质量、电影票房、财富排行、新闻资讯、艺人数据、天文数据、视频播映、微博舆情、福布斯榜单等多维度数据分析
        </p>
      </div>

      <!-- 标签页切换 -->
      <el-tabs
        v-model="activeTab"
        class="data-tabs"
        @tab-change="handleTabChange"
      >
        <el-tab-pane label="🚗 汽车销量" name="car">
          <CarSalesPanel v-if="activeTab === 'car'" />
        </el-tab-pane>

        <el-tab-pane label="🌫️ 空气质量" name="air">
          <AirQualityPanel v-if="activeTab === 'air'" />
        </el-tab-pane>

        <el-tab-pane label="🎬 电影票房" name="movie">
          <MovieBoxOfficePanel v-if="activeTab === 'movie'" />
        </el-tab-pane>

        <el-tab-pane label="💰 财富排行" name="wealth">
          <WealthRankPanel v-if="activeTab === 'wealth'" />
        </el-tab-pane>

        <el-tab-pane label="📰 新闻联播" name="news">
          <NewsCCTVPanel v-if="activeTab === 'news'" />
        </el-tab-pane>

        <el-tab-pane label="⭐ 艺人榜单" name="artist">
          <ArtistRankPanel v-if="activeTab === 'artist'" />
        </el-tab-pane>

        <el-tab-pane label="🌅 日出日落" name="sunrise">
          <SunriseSunsetPanel v-if="activeTab === 'sunrise'" />
        </el-tab-pane>

        <el-tab-pane label="📺 视频播映" name="video">
          <VideoPanel v-if="activeTab === 'video'" />
        </el-tab-pane>

        <el-tab-pane label="📈 微博舆情" name="weibo">
          <WeiboStockPanel v-if="activeTab === 'weibo'" />
        </el-tab-pane>

        <el-tab-pane label="💼 福布斯榜" name="forbes">
          <ForbesInvestorPanel v-if="activeTab === 'forbes'" />
        </el-tab-pane>
      </el-tabs>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import CarSalesPanel from '@/components/alternative/CarSalesPanel.vue'
import AirQualityPanel from '@/components/alternative/AirQualityPanel.vue'
import MovieBoxOfficePanel from '@/components/alternative/MovieBoxOfficePanel.vue'
import WealthRankPanel from '@/components/alternative/WealthRankPanel.vue'
import NewsCCTVPanel from '@/components/alternative/NewsCCTVPanel.vue'
import ArtistRankPanel from '@/components/alternative/ArtistRankPanel.vue'
import SunriseSunsetPanel from '@/components/alternative/SunriseSunsetPanel.vue'
import VideoPanel from '@/components/alternative/VideoPanel.vue'
import WeiboStockPanel from '@/components/alternative/WeiboStockPanel.vue'
import ForbesInvestorPanel from '@/components/alternative/ForbesInvestorPanel.vue'
import type { AlternativeTab } from '@/types/alternative'

const route = useRoute()
const router = useRouter()

// 当前激活的标签页
const activeTab = ref<AlternativeTab>('car')

// 标签页切换处理
const handleTabChange = (tab: AlternativeTab) => {
  // 更新 URL 查询参数
  router.push({
    query: { tab }
  })
}

// 初始化
onMounted(() => {
  // 从 URL 查询参数恢复标签页状态
  const tab = route.query.tab as AlternativeTab
  if (tab && ['car', 'air', 'movie', 'wealth', 'news', 'artist', 'sunrise', 'video', 'weibo', 'forbes'].includes(tab)) {
    activeTab.value = tab
  }
})
</script>

<style scoped>
.alternative-data-page {
  min-height: 100vh;
  padding: var(--spacing-xl) 0;
}

.page-header {
  text-align: center;
  margin-bottom: var(--spacing-2xl);
}

.page-header h1 {
  margin-bottom: var(--spacing-sm);
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.page-header .text-secondary {
  font-size: 17px;
  max-width: 600px;
  margin: 0 auto;
}

/* 标签页样式 */
.data-tabs {
  background: var(--color-bg-secondary);
  border-radius: var(--radius-lg);
  padding: var(--spacing-lg);
  box-shadow: var(--shadow-sm);
}

/* 标签页动画 */
.data-tabs :deep(.el-tabs__item) {
  font-size: 16px;
  font-weight: 500;
  padding: var(--spacing-md) var(--spacing-lg);
  transition: all 250ms ease;
}

.data-tabs :deep(.el-tabs__item:hover) {
  color: var(--color-accent);
}

.data-tabs :deep(.el-tabs__item.is-active) {
  color: var(--color-accent);
  font-weight: 600;
}

.data-tabs :deep(.el-tabs__active-bar) {
  background-color: var(--color-accent);
  height: 3px;
}

.data-tabs :deep(.el-tabs__content) {
  margin-top: var(--spacing-lg);
}

/* 响应式设计 */
@media (max-width: 734px) {
  .alternative-data-page {
    padding: var(--spacing-lg) 0;
  }

  .page-header {
    margin-bottom: var(--spacing-xl);
  }

  .page-header h1 {
    font-size: 32px;
  }

  .page-header .text-secondary {
    font-size: 14px;
    padding: 0 var(--spacing-md);
  }

  .data-tabs {
    padding: var(--spacing-md);
  }

  .data-tabs :deep(.el-tabs__item) {
    font-size: 14px;
    padding: var(--spacing-sm) var(--spacing-md);
  }
}
</style>
