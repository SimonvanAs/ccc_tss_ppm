<script setup lang="ts">
import { onMounted, ref, computed, watch } from 'vue'
import { useI18n } from 'vue-i18n'
import { useRouter } from 'vue-router'
import { useGoals } from '../composables/useGoals'
import { useReviewHeader } from '../composables/useReviewHeader'
import { trackEvent } from '../composables/useAnalytics'
import { submitReview } from '../api/goals'
import { ApiRequestError } from '../api/client'
import { hasRole } from '../api/auth'
import { reassignManager, downloadReviewPdf } from '../api/reviews'
import type { Goal, GoalCreate } from '../types'
import type { TovLevel } from '../types/competency'
import GoalList from '../components/review/GoalList.vue'
import GoalForm from '../components/review/GoalForm.vue'
import WeightIndicator from '../components/review/WeightIndicator.vue'
import ReviewHeader from '../components/review/ReviewHeader.vue'
import CompetencyScoringSection from '../components/review/CompetencyScoringSection.vue'
import ManagerReassignModal from '../components/review/ManagerReassignModal.vue'
import type { Manager } from '../components/review/ManagerReassignModal.vue'
import SaveIndicator from '../components/common/SaveIndicator.vue'
import Modal from '../components/common/Modal.vue'
import ConfirmDialog from '../components/common/ConfirmDialog.vue'

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

// Review header data and auto-save
const {
  review,
  loading: reviewLoading,
  saveStatus,
  loadReview,
  updateJobTitle,
  updateTovLevel,
} = useReviewHeader(props.reviewId)

// Computed to check if TOV level is set
const hasTovLevel = computed(() => Boolean(review.value?.tov_level))

// Computed for header field validation
const isHeaderFieldsValid = computed(() => {
  const jobTitle = review.value?.job_title
  const tovLevel = review.value?.tov_level
  return Boolean(jobTitle && jobTitle.trim() !== '' && tovLevel && tovLevel.trim() !== '')
})

// Combined validation for submission
const canSubmit = computed(() => {
  return isWeightValid.value && isHeaderFieldsValid.value && isGoalSettingStage.value
})

// Check if current user has HR role
const isHrUser = computed(() => hasRole('hr'))

// Stage-based read-only mode: goals can only be edited during GOAL_SETTING stage
const isGoalSettingStage = computed(() => review.value?.stage === 'GOAL_SETTING')

// Read-only if not in goal setting stage or review is not in draft status
const isReadOnly = computed(() => {
  if (!review.value) return true
  return review.value.stage !== 'GOAL_SETTING' || review.value.status !== 'DRAFT'
})

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

// Manager reassignment states
const showReassignModal = ref(false)
const availableManagers = ref<Manager[]>([])
const isReassigning = ref(false)
const reassignError = ref<string | null>(null)

// Computed modal title
const editModalTitle = computed(() =>
  editingGoal.value ? t('goals.edit') : t('goals.addGoal')
)

onMounted(async () => {
  await Promise.all([loadGoals(), loadReview()])
})

// Handle header field updates (auto-save)
function handleJobTitleUpdate(value: string) {
  updateJobTitle(value)
}

function handleTovLevelUpdate(value: string) {
  updateTovLevel(value)
}

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

// Parse backend error and return user-friendly message
function getSubmitErrorMessage(error: unknown): string {
  if (error instanceof ApiRequestError) {
    const detail = error.detail.toLowerCase()

    // Check for specific error types
    if (detail.includes('draft status')) {
      return t('errors.submit.notDraft')
    }
    if (detail.includes('missing required fields') || detail.includes('job_title') || detail.includes('tov_level')) {
      return t('errors.submit.missingFields')
    }
    if (detail.includes('weights must total 100') || detail.includes('weight')) {
      // Extract current weight if available
      const match = error.detail.match(/current:\s*(\d+)%?/)
      if (match) {
        return t('errors.submit.invalidWeight', { current: match[1] })
      }
      return t('errors.submit.invalidWeightGeneric')
    }
    if (detail.includes('not found')) {
      return t('errors.submit.notFound')
    }
  }
  return t('errors.submitFailed')
}

// Handle goal submission
async function handleSubmit() {
  if (!canSubmit.value || isSubmitting.value) {
    return
  }

  isSubmitting.value = true
  submitError.value = null

  try {
    await submitReview(props.reviewId)
    submitSuccess.value = true
    trackEvent('goal_save')

    // Navigate to dashboard after short delay to show success
    setTimeout(() => {
      router.push({ name: 'Dashboard' })
    }, 1500)
  } catch (e) {
    submitError.value = getSubmitErrorMessage(e)
    isSubmitting.value = false
  }
}

// Handle PDF download
async function handleDownloadPdf() {
  try {
    const lang = localStorage.getItem('locale') || 'en'
    const blob = await downloadReviewPdf(props.reviewId, lang)
    const url = window.URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    link.download = `review-${props.reviewId}.pdf`
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    window.URL.revokeObjectURL(url)
  } catch (e) {
    console.error('Failed to download PDF:', e)
  }
}

// Handle opening reassign modal
function handleOpenReassignModal() {
  reassignError.value = null
  // TODO: Load available managers from API when endpoint is available
  // For now, the modal will show with empty list
  showReassignModal.value = true
}

// Handle closing reassign modal
function handleCloseReassignModal() {
  showReassignModal.value = false
  reassignError.value = null
}

// Handle manager reassignment submission
async function handleReassignSubmit(payload: { managerId: string; reason: string }) {
  if (!review.value) return

  isReassigning.value = true
  reassignError.value = null

  try {
    await reassignManager(props.reviewId, payload.managerId, payload.reason || undefined)
    showReassignModal.value = false
    // Reload review to show updated manager
    await loadReview()
  } catch (e) {
    reassignError.value = t('errors.reassignFailed')
  } finally {
    isReassigning.value = false
  }
}
</script>

<template>
  <div class="goal-setting-view">
    <!-- Review Header -->
    <ReviewHeader
      v-if="review"
      :review-id="reviewId"
      :employee-name="review.employee_name ?? ''"
      :manager-name="review.manager_name ?? ''"
      :review-year="review.review_year"
      :status="review.status"
      :stage="review.stage"
      :job-title="review.job_title"
      :tov-level="review.tov_level"
      :goal-setting-completed-at="review.goal_setting_completed_at"
      :mid-year-completed-at="review.mid_year_completed_at"
      :end-year-completed-at="review.end_year_completed_at"
      :is-hr-user="isHrUser"
      :readonly="isReadOnly"
      class="review-header-card"
      @update:job-title="handleJobTitleUpdate"
      @update:tov-level="handleTovLevelUpdate"
      @reassign="handleOpenReassignModal"
    />

    <!-- Save indicator for header -->
    <div v-if="review" class="save-indicator-container">
      <SaveIndicator :status="saveStatus" />
    </div>

    <!-- WHAT-axis Goals Section -->
    <div class="goals-section">
      <!-- Section Header -->
      <div class="section-header-row">
        <div class="section-header-content">
          <h2 class="section-title">{{ t('goals.whatAxisTitle') }}</h2>
          <div class="section-divider"></div>
          <p class="section-subtitle">{{ t('goals.whatAxisSubtitle') }}</p>
        </div>
        <button
          v-if="!isReadOnly"
          class="btn btn-primary"
          :disabled="isMaxGoalsReached"
          @click="handleAddGoal"
        >
          {{ t('goals.addGoal') }}
        </button>
      </div>

      <!-- Error message -->
      <div v-if="error" class="error-banner">
        {{ error }}
      </div>

      <!-- Weight indicator -->
      <div class="weight-indicator-wrapper">
        <WeightIndicator :total="totalWeight" />
      </div>

      <!-- Read-only banner when not in GOAL_SETTING stage -->
      <div v-if="isReadOnly && review" class="readonly-banner">
        {{ t('goals.readOnlyStage', { stage: t(`stageTransition.stages.${review.stage}`) }) }}
      </div>

      <!-- Goals list -->
      <GoalList
        :goals="goals"
        :loading="loading"
        :readonly="isReadOnly"
        @edit="handleEditGoal"
        @delete="handleDeleteGoal"
        @reorder="handleReorder"
      />
    </div>

    <!-- HOW-Axis Competencies Section (preview mode - no scoring) -->
    <CompetencyScoringSection
      v-if="hasTovLevel && review"
      :review-id="reviewId"
      :tov-level="(review.tov_level as TovLevel)"
      :preview-mode="true"
      data-testid="competency-scoring"
    />

    <!-- Footer Actions -->
    <div class="footer-actions">
      <!-- Success message -->
      <div v-if="submitSuccess" class="submit-success">
        {{ t('goals.submitSuccess') }}
      </div>

      <!-- Error message -->
      <div v-if="submitError" class="submit-error">
        {{ submitError }}
      </div>

      <div class="action-buttons">
        <button
          class="btn btn-secondary"
          @click="handleDownloadPdf"
        >
          {{ t('pdf.downloadDraft') }}
        </button>
        <button
          v-if="!isReadOnly"
          class="btn btn-submit"
          :disabled="!canSubmit || isSubmitting || submitSuccess"
          @click="handleSubmit"
        >
          {{ isSubmitting ? t('goals.submitting') : t('goals.submitReview') }}
        </button>
      </div>
      <p v-if="!isReadOnly && !isHeaderFieldsValid && !submitSuccess" class="submit-hint">
        {{ t('goals.headerFieldsRequired') }}
      </p>
      <p v-if="!isReadOnly && isHeaderFieldsValid && !isWeightValid && !submitSuccess" class="submit-hint">
        {{ t('goals.submitHint') }}
      </p>
    </div>

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

    <!-- Manager Reassignment Modal (HR only) -->
    <ManagerReassignModal
      v-if="review"
      :show="showReassignModal"
      :managers="availableManagers"
      :current-manager-id="review.manager_id"
      :loading="isReassigning"
      :error="reassignError ?? ''"
      @submit="handleReassignSubmit"
      @cancel="handleCloseReassignModal"
    />
  </div>
</template>

<style scoped>
.goal-setting-view {
  max-width: 800px;
  margin: 0 auto;
}

.review-header-card {
  margin-bottom: 0.5rem;
}

.save-indicator-container {
  display: flex;
  justify-content: flex-end;
  margin-bottom: 1.5rem;
  min-height: 28px;
}

/* Goals Section Styles */
.goals-section {
  background-color: var(--color-white, #ffffff);
  border-radius: 8px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1), 0 1px 2px rgba(0, 0, 0, 0.06);
  padding: 1.5rem;
  margin-bottom: 1rem;
}

.section-header-row {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 1rem;
}

.section-header-content {
  flex: 1;
}

.section-title {
  font-size: 1.125rem;
  font-weight: 700;
  color: var(--color-magenta, #CC0E70);
  margin: 0 0 0.75rem 0;
}

.section-divider {
  height: 2px;
  background-color: var(--color-magenta, #CC0E70);
  margin-bottom: 0.75rem;
}

.section-subtitle {
  font-size: 0.875rem;
  color: var(--color-gray-600, #6b7280);
  margin: 0;
}

.weight-indicator-wrapper {
  margin-top: 1rem;
  margin-bottom: 0.5rem;
}

/* Footer Actions */
.footer-actions {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 1rem;
  padding: 1.5rem 0;
}

.action-buttons {
  display: flex;
  gap: 1rem;
  justify-content: center;
}

.btn {
  padding: 0.75rem 1.5rem;
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

.btn-secondary {
  background: var(--color-gray-100, #f3f4f6);
  color: var(--color-gray-700, #374151);
  border: 1px solid var(--color-gray-300, #d1d5db);
}

.btn-secondary:hover:not(:disabled) {
  background: var(--color-gray-200, #e5e7eb);
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

.submit-hint {
  margin: 0;
  font-size: 0.875rem;
  color: var(--color-gray-600);
  text-align: center;
}

.submit-success {
  background: #D1FAE5;
  color: #065F46;
  padding: 0.75rem 1.5rem;
  border-radius: 8px;
  font-weight: 600;
  display: inline-block;
}

.submit-error {
  background: #FEE2E2;
  color: #991B1B;
  padding: 0.75rem 1.5rem;
  border-radius: 8px;
  font-weight: 500;
  display: inline-block;
}

.readonly-banner {
  background: #FEF3C7;
  color: #92400E;
  padding: 0.75rem 1rem;
  border-radius: 8px;
  font-size: 0.875rem;
  margin-bottom: 1rem;
  border: 1px solid #FCD34D;
}

/* Responsive */
@media (max-width: 640px) {
  .section-header-row {
    flex-direction: column;
  }

  .action-buttons {
    flex-direction: column;
    width: 100%;
  }

  .action-buttons .btn {
    width: 100%;
  }
}
</style>
