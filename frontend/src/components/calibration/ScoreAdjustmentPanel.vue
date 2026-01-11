<script setup lang="ts">
// TSS PPM v3.0 - ScoreAdjustmentPanel Component
import { ref, computed, watch } from 'vue'
import { useI18n } from 'vue-i18n'
import { adjustReviewScores, type CalibrationReview } from '../../api/calibration'

const { t } = useI18n()

const props = defineProps<{
  sessionId: string
  review: CalibrationReview
}>()

const emit = defineEmits<{
  (e: 'success', adjustment: unknown): void
  (e: 'cancel'): void
}>()

// Form state
const newWhatScore = ref<number | null>(null)
const newHowScore = ref<number | null>(null)
const rationale = ref('')

// UI state
const submitting = ref(false)
const error = ref<string | null>(null)
const success = ref(false)
const rationaleError = ref(false)
const noChangesError = ref(false)

// Initialize scores when review changes
watch(
  () => props.review,
  (review) => {
    newWhatScore.value = review.what_score
    newHowScore.value = review.how_score
    rationale.value = ''
    error.value = null
    success.value = false
    rationaleError.value = false
    noChangesError.value = false
  },
  { immediate: true }
)

// Check if scores have changed
const whatScoreChanged = computed(() => {
  return newWhatScore.value !== props.review.what_score
})

const howScoreChanged = computed(() => {
  return newHowScore.value !== props.review.how_score
})

const hasChanges = computed(() => {
  return whatScoreChanged.value || howScoreChanged.value
})

// Calculate change direction
const whatChangeDirection = computed(() => {
  if (!whatScoreChanged.value || newWhatScore.value === null || props.review.what_score === null) {
    return null
  }
  return newWhatScore.value > props.review.what_score ? 'positive' : 'negative'
})

const howChangeDirection = computed(() => {
  if (!howScoreChanged.value || newHowScore.value === null || props.review.how_score === null) {
    return null
  }
  return newHowScore.value > props.review.how_score ? 'positive' : 'negative'
})

// Format score for display
function formatScore(score: number | null): string {
  if (score === null) return '-'
  return score.toFixed(1)
}

// Clear rationale error when user types
watch(rationale, () => {
  if (rationale.value.trim()) {
    rationaleError.value = false
  }
})

// Clear no changes error when scores change
watch([newWhatScore, newHowScore], () => {
  noChangesError.value = false
})

async function handleSubmit() {
  error.value = null
  success.value = false
  rationaleError.value = false
  noChangesError.value = false

  // Validate rationale
  if (!rationale.value.trim()) {
    rationaleError.value = true
    return
  }

  // Validate that at least one score changed
  if (!hasChanges.value) {
    noChangesError.value = true
    return
  }

  submitting.value = true

  try {
    const result = await adjustReviewScores(props.sessionId, props.review.review_id, {
      what_score: newWhatScore.value ?? undefined,
      how_score: newHowScore.value ?? undefined,
      rationale: rationale.value.trim(),
    })

    success.value = true
    emit('success', result)
  } catch (e) {
    error.value = t('calibration.adjustment.error')
    console.error('Failed to adjust scores:', e)
  } finally {
    submitting.value = false
  }
}

function handleCancel() {
  emit('cancel')
}
</script>

<template>
  <div class="score-adjustment-panel">
    <h3 class="panel-title">{{ t('calibration.adjustment.title') }}</h3>

    <div class="employee-info">
      <span class="label">{{ t('calibration.adjustment.employee') }}:</span>
      <span class="value">{{ review.employee_name }}</span>
    </div>

    <div class="current-scores">
      <h4>{{ t('calibration.adjustment.currentScores') }}</h4>
      <div class="scores-row">
        <div class="score-item">
          <span class="score-label">{{ t('calibration.adjustment.whatScore') }}</span>
          <span class="score-value">{{ formatScore(review.what_score) }}</span>
        </div>
        <div class="score-item">
          <span class="score-label">{{ t('calibration.adjustment.howScore') }}</span>
          <span class="score-value">{{ formatScore(review.how_score) }}</span>
        </div>
      </div>
    </div>

    <form @submit.prevent="handleSubmit">
      <div class="new-scores">
        <h4>{{ t('calibration.adjustment.newScores') }}</h4>

        <div class="score-inputs-row">
          <div class="score-input-group">
            <label for="whatScore">{{ t('calibration.adjustment.whatScore') }}</label>
            <div class="input-with-indicator">
              <input
                id="whatScore"
                v-model.number="newWhatScore"
                type="number"
                name="whatScore"
                min="1"
                max="3"
                step="0.1"
              />
              <span
                v-if="whatScoreChanged"
                class="what-change-indicator"
                :class="whatChangeDirection"
              >
                {{ whatChangeDirection === 'positive' ? '↑' : '↓' }}
              </span>
            </div>
          </div>

          <div class="score-input-group">
            <label for="howScore">{{ t('calibration.adjustment.howScore') }}</label>
            <div class="input-with-indicator">
              <input
                id="howScore"
                v-model.number="newHowScore"
                type="number"
                name="howScore"
                min="1"
                max="3"
                step="0.1"
              />
              <span
                v-if="howScoreChanged"
                class="how-change-indicator"
                :class="howChangeDirection"
              >
                {{ howChangeDirection === 'positive' ? '↑' : '↓' }}
              </span>
            </div>
          </div>
        </div>
      </div>

      <div class="rationale-group">
        <label for="rationale">{{ t('calibration.adjustment.rationale') }} *</label>
        <textarea
          id="rationale"
          v-model="rationale"
          name="rationale"
          rows="3"
          :placeholder="t('calibration.adjustment.rationalePlaceholder')"
          :class="{ 'has-error': rationaleError }"
        />
        <span v-if="rationaleError" class="error-message">
          {{ t('calibration.adjustment.rationaleRequired') }}
        </span>
      </div>

      <div v-if="noChangesError" class="no-changes-error">
        {{ t('calibration.adjustment.noChanges') }}
      </div>

      <div v-if="error" class="api-error">
        {{ error }}
      </div>

      <div v-if="success" class="success-message">
        {{ t('calibration.adjustment.success') }}
      </div>

      <div class="form-actions">
        <button type="button" class="cancel-btn" @click="handleCancel">
          {{ t('calibration.adjustment.cancel') }}
        </button>
        <button type="submit" class="submit-btn" :disabled="submitting">
          {{ submitting ? t('calibration.adjustment.submitting') : t('calibration.adjustment.submit') }}
        </button>
      </div>
    </form>
  </div>
</template>

<style scoped>
.score-adjustment-panel {
  background: white;
  border: 1px solid #e0e0e0;
  border-radius: 8px;
  padding: 1.5rem;
}

.panel-title {
  margin: 0 0 1rem;
  color: var(--navy, #004a91);
  font-family: Tahoma, sans-serif;
  font-size: 1.1rem;
}

.employee-info {
  margin-bottom: 1rem;
  padding-bottom: 1rem;
  border-bottom: 1px solid #eee;
}

.employee-info .label {
  color: #666;
  font-family: Tahoma, sans-serif;
}

.employee-info .value {
  font-weight: 600;
  color: #333;
  margin-left: 0.5rem;
  font-family: Tahoma, sans-serif;
}

.current-scores h4,
.new-scores h4 {
  margin: 0 0 0.5rem;
  font-size: 0.9rem;
  color: #666;
  font-family: Tahoma, sans-serif;
}

.scores-row {
  display: flex;
  gap: 2rem;
  margin-bottom: 1rem;
}

.score-item {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.score-label {
  font-size: 0.8rem;
  color: #999;
  font-family: Tahoma, sans-serif;
}

.score-value {
  font-size: 1.5rem;
  font-weight: bold;
  color: var(--navy, #004a91);
  font-family: Tahoma, sans-serif;
}

.new-scores {
  margin-bottom: 1rem;
}

.score-inputs-row {
  display: flex;
  gap: 1.5rem;
}

.score-input-group {
  flex: 1;
}

.score-input-group label {
  display: block;
  margin-bottom: 0.5rem;
  font-size: 0.85rem;
  color: #666;
  font-family: Tahoma, sans-serif;
}

.input-with-indicator {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.score-input-group input {
  width: 100%;
  padding: 0.75rem;
  border: 1px solid #ccc;
  border-radius: 4px;
  font-family: Tahoma, sans-serif;
  font-size: 1rem;
}

.score-input-group input:focus {
  outline: none;
  border-color: var(--magenta, #cc0e70);
  box-shadow: 0 0 0 2px rgba(204, 14, 112, 0.1);
}

.what-change-indicator,
.how-change-indicator {
  font-size: 1.2rem;
  font-weight: bold;
  min-width: 1.5rem;
  text-align: center;
}

.what-change-indicator.positive,
.how-change-indicator.positive {
  color: #2e7d32;
}

.what-change-indicator.negative,
.how-change-indicator.negative {
  color: #c00;
}

.rationale-group {
  margin-bottom: 1rem;
}

.rationale-group label {
  display: block;
  margin-bottom: 0.5rem;
  font-size: 0.85rem;
  color: #666;
  font-family: Tahoma, sans-serif;
}

.rationale-group textarea {
  width: 100%;
  padding: 0.75rem;
  border: 1px solid #ccc;
  border-radius: 4px;
  font-family: Tahoma, sans-serif;
  font-size: 1rem;
  resize: vertical;
  box-sizing: border-box;
}

.rationale-group textarea:focus {
  outline: none;
  border-color: var(--magenta, #cc0e70);
  box-shadow: 0 0 0 2px rgba(204, 14, 112, 0.1);
}

.rationale-group textarea.has-error {
  border-color: #c00;
}

.error-message {
  display: block;
  margin-top: 0.25rem;
  color: #c00;
  font-size: 0.85rem;
  font-family: Tahoma, sans-serif;
}

.no-changes-error,
.api-error {
  padding: 0.75rem;
  background-color: #ffebee;
  color: #c00;
  border-radius: 4px;
  margin-bottom: 1rem;
  font-size: 0.9rem;
  font-family: Tahoma, sans-serif;
}

.success-message {
  padding: 0.75rem;
  background-color: #e8f5e9;
  color: #2e7d32;
  border-radius: 4px;
  margin-bottom: 1rem;
  font-size: 0.9rem;
  font-family: Tahoma, sans-serif;
}

.form-actions {
  display: flex;
  justify-content: flex-end;
  gap: 0.75rem;
  padding-top: 1rem;
  border-top: 1px solid #eee;
}

.cancel-btn {
  padding: 0.75rem 1.25rem;
  background: #f5f5f5;
  color: #333;
  border: 1px solid #ccc;
  border-radius: 4px;
  cursor: pointer;
  font-family: Tahoma, sans-serif;
}

.cancel-btn:hover {
  background: #eee;
}

.submit-btn {
  padding: 0.75rem 1.25rem;
  background-color: var(--magenta, #cc0e70);
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-family: Tahoma, sans-serif;
  font-weight: bold;
}

.submit-btn:hover:not(:disabled) {
  background-color: #a00b5a;
}

.submit-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}
</style>
