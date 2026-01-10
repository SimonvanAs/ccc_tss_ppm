<script setup lang="ts">
import { useI18n } from 'vue-i18n'
import type { Goal } from '../../types'
import GoalItem from './GoalItem.vue'

defineProps<{
  goals: Goal[]
  loading?: boolean
  readonly?: boolean
}>()

const emit = defineEmits<{
  edit: [goal: Goal]
  delete: [goal: Goal]
}>()

const { t } = useI18n()
</script>

<template>
  <div class="goal-list">
    <!-- Loading state -->
    <div v-if="loading" class="loading-state">
      <div class="spinner"></div>
      <p>{{ t('goals.loading') }}</p>
    </div>

    <!-- Empty state -->
    <div v-else-if="goals.length === 0" class="empty-state">
      <div class="empty-icon">📋</div>
      <h3>{{ t('goals.emptyTitle') }}</h3>
      <p>{{ t('goals.emptyDescription') }}</p>
    </div>

    <!-- Goal list -->
    <div v-else class="goals">
      <GoalItem
        v-for="goal in goals"
        :key="goal.id"
        :goal="goal"
        :readonly="readonly"
        @edit="emit('edit', $event)"
        @delete="emit('delete', $event)"
      />
    </div>
  </div>
</template>

<style scoped>
.goal-list {
  min-height: 200px;
}

.loading-state,
.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 3rem 1rem;
  text-align: center;
  color: var(--color-gray-600);
}

.spinner {
  width: 40px;
  height: 40px;
  border: 3px solid var(--color-gray-200);
  border-top-color: var(--color-magenta);
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin-bottom: 1rem;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

.empty-icon {
  font-size: 3rem;
  margin-bottom: 1rem;
}

.empty-state h3 {
  margin: 0 0 0.5rem;
  color: var(--color-gray-900);
}

.empty-state p {
  margin: 0;
  font-size: 0.875rem;
}

.goals {
  display: flex;
  flex-direction: column;
}
</style>
