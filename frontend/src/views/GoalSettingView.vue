<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { useI18n } from 'vue-i18n'
import { useGoals } from '../composables/useGoals'
import type { Goal } from '../types'
import GoalList from '../components/review/GoalList.vue'
import WeightIndicator from '../components/review/WeightIndicator.vue'

const props = defineProps<{
  reviewId: string
}>()

const { t } = useI18n()

const {
  goals,
  loading,
  error,
  totalWeight,
  isWeightValid,
  isMaxGoalsReached,
  loadGoals,
  removeGoal,
} = useGoals(props.reviewId)

const showAddModal = ref(false)
const editingGoal = ref<Goal | null>(null)

onMounted(async () => {
  await loadGoals()
})

function handleAddGoal() {
  showAddModal.value = true
}

function handleEditGoal(goal: Goal) {
  editingGoal.value = goal
}

async function handleDeleteGoal(goal: Goal) {
  if (confirm(t('goals.confirmDelete', { title: goal.title }))) {
    await removeGoal(goal.id)
  }
}

function handleSubmit() {
  // TODO: Implement submit logic
  console.log('Submit review')
}
</script>

<template>
  <div class="goal-setting-view">
    <header class="page-header">
      <div class="header-content">
        <h1>{{ t('goals.pageTitle') }}</h1>
        <p class="subtitle">{{ t('goals.pageSubtitle') }}</p>
      </div>
      <div class="header-actions">
        <button
          class="btn btn-primary"
          :disabled="isMaxGoalsReached"
          @click="handleAddGoal"
        >
          {{ t('goals.addGoal') }}
        </button>
      </div>
    </header>

    <!-- Error message -->
    <div v-if="error" class="error-banner">
      {{ error }}
    </div>

    <!-- Weight indicator -->
    <WeightIndicator :total="totalWeight" />

    <!-- Goals list -->
    <section class="goals-section">
      <GoalList
        :goals="goals"
        :loading="loading"
        @edit="handleEditGoal"
        @delete="handleDeleteGoal"
      />
    </section>

    <!-- Submit button -->
    <footer class="page-footer">
      <button
        class="btn btn-submit"
        :disabled="!isWeightValid"
        @click="handleSubmit"
      >
        {{ t('goals.submit') }}
      </button>
      <p v-if="!isWeightValid" class="submit-hint">
        {{ t('goals.submitHint') }}
      </p>
    </footer>

    <!-- TODO: Add GoalForm modal for add/edit -->
  </div>
</template>

<style scoped>
.goal-setting-view {
  max-width: 800px;
  margin: 0 auto;
  padding: 1.5rem;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 1.5rem;
}

.header-content h1 {
  margin: 0 0 0.25rem;
  font-size: 1.5rem;
  color: var(--color-navy);
}

.subtitle {
  margin: 0;
  color: var(--color-gray-600);
  font-size: 0.875rem;
}

.btn {
  padding: 0.625rem 1.25rem;
  border: none;
  border-radius: 6px;
  font-family: inherit;
  font-size: 0.875rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
}

.btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.btn-primary {
  background: var(--color-magenta);
  color: white;
}

.btn-primary:hover:not(:disabled) {
  background: #a00b5a;
}

.btn-submit {
  background: var(--color-navy);
  color: white;
  padding: 0.75rem 2rem;
}

.btn-submit:hover:not(:disabled) {
  background: #003570;
}

.error-banner {
  background: #FEE2E2;
  color: #991B1B;
  padding: 1rem;
  border-radius: 8px;
  margin-bottom: 1rem;
}

.goals-section {
  margin: 1.5rem 0;
}

.page-footer {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.75rem;
  margin-top: 2rem;
  padding-top: 1.5rem;
  border-top: 1px solid var(--color-gray-200);
}

.submit-hint {
  margin: 0;
  font-size: 0.875rem;
  color: var(--color-gray-600);
}
</style>
