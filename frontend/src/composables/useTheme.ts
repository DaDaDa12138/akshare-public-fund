/**
 * 主题切换 Composable
 * 支持浅色、深色和自动（跟随系统）三种模式
 */
import { ref, watch, onMounted } from 'vue'

export type ThemeMode = 'light' | 'dark' | 'auto'

// 全局状态（在所有组件间共享）
const currentTheme = ref<ThemeMode>('auto')
const effectiveTheme = ref<'light' | 'dark'>('light')

// 系统主题变化监听器
let mediaQuery: MediaQueryList | null = null

/**
 * 获取系统偏好的主题
 */
function getSystemTheme(): 'light' | 'dark' {
  if (window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches) {
    return 'dark'
  }
  return 'light'
}

/**
 * 计算实际生效的主题
 */
function computeEffectiveTheme(mode: ThemeMode): 'light' | 'dark' {
  if (mode === 'auto') {
    return getSystemTheme()
  }
  return mode
}

/**
 * 应用主题到 DOM
 */
function applyTheme(theme: 'light' | 'dark') {
  const root = document.documentElement

  if (theme === 'dark') {
    root.setAttribute('data-theme', 'dark')
  } else {
    root.setAttribute('data-theme', 'light')
  }

  effectiveTheme.value = theme
}

/**
 * 保存主题设置到 localStorage
 */
function saveThemePreference(mode: ThemeMode) {
  localStorage.setItem('theme-preference', mode)
}

/**
 * 从 localStorage 加载主题设置
 */
function loadThemePreference(): ThemeMode {
  const saved = localStorage.getItem('theme-preference')
  if (saved === 'light' || saved === 'dark' || saved === 'auto') {
    return saved
  }
  return 'auto'
}

/**
 * 主题切换 Composable
 */
export function useTheme() {
  /**
   * 设置主题模式
   */
  function setTheme(mode: ThemeMode) {
    currentTheme.value = mode
    saveThemePreference(mode)

    const effective = computeEffectiveTheme(mode)
    applyTheme(effective)
  }

  /**
   * 切换主题（在三种模式间循环）
   */
  function toggleTheme() {
    const modes: ThemeMode[] = ['light', 'dark', 'auto']
    const currentIndex = modes.indexOf(currentTheme.value)
    const nextIndex = (currentIndex + 1) % modes.length
    setTheme(modes[nextIndex])
  }

  /**
   * 切换浅色/深色（忽略自动模式）
   */
  function toggleLightDark() {
    if (effectiveTheme.value === 'light') {
      setTheme('dark')
    } else {
      setTheme('light')
    }
  }

  /**
   * 初始化主题系统
   */
  function initTheme() {
    // 加载保存的设置
    const savedMode = loadThemePreference()
    currentTheme.value = savedMode

    // 应用主题
    const effective = computeEffectiveTheme(savedMode)
    applyTheme(effective)

    // 监听系统主题变化
    if (window.matchMedia) {
      mediaQuery = window.matchMedia('(prefers-color-scheme: dark)')

      const handleSystemThemeChange = () => {
        if (currentTheme.value === 'auto') {
          const newEffective = computeEffectiveTheme('auto')
          applyTheme(newEffective)
        }
      }

      // 使用新的 API 或回退到旧 API
      if (mediaQuery.addEventListener) {
        mediaQuery.addEventListener('change', handleSystemThemeChange)
      } else if (mediaQuery.addListener) {
        // @ts-ignore - 兼容旧浏览器
        mediaQuery.addListener(handleSystemThemeChange)
      }
    }
  }

  /**
   * 获取主题图标
   */
  function getThemeIcon(): string {
    switch (currentTheme.value) {
      case 'light':
        return 'Sunny'
      case 'dark':
        return 'Moon'
      case 'auto':
        return 'Monitor'
      default:
        return 'Monitor'
    }
  }

  /**
   * 获取主题标签
   */
  function getThemeLabel(): string {
    switch (currentTheme.value) {
      case 'light':
        return '浅色模式'
      case 'dark':
        return '深色模式'
      case 'auto':
        return '跟随系统'
      default:
        return '跟随系统'
    }
  }

  // 组件挂载时初始化
  onMounted(() => {
    initTheme()
  })

  return {
    currentTheme,
    effectiveTheme,
    setTheme,
    toggleTheme,
    toggleLightDark,
    initTheme,
    getThemeIcon,
    getThemeLabel
  }
}
