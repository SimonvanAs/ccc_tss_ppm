<script setup lang="ts">
import { ref, computed, watch } from 'vue'
import { useI18n } from 'vue-i18n'
import { GoalType } from '../../types'
import type { Goal, GoalCreate } from '../../types'

const props = defineProps<{
  reviewId: string
  goal?: Goal
  loading?: boolean
}>()

const emit = defineEmits<{
  save: [data: GoalCreate]
  cancel: []
}>()

const { t } = useI18n()

// Form state - initialize with goal data if provided (edit mode)
const title = ref(props.goal?.title ?? '')
const description = ref(props.goal?.description ?? '')
const goalType = ref<GoalType>(props.goal?.goal_type ?? GoalType.STANDARD)
const weight = ref(props.goal?.weight ?? 20)

// Validation errors
const errors = ref<Record<string, string>>({})

// Watch for goal changes (if prop changes after mount)
watch(() => props.goal, (newGoal) => {
  if (newGoal) {
    title.value = newGoal.title
    description.value = newGoal.description || ''
    goalType.value = newGoal.goal_type
    weight.value = newGoal.weight
  }
})

// Clear specific field error when input changes
watch(title, () => {
  if (errors.value.title) {
    delete errors.value.title
    errors.value = { ...errors.value }
  }
})

watch(weight, () => {
  if (errors.value.weight) {
    delete errors.value.weight
    errors.value = { ...errors.value }
  }
})

// Computed display value for weight
const weightDisplay = computed(() => `${weight.value}%`)

// Snap weight to nearest multiple of 5 on blur
function snapWeight() {
  const snapped = Math.round(weight.value / 5) * 5
  weight.value = Math.max(5, Math.min(100, snapped))
}

// Validate form and return true if valid
function validate(): boolean {
  errors.value = {}

  // Title validation
  if (!title.value.trim()) {
    errors.value.title = t('validation.required')
  } else if (title.value.length > 500) {
    errors.value.title = t('validation.maxLength', { max: 500 })
  }

  // Weight validation
  if (weight.value < 5 || weight.value > 100) {
    errors.value.weight = t('validation.weightRange')
  } else if (weight.value % 5 !== 0) {
    errors.value.weight = t('goals.form.weightStep')
  }

  return Object.keys(errors.value).length === 0
}

// Handle form submission
function handleSubmit() {
  if (!validate()) {
    return
  }

  const data: GoalCreate = {
    title: title.value.trim(),
    description: description.value.trim() || undefined,
    goal_type: goalType.value,
    weight: weight.value,
  }

  emit('save', data)
}

// Handle cancel
function handleCancel() {
  emit('cancel')
}
</script>

<template>
  <form class="goal-form" @submit.prevent="handleSubmit">
    <!-- Title field -->
    <div class="form-group">
      <label for="title" class="form-label">
        {{ t('goals.goalTitle') }} <span class="required">*</span>
      </label>
      <input
        id="title"
        v-model="title"
        name="title"
        type="text"
        class="form-input"
        :class="{ 'is-invalid': errors.title }"
        :placeholder="t('goals.form.titlePlaceholder')"
        :disabled="loading"
        maxlength="500"
      />
      <p v-if="errors.title" class="error-message" data-field="title">
        {{ errors.title }}
      </p>
    </div>

    <!-- Description field -->
    <div class="form-group">
      <label for="description" class="form-label">
        {{ t('goals.description') }}
      </label>
      <textarea
        id="description"
        v-model="description"
        name="description"
        class="form-textarea"
        :placeholder="t('goals.form.descriptionPlaceholder')"
        :disabled="loading"
        rows="3"
      />
    </div>

    <!-- Goal type field -->
    <div class="form-group">
      <label for="goal_type" class="form-label">
        {{ t('goals.type') }}
      </label>
      <select
        id="goal_type"
        v-model="goalType"
        name="goal_type"
        class="form-select"
        :disabled="loading"
      >
        <option :value="GoalType.STANDARD">
          {{ t('goals.types.STANDARD') }}
        </option>
        <option :value="GoalType.KAR">
          {{ t('goals.types.KAR') }}
        </option>
        <option :value="GoalType.SCF">
          {{ t('goals.types.SCF') }}
        </option>
      </select>
    </div>

    <!-- Weight field -->
    <div class="form-group">
      <label for="weight" class="form-label">
        {{ t('goals.weight') }}
      </label>
      <div class="weight-input-group">
        <input
          id="weight"
          v-model.number="weight"
          name="weight"
          type="number"
          class="form-input weight-input"
          :class="{ 'is-invalid': errors.weight }"
          min="5"
          max="100"
          step="5"
          :disabled="loading"
          @blur="snapWeight"
        />
        <span class="weight-display">{{ weightDisplay }}</span>
      </div>
      <p v-if="errors.weight" class="error-message" data-field="weight">
        {{ errors.weight }}
      </p>
    </div>

    <!-- Form actions -->
    <div class="form-actions">
      <button
        type="button"
        class="btn btn-secondary"
        :disabled="loading"
        @click="handleCancel"
      >
        {{ t('actions.cancel') }}
      </button>
      <button
        type="submit"
        class="btn btn-primary"
        :disabled="loading"
      >
        {{ loading ? t('review.saving') : t('actions.save') }}
      </button>
    </div>
  </form>
</template>

<style scoped>
.goal-form {
  display: flex;
  flex-direction: column;
  gap: 1.25rem;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.form-label {
  font-weight: 600;
  font-size: 0.875rem;
  color: var(--color-gray-700);
}

.required {
  color: var(--color-magenta);
}

.form-input,
.form-textarea,
.form-select {
  padding: 0.625rem 0.75rem;
  border: 1px solid var(--color-gray-300);
  border-radius: 6px;
  font-family: inherit;
  font-size: 0.875rem;
  color: var(--color-gray-900);
  background: var(--color-white);
  transition: border-color 0.2s, box-shadow 0.2s;
}

.form-input:focus,
.form-textarea:focus,
.form-select:focus {
  outline: none;
  border-color: var(--color-navy);
  box-shadow: 0 0 0 3px rgba(0, 74, 145, 0.1);
}

.form-input.is-invalid,
.form-textarea.is-invalid {
  border-color: var(--color-grid-red);
}

.form-input:disabled,
.form-textarea:disabled,
.form-select:disabled {
  background: var(--color-gray-100);
  cursor: not-allowed;
}

.form-textarea {
  resize: vertical;
  min-height: 80px;
}

.weight-input-group {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.weight-input {
  width: 100px;
}

.weight-display {
  font-weight: 600;
  font-size: 1.125rem;
  color: var(--color-navy);
}

.error-message {
  margin: 0;
  font-size: 0.75rem;
  color: var(--color-grid-red);
}

.form-actions {
  display: flex;
  justify-content: flex-end;
  gap: 0.75rem;
  margin-top: 0.5rem;
  padding-top: 1rem;
  border-top: 1px solid var(--color-gray-200);
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
  background: var(--color-gray-200);
  color: var(--color-gray-700);
}

.btn-secondary:hover:not(:disabled) {
  background: var(--color-gray-300);
}

.btn-primary {
  background: var(--color-navy);
  color: white;
}

.btn-primary:hover:not(:disabled) {
  background: #003570;
}
</style>
