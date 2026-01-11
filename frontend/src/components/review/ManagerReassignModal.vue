<script setup lang="ts">
import { ref, computed, watch } from 'vue'
import { useI18n } from 'vue-i18n'

export interface Manager {
  id: string
  name: string
}

const props = withDefaults(
  defineProps<{
    show: boolean
    managers: Manager[]
    currentManagerId: string
    loading: boolean
    error?: string
  }>(),
  {
    error: '',
  }
)

const emit = defineEmits<{
  (e: 'submit', payload: { managerId: string; reason: string }): void
  (e: 'cancel'): void
}>()

const { t } = useI18n()

const selectedManagerId = ref('')
const reason = ref('')

// Filter out current manager from dropdown options
const availableManagers = computed(() => {
  return props.managers.filter((m) => m.id !== props.currentManagerId)
})

// Check if submit is allowed
const canSubmit = computed(() => {
  return selectedManagerId.value !== '' && !props.loading
})

// Reset form when modal is closed
watch(
  () => props.show,
  (newShow) => {
    if (!newShow) {
      selectedManagerId.value = ''
      reason.value = ''
    }
  }
)

function handleSubmit() {
  if (!canSubmit.value) return
  emit('submit', {
    managerId: selectedManagerId.value,
    reason: reason.value,
  })
}

function handleCancel() {
  emit('cancel')
}

function handleClose() {
  emit('cancel')
}
</script>

<template>
  <div v-if="show" data-testid="reassign-modal" class="modal-overlay">
    <div class="modal-container">
      <!-- Header -->
      <div class="modal-header">
        <h2 class="modal-title">{{ t('managerReassign.title') }}</h2>
        <button
          type="button"
          data-testid="close-button"
          class="close-button"
          :disabled="loading"
          @click="handleClose"
        >
          <span aria-hidden="true">&times;</span>
        </button>
      </div>

      <!-- Body -->
      <div class="modal-body">
        <!-- Error message -->
        <div v-if="error" data-testid="error-message" class="error-message">
          {{ error }}
        </div>

        <!-- Manager selection -->
        <div class="form-group">
          <label for="manager-select" class="form-label">
            {{ t('managerReassign.selectManager') }}
          </label>
          <select
            id="manager-select"
            v-model="selectedManagerId"
            data-testid="manager-select"
            class="form-select"
            :disabled="loading"
          >
            <option value="">{{ t('managerReassign.selectPlaceholder') }}</option>
            <option
              v-for="manager in availableManagers"
              :key="manager.id"
              :value="manager.id"
            >
              {{ manager.name }}
            </option>
          </select>
        </div>

        <!-- Reason (optional) -->
        <div class="form-group">
          <label for="reason-input" class="form-label">
            {{ t('managerReassign.reason') }}
            <span class="optional-label">{{ t('managerReassign.optional') }}</span>
          </label>
          <textarea
            id="reason-input"
            v-model="reason"
            data-testid="reason-input"
            class="form-textarea"
            :placeholder="t('managerReassign.reasonPlaceholder')"
            :disabled="loading"
            rows="3"
          ></textarea>
        </div>
      </div>

      <!-- Footer -->
      <div class="modal-footer">
        <button
          type="button"
          data-testid="cancel-button"
          class="btn btn-secondary"
          :disabled="loading"
          @click="handleCancel"
        >
          {{ t('actions.cancel') }}
        </button>
        <button
          type="button"
          data-testid="submit-button"
          class="btn btn-primary"
          :disabled="!canSubmit"
          @click="handleSubmit"
        >
          {{ loading ? t('managerReassign.submitting') : t('managerReassign.submit') }}
        </button>
      </div>
    </div>
  </div>
</template>

<style scoped>
.modal-overlay {
  position: fixed;
  inset: 0;
  background-color: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.modal-container {
  background: white;
  border-radius: 8px;
  box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04);
  width: 100%;
  max-width: 480px;
  max-height: 90vh;
  overflow: hidden;
  display: flex;
  flex-direction: column;
}

.modal-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 1rem 1.5rem;
  border-bottom: 1px solid var(--color-gray-200, #e5e7eb);
}

.modal-title {
  font-size: 1.125rem;
  font-weight: 600;
  color: var(--color-gray-900, #111827);
  margin: 0;
}

.close-button {
  background: none;
  border: none;
  font-size: 1.5rem;
  line-height: 1;
  color: var(--color-gray-500, #6b7280);
  cursor: pointer;
  padding: 0.25rem;
}

.close-button:hover:not(:disabled) {
  color: var(--color-gray-700, #374151);
}

.close-button:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.modal-body {
  padding: 1.5rem;
  overflow-y: auto;
}

.error-message {
  background: #fee2e2;
  color: #991b1b;
  padding: 0.75rem 1rem;
  border-radius: 6px;
  margin-bottom: 1rem;
  font-size: 0.875rem;
}

.form-group {
  margin-bottom: 1.25rem;
}

.form-group:last-child {
  margin-bottom: 0;
}

.form-label {
  display: block;
  font-size: 0.875rem;
  font-weight: 500;
  color: var(--color-gray-700, #374151);
  margin-bottom: 0.5rem;
}

.optional-label {
  font-weight: 400;
  color: var(--color-gray-500, #6b7280);
  margin-left: 0.25rem;
}

.form-select,
.form-textarea {
  width: 100%;
  padding: 0.625rem 0.75rem;
  font-size: 0.875rem;
  border: 1px solid var(--color-gray-300, #d1d5db);
  border-radius: 6px;
  background-color: white;
  color: var(--color-gray-900, #111827);
  transition: border-color 0.15s, box-shadow 0.15s;
}

.form-select:focus,
.form-textarea:focus {
  outline: none;
  border-color: var(--color-magenta, #cc0e70);
  box-shadow: 0 0 0 3px rgba(204, 14, 112, 0.1);
}

.form-select:disabled,
.form-textarea:disabled {
  background-color: var(--color-gray-100, #f3f4f6);
  cursor: not-allowed;
}

.form-textarea {
  resize: vertical;
  min-height: 80px;
}

.modal-footer {
  display: flex;
  justify-content: flex-end;
  gap: 0.75rem;
  padding: 1rem 1.5rem;
  border-top: 1px solid var(--color-gray-200, #e5e7eb);
  background-color: var(--color-gray-50, #f9fafb);
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

.btn-secondary {
  background: white;
  color: var(--color-gray-700, #374151);
  border: 1px solid var(--color-gray-300, #d1d5db);
}

.btn-secondary:hover:not(:disabled) {
  background: var(--color-gray-50, #f9fafb);
}

.btn-primary {
  background: var(--color-magenta, #cc0e70);
  color: white;
}

.btn-primary:hover:not(:disabled) {
  background: #a00b5a;
}
</style>
