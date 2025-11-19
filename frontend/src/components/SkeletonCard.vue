<template>
  <div class="skeleton-card">
    <div class="skeleton-header">
      <div class="skeleton-title"></div>
      <div class="skeleton-subtitle"></div>
    </div>
    <div class="skeleton-content">
      <div class="skeleton-line" v-for="i in lines" :key="i" :style="{ width: getLineWidth(i) }"></div>
    </div>
  </div>
</template>

<script setup lang="ts">
interface Props {
  lines?: number
}

const props = withDefaults(defineProps<Props>(), {
  lines: 3
})

const getLineWidth = (index: number) => {
  // 最后一行随机短一些,模拟真实内容
  if (index === props.lines) {
    return `${60 + Math.random() * 30}%`
  }
  return '100%'
}
</script>

<style scoped>
.skeleton-card {
  background: var(--color-bg-secondary);
  border-radius: var(--radius-lg);
  padding: var(--spacing-lg);
  box-shadow: var(--shadow-sm);
}

.skeleton-header {
  margin-bottom: var(--spacing-md);
}

.skeleton-title {
  height: 24px;
  width: 40%;
  background: linear-gradient(
    90deg,
    var(--color-bg-tertiary) 0%,
    var(--color-border-light) 50%,
    var(--color-bg-tertiary) 100%
  );
  background-size: 200% 100%;
  animation: shimmer 1.5s infinite;
  border-radius: var(--radius-sm);
  margin-bottom: var(--spacing-sm);
}

.skeleton-subtitle {
  height: 16px;
  width: 30%;
  background: linear-gradient(
    90deg,
    var(--color-bg-tertiary) 0%,
    var(--color-border-light) 50%,
    var(--color-bg-tertiary) 100%
  );
  background-size: 200% 100%;
  animation: shimmer 1.5s infinite;
  border-radius: var(--radius-sm);
}

.skeleton-content {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-sm);
}

.skeleton-line {
  height: 20px;
  background: linear-gradient(
    90deg,
    var(--color-bg-tertiary) 0%,
    var(--color-border-light) 50%,
    var(--color-bg-tertiary) 100%
  );
  background-size: 200% 100%;
  animation: shimmer 1.5s infinite;
  border-radius: var(--radius-sm);
}

@keyframes shimmer {
  0% {
    background-position: 200% 0;
  }
  100% {
    background-position: -200% 0;
  }
}
</style>
