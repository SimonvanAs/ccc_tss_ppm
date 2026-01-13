<script setup lang="ts">
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'
import type { ReviewStatus, ReviewStage } from '../../api/reviews'
import VoiceInput from '../common/VoiceInput.vue'

const props = withDefaults(
  defineProps<{
    reviewId: string
    employeeName: string
    managerName: string
    reviewYear: number
    status: ReviewStatus
    stage: ReviewStage
    jobTitle: string | null
    tovLevel: string | null
    businessUnit?: string | null
    goalSettingCompletedAt: string | null
    midYearCompletedAt: string | null
    endYearCompletedAt: string | null
    isHrUser?: boolean
    readonly?: boolean
  }>(),
  {
    isHrUser: false,
    businessUnit: null,
    readonly: false,
  }
)

const emit = defineEmits<{
  'update:jobTitle': [value: string]
  'update:tovLevel': [value: string]
  'reassign': []
}>()

const { t } = useI18n()

const isEditable = computed(() => props.status === 'DRAFT' && !props.readonly)

const tovLevelOptions = ['A', 'B', 'C', 'D']

// Format review date for display
const formattedReviewDate = computed(() => {
  const today = new Date()
  return today.toLocaleDateString('en-GB', {
    day: '2-digit',
    month: '2-digit',
    year: 'numeric'
  })
})

function handleJobTitleChange(event: Event) {
  const target = event.target as HTMLInputElement
  emit('update:jobTitle', target.value)
}

function handleJobTitleVoice(text: string) {
  const currentValue = props.jobTitle ?? ''
  emit('update:jobTitle', currentValue + (currentValue ? ' ' : '') + text)
}

function handleTovLevelChange(event: Event) {
  const target = event.target as HTMLSelectElement
  emit('update:tovLevel', target.value)
}

function handleReassign() {
  emit('reassign')
}
</script>

<template>
  <div class="review-header">
    <!-- Section Header -->
    <div class="section-header">
      <h2 class="section-title">{{ t('reviewHeader.employeeInformation') }}</h2>
      <div class="section-divider"></div>
    </div>

    <!-- Form Grid -->
    <div class="form-grid">
      <!-- Row 1 -->
      <div class="form-field">
        <label class="field-label">
          {{ t('reviewHeader.employeeName') }} <span class="required">*</span>
        </label>
        <div class="field-value-display">{{ employeeName }}</div>
      </div>

      <div class="form-field">
        <label class="field-label" for="job-title">
          {{ t('reviewHeader.functionTitle') }} <span class="required">*</span>
        </label>
        <div class="input-with-voice">
          <input
            id="job-title"
            data-testid="job-title-input"
            type="text"
            class="field-input"
            :value="jobTitle ?? ''"
            :disabled="!isEditable"
            :placeholder="t('reviewHeader.functionTitlePlaceholder')"
            @input="handleJobTitleChange"
          />
          <VoiceInput
            v-if="isEditable"
            :disabled="!isEditable"
            @transcription="handleJobTitleVoice"
          />
        </div>
      </div>

      <!-- Row 2 -->
      <div class="form-field">
        <label class="field-label">
          {{ t('reviewHeader.businessUnit') }} <span class="required">*</span>
        </label>
        <div class="field-value-display">{{ businessUnit || '-' }}</div>
      </div>

      <div class="form-field">
        <label class="field-label" for="tov-level">
          {{ t('reviewHeader.ideLevel') }} <span class="required">*</span>
        </label>
        <select
          id="tov-level"
          data-testid="tov-level-select"
          class="field-select"
          :value="tovLevel ?? ''"
          :disabled="!isEditable"
          @change="handleTovLevelChange"
        >
          <option value="" disabled>{{ t('reviewHeader.selectLevel') }}</option>
          <option v-for="level in tovLevelOptions" :key="level" :value="level">
            {{ t(`reviewHeader.tovLevelOption.${level}`) }}
          </option>
        </select>
      </div>

      <!-- Row 3 -->
      <div class="form-field">
        <label class="field-label">
          {{ t('reviewHeader.reviewDate') }} <span class="required">*</span>
        </label>
        <div class="field-value-display">{{ formattedReviewDate }}</div>
      </div>

      <div class="form-field">
        <label class="field-label">
          {{ t('reviewHeader.managerName') }}
        </label>
        <div class="manager-field">
          <span class="field-value-display">{{ managerName }}</span>
          <button
            v-if="isHrUser"
            data-testid="reassign-button"
            type="button"
            class="reassign-button"
            @click="handleReassign"
          >
            {{ t('managerReassign.reassignButton') }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.review-header {
  background-color: var(--color-white, #ffffff);
  border-radius: 8px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1), 0 1px 2px rgba(0, 0, 0, 0.06);
  padding: 1.5rem;
}

.section-header {
  margin-bottom: 1.5rem;
}

.section-title {
  font-size: 1.125rem;
  font-weight: 700;
  color: var(--color-magenta, #CC0E70);
  margin: 0 0 0.75rem 0;
}

.section-divider {
  height: 2px;
  background-color: var(--color-magenta, #CC0E70);
}

.form-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 1.5rem;
}

.form-field {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.field-label {
  font-size: 0.875rem;
  font-weight: 500;
  color: var(--color-gray-700, #374151);
}

.required {
  color: var(--color-magenta, #CC0E70);
}

.field-value-display {
  font-size: 0.9375rem;
  padding: 0.625rem 0.875rem;
  color: var(--color-gray-900, #111827);
  background-color: var(--color-gray-50, #f9fafb);
  border: 1px solid var(--color-gray-200, #e5e7eb);
  border-radius: 6px;
}

.manager-field {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.manager-field .field-value-display {
  flex: 1;
}

.reassign-button {
  padding: 0.5rem 0.75rem;
  font-size: 0.75rem;
  font-weight: 500;
  color: var(--color-magenta, #CC0E70);
  background: none;
  border: 1px solid var(--color-magenta, #CC0E70);
  border-radius: 4px;
  cursor: pointer;
  transition: all 0.2s;
  white-space: nowrap;
}

.reassign-button:hover {
  background: var(--color-magenta, #CC0E70);
  color: white;
}

.input-with-voice {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.field-input {
  flex: 1;
  font-family: inherit;
  font-size: 0.9375rem;
  padding: 0.625rem 0.875rem;
  border: 1px solid var(--color-gray-300, #d1d5db);
  border-radius: 6px;
  background-color: var(--color-white, #ffffff);
  color: var(--color-gray-900, #111827);
  transition: border-color 0.2s, box-shadow 0.2s;
}

.field-input::placeholder {
  color: var(--color-gray-400, #9ca3af);
}

.field-input:focus {
  outline: none;
  border-color: var(--color-navy, #004A91);
  box-shadow: 0 0 0 3px rgba(0, 74, 145, 0.1);
}

.field-input:disabled {
  background-color: var(--color-gray-50, #f9fafb);
  color: var(--color-gray-500, #6b7280);
  cursor: not-allowed;
}

.field-select {
  font-family: inherit;
  font-size: 0.9375rem;
  padding: 0.625rem 0.875rem;
  border: 1px solid var(--color-gray-300, #d1d5db);
  border-radius: 6px;
  background-color: var(--color-white, #ffffff);
  color: var(--color-gray-900, #111827);
  cursor: pointer;
  transition: border-color 0.2s, box-shadow 0.2s;
  appearance: none;
  background-image: url("data:image/svg+xml,%3csvg xmlns='http://www.w3.org/2000/svg' fill='none' viewBox='0 0 20 20'%3e%3cpath stroke='%236b7280' stroke-linecap='round' stroke-linejoin='round' stroke-width='1.5' d='M6 8l4 4 4-4'/%3e%3c/svg%3e");
  background-position: right 0.5rem center;
  background-repeat: no-repeat;
  background-size: 1.5em 1.5em;
  padding-right: 2.5rem;
}

.field-select:focus {
  outline: none;
  border-color: var(--color-navy, #004A91);
  box-shadow: 0 0 0 3px rgba(0, 74, 145, 0.1);
}

.field-select:disabled {
  background-color: var(--color-gray-50, #f9fafb);
  color: var(--color-gray-500, #6b7280);
  cursor: not-allowed;
}

/* Responsive */
@media (max-width: 640px) {
  .form-grid {
    grid-template-columns: 1fr;
  }
}
</style>
