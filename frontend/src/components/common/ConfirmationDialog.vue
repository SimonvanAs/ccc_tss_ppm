<script setup lang="ts">
interface Props {
  modelValue: boolean
  title: string
  message: string
  confirmText?: string
  cancelText?: string
  loading?: boolean
  variant?: 'default' | 'danger'
}

const props = withDefaults(defineProps<Props>(), {
  confirmText: 'Confirm',
  cancelText: 'Cancel',
  loading: false,
  variant: 'default',
})

const emit = defineEmits<{
  (e: 'update:modelValue', value: boolean): void
  (e: 'confirm'): void
  (e: 'cancel'): void
}>()

function handleCancel() {
  if (!props.loading) {
    emit('update:modelValue', false)
    emit('cancel')
  }
}

function handleConfirm() {
  if (!props.loading) {
    emit('update:modelValue', false)
    emit('confirm')
  }
}

function handleBackdropClick() {
  if (!props.loading) {
    emit('update:modelValue', false)
  }
}
</script>

<template>
  <Teleport to="body">
    <div v-if="modelValue" class="dialog-overlay">
      <div class="dialog-backdrop" @click="handleBackdropClick"></div>
      <div class="dialog-content" role="dialog" aria-modal="true">
        <h3 class="dialog-title">{{ title }}</h3>
        <p class="dialog-message">{{ message }}</p>
        <div class="dialog-actions">
          <button
            class="cancel-button"
            :disabled="loading"
            @click="handleCancel"
          >
            {{ cancelText }}
          </button>
          <button
            class="confirm-button"
            :class="{ danger: variant === 'danger' }"
            :disabled="loading"
            @click="handleConfirm"
          >
            <span v-if="loading" class="loading-spinner"></span>
            <span v-else>{{ confirmText }}</span>
          </button>
        </div>
      </div>
    </div>
  </Teleport>
</template>

<style scoped>
.dialog-overlay {
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
  display: inline-flex;
  align-items: center;
  justify-content: center;
  padding: 0.625rem 1.25rem;
  font-size: 0.875rem;
  font-weight: 600;
  border-radius: 6px;
  cursor: pointer;
  transition: background-color 0.2s, opacity 0.2s;
  min-width: 90px;
}

.cancel-button {
  background: var(--color-gray-100);
  border: 1px solid var(--color-gray-300);
  color: var(--color-gray-700);
}

.cancel-button:hover:not(:disabled) {
  background: var(--color-gray-200);
}

.cancel-button:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.confirm-button {
  background: var(--color-magenta);
  border: none;
  color: var(--color-white);
}

.confirm-button:hover:not(:disabled) {
  background: var(--color-navy);
}

.confirm-button:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.confirm-button.danger {
  background: var(--color-grid-red, #dc2626);
}

.confirm-button.danger:hover:not(:disabled) {
  background: #b91c1c;
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
</style>
