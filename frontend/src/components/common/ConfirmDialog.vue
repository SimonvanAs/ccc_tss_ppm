<script setup lang="ts">
import { useI18n } from 'vue-i18n'
import Modal from './Modal.vue'

const props = defineProps<{
  show: boolean
  title: string
  message: string
  confirmText?: string
  cancelText?: string
  danger?: boolean
}>()

const emit = defineEmits<{
  confirm: []
  cancel: []
}>()

const { t } = useI18n()

const confirmLabel = props.confirmText || t('actions.confirm')
const cancelLabel = props.cancelText || t('actions.cancel')
</script>

<template>
  <Modal :show="show" :title="title" size="small" @close="emit('cancel')">
    <div class="confirm-dialog">
      <p class="message">{{ message }}</p>
      <div class="actions">
        <button
          type="button"
          class="btn btn-secondary"
          @click="emit('cancel')"
        >
          {{ cancelLabel }}
        </button>
        <button
          type="button"
          :class="['btn', danger ? 'btn-danger' : 'btn-primary']"
          @click="emit('confirm')"
        >
          {{ confirmLabel }}
        </button>
      </div>
    </div>
  </Modal>
</template>

<style scoped>
.confirm-dialog {
  text-align: center;
}

.message {
  margin: 0 0 1.5rem;
  font-size: 0.9375rem;
  color: var(--color-gray-700);
  line-height: 1.5;
}

.actions {
  display: flex;
  gap: 0.75rem;
  justify-content: center;
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
  min-width: 100px;
}

.btn-secondary {
  background: var(--color-gray-200);
  color: var(--color-gray-700);
}

.btn-secondary:hover {
  background: var(--color-gray-300);
}

.btn-primary {
  background: var(--color-navy);
  color: white;
}

.btn-primary:hover {
  background: #003570;
}

.btn-danger {
  background: var(--color-grid-red);
  color: white;
}

.btn-danger:hover {
  background: #b91c1c;
}
</style>
