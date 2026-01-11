<script setup lang="ts">
import { ref, computed } from 'vue'
import { useI18n } from 'vue-i18n'

interface ReviewSummary {
  employeeName: string
  stage: string
}

const props = defineProps<{
  modelValue: boolean
  reviewSummary: ReviewSummary
  loading?: boolean
}>()

const emit = defineEmits<{
  'update:modelValue': [value: boolean]
  reject: [feedback: string]
}>()

const { t } = useI18n()

const feedback = ref('')
const MIN_FEEDBACK_LENGTH = 10
const MAX_FEEDBACK_LENGTH = 1000

const feedbackLength = computed(() => feedback.value.length)
const isValidFeedback = computed(
  () => feedback.value.trim().length >= MIN_FEEDBACK_LENGTH
)
const canSubmit = computed(() => isValidFeedback.value && !props.loading)

function handleSubmit() {
  if (canSubmit.value) {
    emit('reject', feedback.value.trim())
  }
}

function handleCancel() {
  feedback.value = ''
  emit('update:modelValue', false)
}

function handleBackdropClick(event: MouseEvent) {
  if (event.target === event.currentTarget) {
    handleCancel()
  }
}

function formatStage(stage: string): string {
  const stageMap: Record<string, string> = {
    GOAL_SETTING: t('review.stages.goalSetting'),
    MID_YEAR_REVIEW: t('review.stages.midYear'),
    END_YEAR_REVIEW: t('review.stages.endYear'),
  }
  return stageMap[stage] || stage
}
</script>

<template>
  <Teleport to="body">
    <Transition name="modal">
      <div
        v-if="modelValue"
        class="rejection-modal modal-backdrop"
        @click="handleBackdropClick"
      >
        <div class="modal-content" role="dialog" aria-modal="true">
          <header class="modal-header">
            <h2 class="modal-title">{{ t('signature.rejectReview') }}</h2>
          </header>

          <div class="modal-body">
            <!-- Review Info -->
            <div class="review-info">
              <div class="info-item">
                <span class="info-label">{{ t('review.employee') }}</span>
                <span class="info-value">{{ reviewSummary.employeeName }}</span>
              </div>
              <div class="info-item">
                <span class="info-label">{{ t('review.stage') }}</span>
                <span class="info-value">{{ formatStage(reviewSummary.stage) }}</span>
              </div>
            </div>

            <!-- Feedback Section -->
            <div class="feedback-section">
              <label for="rejection-feedback" class="feedback-label">
                {{ t('signature.feedbackRequired') }}
              </label>
              <textarea
                id="rejection-feedback"
                v-model="feedback"
                class="feedback-textarea"
                :placeholder="t('signature.feedbackPlaceholder')"
                :disabled="loading"
                :maxlength="MAX_FEEDBACK_LENGTH"
                rows="5"
              ></textarea>
              <div class="feedback-meta">
                <span
                  v-if="!isValidFeedback && feedback.length > 0"
                  class="validation-message"
                >
                  {{ t('signature.feedbackMinLength', { min: MIN_FEEDBACK_LENGTH }) }}
                </span>
                <span class="character-count">
                  {{ feedbackLength }} / {{ MAX_FEEDBACK_LENGTH }}
                </span>
              </div>
            </div>
          </div>

          <footer class="modal-footer">
            <button
              type="button"
              class="cancel-button"
              :disabled="loading"
              @click="handleCancel"
            >
              {{ t('actions.cancel') }}
            </button>

            <button
              type="button"
              class="submit-button warning"
              :disabled="!canSubmit"
              @click="handleSubmit"
            >
              <span v-if="loading" class="loading-spinner"></span>
              <span v-else>{{ t('signature.submitFeedback') }}</span>
            </button>
          </footer>
        </div>
      </div>
    </Transition>
  </Teleport>
</template>

<style scoped>
.modal-backdrop {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  padding: 1rem;
}

.modal-content {
  background: var(--color-white, #fff);
  border-radius: 12px;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
  width: 100%;
  max-width: 520px;
  max-height: 90vh;
  overflow: hidden;
  display: flex;
  flex-direction: column;
}

.modal-header {
  padding: 1.25rem 1.5rem;
  border-bottom: 1px solid var(--color-gray-200, #e5e7eb);
}

.modal-title {
  margin: 0;
  font-size: 1.25rem;
  font-weight: 600;
  color: var(--color-navy, #004A91);
}

.modal-body {
  padding: 1.5rem;
  overflow-y: auto;
}

.review-info {
  display: flex;
  gap: 2rem;
  margin-bottom: 1.5rem;
  padding-bottom: 1rem;
  border-bottom: 1px solid var(--color-gray-200, #e5e7eb);
}

.info-item {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.info-label {
  font-size: 0.75rem;
  color: var(--color-gray-500, #6b7280);
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.info-value {
  font-size: 0.9375rem;
  font-weight: 500;
  color: var(--color-gray-900, #111827);
}

.feedback-section {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.feedback-label {
  font-size: 0.9375rem;
  font-weight: 500;
  color: var(--color-gray-700, #374151);
}

.feedback-textarea {
  width: 100%;
  padding: 0.75rem;
  border: 1px solid var(--color-gray-300, #d1d5db);
  border-radius: 8px;
  font-family: inherit;
  font-size: 0.9375rem;
  line-height: 1.5;
  resize: vertical;
  transition: border-color 0.2s, box-shadow 0.2s;
}

.feedback-textarea:focus {
  outline: none;
  border-color: var(--color-magenta, #CC0E70);
  box-shadow: 0 0 0 3px rgba(204, 14, 112, 0.1);
}

.feedback-textarea:disabled {
  background: var(--color-gray-50, #f9fafb);
  cursor: not-allowed;
}

.feedback-textarea::placeholder {
  color: var(--color-gray-400, #9ca3af);
}

.feedback-meta {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 1rem;
}

.validation-message {
  font-size: 0.8125rem;
  color: var(--color-error, #dc2626);
}

.character-count {
  font-size: 0.75rem;
  color: var(--color-gray-500, #6b7280);
  margin-left: auto;
}

.modal-footer {
  display: flex;
  justify-content: flex-end;
  gap: 0.75rem;
  padding: 1rem 1.5rem;
  border-top: 1px solid var(--color-gray-200, #e5e7eb);
  background: var(--color-gray-50, #f9fafb);
}

.cancel-button,
.submit-button {
  padding: 0.625rem 1.25rem;
  font-size: 0.9375rem;
  font-weight: 500;
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.2s;
}

.cancel-button {
  background: var(--color-white, #fff);
  border: 1px solid var(--color-gray-300, #d1d5db);
  color: var(--color-gray-700, #374151);
}

.cancel-button:hover:not(:disabled) {
  background: var(--color-gray-50, #f9fafb);
  border-color: var(--color-gray-400, #9ca3af);
}

.submit-button {
  background: var(--color-warning, #f59e0b);
  border: none;
  color: white;
  min-width: 180px;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
}

.submit-button:hover:not(:disabled) {
  background: #d97706;
}

.submit-button:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.cancel-button:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.loading-spinner {
  width: 1rem;
  height: 1rem;
  border: 2px solid rgba(255, 255, 255, 0.3);
  border-top-color: white;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

/* Transition animations */
.modal-enter-active,
.modal-leave-active {
  transition: opacity 0.2s ease;
}

.modal-enter-active .modal-content,
.modal-leave-active .modal-content {
  transition: transform 0.2s ease, opacity 0.2s ease;
}

.modal-enter-from,
.modal-leave-to {
  opacity: 0;
}

.modal-enter-from .modal-content,
.modal-leave-to .modal-content {
  transform: scale(0.95);
  opacity: 0;
}
</style>
