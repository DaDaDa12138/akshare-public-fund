<template>
  <div class="theme-switch">
    <el-dropdown trigger="click" @command="handleCommand">
      <el-button circle :title="getThemeLabel()">
        <el-icon :size="18">
          <component :is="iconComponent" />
        </el-icon>
      </el-button>
      <template #dropdown>
        <el-dropdown-menu>
          <el-dropdown-item
            command="light"
            :class="{ active: currentTheme === 'light' }"
          >
            <el-icon><Sunny /></el-icon>
            <span>浅色模式</span>
          </el-dropdown-item>
          <el-dropdown-item
            command="dark"
            :class="{ active: currentTheme === 'dark' }"
          >
            <el-icon><Moon /></el-icon>
            <span>深色模式</span>
          </el-dropdown-item>
          <el-dropdown-item
            command="auto"
            :class="{ active: currentTheme === 'auto' }"
          >
            <el-icon><Monitor /></el-icon>
            <span>跟随系统</span>
          </el-dropdown-item>
        </el-dropdown-menu>
      </template>
    </el-dropdown>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { Sunny, Moon, Monitor } from '@element-plus/icons-vue'
import { useTheme, type ThemeMode } from '@/composables/useTheme'

const { currentTheme, setTheme, getThemeLabel } = useTheme()

// 根据当前主题选择图标组件
const iconComponent = computed(() => {
  switch (currentTheme.value) {
    case 'light':
      return Sunny
    case 'dark':
      return Moon
    case 'auto':
      return Monitor
    default:
      return Monitor
  }
})

function handleCommand(command: ThemeMode) {
  setTheme(command)
}
</script>

<style scoped>
.theme-switch {
  display: inline-flex;
  align-items: center;
}

.theme-switch :deep(.el-button) {
  background: var(--color-bg-secondary);
  border-color: var(--color-border);
  color: var(--color-text-primary);
  transition: all var(--transition-base);
}

.theme-switch :deep(.el-button:hover) {
  background: var(--color-bg-tertiary);
  border-color: var(--color-accent);
  color: var(--color-accent);
}

:deep(.el-dropdown-menu__item) {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 16px;
}

:deep(.el-dropdown-menu__item.active) {
  color: var(--color-accent);
  font-weight: 500;
}

:deep(.el-dropdown-menu__item .el-icon) {
  font-size: 16px;
}
</style>
