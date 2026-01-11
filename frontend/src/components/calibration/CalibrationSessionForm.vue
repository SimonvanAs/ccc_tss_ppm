<script setup lang="ts">
// TSS PPM v3.0 - CalibrationSessionForm Component
import { ref, computed, watch } from 'vue'
import { useI18n } from 'vue-i18n'
import {
  createCalibrationSession,
  updateCalibrationSession,
  type CalibrationSession,
  type CalibrationSessionCreate,
  type CalibrationScope,
} from '../../api/calibration'

const { t } = useI18n()

const props = defineProps<{
  session?: CalibrationSession
}>()

const emit = defineEmits<{
  (e: 'success', session: CalibrationSession): void
  (e: 'cancel'): void
}>()

const isEditMode = computed(() => !!props.session)

// Form state
const name = ref('')
const description = ref('')
const reviewYear = ref(new Date().getFullYear())
const scope = ref<CalibrationScope>('COMPANY_WIDE')

// UI state
const submitting = ref(false)
const errors = ref<{ name?: string; reviewYear?: string }>({})

// Populate form in edit mode
watch(
  () => props.session,
  (session) => {
    if (session) {
      name.value = session.name
      description.value = session.description || ''
      reviewYear.value = session.review_year
      scope.value = session.scope
    }
  },
  { immediate: true }
)

function validate(): boolean {
  errors.value = {}

  if (!name.value.trim()) {
    errors.value.name = t('calibration.form.validation.nameRequired')
  }

  if (!reviewYear.value) {
    errors.value.reviewYear = t('calibration.form.validation.yearRequired')
  }

  return Object.keys(errors.value).length === 0
}

async function handleSubmit() {
  if (!validate()) return

  submitting.value = true

  try {
    const formData: CalibrationSessionCreate = {
      name: name.value.trim(),
      description: description.value.trim() || undefined,
      review_year: Number(reviewYear.value),
      scope: scope.value,
    }

    let result: CalibrationSession

    if (isEditMode.value && props.session) {
      result = await updateCalibrationSession(props.session.id, {
        name: formData.name,
        description: formData.description,
      })
    } else {
      result = await createCalibrationSession(formData)
    }

    emit('success', result)
  } catch (error) {
    console.error('Failed to save session:', error)
  } finally {
    submitting.value = false
  }
}

function handleCancel() {
  emit('cancel')
}
</script>

<template>
  <div class="calibration-session-form">
    <h2 class="form-title">
      {{ isEditMode ? t('calibration.form.title.edit') : t('calibration.form.title.create') }}
    </h2>

    <form @submit.prevent="handleSubmit">
      <div class="form-group">
        <label for="name">{{ t('calibration.form.name') }}</label>
        <input
          id="name"
          v-model="name"
          type="text"
          name="name"
          :placeholder="t('calibration.form.namePlaceholder')"
          :class="{ 'has-error': errors.name }"
        />
        <span v-if="errors.name" class="error-message">{{ errors.name }}</span>
      </div>

      <div class="form-group">
        <label for="description">{{ t('calibration.form.description') }}</label>
        <textarea
          id="description"
          v-model="description"
          name="description"
          rows="3"
          :placeholder="t('calibration.form.descriptionPlaceholder')"
        />
      </div>

      <div class="form-row">
        <div class="form-group">
          <label for="reviewYear">{{ t('calibration.form.reviewYear') }}</label>
          <input
            id="reviewYear"
            v-model.number="reviewYear"
            type="number"
            name="reviewYear"
            min="2000"
            max="2100"
            :class="{ 'has-error': errors.reviewYear }"
          />
          <span v-if="errors.reviewYear" class="error-message">{{ errors.reviewYear }}</span>
        </div>

        <div class="form-group">
          <label for="scope">{{ t('calibration.form.scope') }}</label>
          <select id="scope" v-model="scope" name="scope">
            <option value="COMPANY_WIDE">{{ t('calibration.form.scope.COMPANY_WIDE') }}</option>
            <option value="BUSINESS_UNIT">{{ t('calibration.form.scope.BUSINESS_UNIT') }}</option>
          </select>
        </div>
      </div>

      <div class="form-actions">
        <button type="button" class="cancel-btn" @click="handleCancel">
          {{ t('calibration.form.cancel') }}
        </button>
        <button type="submit" class="submit-btn" :disabled="submitting">
          {{ isEditMode ? t('calibration.form.submit.edit') : t('calibration.form.submit.create') }}
        </button>
      </div>
    </form>
  </div>
</template>

<style scoped>
.calibration-session-form {
  max-width: 600px;
  padding: 1.5rem;
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.form-title {
  margin: 0 0 1.5rem;
  color: var(--navy, #004a91);
  font-family: Tahoma, sans-serif;
}

.form-group {
  margin-bottom: 1rem;
}

.form-group label {
  display: block;
  margin-bottom: 0.5rem;
  font-weight: 500;
  color: #333;
  font-family: Tahoma, sans-serif;
}

.form-group input,
.form-group textarea,
.form-group select {
  width: 100%;
  padding: 0.75rem;
  border: 1px solid #ccc;
  border-radius: 4px;
  font-family: Tahoma, sans-serif;
  font-size: 1rem;
  box-sizing: border-box;
}

.form-group input:focus,
.form-group textarea:focus,
.form-group select:focus {
  outline: none;
  border-color: var(--magenta, #cc0e70);
  box-shadow: 0 0 0 2px rgba(204, 14, 112, 0.1);
}

.form-group input.has-error,
.form-group textarea.has-error {
  border-color: #c00;
}

.error-message {
  display: block;
  margin-top: 0.25rem;
  color: #c00;
  font-size: 0.85rem;
}

.form-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1rem;
}

.form-actions {
  display: flex;
  justify-content: flex-end;
  gap: 1rem;
  margin-top: 1.5rem;
  padding-top: 1rem;
  border-top: 1px solid #eee;
}

.cancel-btn {
  padding: 0.75rem 1.5rem;
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
  padding: 0.75rem 1.5rem;
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
