<script setup lang="ts">
// TSS PPM v3.0 - Business Unit Create/Edit Modal
import { ref, computed, onMounted } from 'vue'
import { useI18n } from 'vue-i18n'
import {
  createBusinessUnit,
  updateBusinessUnit,
  type BusinessUnit,
  type BusinessUnitCreateRequest,
  type BusinessUnitUpdateRequest,
} from '@/api/admin'

const { t } = useI18n()

const props = defineProps<{
  unit: BusinessUnit | null
  availableParents: BusinessUnit[]
}>()

const emit = defineEmits<{
  close: []
  save: []
}>()

const saving = ref(false)
const error = ref<string | null>(null)

const formData = ref<BusinessUnitCreateRequest>({
  name: '',
  code: '',
  parent_id: null,
})

const isEditing = computed(() => props.unit !== null)

const title = computed(() =>
  isEditing.value ? t('admin.businessUnits.editTitle') : t('admin.businessUnits.createTitle')
)

const isValid = computed(() => {
  return formData.value.name.trim().length > 0 && formData.value.code.trim().length > 0
})

async function handleSubmit() {
  if (!isValid.value) return

  saving.value = true
  error.value = null

  try {
    if (isEditing.value && props.unit) {
      const updateData: BusinessUnitUpdateRequest = {
        name: formData.value.name,
        code: formData.value.code,
        parent_id: formData.value.parent_id,
      }
      await updateBusinessUnit(props.unit.id, updateData)
    } else {
      await createBusinessUnit(formData.value)
    }
    emit('save')
  } catch (err) {
    error.value = err instanceof Error ? err.message : t('admin.businessUnits.saveError')
  } finally {
    saving.value = false
  }
}

function handleClose() {
  emit('close')
}

function handleOverlayClick(event: MouseEvent) {
  if (event.target === event.currentTarget) {
    handleClose()
  }
}

onMounted(() => {
  if (props.unit) {
    formData.value = {
      name: props.unit.name,
      code: props.unit.code,
      parent_id: props.unit.parent_id,
    }
  }
})
</script>

<template>
  <div class="modal-overlay" @click="handleOverlayClick">
    <div class="modal-content">
      <div class="modal-header">
        <h2>{{ title }}</h2>
        <button class="btn-close" @click="handleClose">
          <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <line x1="18" y1="6" x2="6" y2="18"></line>
            <line x1="6" y1="6" x2="18" y2="18"></line>
          </svg>
        </button>
      </div>

      <form @submit.prevent="handleSubmit">
        <div v-if="error" class="error-message">
          {{ error }}
        </div>

        <div class="form-group">
          <label for="bu-name">{{ t('admin.businessUnits.name') }} *</label>
          <input
            id="bu-name"
            v-model="formData.name"
            type="text"
            class="form-control"
            :placeholder="t('admin.businessUnits.namePlaceholder')"
            required
          />
        </div>

        <div class="form-group">
          <label for="bu-code">{{ t('admin.businessUnits.code') }} *</label>
          <input
            id="bu-code"
            v-model="formData.code"
            type="text"
            class="form-control"
            :placeholder="t('admin.businessUnits.codePlaceholder')"
            required
          />
          <small class="help-text">{{ t('admin.businessUnits.codeHelp') }}</small>
        </div>

        <div class="form-group">
          <label for="bu-parent">{{ t('admin.businessUnits.parent') }}</label>
          <select
            id="bu-parent"
            v-model="formData.parent_id"
            class="form-control"
          >
            <option :value="null">{{ t('admin.businessUnits.noParent') }}</option>
            <option v-for="parent in availableParents" :key="parent.id" :value="parent.id">
              {{ parent.name }} ({{ parent.code }})
            </option>
          </select>
          <small class="help-text">{{ t('admin.businessUnits.parentHelp') }}</small>
        </div>

        <div class="modal-actions">
          <button type="button" class="btn btn-secondary" :disabled="saving" @click="handleClose">
            {{ t('common.cancel') }}
          </button>
          <button type="submit" class="btn btn-primary" :disabled="!isValid || saving">
            <span v-if="saving" class="spinner-small"></span>
            {{ saving ? t('common.saving') : t('common.save') }}
          </button>
        </div>
      </form>
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

.modal-content {
  background: white;
  border-radius: 0.5rem;
  max-width: 500px;
  width: 90%;
  max-height: 90vh;
  overflow-y: auto;
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1rem 1.5rem;
  border-bottom: 1px solid var(--color-border);
}

.modal-header h2 {
  margin: 0;
  font-size: 1.25rem;
}

.btn-close {
  background: none;
  border: none;
  padding: 0.25rem;
  cursor: pointer;
  color: var(--color-text-muted);
  border-radius: 0.25rem;
  transition: all 0.15s ease;
}

.btn-close:hover {
  background-color: var(--color-bg-hover);
  color: var(--color-text);
}

form {
  padding: 1.5rem;
}

.error-message {
  padding: 0.75rem 1rem;
  background-color: var(--color-error-bg, #fee2e2);
  color: var(--color-error, #dc2626);
  border-radius: 0.375rem;
  margin-bottom: 1rem;
  font-size: 0.875rem;
}

.form-group {
  margin-bottom: 1rem;
}

.form-group label {
  display: block;
  margin-bottom: 0.25rem;
  font-weight: 500;
  color: var(--color-text);
  font-size: 0.875rem;
}

.form-control {
  width: 100%;
  padding: 0.5rem 0.75rem;
  border: 1px solid var(--color-border);
  border-radius: 0.375rem;
  font-size: 0.875rem;
  transition: border-color 0.15s ease;
}

.form-control:focus {
  outline: none;
  border-color: var(--color-primary);
  box-shadow: 0 0 0 3px rgba(204, 14, 112, 0.1);
}

.help-text {
  display: block;
  margin-top: 0.25rem;
  font-size: 0.75rem;
  color: var(--color-text-muted);
}

.modal-actions {
  display: flex;
  justify-content: flex-end;
  gap: 0.75rem;
  margin-top: 1.5rem;
  padding-top: 1rem;
  border-top: 1px solid var(--color-border);
}

.btn {
  padding: 0.5rem 1rem;
  border-radius: 0.375rem;
  font-weight: 500;
  font-size: 0.875rem;
  cursor: pointer;
  transition: all 0.15s ease;
  display: inline-flex;
  align-items: center;
}

.btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.btn-primary {
  background-color: var(--color-primary, #cc0e70);
  color: white;
  border: none;
}

.btn-primary:hover:not(:disabled) {
  background-color: var(--color-primary-dark, #a00b5a);
}

.btn-secondary {
  background-color: white;
  color: var(--color-text);
  border: 1px solid var(--color-border);
}

.btn-secondary:hover:not(:disabled) {
  background-color: var(--color-bg-hover);
}

.spinner-small {
  display: inline-block;
  width: 1rem;
  height: 1rem;
  border: 2px solid rgba(255, 255, 255, 0.3);
  border-top-color: white;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
  margin-right: 0.5rem;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}
</style>
