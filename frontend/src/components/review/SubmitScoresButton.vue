<script setup lang="ts">
import { ref } from 'vue'

interface Props {
  allScoresComplete: boolean
  isSubmitting?: boolean
  hasError?: boolean
  errorMessage?: string
}

const props = withDefaults(defineProps<Props>(), {
  isSubmitting: false,
  hasError: false,
  errorMessage: '',
})

const emit = defineEmits<{
  (e: 'submit'): void
}>()

const showDialog = ref(false)

function handleClick() {
  if (props.allScoresComplete && !props.isSubmitting) {
    showDialog.value = true
  }
}

function handleCancel() {
  showDialog.value = false
}

function handleConfirm() {
  showDialog.value = false
  emit('submit')
}

const disabledTooltip = 'Complete all scores before submitting'
</script>

<template>
  <div class="submit-scores-button-wrapper">
    <button
      class="submit-button"
      :class="{ disabled: !allScoresComplete || isSubmitting }"
      :disabled="!allScoresComplete || isSubmitting"
      :title="!allScoresComplete ? disabledTooltip : undefined"
      @click="handleClick"
    >
      <span v-if="isSubmitting" class="loading-spinner"></span>
      <span v-else>Submit Scores</span>
    </button>

    <div v-if="hasError" class="error-message">
      {{ errorMessage }}
    </div>

    <div v-if="showDialog" class="confirmation-dialog">
      <div class="dialog-backdrop" @click="handleCancel"></div>
      <div class="dialog-content">
        <h3 class="dialog-title">Confirm Submission</h3>
        <p class="dialog-message">
          Are you sure you want to submit these scores? This action will send the review for employee signature.
        </p>
        <div class="dialog-actions">
          <button class="cancel-button" @click="handleCancel">
            Cancel
          </button>
          <button class="confirm-button" @click="handleConfirm">
            Confirm
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.submit-scores-button-wrapper {
  position: relative;
}

.submit-button {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
  padding: 0.75rem 1.5rem;
  font-size: 1rem;
  font-weight: 600;
  color: var(--color-white);
  background-color: var(--color-navy);
  border: none;
  border-radius: 8px;
  cursor: pointer;
  transition: background-color 0.2s, opacity 0.2s;
  min-width: 150px;
}

.submit-button:hover:not(.disabled) {
  background-color: var(--color-magenta);
}

.submit-button.disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.loading-spinner {
  width: 1rem;
  height: 1rem;
  border: 2px solid var(--color-white);
  border-top-color: transparent;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

.error-message {
  margin-top: 0.5rem;
  padding: 0.5rem 0.75rem;
  color: #991B1B;
  background: #FEF2F2;
  border: 1px solid var(--color-grid-red);
  border-radius: 4px;
  font-size: 0.875rem;
}

.confirmation-dialog {
  position: fixed;
  inset: 0;
  z-index: 1000;
  display: flex;
  align-items: center;
  justify-content: center;
}

.dialog-backdrop {
  position: absolute;
  inset: 0;
  background: rgba(0, 0, 0, 0.5);
}

.dialog-content {
  position: relative;
  background: var(--color-white);
  border-radius: 12px;
  padding: 1.5rem;
  max-width: 400px;
  width: 90%;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1), 0 10px 20px rgba(0, 0, 0, 0.1);
}

.dialog-title {
  font-size: 1.25rem;
  font-weight: 600;
  color: var(--color-navy);
  margin: 0 0 1rem;
}

.dialog-message {
  font-size: 0.9375rem;
  color: var(--color-gray-700);
  margin: 0 0 1.5rem;
  line-height: 1.5;
}

.dialog-actions {
  display: flex;
  gap: 0.75rem;
  justify-content: flex-end;
}

.cancel-button,
.confirm-button {
  padding: 0.625rem 1.25rem;
  font-size: 0.875rem;
  font-weight: 600;
  border-radius: 6px;
  cursor: pointer;
  transition: background-color 0.2s;
}

.cancel-button {
  background: var(--color-gray-100);
  border: 1px solid var(--color-gray-300);
  color: var(--color-gray-700);
}

.cancel-button:hover {
  background: var(--color-gray-200);
}

.confirm-button {
  background: var(--color-magenta);
  border: none;
  color: var(--color-white);
}

.confirm-button:hover {
  background: var(--color-navy);
}
</style>
