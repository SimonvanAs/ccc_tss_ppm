<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useI18n } from 'vue-i18n'
import { useRouter } from 'vue-router'
import { getCurrentUser, logout } from '../api/auth'
import { Card, SectionHeader } from '../components/layout'
import { getReviewForUser, type ReviewDetails } from '../api/reviews'

const { t } = useI18n()
const router = useRouter()
const user = getCurrentUser()

// Get the first name from the user's full name
const firstName = computed(() => {
  if (!user?.name) return ''
  return user.name.split(' ')[0]
})

// Current year for the workflow
const currentYear = new Date().getFullYear()

// Review data for current year
const currentReview = ref<ReviewDetails | null>(null)
const loading = ref(true)

// Historical reviews (previous years)
const historicalReviews = ref<ReviewDetails[]>([])

// Workflow steps configuration
type WorkflowStatus = 'notStarted' | 'inProgress' | 'pendingApproval' | 'completed'

interface WorkflowStep {
  id: string
  labelKey: string
  stage: string
}

const workflowSteps: WorkflowStep[] = [
  { id: 'goals', labelKey: 'dashboard.workflow.goals', stage: 'GOAL_SETTING' },
  { id: 'midYear', labelKey: 'dashboard.workflow.midYear', stage: 'MID_YEAR_REVIEW' },
  { id: 'endYear', labelKey: 'dashboard.workflow.endYear', stage: 'END_YEAR_REVIEW' },
]

// Check if current year review exists
const hasCurrentReview = computed(() => currentReview.value !== null)

// Get review stage and status with fallbacks
const reviewStage = computed(() => currentReview.value?.stage || 'GOAL_SETTING')
const reviewStatus = computed(() => currentReview.value?.status || 'DRAFT')

// Determine status for each workflow step based on review stage and status
function getStepStatus(step: WorkflowStep): WorkflowStatus {
  // If no review exists, all steps are not started
  if (!hasCurrentReview.value) {
    return 'notStarted'
  }

  const stageOrder = ['GOAL_SETTING', 'MID_YEAR_REVIEW', 'END_YEAR_REVIEW']
  const currentStageIndex = stageOrder.indexOf(reviewStage.value)
  const stepStageIndex = stageOrder.indexOf(step.stage)

  // If step is before current stage, it's completed
  if (stepStageIndex < currentStageIndex) {
    return 'completed'
  }

  // If step is after current stage, it's not started
  if (stepStageIndex > currentStageIndex) {
    return 'notStarted'
  }

  // Step is current stage - check review status
  if (reviewStatus.value === 'SIGNED' || reviewStatus.value === 'ARCHIVED') {
    return 'completed'
  }
  if (reviewStatus.value.includes('PENDING') || reviewStatus.value.includes('EMPLOYEE_SIGNED')) {
    return 'pendingApproval'
  }
  return 'inProgress'
}

// Check if step is clickable (current or completed, and review exists)
function isStepClickable(step: WorkflowStep): boolean {
  if (!hasCurrentReview.value) return false
  const status = getStepStatus(step)
  return status !== 'notStarted'
}

// Get status message for a step
function getStatusMessage(step: WorkflowStep): string {
  const status = getStepStatus(step)
  return t(`dashboard.workflow.statusMessages.${step.id}.${status}`)
}

// Navigate to review when clicking a step
function handleStepClick(step: WorkflowStep) {
  if (!isStepClickable(step) || !currentReview.value?.id) return

  // Navigate to goal setting or review scoring based on stage
  if (step.stage === 'GOAL_SETTING') {
    router.push({ name: 'goal-setting', params: { reviewId: currentReview.value.id } })
  } else {
    router.push({ name: 'review-scoring', params: { reviewId: currentReview.value.id } })
  }
}

// Navigate to a historical review
function viewHistoricalReview(review: ReviewDetails) {
  router.push({ name: 'goal-setting', params: { reviewId: review.id } })
}

// Get status badge for historical review
function getHistoricalBadge(review: ReviewDetails): { text: string; class: string } {
  if (review.status === 'ARCHIVED') {
    return { text: t('review.statuses.ARCHIVED'), class: 'badge-archived' }
  }
  if (review.status === 'SIGNED') {
    return { text: t('review.statuses.SIGNED'), class: 'badge-signed' }
  }
  return { text: t(`review.statuses.${review.status}`), class: 'badge-default' }
}

// Format grid position for display
function formatGridPosition(review: ReviewDetails): string {
  if (review.what_score === null || review.how_score === null) {
    return '-'
  }
  const what = review.what_score >= 2.5 ? 3 : review.what_score >= 1.5 ? 2 : 1
  const how = review.how_score >= 2.5 ? 3 : review.how_score >= 1.5 ? 2 : 1
  return `(${what}, ${how})`
}

// Fetch user's reviews
onMounted(async () => {
  try {
    // Fetch current year review
    const review = await getReviewForUser(currentYear)
    currentReview.value = review

    // Fetch historical reviews (previous 2 years)
    const historicalYears = [currentYear - 1, currentYear - 2]
    const historicalPromises = historicalYears.map(year => getReviewForUser(year))
    const results = await Promise.all(historicalPromises)

    // Filter out nulls and only include completed reviews (END_YEAR stage with SIGNED/ARCHIVED status)
    historicalReviews.value = results.filter((r): r is ReviewDetails =>
      r !== null &&
      r.stage === 'END_YEAR_REVIEW' &&
      (r.status === 'SIGNED' || r.status === 'ARCHIVED')
    )
  } catch (error) {
    console.error('Failed to fetch reviews:', error)
  } finally {
    loading.value = false
  }
})
</script>

<template>
  <div class="dashboard">
    <!-- Page Header -->
    <SectionHeader :title="t('dashboard.title')">
      <template #subtitle>
        {{ t('dashboard.welcomeUser', { name: firstName }) }}
      </template>
    </SectionHeader>

    <!-- Year Workflow -->
    <Card class="workflow-card">
      <h3 class="workflow-title">{{ t('dashboard.yearWorkflow', { year: currentYear }) }}</h3>

      <!-- No review message -->
      <div v-if="!loading && !hasCurrentReview" class="no-review-message">
        <div class="no-review-icon">📋</div>
        <p class="no-review-text">{{ t('dashboard.noReviewYet') }}</p>
        <p class="no-review-hint">{{ t('dashboard.noReviewHint') }}</p>
      </div>

      <!-- Workflow Timeline -->
      <div v-else class="workflow-timeline">
        <template v-for="(step, index) in workflowSteps" :key="step.id">
          <!-- Workflow Step -->
          <div
            class="workflow-step"
            :class="{
              'is-clickable': isStepClickable(step),
              'is-completed': getStepStatus(step) === 'completed',
              'is-active': getStepStatus(step) === 'inProgress' || getStepStatus(step) === 'pendingApproval',
              'is-pending': getStepStatus(step) === 'notStarted'
            }"
            @click="handleStepClick(step)"
          >
            <div class="step-node">
              <!-- Status badge -->
              <div
                v-if="getStepStatus(step) !== 'notStarted'"
                class="status-badge"
                :class="{
                  'status-completed': getStepStatus(step) === 'completed',
                  'status-active': getStepStatus(step) === 'inProgress',
                  'status-pending': getStepStatus(step) === 'pendingApproval'
                }"
              >
                <span v-if="getStepStatus(step) === 'completed'" class="badge-icon">✓</span>
                <span v-else-if="getStepStatus(step) === 'inProgress'" class="badge-icon">●</span>
                <span v-else class="badge-icon">!</span>
              </div>
            </div>
            <span class="step-label">{{ t(step.labelKey) }}</span>

            <!-- Status message tooltip -->
            <div v-if="hasCurrentReview" class="status-message">
              {{ getStatusMessage(step) }}
            </div>
          </div>

          <!-- Connector line (not after last step) -->
          <div v-if="index < workflowSteps.length - 1" class="workflow-connector">
            <div class="connector-line"></div>
            <div class="connector-arrow"></div>
          </div>
        </template>
      </div>
    </Card>

    <!-- Historical Reviews -->
    <Card v-if="historicalReviews.length > 0" class="history-card">
      <h3 class="card-title">{{ t('dashboard.previousReviews') }}</h3>
      <div class="history-list">
        <div
          v-for="review in historicalReviews"
          :key="review.id"
          class="history-item"
          @click="viewHistoricalReview(review)"
        >
          <div class="history-year">{{ review.review_year }}</div>
          <div class="history-details">
            <div class="history-scores">
              <span class="score-label">WHAT:</span>
              <span class="score-value">{{ review.what_score?.toFixed(2) || '-' }}</span>
              <span class="score-label">HOW:</span>
              <span class="score-value">{{ review.how_score?.toFixed(2) || '-' }}</span>
              <span class="score-label">Grid:</span>
              <span class="score-value">{{ formatGridPosition(review) }}</span>
            </div>
          </div>
          <span class="history-badge" :class="getHistoricalBadge(review).class">
            {{ getHistoricalBadge(review).text }}
          </span>
        </div>
      </div>
    </Card>

    <!-- User Info Card -->
    <Card v-if="user" class="user-card">
      <h3 class="card-title">{{ t('dashboard.loggedInAs') }}</h3>
      <p><strong>{{ t('dashboard.email') }}:</strong> {{ user.email }}</p>
      <p><strong>{{ t('dashboard.name') }}:</strong> {{ user.name }}</p>
      <p><strong>{{ t('dashboard.roles') }}:</strong> {{ user.roles.join(', ') }}</p>
      <button @click="logout" class="logout-btn">{{ t('nav.logout') }}</button>
    </Card>
  </div>
</template>

<style scoped>
.dashboard {
  max-width: 1200px;
  margin: 0 auto;
}

.user-card,
.workflow-card,
.history-card {
  margin-top: 1rem;
}

.card-title {
  color: var(--color-magenta, #CC0E70);
  margin: 0 0 1rem;
  font-size: 1rem;
  font-weight: 600;
}

.user-card p {
  margin: 0.5rem 0;
}

.logout-btn {
  margin-top: 1rem;
  background: var(--color-magenta, #CC0E70);
  color: white;
  border: none;
  padding: 0.5rem 1rem;
  border-radius: 4px;
  cursor: pointer;
  font-family: inherit;
  font-weight: 500;
}

.logout-btn:hover {
  opacity: 0.9;
}

/* Workflow Card */
.workflow-title {
  color: var(--color-magenta, #CC0E70);
  margin: 0 0 1.5rem;
  font-size: 1.125rem;
  font-weight: 600;
}

/* No Review Message */
.no-review-message {
  text-align: center;
  padding: 2rem 1rem;
}

.no-review-icon {
  font-size: 3rem;
  margin-bottom: 1rem;
}

.no-review-text {
  font-size: 1.125rem;
  font-weight: 600;
  color: var(--color-gray-700, #374151);
  margin: 0 0 0.5rem;
}

.no-review-hint {
  font-size: 0.875rem;
  color: var(--color-gray-500, #6b7280);
  margin: 0;
}

/* Year Workflow Timeline */
.workflow-timeline {
  display: flex;
  align-items: flex-start;
  justify-content: center;
  padding: 1.5rem 1rem 2rem;
  gap: 0;
}

.workflow-step {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.5rem;
  position: relative;
  padding: 0 0.5rem;
  cursor: default;
}

.workflow-step.is-clickable {
  cursor: pointer;
}

.workflow-step.is-clickable:hover .step-node {
  transform: scale(1.05);
  box-shadow: 0 4px 12px rgba(204, 14, 112, 0.3);
}

.workflow-step.is-clickable:hover .status-message {
  opacity: 1;
  visibility: visible;
  transform: translateX(-50%) translateY(0);
}

.step-node {
  width: 100px;
  height: 40px;
  background-color: var(--color-magenta, #CC0E70);
  border-radius: 20px;
  position: relative;
  transition: all 0.2s ease;
}

.workflow-step.is-pending .step-node {
  background-color: var(--color-gray-300, #d1d5db);
}

.step-label {
  font-size: 0.875rem;
  font-weight: 500;
  color: var(--color-magenta, #CC0E70);
  text-align: center;
  white-space: nowrap;
}

.workflow-step.is-pending .step-label {
  color: var(--color-gray-400, #9ca3af);
}

/* Status Badge */
.status-badge {
  position: absolute;
  top: -6px;
  right: -6px;
  width: 20px;
  height: 20px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 0.75rem;
  font-weight: 700;
  border: 2px solid white;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.15);
}

.status-badge.status-completed {
  background-color: #10B981;
  color: white;
}

.status-badge.status-active {
  background-color: var(--color-magenta, #CC0E70);
  color: white;
}

.status-badge.status-pending {
  background-color: #F59E0B;
  color: white;
}

.badge-icon {
  font-size: 0.625rem;
  line-height: 1;
}

/* Status Message Tooltip */
.status-message {
  position: absolute;
  top: calc(100% + 0.75rem);
  left: 50%;
  transform: translateX(-50%) translateY(4px);
  background-color: var(--color-gray-800, #1f2937);
  color: white;
  font-size: 0.75rem;
  padding: 0.5rem 0.75rem;
  border-radius: 6px;
  white-space: nowrap;
  opacity: 0;
  visibility: hidden;
  transition: all 0.2s ease;
  z-index: 10;
}

.status-message::before {
  content: '';
  position: absolute;
  bottom: 100%;
  left: 50%;
  transform: translateX(-50%);
  border: 6px solid transparent;
  border-bottom-color: var(--color-gray-800, #1f2937);
}

/* Connector */
.workflow-connector {
  display: flex;
  align-items: center;
  margin-top: 20px;
  min-width: 60px;
  flex: 1;
  max-width: 120px;
}

.connector-line {
  flex: 1;
  height: 2px;
  background-color: var(--color-gray-300, #d1d5db);
}

.connector-arrow {
  width: 0;
  height: 0;
  border-left: 8px solid var(--color-gray-300, #d1d5db);
  border-top: 5px solid transparent;
  border-bottom: 5px solid transparent;
}

/* Historical Reviews */
.history-card {
  margin-top: 1rem;
}

.history-list {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.history-item {
  display: flex;
  align-items: center;
  gap: 1rem;
  padding: 1rem;
  background: var(--color-gray-50, #f9fafb);
  border-radius: 8px;
  cursor: pointer;
  transition: background 0.2s ease;
}

.history-item:hover {
  background: var(--color-gray-100, #f3f4f6);
}

.history-year {
  font-size: 1.25rem;
  font-weight: 700;
  color: var(--color-magenta, #CC0E70);
  min-width: 60px;
}

.history-details {
  flex: 1;
}

.history-scores {
  display: flex;
  gap: 0.5rem;
  align-items: center;
  flex-wrap: wrap;
}

.score-label {
  font-size: 0.75rem;
  color: var(--color-gray-500, #6b7280);
  font-weight: 500;
}

.score-value {
  font-size: 0.875rem;
  font-weight: 600;
  color: var(--color-gray-700, #374151);
  margin-right: 0.75rem;
}

.history-badge {
  font-size: 0.75rem;
  font-weight: 600;
  padding: 0.25rem 0.75rem;
  border-radius: 9999px;
  white-space: nowrap;
}

.badge-archived {
  background: var(--color-gray-200, #e5e7eb);
  color: var(--color-gray-600, #4b5563);
}

.badge-signed {
  background: #D1FAE5;
  color: #065F46;
}

.badge-default {
  background: var(--color-gray-200, #e5e7eb);
  color: var(--color-gray-600, #4b5563);
}

/* Responsive */
@media (max-width: 640px) {
  .workflow-timeline {
    flex-direction: column;
    align-items: center;
    gap: 0;
    padding: 1rem;
  }

  .workflow-connector {
    flex-direction: column;
    min-width: auto;
    height: 40px;
    margin: 0;
    margin-left: 0;
  }

  .connector-line {
    width: 2px;
    height: 100%;
    flex: 1;
  }

  .connector-arrow {
    border-left: 5px solid transparent;
    border-right: 5px solid transparent;
    border-top: 8px solid var(--color-gray-300, #d1d5db);
    border-bottom: none;
  }

  .status-message {
    position: static;
    transform: none;
    opacity: 1;
    visibility: visible;
    margin-top: 0.25rem;
    background: transparent;
    color: var(--color-gray-600, #6b7280);
    padding: 0;
  }

  .status-message::before {
    display: none;
  }

  .history-item {
    flex-wrap: wrap;
  }

  .history-scores {
    font-size: 0.75rem;
  }
}
</style>
