<script setup lang="ts">
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'
import { SaveStatus } from '../../composables/useAutoSave'

const props = defineProps<{
  status: SaveStatus
  errorMessage?: string
}>()

const { t } = useI18n()

const isVisible = computed(() => props.status !== SaveStatus.IDLE)

const statusClass = computed(() => {
  switch (props.status) {
    case SaveStatus.SAVING:
      return 'is-saving'
    case SaveStatus.SAVED:
      return 'is-saved'
    case SaveStatus.ERROR:
      return 'is-error'
    default:
      return ''
  }
})

const displayText = computed(() => {
  switch (props.status) {
    case SaveStatus.SAVING:
      return t('review.saving')
    case SaveStatus.SAVED:
      return t('review.saved')
    case SaveStatus.ERROR:
      return props.errorMessage || t('errors.generic')
    default:
      return ''
  }
})
</script>

<template>
  <Transition name="fade">
    <div
      v-if="isVisible"
      :class="['save-indicator', statusClass]"
      role="status"
      aria-live="polite"
    >
      <!-- Saving spinner -->
      <span v-if="status === SaveStatus.SAVING" class="spinner" aria-hidden="true"></span>

      <!-- Saved checkmark -->
      <span v-else-if="status === SaveStatus.SAVED" class="checkmark" aria-hidden="true">✓</span>

      <!-- Error icon -->
      <span v-else-if="status === SaveStatus.ERROR" class="error-icon" aria-hidden="true">!</span>

      <!-- Status text -->
      <span class="status-text">{{ displayText }}</span>
    </div>
  </Transition>
</template>

<style scoped>
.save-indicator {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.375rem 0.75rem;
  border-radius: 4px;
  font-size: 0.8125rem;
  font-weight: 500;
}

.is-saving {
  background: var(--color-gray-100);
  color: var(--color-gray-600);
}

.is-saved {
  background: #D1FAE5;
  color: #065F46;
}

.is-error {
  background: #FEE2E2;
  color: #991B1B;
}

.spinner {
  width: 14px;
  height: 14px;
  border: 2px solid currentColor;
  border-top-color: transparent;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

.checkmark {
  font-size: 0.875rem;
  font-weight: bold;
}

.error-icon {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 16px;
  height: 16px;
  background: currentColor;
  color: white;
  border-radius: 50%;
  font-size: 0.75rem;
  font-weight: bold;
}

.error-icon::before {
  content: '!';
  color: #FEE2E2;
}

.status-text {
  white-space: nowrap;
}

/* Transition animations */
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.2s ease, transform 0.2s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
  transform: translateY(-4px);
}
</style>
