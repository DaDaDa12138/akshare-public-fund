<template>
  <div class="empty-state">
    <div class="empty-icon">
      <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
        <circle cx="12" cy="12" r="10"></circle>
        <line x1="12" y1="8" x2="12" y2="12"></line>
        <line x1="12" y1="16" x2="12.01" y2="16"></line>
      </svg>
    </div>
    <div class="empty-title">{{ title }}</div>
    <div class="empty-description" v-if="description">{{ description }}</div>
    <slot name="action"></slot>
  </div>
</template>

<script setup lang="ts">
interface Props {
  title?: string
  description?: string
}

withDefaults(defineProps<Props>(), {
  title: '暂无数据',
  description: ''
})
</script>

<style scoped>
.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: var(--spacing-3xl) var(--spacing-lg);
  min-height: 200px;
}

.empty-icon {
  width: 64px;
  height: 64px;
  margin-bottom: var(--spacing-lg);
  color: var(--color-text-tertiary);
  opacity: 0;
  animation: fadeInScale 0.5s ease forwards;
}

.empty-icon svg {
  width: 100%;
  height: 100%;
}

.empty-title {
  font-size: 18px;
  font-weight: 600;
  color: var(--color-text-secondary);
  margin-bottom: var(--spacing-sm);
  opacity: 0;
  animation: fadeInUp 0.5s ease 0.1s forwards;
}

.empty-description {
  font-size: 14px;
  color: var(--color-text-tertiary);
  text-align: center;
  max-width: 400px;
  line-height: 1.6;
  opacity: 0;
  animation: fadeInUp 0.5s ease 0.2s forwards;
}

@keyframes fadeInScale {
  from {
    opacity: 0;
    transform: scale(0.8);
  }
  to {
    opacity: 1;
    transform: scale(1);
  }
}

@keyframes fadeInUp {
  from {
    opacity: 0;
    transform: translateY(10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}
</style>
