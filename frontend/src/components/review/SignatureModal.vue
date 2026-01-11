<script setup lang="ts">
import { ref, computed } from 'vue'
import { useI18n } from 'vue-i18n'

interface ReviewSummary {
  employeeName: string
  stage: string
  whatScore?: number
  howScore?: number
}

const props = defineProps<{
  modelValue: boolean
  reviewSummary: ReviewSummary
  loading?: boolean
}>()

const emit = defineEmits<{
  'update:modelValue': [value: boolean]
  sign: []
}>()

const { t } = useI18n()

const acknowledged = ref(false)

const canSign = computed(() => acknowledged.value && !props.loading)

function handleSign() {
  if (canSign.value) {
    emit('sign')
  }
}

function handleCancel() {
  acknowledged.value = false
  emit('update:modelValue', false)
}

function handleBackdropClick(event: MouseEvent) {
  if (event.target === event.currentTarget) {
    handleCancel()
  }
}

function formatScore(score?: number): string {
  return score !== undefined ? score.toFixed(2) : '-'
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
        class="signature-modal modal-backdrop"
        @click="handleBackdropClick"
      >
        <div class="modal-content" role="dialog" aria-modal="true">
          <header class="modal-header">
            <h2 class="modal-title">{{ t('signature.signReview') }}</h2>
          </header>

          <div class="modal-body">
            <!-- Review Summary -->
            <div class="review-summary">
              <h3 class="summary-title">{{ t('signature.reviewSummary') }}</h3>

              <div class="summary-grid">
                <div class="summary-item">
                  <span class="summary-label">{{ t('review.employee') }}</span>
                  <span class="summary-value">{{ reviewSummary.employeeName }}</span>
                </div>

                <div class="summary-item">
                  <span class="summary-label">{{ t('review.stage') }}</span>
                  <span class="summary-value">{{ formatStage(reviewSummary.stage) }}</span>
                </div>

                <div class="summary-item">
                  <span class="summary-label">{{ t('review.whatScore') }}</span>
                  <span class="summary-value score">{{ formatScore(reviewSummary.whatScore) }}</span>
                </div>

                <div class="summary-item">
                  <span class="summary-label">{{ t('review.howScore') }}</span>
                  <span class="summary-value score">{{ formatScore(reviewSummary.howScore) }}</span>
                </div>
              </div>
            </div>

            <!-- Acknowledgment Checkbox -->
            <label class="acknowledgment">
              <input
                v-model="acknowledged"
                type="checkbox"
                :disabled="loading"
              />
              <span class="acknowledgment-text">
                {{ t('signature.acknowledgment') }}
              </span>
            </label>
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
              class="sign-button primary"
              :disabled="!canSign"
              @click="handleSign"
            >
              <span v-if="loading" class="loading-spinner"></span>
              <span v-else>{{ t('signature.signReview') }}</span>
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
  max-width: 480px;
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

.review-summary {
  background: var(--color-gray-50, #f9fafb);
  border-radius: 8px;
  padding: 1rem;
  margin-bottom: 1.5rem;
}

.summary-title {
  margin: 0 0 1rem;
  font-size: 0.875rem;
  font-weight: 600;
  color: var(--color-gray-600, #4b5563);
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.summary-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 0.75rem;
}

.summary-item {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.summary-label {
  font-size: 0.75rem;
  color: var(--color-gray-500, #6b7280);
}

.summary-value {
  font-size: 0.9375rem;
  font-weight: 500;
  color: var(--color-gray-900, #111827);
}

.summary-value.score {
  font-size: 1.125rem;
  font-weight: 600;
  color: var(--color-navy, #004A91);
}

.acknowledgment {
  display: flex;
  align-items: flex-start;
  gap: 0.75rem;
  cursor: pointer;
  padding: 0.75rem;
  border: 1px solid var(--color-gray-200, #e5e7eb);
  border-radius: 8px;
  transition: border-color 0.2s;
}

.acknowledgment:hover {
  border-color: var(--color-magenta, #CC0E70);
}

.acknowledgment input[type="checkbox"] {
  width: 1.25rem;
  height: 1.25rem;
  margin-top: 0.125rem;
  accent-color: var(--color-magenta, #CC0E70);
  cursor: pointer;
}

.acknowledgment-text {
  font-size: 0.9375rem;
  color: var(--color-gray-700, #374151);
  line-height: 1.5;
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
.sign-button {
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

.sign-button {
  background: var(--color-magenta, #CC0E70);
  border: none;
  color: white;
  min-width: 140px;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
}

.sign-button:hover:not(:disabled) {
  background: #a30b5a;
}

.sign-button:disabled {
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
