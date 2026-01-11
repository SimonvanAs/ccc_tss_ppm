<script setup lang="ts">
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'

const props = defineProps<{
  total: number
  target?: number
}>()

const { t } = useI18n()

const targetWeight = computed(() => props.target ?? 100)

const isValid = computed(() => props.total === targetWeight.value)
const isOverweight = computed(() => props.total > targetWeight.value)

const statusClass = computed(() => {
  if (isValid.value) return 'status-valid'
  if (isOverweight.value) return 'status-overweight'
  return 'status-underweight'
})

const statusIcon = computed(() => {
  if (isValid.value) return '✓'
  return '!'
})

const percentage = computed(() => {
  return Math.min((props.total / targetWeight.value) * 100, 100)
})
</script>

<template>
  <div :class="['weight-indicator', statusClass]">
    <div class="weight-bar">
      <div class="weight-progress" :style="{ width: `${percentage}%` }"></div>
    </div>
    <div class="weight-info">
      <span class="weight-status">
        <span class="status-icon">{{ statusIcon }}</span>
        <span class="weight-value">{{ total }}%</span>
        <span class="weight-separator">/</span>
        <span class="weight-target">{{ targetWeight }}%</span>
      </span>
      <span class="weight-message">
        <template v-if="isValid">
          {{ t('goals.weightValid') }}
        </template>
        <template v-else-if="isOverweight">
          {{ t('goals.weightOver', { amount: total - targetWeight }) }}
        </template>
        <template v-else>
          {{ t('goals.weightUnder', { amount: targetWeight - total }) }}
        </template>
      </span>
    </div>
  </div>
</template>

<style scoped>
.weight-indicator {
  padding: 0.75rem 0;
}

.weight-bar {
  height: 4px;
  background: var(--color-gray-200);
  border-radius: 2px;
  overflow: hidden;
  margin-bottom: 0.5rem;
}

.weight-progress {
  height: 100%;
  border-radius: 2px;
  transition: width 0.3s ease;
}

.status-valid .weight-progress {
  background: var(--color-grid-green);
}

.status-underweight .weight-progress {
  background: var(--color-grid-orange);
}

.status-overweight .weight-progress {
  background: var(--color-grid-red);
}

.weight-info {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.weight-status {
  display: flex;
  align-items: center;
  gap: 0.25rem;
  font-weight: 600;
}

.status-icon {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 16px;
  height: 16px;
  border-radius: 50%;
  font-size: 0.625rem;
  margin-right: 0.25rem;
}

.status-valid .status-icon {
  background: var(--color-grid-green);
  color: white;
}

.status-underweight .status-icon,
.status-overweight .status-icon {
  background: var(--color-grid-orange);
  color: white;
}

.status-overweight .status-icon {
  background: var(--color-grid-red);
}

.weight-value {
  font-size: 0.875rem;
}

.status-valid .weight-value {
  color: var(--color-grid-green);
}

.status-underweight .weight-value {
  color: var(--color-grid-orange);
}

.status-overweight .weight-value {
  color: var(--color-grid-red);
}

.weight-separator {
  color: var(--color-gray-500);
  margin: 0 0.125rem;
  font-size: 0.875rem;
}

.weight-target {
  color: var(--color-gray-500);
  font-size: 0.875rem;
}

.weight-message {
  font-size: 0.75rem;
  color: var(--color-gray-500);
}
</style>
