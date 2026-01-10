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
  background: var(--color-white);
  border: 1px solid var(--color-gray-200);
  border-radius: 8px;
  padding: 1rem;
}

.weight-bar {
  height: 8px;
  background: var(--color-gray-200);
  border-radius: 4px;
  overflow: hidden;
  margin-bottom: 0.75rem;
}

.weight-progress {
  height: 100%;
  border-radius: 4px;
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
  font-weight: bold;
}

.status-icon {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 20px;
  height: 20px;
  border-radius: 50%;
  font-size: 0.75rem;
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
  font-size: 1.25rem;
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
  color: var(--color-gray-600);
  margin: 0 0.125rem;
}

.weight-target {
  color: var(--color-gray-600);
  font-size: 1rem;
}

.weight-message {
  font-size: 0.875rem;
  color: var(--color-gray-600);
}
</style>
