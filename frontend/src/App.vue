<template>
  <div class="app">
    <!-- 导航栏 -->
    <nav class="navbar glass">
      <div class="container navbar-content">
        <div class="navbar-brand">
          <h2>AkShare 基金数据平台</h2>
        </div>
        <div class="navbar-menu">
          <router-link to="/" class="nav-link">基金搜索</router-link>
          <router-link to="/chart" class="nav-link">净值走势</router-link>
          <router-link to="/ranking" class="nav-link">基金排行</router-link>
          <router-link to="/money" class="nav-link">货币基金</router-link>
          <router-link to="/dividend" class="nav-link">分红排行</router-link>
          <router-link to="/compare" class="nav-link">基金对比</router-link>
          <router-link to="/favorites" class="nav-link">自选基金</router-link>
          <router-link to="/alternative" class="nav-link">另类数据</router-link>
          <router-link to="/admin" class="nav-link">数据管理</router-link>
          <ThemeSwitch />
        </div>
      </div>
    </nav>

    <!-- 主内容区 -->
    <main class="main-content">
      <router-view v-slot="{ Component }">
        <transition name="fade" mode="out-in">
          <component :is="Component" />
        </transition>
      </router-view>
    </main>

    <!-- 页脚 -->
    <footer class="footer">
      <div class="container">
        <p class="text-secondary text-center">
          Powered by AkShare | 数据仅供参考，不构成投资建议
        </p>
      </div>
    </footer>
  </div>
</template>

<script setup lang="ts">
import { onMounted } from 'vue'
import { useFundStore } from '@/stores/fund'
import { useFavoritesStore } from '@/stores/favorites'
import { useTheme } from '@/composables/useTheme'
import ThemeSwitch from '@/components/ThemeSwitch.vue'

const fundStore = useFundStore()
const favoritesStore = useFavoritesStore()
const { initTheme } = useTheme()

// 预加载基金列表和收藏列表，初始化主题
onMounted(() => {
  initTheme()
  fundStore.loadFundList()
  favoritesStore.loadFavorites()
})
</script>

<style scoped>
.app {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
}

.navbar {
  position: sticky;
  top: 0;
  z-index: 100;
  border-bottom: 1px solid var(--color-border);
}

.navbar-content {
  display: flex;
  align-items: center;
  justify-content: space-between;
  height: 64px;
}

.navbar-brand h2 {
  font-size: 21px;
  font-weight: 600;
  margin: 0;
  background: linear-gradient(90deg, var(--color-text-primary), var(--color-accent));
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.navbar-menu {
  display: flex;
  gap: var(--spacing-lg);
}

.nav-link {
  position: relative;
  padding: var(--spacing-sm) 0;
  font-size: 17px;
  color: var(--color-text-primary);
  text-decoration: none;
  transition: color var(--transition-base);
}

.nav-link:hover {
  color: var(--color-accent);
}

.nav-link::after {
  content: '';
  position: absolute;
  bottom: 0;
  left: 0;
  width: 0;
  height: 2px;
  background-color: var(--color-accent);
  transition: width var(--transition-base);
}

.nav-link:hover::after,
.nav-link.router-link-active::after {
  width: 100%;
}

.router-link-active {
  color: var(--color-accent);
}

.main-content {
  flex: 1;
  padding: var(--spacing-2xl) 0;
}

.footer {
  padding: var(--spacing-lg) 0;
  border-top: 1px solid var(--color-border);
  background-color: var(--color-bg-secondary);
}

/* 页面切换动画 */
.fade-enter-active,
.fade-leave-active {
  transition: opacity var(--transition-base), transform var(--transition-base);
}

.fade-enter-from {
  opacity: 0;
  transform: translateY(10px);
}

.fade-leave-to {
  opacity: 0;
  transform: translateY(-10px);
}

@media (max-width: 734px) {
  .navbar-brand h2 {
    font-size: 17px;
  }

  .navbar-menu {
    gap: var(--spacing-md);
  }

  .nav-link {
    font-size: 15px;
  }

  .main-content {
    padding: var(--spacing-lg) 0;
  }
}
</style>
