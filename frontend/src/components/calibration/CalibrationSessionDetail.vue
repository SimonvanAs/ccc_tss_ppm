<script setup lang="ts">
// TSS PPM v3.0 - CalibrationSessionDetail Component
import { ref, computed, onMounted } from 'vue'
import { useI18n } from 'vue-i18n'
import {
  fetchCalibrationSession,
  fetchSessionReviews,
  fetchSessionParticipants,
  startCalibrationSession,
  completeCalibrationSession,
  deleteCalibrationSession,
  type CalibrationSession,
  type CalibrationReview,
  type CalibrationParticipant,
} from '../../api/calibration'
import CalibrationNineGrid from './CalibrationNineGrid.vue'
import ScoreAdjustmentPanel from './ScoreAdjustmentPanel.vue'
import CalibrationNotesPanel from './CalibrationNotesPanel.vue'

const { t } = useI18n()

const props = defineProps<{
  sessionId: string
}>()

const emit = defineEmits<{
  (e: 'back'): void
  (e: 'edit', session: CalibrationSession): void
  (e: 'deleted'): void
  (e: 'status-changed', session: CalibrationSession): void
}>()

const session = ref<CalibrationSession | null>(null)
const reviews = ref<CalibrationReview[]>([])
const participants = ref<CalibrationParticipant[]>([])
const loading = ref(true)
const error = ref<string | null>(null)
const showDeleteConfirm = ref(false)
const actionLoading = ref(false)
const selectedReview = ref<CalibrationReview | null>(null)

const isPreparation = computed(() => session.value?.status === 'PREPARATION')
const isInProgress = computed(() => session.value?.status === 'IN_PROGRESS')
const showCalibrationGrid = computed(() => isInProgress.value && reviews.value.length > 0)

function getStatusClass(status: string): string {
  return `status-${status.toLowerCase().replace('_', '-')}`
}

function formatDate(dateString: string): string {
  const date = new Date(dateString)
  return date.toLocaleDateString(undefined, {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
  })
}

function formatScore(score: number | null): string {
  if (score === null) return '-'
  return score.toFixed(1)
}

async function loadData() {
  loading.value = true
  error.value = null

  try {
    const [sessionData, reviewsData, participantsData] = await Promise.all([
      fetchCalibrationSession(props.sessionId),
      fetchSessionReviews(props.sessionId),
      fetchSessionParticipants(props.sessionId),
    ])

    session.value = sessionData
    reviews.value = reviewsData
    participants.value = participantsData
  } catch (e) {
    error.value = e instanceof Error ? e.message : 'Failed to load session'
  } finally {
    loading.value = false
  }
}

async function handleStartSession() {
  if (!session.value) return

  actionLoading.value = true
  try {
    const updated = await startCalibrationSession(session.value.id)
    session.value = updated
    emit('status-changed', updated)
  } catch (e) {
    console.error('Failed to start session:', e)
  } finally {
    actionLoading.value = false
  }
}

async function handleCompleteSession() {
  if (!session.value) return

  actionLoading.value = true
  try {
    const updated = await completeCalibrationSession(session.value.id)
    session.value = updated
    emit('status-changed', updated)
  } catch (e) {
    console.error('Failed to complete session:', e)
  } finally {
    actionLoading.value = false
  }
}

function handleEdit() {
  if (session.value) {
    emit('edit', session.value)
  }
}

function handleDeleteClick() {
  showDeleteConfirm.value = true
}

async function handleDeleteConfirm() {
  if (!session.value) return

  actionLoading.value = true
  try {
    await deleteCalibrationSession(session.value.id)
    emit('deleted')
  } catch (e) {
    console.error('Failed to delete session:', e)
  } finally {
    actionLoading.value = false
    showDeleteConfirm.value = false
  }
}

function handleDeleteCancel() {
  showDeleteConfirm.value = false
}

function handleBack() {
  emit('back')
}

// Grid and panel interaction handlers
function handleReviewSelect(review: CalibrationReview) {
  selectedReview.value = review
}

async function handleAdjustmentSuccess() {
  // Refresh reviews to get updated scores
  try {
    reviews.value = await fetchSessionReviews(props.sessionId)
    // Update the selected review with the new data
    if (selectedReview.value) {
      const updated = reviews.value.find((r) => r.review_id === selectedReview.value?.review_id)
      if (updated) {
        selectedReview.value = updated
      }
    }
  } catch (e) {
    console.error('Failed to refresh reviews:', e)
  }
}

function handleAdjustmentCancel() {
  selectedReview.value = null
}

onMounted(loadData)
</script>

<template>
  <div class="calibration-session-detail">
    <div v-if="loading" class="loading-state">
      {{ t('calibration.detail.loading') }}
    </div>

    <div v-else-if="error" class="error-state">
      {{ error }}
    </div>

    <template v-else-if="session">
      <div class="detail-header">
        <button class="back-btn" @click="handleBack">
          {{ t('calibration.detail.back') }}
        </button>

        <div class="header-content">
          <h2 class="session-name">{{ session.name }}</h2>
          <span class="status-badge" :class="getStatusClass(session.status)">
            {{ t(`calibration.status.${session.status}`) }}
          </span>
        </div>

        <div class="header-actions">
          <button
            v-if="isPreparation"
            class="start-session-btn"
            :disabled="actionLoading"
            @click="handleStartSession"
          >
            {{ t('calibration.detail.startSession') }}
          </button>
          <button
            v-if="isInProgress"
            class="complete-session-btn"
            :disabled="actionLoading"
            @click="handleCompleteSession"
          >
            {{ t('calibration.detail.completeSession') }}
          </button>
          <button
            v-if="isPreparation"
            class="edit-btn"
            :disabled="actionLoading"
            @click="handleEdit"
          >
            {{ t('calibration.detail.edit') }}
          </button>
          <button
            v-if="isPreparation"
            class="delete-btn"
            :disabled="actionLoading"
            @click="handleDeleteClick"
          >
            {{ t('calibration.detail.delete') }}
          </button>
        </div>
      </div>

      <div class="session-info">
        <div v-if="session.description" class="info-item">
          <span class="info-label">{{ t('calibration.detail.description') }}:</span>
          <span class="info-value">{{ session.description }}</span>
        </div>
        <div class="info-row">
          <div class="info-item">
            <span class="info-label">{{ t('calibration.detail.reviewYear') }}:</span>
            <span class="info-value">{{ session.review_year }}</span>
          </div>
          <div class="info-item">
            <span class="info-label">{{ t('calibration.detail.scope') }}:</span>
            <span class="info-value">{{ session.scope }}</span>
          </div>
          <div class="info-item">
            <span class="info-label">{{ t('calibration.detail.createdAt') }}:</span>
            <span class="info-value">{{ formatDate(session.created_at) }}</span>
          </div>
        </div>
      </div>

      <!-- Calibration Grid View (shown when session is in progress) -->
      <div v-if="showCalibrationGrid" class="calibration-grid-section">
        <div class="grid-main">
          <section class="grid-container">
            <h3>{{ t('calibration.grid.title') }}</h3>
            <CalibrationNineGrid
              :reviews="reviews"
              :selected-review-id="selectedReview?.review_id"
              @select="handleReviewSelect"
            />
          </section>

          <section class="notes-section">
            <CalibrationNotesPanel
              :session-id="sessionId"
              :review-id="selectedReview?.review_id"
            />
          </section>
        </div>

        <div v-if="selectedReview" class="grid-sidebar">
          <ScoreAdjustmentPanel
            :session-id="sessionId"
            :review="selectedReview"
            @success="handleAdjustmentSuccess"
            @cancel="handleAdjustmentCancel"
          />
        </div>
      </div>

      <!-- Standard Reviews List (shown when not in calibration mode) -->
      <div v-else class="content-sections">
        <section class="reviews-section">
          <h3>{{ t('calibration.detail.reviews') }}</h3>

          <div v-if="reviews.length === 0" class="empty-state">
            {{ t('calibration.detail.noReviews') }}
          </div>

          <div v-else class="reviews-list">
            <div v-for="review in reviews" :key="review.review_id" class="review-item">
              <div class="review-employee">
                <span class="employee-name">{{ review.employee_name }}</span>
                <span v-if="review.manager_first_name" class="manager-name">
                  Manager: {{ review.manager_first_name }} {{ review.manager_last_name }}
                </span>
              </div>
              <div class="review-scores">
                <span class="score-item">
                  <span class="score-label">WHAT:</span>
                  <span class="score-value">{{ formatScore(review.what_score) }}</span>
                </span>
                <span class="score-item">
                  <span class="score-label">HOW:</span>
                  <span class="score-value">{{ formatScore(review.how_score) }}</span>
                </span>
              </div>
            </div>
          </div>
        </section>

        <section class="participants-section">
          <h3>{{ t('calibration.detail.participants') }}</h3>

          <div v-if="participants.length === 0" class="empty-state">
            {{ t('calibration.detail.noParticipants') }}
          </div>

          <div v-else class="participants-list">
            <div
              v-for="participant in participants"
              :key="participant.user_id"
              class="participant-item"
            >
              <span class="participant-name">
                {{ participant.first_name }} {{ participant.last_name }}
              </span>
              <span class="participant-role">{{ participant.role }}</span>
            </div>
          </div>
        </section>
      </div>

      <!-- Delete Confirmation Dialog -->
      <div v-if="showDeleteConfirm" class="delete-dialog-overlay">
        <div class="delete-dialog">
          <h3>Delete Session</h3>
          <p>Are you sure you want to delete this calibration session? This action cannot be undone.</p>
          <div class="dialog-actions">
            <button class="cancel-delete-btn" @click="handleDeleteCancel">
              Cancel
            </button>
            <button
              class="confirm-delete-btn"
              :disabled="actionLoading"
              @click="handleDeleteConfirm"
            >
              Delete
            </button>
          </div>
        </div>
      </div>
    </template>
  </div>
</template>

<style scoped>
.calibration-session-detail {
  padding: 1rem;
}

.loading-state,
.error-state {
  text-align: center;
  padding: 3rem;
  color: #666;
  font-family: Tahoma, sans-serif;
}

.error-state {
  color: #c00;
}

.detail-header {
  display: flex;
  align-items: center;
  gap: 1rem;
  margin-bottom: 1.5rem;
  padding-bottom: 1rem;
  border-bottom: 1px solid #e0e0e0;
}

.back-btn {
  padding: 0.5rem 1rem;
  background: #f5f5f5;
  color: #333;
  border: 1px solid #ccc;
  border-radius: 4px;
  cursor: pointer;
  font-family: Tahoma, sans-serif;
}

.back-btn:hover {
  background: #eee;
}

.header-content {
  flex: 1;
  display: flex;
  align-items: center;
  gap: 1rem;
}

.session-name {
  margin: 0;
  color: var(--navy, #004a91);
  font-family: Tahoma, sans-serif;
}

.status-badge {
  padding: 0.25rem 0.75rem;
  border-radius: 4px;
  font-size: 0.85rem;
  font-weight: bold;
  text-transform: uppercase;
}

.status-preparation {
  background-color: #e3f2fd;
  color: #1565c0;
}

.status-in-progress {
  background-color: #fff3e0;
  color: #e65100;
}

.status-pending-approval {
  background-color: #fce4ec;
  color: #c2185b;
}

.status-completed {
  background-color: #e8f5e9;
  color: #2e7d32;
}

.status-cancelled {
  background-color: #fafafa;
  color: #616161;
}

.header-actions {
  display: flex;
  gap: 0.5rem;
}

.start-session-btn,
.complete-session-btn {
  padding: 0.5rem 1rem;
  background-color: var(--magenta, #cc0e70);
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-family: Tahoma, sans-serif;
  font-weight: bold;
}

.start-session-btn:hover:not(:disabled),
.complete-session-btn:hover:not(:disabled) {
  background-color: #a00b5a;
}

.edit-btn {
  padding: 0.5rem 1rem;
  background: #f5f5f5;
  color: #333;
  border: 1px solid #ccc;
  border-radius: 4px;
  cursor: pointer;
  font-family: Tahoma, sans-serif;
}

.edit-btn:hover:not(:disabled) {
  background: #eee;
}

.delete-btn {
  padding: 0.5rem 1rem;
  background: #fff;
  color: #c00;
  border: 1px solid #c00;
  border-radius: 4px;
  cursor: pointer;
  font-family: Tahoma, sans-serif;
}

.delete-btn:hover:not(:disabled) {
  background: #ffebee;
}

button:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.session-info {
  background: #f9f9f9;
  padding: 1rem;
  border-radius: 8px;
  margin-bottom: 1.5rem;
}

.info-item {
  margin-bottom: 0.5rem;
}

.info-row {
  display: flex;
  gap: 2rem;
  flex-wrap: wrap;
}

.info-row .info-item {
  margin-bottom: 0;
}

.info-label {
  color: #666;
  font-family: Tahoma, sans-serif;
}

.info-value {
  color: #333;
  font-weight: 500;
  margin-left: 0.5rem;
  font-family: Tahoma, sans-serif;
}

.content-sections {
  display: grid;
  grid-template-columns: 2fr 1fr;
  gap: 1.5rem;
}

.reviews-section,
.participants-section {
  background: white;
  border: 1px solid #e0e0e0;
  border-radius: 8px;
  padding: 1rem;
}

.reviews-section h3,
.participants-section h3 {
  margin: 0 0 1rem;
  color: var(--navy, #004a91);
  font-family: Tahoma, sans-serif;
}

.empty-state {
  color: #999;
  text-align: center;
  padding: 2rem;
  font-family: Tahoma, sans-serif;
}

.reviews-list,
.participants-list {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.review-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.75rem;
  background: #f9f9f9;
  border-radius: 4px;
}

.review-employee {
  display: flex;
  flex-direction: column;
}

.employee-name {
  font-weight: 500;
  color: #333;
  font-family: Tahoma, sans-serif;
}

.manager-name {
  font-size: 0.85rem;
  color: #666;
  font-family: Tahoma, sans-serif;
}

.review-scores {
  display: flex;
  gap: 1rem;
}

.score-item {
  display: flex;
  gap: 0.25rem;
}

.score-label {
  color: #666;
  font-size: 0.85rem;
  font-family: Tahoma, sans-serif;
}

.score-value {
  font-weight: bold;
  color: var(--navy, #004a91);
  font-family: Tahoma, sans-serif;
}

.participant-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.5rem;
  background: #f9f9f9;
  border-radius: 4px;
}

.participant-name {
  font-family: Tahoma, sans-serif;
  color: #333;
}

.participant-role {
  font-size: 0.75rem;
  font-weight: bold;
  text-transform: uppercase;
  padding: 0.25rem 0.5rem;
  background: #e3f2fd;
  color: #1565c0;
  border-radius: 4px;
  font-family: Tahoma, sans-serif;
}

.delete-dialog-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.delete-dialog {
  background: white;
  padding: 1.5rem;
  border-radius: 8px;
  max-width: 400px;
  width: 100%;
}

.delete-dialog h3 {
  margin: 0 0 1rem;
  color: #c00;
  font-family: Tahoma, sans-serif;
}

.delete-dialog p {
  margin: 0 0 1.5rem;
  color: #333;
  font-family: Tahoma, sans-serif;
}

.dialog-actions {
  display: flex;
  justify-content: flex-end;
  gap: 0.5rem;
}

.cancel-delete-btn {
  padding: 0.5rem 1rem;
  background: #f5f5f5;
  color: #333;
  border: 1px solid #ccc;
  border-radius: 4px;
  cursor: pointer;
  font-family: Tahoma, sans-serif;
}

.cancel-delete-btn:hover {
  background: #eee;
}

.confirm-delete-btn {
  padding: 0.5rem 1rem;
  background: #c00;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-family: Tahoma, sans-serif;
  font-weight: bold;
}

.confirm-delete-btn:hover:not(:disabled) {
  background: #a00;
}

/* Calibration Grid Section Styles */
.calibration-grid-section {
  display: grid;
  grid-template-columns: 1fr 350px;
  gap: 1.5rem;
}

.calibration-grid-section .grid-main {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.calibration-grid-section .grid-container {
  background: white;
  border: 1px solid #e0e0e0;
  border-radius: 8px;
  padding: 1.5rem;
}

.calibration-grid-section .grid-container h3 {
  margin: 0 0 1rem;
  color: var(--navy, #004a91);
  font-family: Tahoma, sans-serif;
}

.calibration-grid-section .notes-section {
  flex: 1;
}

.calibration-grid-section .grid-sidebar {
  min-width: 0;
}

@media (max-width: 1024px) {
  .calibration-grid-section {
    grid-template-columns: 1fr;
  }
}
</style>
