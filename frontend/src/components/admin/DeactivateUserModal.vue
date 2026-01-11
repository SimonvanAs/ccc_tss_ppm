<script setup lang="ts">
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'
import type { AdminUser } from '../../api/admin'

const props = defineProps<{
  show: boolean
  user: AdminUser | null
  loading: boolean
}>()

const emit = defineEmits<{
  (e: 'confirm'): void
  (e: 'cancel'): void
}>()

const { t } = useI18n()

// Determine if this is a deactivate or activate action
const isDeactivate = computed(() => props.user?.enabled ?? true)

// Title based on action
const title = computed(() =>
  isDeactivate.value
    ? t('admin.users.deactivateUser')
    : t('admin.users.activateUser')
)

// User display name
const userName = computed(() => {
  if (!props.user) return ''
  if (props.user.first_name && props.user.last_name) {
    return `${props.user.first_name} ${props.user.last_name}`
  }
  return props.user.email
})

// Confirmation message
const confirmMessage = computed(() =>
  isDeactivate.value
    ? t('admin.users.deactivateConfirm', { name: userName.value })
    : t('admin.users.activateConfirm', { name: userName.value })
)

// Warning message
const warningMessage = computed(() =>
  isDeactivate.value
    ? t('admin.users.deactivateWarning')
    : t('admin.users.activateWarning')
)

// Handle overlay click
function handleOverlayClick(event: MouseEvent) {
  if (event.target === event.currentTarget) {
    emit('cancel')
  }
}
</script>

<template>
  <div v-if="show" class="modal-overlay" @click="handleOverlayClick">
    <div class="modal-content" @click.stop>
      <div class="modal-header">
        <h2 class="modal-title">{{ title }}</h2>
      </div>

      <div class="modal-body">
        <p class="confirm-message">{{ confirmMessage }}</p>
        <p class="warning-message">{{ warningMessage }}</p>
      </div>

      <div class="modal-footer">
        <button
          data-testid="cancel-button"
          class="btn btn-secondary"
          :disabled="loading"
          @click="emit('cancel')"
        >
          {{ t('admin.users.cancel') }}
        </button>
        <button
          data-testid="confirm-button"
          class="btn"
          :class="isDeactivate ? 'btn-danger' : 'btn-success'"
          :disabled="loading"
          @click="emit('confirm')"
        >
          {{ loading ? t('admin.users.processing') : t('admin.users.confirm') }}
        </button>
      </div>
    </div>
  </div>
</template>

<style scoped>
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(0, 0, 0, 0.5);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
}

.modal-content {
  background: white;
  border-radius: 8px;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1), 0 10px 20px rgba(0, 0, 0, 0.15);
  width: 100%;
  max-width: 400px;
}

.modal-header {
  padding: 1.25rem 1.5rem;
  border-bottom: 1px solid var(--color-gray-200, #e5e7eb);
}

.modal-title {
  margin: 0;
  font-size: 1.125rem;
  font-weight: 600;
  color: var(--color-gray-900, #111827);
}

.modal-body {
  padding: 1.5rem;
}

.confirm-message {
  margin: 0 0 0.75rem 0;
  font-size: 0.875rem;
  color: var(--color-gray-700, #374151);
}

.warning-message {
  margin: 0;
  font-size: 0.875rem;
  color: var(--color-gray-500, #6b7280);
}

.modal-footer {
  padding: 1rem 1.5rem;
  border-top: 1px solid var(--color-gray-200, #e5e7eb);
  display: flex;
  justify-content: flex-end;
  gap: 0.75rem;
}

.btn {
  padding: 0.5rem 1rem;
  border: none;
  border-radius: 6px;
  font-family: inherit;
  font-size: 0.875rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
}

.btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.btn-secondary {
  background-color: var(--color-gray-100, #f3f4f6);
  color: var(--color-gray-700, #374151);
}

.btn-secondary:hover:not(:disabled) {
  background-color: var(--color-gray-200, #e5e7eb);
}

.btn-danger {
  background-color: #dc2626;
  color: white;
}

.btn-danger:hover:not(:disabled) {
  background-color: #b91c1c;
}

.btn-success {
  background-color: #16a34a;
  color: white;
}

.btn-success:hover:not(:disabled) {
  background-color: #15803d;
}
</style>
