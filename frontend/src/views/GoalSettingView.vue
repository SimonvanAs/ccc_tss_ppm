<script setup lang="ts">
import { onMounted, ref, computed } from 'vue'
import { useI18n } from 'vue-i18n'
import { useRouter } from 'vue-router'
import { useGoals } from '../composables/useGoals'
import { submitReview } from '../api/goals'
import type { Goal, GoalCreate } from '../types'
import GoalList from '../components/review/GoalList.vue'
import GoalForm from '../components/review/GoalForm.vue'
import WeightIndicator from '../components/review/WeightIndicator.vue'
import Modal from '../components/common/Modal.vue'
import ConfirmDialog from '../components/common/ConfirmDialog.vue'
import { Card, SectionHeader } from '../components/layout'

const props = defineProps<{
  reviewId: string
}>()

const router = useRouter()

const { t } = useI18n()

const {
  goals,
  loading,
  error,
  totalWeight,
  isWeightValid,
  isMaxGoalsReached,
  loadGoals,
  addGoal,
  editGoal,
  removeGoal,
  setGoalOrder,
} = useGoals(props.reviewId)

// Modal states
const showAddModal = ref(false)
const showEditModal = ref(false)
const showDeleteDialog = ref(false)
const editingGoal = ref<Goal | null>(null)
const deletingGoal = ref<Goal | null>(null)
const isSaving = ref(false)

// Submission states
const isSubmitting = ref(false)
const submitSuccess = ref(false)
const submitError = ref<string | null>(null)

// Computed modal title
const editModalTitle = computed(() =>
  editingGoal.value ? t('goals.edit') : t('goals.addGoal')
)

onMounted(async () => {
  await loadGoals()
})

// Handle add goal button click
function handleAddGoal() {
  editingGoal.value = null
  showAddModal.value = true
}

// Handle edit button click on a goal
function handleEditGoal(goal: Goal) {
  editingGoal.value = goal
  showEditModal.value = true
}

// Handle delete button click on a goal
function handleDeleteGoal(goal: Goal) {
  deletingGoal.value = goal
  showDeleteDialog.value = true
}

// Handle form submission for new goal
async function handleCreateGoal(data: GoalCreate) {
  isSaving.value = true
  try {
    await addGoal(data)
    showAddModal.value = false
  } catch (e) {
    // Error is handled by useGoals composable
  } finally {
    isSaving.value = false
  }
}

// Handle form submission for editing existing goal
async function handleUpdateGoal(data: GoalCreate) {
  if (!editingGoal.value) return

  isSaving.value = true
  try {
    await editGoal(editingGoal.value.id, data)
    showEditModal.value = false
    editingGoal.value = null
  } catch (e) {
    // Error is handled by useGoals composable
  } finally {
    isSaving.value = false
  }
}

// Handle delete confirmation
async function handleConfirmDelete() {
  if (!deletingGoal.value) return

  try {
    await removeGoal(deletingGoal.value.id)
    showDeleteDialog.value = false
    deletingGoal.value = null
  } catch (e) {
    // Error is handled by useGoals composable
  }
}

// Handle cancel actions
function handleCancelAdd() {
  showAddModal.value = false
}

function handleCancelEdit() {
  showEditModal.value = false
  editingGoal.value = null
}

function handleCancelDelete() {
  showDeleteDialog.value = false
  deletingGoal.value = null
}

// Handle goal reordering
async function handleReorder(goalIds: string[]) {
  try {
    await setGoalOrder(goalIds)
  } catch (e) {
    // Error is handled by useGoals composable
  }
}

// Handle goal submission
async function handleSubmit() {
  if (!isWeightValid.value || isSubmitting.value) {
    return
  }

  isSubmitting.value = true
  submitError.value = null

  try {
    await submitReview(props.reviewId)
    submitSuccess.value = true

    // Navigate to dashboard after short delay to show success
    setTimeout(() => {
      router.push({ name: 'dashboard' })
    }, 1500)
  } catch (e) {
    submitError.value = t('errors.submitFailed')
    isSubmitting.value = false
  }
}
</script>

<template>
  <div class="goal-setting-view">
    <!-- Page Header -->
    <SectionHeader :title="t('goals.pageTitle')">
      <template #subtitle>
        {{ t('goals.pageSubtitle') }}
      </template>
      <template #actions>
        <button
          class="btn btn-primary"
          :disabled="isMaxGoalsReached"
          @click="handleAddGoal"
        >
          {{ t('goals.addGoal') }}
        </button>
      </template>
    </SectionHeader>

    <!-- Error message -->
    <div v-if="error" class="error-banner">
      {{ error }}
    </div>

    <!-- Weight indicator -->
    <Card padding="sm" class="weight-card">
      <WeightIndicator :total="totalWeight" />
    </Card>

    <!-- Goals list -->
    <Card class="goals-card">
      <GoalList
        :goals="goals"
        :loading="loading"
        @edit="handleEditGoal"
        @delete="handleDeleteGoal"
        @reorder="handleReorder"
      />
    </Card>

    <!-- Submit section -->
    <Card class="submit-card">
      <!-- Success message -->
      <div v-if="submitSuccess" class="submit-success">
        {{ t('goals.submitSuccess') }}
      </div>

      <!-- Error message -->
      <div v-if="submitError" class="submit-error">
        {{ submitError }}
      </div>

      <div class="submit-actions">
        <button
          class="btn btn-submit"
          :disabled="!isWeightValid || isSubmitting || submitSuccess"
          @click="handleSubmit"
        >
          {{ isSubmitting ? t('goals.submitting') : t('goals.submit') }}
        </button>
        <p v-if="!isWeightValid && !submitSuccess" class="submit-hint">
          {{ t('goals.submitHint') }}
        </p>
      </div>
    </Card>

    <!-- Add Goal Modal -->
    <Modal
      :show="showAddModal"
      :title="t('goals.addGoal')"
      @close="handleCancelAdd"
    >
      <GoalForm
        :review-id="reviewId"
        :loading="isSaving"
        @save="handleCreateGoal"
        @cancel="handleCancelAdd"
      />
    </Modal>

    <!-- Edit Goal Modal -->
    <Modal
      :show="showEditModal"
      :title="t('goals.edit')"
      @close="handleCancelEdit"
    >
      <GoalForm
        v-if="editingGoal"
        :review-id="reviewId"
        :goal="editingGoal"
        :loading="isSaving"
        @save="handleUpdateGoal"
        @cancel="handleCancelEdit"
      />
    </Modal>

    <!-- Delete Confirmation Dialog -->
    <ConfirmDialog
      :show="showDeleteDialog"
      :title="t('goals.deleteGoal')"
      :message="deletingGoal ? t('goals.confirmDelete', { title: deletingGoal.title }) : ''"
      :confirm-text="t('actions.delete')"
      danger
      @confirm="handleConfirmDelete"
      @cancel="handleCancelDelete"
    />
  </div>
</template>

<style scoped>
.goal-setting-view {
  max-width: 800px;
  margin: 0 auto;
}

.weight-card {
  margin-bottom: 1rem;
}

.goals-card {
  margin-bottom: 1.5rem;
}

.submit-card {
  text-align: center;
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

.submit-actions {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.75rem;
}

.submit-hint {
  margin: 0;
  font-size: 0.875rem;
  color: var(--color-gray-600);
}

.submit-success {
  background: #D1FAE5;
  color: #065F46;
  padding: 0.75rem 1.5rem;
  border-radius: 8px;
  font-weight: 600;
  margin-bottom: 1rem;
  display: inline-block;
}

.submit-error {
  background: #FEE2E2;
  color: #991B1B;
  padding: 0.75rem 1.5rem;
  border-radius: 8px;
  font-weight: 500;
  margin-bottom: 1rem;
  display: inline-block;
}
</style>
