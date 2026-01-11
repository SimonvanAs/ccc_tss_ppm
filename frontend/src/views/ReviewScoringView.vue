<script setup lang="ts">
import { computed, ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { useScoring } from '../composables/useScoring'
import { submitScores as submitScoresApi } from '../api/scores'
import {
  fetchReview,
  signReview as signReviewApi,
  rejectReview as rejectReviewApi,
} from '../api/reviews'
import type { ReviewDetails, ReviewStatus, ReviewStage } from '../api/reviews'
import { fetchGoals } from '../api/goals'
import { getCompetencies } from '../api/competencies'
import { calculateWhatScore, calculateHowScore } from '../services/scoring'
import { getCurrentUser } from '../api/auth'
import GoalScoringSection from '../components/review/GoalScoringSection.vue'
import CompetencyScoringSection from '../components/review/CompetencyScoringSection.vue'
import NineGrid from '../components/review/NineGrid.vue'
import ScoreSummary from '../components/review/ScoreSummary.vue'
import SaveIndicator from '../components/common/SaveIndicator.vue'
import SubmitScoresButton from '../components/review/SubmitScoresButton.vue'
import SignatureStatus from '../components/review/SignatureStatus.vue'
import SignatureModal from '../components/review/SignatureModal.vue'
import RejectionModal from '../components/review/RejectionModal.vue'
import PDFDownloadButton from '../components/review/PDFDownloadButton.vue'
import { Card, SectionHeader } from '../components/layout'
import type { Goal } from '../components/review/GoalScoringSection.vue'
import type { Competency } from '../components/review/CompetencyScoringSection.vue'
import type { TovLevel } from '../types/competency'

const props = defineProps<{
  reviewId: string
}>()

const router = useRouter()
const { t } = useI18n()

// Data state
const goals = ref<Goal[]>([])
const competencies = ref<Competency[]>([])
const tovLevel = ref<TovLevel>('B')
const isDataLoading = ref(true)
const dataError = ref<string | null>(null)
const readOnly = ref(false)

// Review data for signature flow
const reviewData = ref<ReviewDetails | null>(null)
const currentUserId = ref<string | null>(null)

// Submit state
const isSubmitting = ref(false)
const submitError = ref<string | null>(null)

// Signature modal state
const showSignatureModal = ref(false)
const showRejectionModal = ref(false)
const isSigningOrRejecting = ref(false)
const signatureError = ref<string | null>(null)

const {
  goalScores,
  competencyScores,
  saveStatus,
  isLoading,
  loadError,
  allScoresComplete,
  setGoalScore,
  setGoalFeedback,
  setCompetencyScore,
  setRequiredGoals,
  setRequiredCompetencies,
  loadScores,
} = useScoring(props.reviewId)

// Calculate WHAT score from goals
const whatScoreResult = computed(() => {
  const goalScoreData = goals.value.map((g) => ({
    id: g.id,
    score: goalScores.value[g.id]?.score ?? 0,
    weight: g.weight,
    goalType: g.goal_type,
  }))

  // Only calculate if all goals have scores
  const allScored = goalScoreData.every((g) => g.score > 0)
  if (!allScored) return null

  return calculateWhatScore(goalScoreData)
})

// Calculate HOW score from competencies
const howScoreResult = computed(() => {
  const compScoreData = competencies.value.map((c) => ({
    id: c.id,
    score: competencyScores.value[c.id]?.score ?? 0,
  }))

  // Only calculate if all competencies have scores
  const allScored = compScoreData.every((c) => c.score > 0)
  if (!allScored) return null

  return calculateHowScore(compScoreData)
})

const whatScore = computed(() => whatScoreResult.value?.score ?? null)
const howScore = computed(() => howScoreResult.value?.score ?? null)
const whatVetoActive = computed(() => whatScoreResult.value?.vetoActive ?? false)
const whatVetoType = computed(() => whatScoreResult.value?.vetoReason ?? null)
const howVetoActive = computed(() => howScoreResult.value?.vetoActive ?? false)

// Signature computed properties
const reviewStatus = computed<ReviewStatus>(() => reviewData.value?.status ?? 'DRAFT')
const reviewStage = computed<ReviewStage>(() => reviewData.value?.stage ?? 'GOAL_SETTING')

const isCurrentUserEmployee = computed(() => {
  return currentUserId.value === reviewData.value?.employee_id
})

const isCurrentUserManager = computed(() => {
  return currentUserId.value === reviewData.value?.manager_id
})

// Signature visibility rules
const canEmployeeSign = computed(() => {
  return isCurrentUserEmployee.value && reviewStatus.value === 'PENDING_EMPLOYEE_SIGNATURE'
})

const canManagerSign = computed(() => {
  return isCurrentUserManager.value && reviewStatus.value === 'PENDING_MANAGER_SIGNATURE'
})

const canSign = computed(() => canEmployeeSign.value || canManagerSign.value)

const canReject = computed(() => {
  // Employee can reject when pending their signature
  if (isCurrentUserEmployee.value && reviewStatus.value === 'PENDING_EMPLOYEE_SIGNATURE') {
    return true
  }
  // Manager can reject when pending their signature
  if (isCurrentUserManager.value && reviewStatus.value === 'PENDING_MANAGER_SIGNATURE') {
    return true
  }
  return false
})

const employeeSignature = computed(() => {
  if (reviewData.value?.employee_signature_date && reviewData.value?.employee_signature_by) {
    return {
      signedBy: reviewData.value.employee_signature_by,
      signedAt: new Date(reviewData.value.employee_signature_date),
    }
  }
  return undefined
})

const managerSignature = computed(() => {
  if (reviewData.value?.manager_signature_date && reviewData.value?.manager_signature_by) {
    return {
      signedBy: reviewData.value.manager_signature_by,
      signedAt: new Date(reviewData.value.manager_signature_date),
    }
  }
  return undefined
})

const reviewSummary = computed(() => ({
  employeeName: reviewData.value?.employee_name ?? '',
  stage: reviewStage.value,
  whatScore: whatScore.value ?? undefined,
  howScore: howScore.value ?? undefined,
}))

// Event handlers
function handleGoalScoreChange(goalId: string, score: number) {
  setGoalScore(goalId, score)
}

function handleGoalFeedbackChange(goalId: string, feedback: string) {
  setGoalFeedback(goalId, feedback)
}

function handleCompetencyScoreChange(payload: { competencyId: string; score: number }) {
  setCompetencyScore(payload.competencyId, payload.score)
}

async function handleSubmit() {
  if (isSubmitting.value) return

  isSubmitting.value = true
  submitError.value = null

  try {
    await submitScoresApi(props.reviewId)
    // Reload review data to get updated status
    await loadReviewData()
  } catch (error) {
    submitError.value = error instanceof Error ? error.message : 'Submission failed'
  } finally {
    isSubmitting.value = false
  }
}

// Signature handlers
function openSignatureModal() {
  signatureError.value = null
  showSignatureModal.value = true
}

function openRejectionModal() {
  signatureError.value = null
  showRejectionModal.value = true
}

async function handleSign() {
  if (isSigningOrRejecting.value) return

  isSigningOrRejecting.value = true
  signatureError.value = null

  try {
    await signReviewApi(props.reviewId)
    showSignatureModal.value = false
    // Reload review data to get updated status
    await loadReviewData()
  } catch (error) {
    signatureError.value = error instanceof Error ? error.message : 'Signing failed'
  } finally {
    isSigningOrRejecting.value = false
  }
}

async function handleReject(feedback: string) {
  if (isSigningOrRejecting.value) return

  isSigningOrRejecting.value = true
  signatureError.value = null

  try {
    await rejectReviewApi(props.reviewId, feedback)
    showRejectionModal.value = false
    // Reload review data to get updated status
    await loadReviewData()
  } catch (error) {
    signatureError.value = error instanceof Error ? error.message : 'Rejection failed'
  } finally {
    isSigningOrRejecting.value = false
  }
}

function handlePdfError(error: Error) {
  console.error('PDF download failed:', error.message)
  // Could show a toast or notification here
}

// Load review data
async function loadReviewData() {
  isDataLoading.value = true
  dataError.value = null

  try {
    // Fetch review to get TOV level and status
    const review = await fetchReview(props.reviewId)

    // Store review data for signature flow
    reviewData.value = review

    // Check if read-only based on status (scoring is read-only unless DRAFT)
    readOnly.value = review.status !== 'DRAFT'

    // Set TOV level
    tovLevel.value = (review.tov_level as TovLevel) || 'B'

    // Fetch goals and competencies in parallel
    const [goalsData, compsData] = await Promise.all([
      fetchGoals(props.reviewId),
      review.tov_level ? getCompetencies(review.tov_level as TovLevel) : Promise.resolve([]),
    ])

    goals.value = goalsData
    competencies.value = compsData

    // Set required items for scoring composable
    setRequiredGoals(goalsData.map((g) => g.id))
    setRequiredCompetencies(compsData.map((c) => c.id))

    // Load existing scores
    await loadScores()
  } catch (error) {
    dataError.value = error instanceof Error ? error.message : 'Failed to load review data'
  } finally {
    isDataLoading.value = false
  }
}

// Initialize
onMounted(() => {
  // Get current user ID for signature visibility
  const user = getCurrentUser()
  currentUserId.value = user?.id ?? null

  loadReviewData()
})
</script>

<template>
  <div class="review-scoring-view">
    <!-- Page Header -->
    <SectionHeader title="Score Review">
      <template #actions>
        <SaveIndicator :status="saveStatus" />
      </template>
    </SectionHeader>

    <!-- Loading state -->
    <Card v-if="isDataLoading || isLoading" class="state-card">
      <div class="loading-state">
        Loading review data...
      </div>
    </Card>

    <!-- Error state -->
    <Card v-else-if="dataError || loadError" class="state-card">
      <div class="error-state">
        {{ dataError || loadError }}
      </div>
    </Card>

    <div v-else class="scoring-layout">
      <main class="scoring-main">
        <GoalScoringSection
          :goals="goals"
          :scores="goalScores"
          :disabled="readOnly"
          @score-change="handleGoalScoreChange"
          @feedback-change="handleGoalFeedbackChange"
        />

        <CompetencyScoringSection
          :review-id="props.reviewId"
          :tov-level="tovLevel"
          :disabled="readOnly"
          @score-change="handleCompetencyScoreChange"
        />

        <!-- Submit for Signature (manager only, DRAFT status) -->
        <Card v-if="!readOnly" class="submit-card">
          <div class="submit-section">
            <SubmitScoresButton
              :all-scores-complete="allScoresComplete"
              :is-submitting="isSubmitting"
              :has-error="!!submitError"
              :error-message="submitError || ''"
              @submit="handleSubmit"
            />
          </div>
        </Card>

        <!-- Signature Actions (when pending signature) -->
        <Card v-if="canSign || canReject" class="signature-actions-card">
          <div class="signature-actions">
            <p v-if="signatureError" class="signature-error">{{ signatureError }}</p>
            <div class="signature-buttons">
              <button
                v-if="canReject"
                type="button"
                class="reject-button"
                @click="openRejectionModal"
              >
                {{ t('signature.rejectReview') }}
              </button>
              <button
                v-if="canSign"
                type="button"
                class="sign-button"
                @click="openSignatureModal"
              >
                {{ t('signature.signReview') }}
              </button>
            </div>
          </div>
        </Card>
      </main>

      <aside class="scoring-sidebar">
        <Card class="sidebar-card" padding="md">
          <h3 class="sidebar-title">Performance Grid</h3>
          <NineGrid
            :what-score="whatScore"
            :how-score="howScore"
            :veto-active="whatVetoActive || howVetoActive"
            :veto-type="whatVetoType"
            compact
          />
        </Card>

        <Card class="sidebar-card" padding="md">
          <h3 class="sidebar-title">Score Summary</h3>
          <ScoreSummary
            :what-score="whatScore"
            :how-score="howScore"
            :what-veto-active="whatVetoActive"
            :what-veto-type="whatVetoType"
            :how-veto-active="howVetoActive"
            compact
          />
        </Card>

        <!-- Signature Status -->
        <Card class="sidebar-card" padding="md">
          <h3 class="sidebar-title">{{ t('signature.status.title') }}</h3>
          <SignatureStatus
            :status="reviewStatus"
            :employee-signature="employeeSignature"
            :manager-signature="managerSignature"
            :was-rejected="!!reviewData?.rejection_feedback"
          />
        </Card>

        <!-- PDF Download -->
        <Card class="sidebar-card" padding="md">
          <PDFDownloadButton
            :review-id="props.reviewId"
            :status="reviewStatus"
            :employee-name="reviewData?.employee_name ?? undefined"
            :review-year="reviewData?.review_year"
            @error="handlePdfError"
          />
        </Card>
      </aside>
    </div>

    <!-- Signature Modal -->
    <SignatureModal
      v-model="showSignatureModal"
      :review-summary="reviewSummary"
      :loading="isSigningOrRejecting"
      @sign="handleSign"
    />

    <!-- Rejection Modal -->
    <RejectionModal
      v-model="showRejectionModal"
      :review-summary="reviewSummary"
      :loading="isSigningOrRejecting"
      @reject="handleReject"
    />
  </div>
</template>

<style scoped>
.review-scoring-view {
  max-width: 1400px;
  margin: 0 auto;
}

.state-card {
  margin-top: 1rem;
}

.loading-state {
  text-align: center;
  padding: 2rem;
  color: var(--color-gray-600);
}

.error-state {
  text-align: center;
  padding: 2rem;
  color: var(--color-error);
}

.scoring-layout {
  display: grid;
  grid-template-columns: 1fr 280px;
  gap: 1.5rem;
  margin-top: 1rem;
}

@media (max-width: 1024px) {
  .scoring-layout {
    grid-template-columns: 1fr;
  }

  .scoring-sidebar {
    order: -1;
    display: flex;
    gap: 1rem;
  }

  .sidebar-card {
    flex: 1;
  }
}

@media (max-width: 768px) {
  .scoring-sidebar {
    flex-direction: column;
  }

  .sidebar-card {
    flex: none;
  }

  .scoring-main {
    gap: 1.5rem;
  }

  .submit-section {
    justify-content: center;
  }
}

@media (max-width: 480px) {
  .scoring-layout {
    gap: 1rem;
  }
}

.scoring-main {
  display: flex;
  flex-direction: column;
  gap: 2rem;
}

.submit-card {
  margin-top: 1rem;
}

.submit-section {
  display: flex;
  justify-content: flex-end;
}

.scoring-sidebar {
  display: flex;
  flex-direction: column;
  gap: 1rem;
  position: sticky;
  top: 1rem;
  align-self: start;
}

.sidebar-title {
  font-size: 0.875rem;
  font-weight: 600;
  color: var(--color-gray-600);
  margin: 0 0 1rem;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

/* Signature Actions */
.signature-actions-card {
  margin-top: 1rem;
}

.signature-actions {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.signature-error {
  margin: 0;
  padding: 0.75rem;
  background: rgba(220, 38, 38, 0.1);
  border-radius: 6px;
  color: var(--color-error, #dc2626);
  font-size: 0.875rem;
}

.signature-buttons {
  display: flex;
  justify-content: flex-end;
  gap: 0.75rem;
}

.sign-button,
.reject-button {
  padding: 0.625rem 1.25rem;
  font-size: 0.9375rem;
  font-weight: 500;
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.2s;
}

.sign-button {
  background: var(--color-magenta, #CC0E70);
  border: none;
  color: white;
}

.sign-button:hover {
  background: #a30b5a;
}

.reject-button {
  background: var(--color-white, #fff);
  border: 1px solid var(--color-gray-300, #d1d5db);
  color: var(--color-gray-700, #374151);
}

.reject-button:hover {
  background: var(--color-gray-50, #f9fafb);
  border-color: var(--color-gray-400, #9ca3af);
}

@media (max-width: 480px) {
  .signature-buttons {
    flex-direction: column;
  }

  .sign-button,
  .reject-button {
    width: 100%;
  }
}
</style>
