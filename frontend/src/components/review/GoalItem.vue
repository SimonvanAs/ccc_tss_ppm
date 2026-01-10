<script setup lang="ts">
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'
import type { Goal } from '../../types'
import { GoalType } from '../../types'

const props = defineProps<{
  goal: Goal
  readonly?: boolean
}>()

const emit = defineEmits<{
  edit: [goal: Goal]
  delete: [goal: Goal]
}>()

const { t } = useI18n()

const goalTypeBadgeClass = computed(() => {
  switch (props.goal.goal_type) {
    case GoalType.KAR:
      return 'badge-kar'
    case GoalType.SCF:
      return 'badge-scf'
    default:
      return 'badge-standard'
  }
})

const goalTypeLabel = computed(() => {
  switch (props.goal.goal_type) {
    case GoalType.KAR:
      return 'KAR'
    case GoalType.SCF:
      return 'SCF'
    default:
      return t('goals.typeStandard')
  }
})

function handleEdit() {
  emit('edit', props.goal)
}

function handleDelete() {
  emit('delete', props.goal)
}
</script>

<template>
  <div class="goal-item">
    <div class="goal-content">
      <div class="goal-header">
        <span :class="['goal-type-badge', goalTypeBadgeClass]">
          {{ goalTypeLabel }}
        </span>
        <span class="goal-weight">{{ goal.weight }}%</span>
      </div>
      <h3 class="goal-title">{{ goal.title }}</h3>
      <p v-if="goal.description" class="goal-description">
        {{ goal.description }}
      </p>
    </div>
    <div v-if="!readonly" class="goal-actions">
      <button
        class="btn-icon btn-edit"
        :title="t('goals.edit')"
        @click="handleEdit"
      >
        <span class="icon">✏️</span>
      </button>
      <button
        class="btn-icon btn-delete"
        :title="t('goals.delete')"
        @click="handleDelete"
      >
        <span class="icon">🗑️</span>
      </button>
    </div>
  </div>
</template>

<style scoped>
.goal-item {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  background: var(--color-white);
  border: 1px solid var(--color-gray-200);
  border-radius: 8px;
  padding: 1rem;
  margin-bottom: 0.75rem;
}

.goal-content {
  flex: 1;
}

.goal-header {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  margin-bottom: 0.5rem;
}

.goal-type-badge {
  font-size: 0.75rem;
  font-weight: bold;
  padding: 0.25rem 0.5rem;
  border-radius: 4px;
  text-transform: uppercase;
}

.badge-standard {
  background: var(--color-gray-200);
  color: var(--color-gray-600);
}

.badge-kar {
  background: #FEF3C7;
  color: #92400E;
}

.badge-scf {
  background: #FEE2E2;
  color: #991B1B;
}

.goal-weight {
  font-size: 0.875rem;
  font-weight: bold;
  color: var(--color-navy);
}

.goal-title {
  margin: 0;
  font-size: 1rem;
  color: var(--color-gray-900);
}

.goal-description {
  margin: 0.5rem 0 0;
  font-size: 0.875rem;
  color: var(--color-gray-600);
  line-height: 1.4;
}

.goal-actions {
  display: flex;
  gap: 0.5rem;
  margin-left: 1rem;
}

.btn-icon {
  background: transparent;
  border: 1px solid var(--color-gray-200);
  border-radius: 4px;
  padding: 0.5rem;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-icon:hover {
  background: var(--color-gray-100);
}

.btn-edit:hover {
  border-color: var(--color-navy);
}

.btn-delete:hover {
  border-color: var(--color-grid-red);
}

.icon {
  font-size: 1rem;
}
</style>
