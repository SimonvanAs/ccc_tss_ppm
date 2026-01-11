<script setup lang="ts">
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'
import type { ReviewStatus, ReviewStage } from '../../api/reviews'

const props = defineProps<{
  reviewId: string
  employeeName: string
  managerName: string
  reviewYear: number
  status: ReviewStatus
  stage: ReviewStage
  jobTitle: string | null
  tovLevel: string | null
  goalSettingCompletedAt: string | null
  midYearCompletedAt: string | null
  endYearCompletedAt: string | null
}>()

const emit = defineEmits<{
  'update:jobTitle': [value: string]
  'update:tovLevel': [value: string]
}>()

const { t, d } = useI18n()

const isEditable = computed(() => props.status === 'DRAFT')

const tovLevelOptions = ['A', 'B', 'C', 'D']

function formatStageDate(dateStr: string | null): string {
  if (!dateStr) {
    return t('reviewHeader.pending')
  }
  return d(new Date(dateStr), 'short')
}

function handleJobTitleChange(event: Event) {
  const target = event.target as HTMLInputElement
  emit('update:jobTitle', target.value)
}

function handleTovLevelChange(event: Event) {
  const target = event.target as HTMLSelectElement
  emit('update:tovLevel', target.value)
}
</script>

<template>
  <div class="review-header">
    <div class="review-header-grid">
      <!-- Row 1: Employee, Manager, Year -->
      <div class="header-row info-row">
        <div class="header-field">
          <label class="field-label">{{ t('reviewHeader.employee') }}</label>
          <span class="field-value">{{ employeeName }}</span>
        </div>
        <div class="header-field">
          <label class="field-label">{{ t('reviewHeader.manager') }}</label>
          <span class="field-value">{{ managerName }}</span>
        </div>
        <div class="header-field">
          <label class="field-label">{{ t('reviewHeader.reviewYear') }}</label>
          <span class="field-value">{{ reviewYear }}</span>
        </div>
      </div>

      <!-- Row 2: Job Title, TOV Level -->
      <div class="header-row editable-row">
        <div class="header-field">
          <label class="field-label" for="job-title-input">
            {{ t('reviewHeader.jobTitle') }}
          </label>
          <input
            id="job-title-input"
            data-testid="job-title-input"
            type="text"
            class="field-input"
            :value="jobTitle ?? ''"
            :disabled="!isEditable"
            :placeholder="t('reviewHeader.jobTitlePlaceholder')"
            @input="handleJobTitleChange"
          />
        </div>
        <div class="header-field">
          <label class="field-label" for="tov-level-select">
            {{ t('reviewHeader.tovLevel') }}
          </label>
          <select
            id="tov-level-select"
            data-testid="tov-level-select"
            class="field-select"
            :value="tovLevel ?? ''"
            :disabled="!isEditable"
            @change="handleTovLevelChange"
          >
            <option value="" disabled>{{ t('reviewHeader.selectTovLevel') }}</option>
            <option v-for="level in tovLevelOptions" :key="level" :value="level">
              {{ t(`reviewHeader.tovLevelOption.${level}`) }}
            </option>
          </select>
        </div>
      </div>

      <!-- Row 3: Stage Dates -->
      <div class="header-row dates-row">
        <div class="header-field">
          <label class="field-label">{{ t('reviewHeader.goalSettingCompleted') }}</label>
          <span class="field-value date-value">
            {{ formatStageDate(goalSettingCompletedAt) }}
          </span>
        </div>
        <div class="header-field">
          <label class="field-label">{{ t('reviewHeader.midYearCompleted') }}</label>
          <span class="field-value date-value">
            {{ formatStageDate(midYearCompletedAt) }}
          </span>
        </div>
        <div class="header-field">
          <label class="field-label">{{ t('reviewHeader.endYearCompleted') }}</label>
          <span class="field-value date-value">
            {{ formatStageDate(endYearCompletedAt) }}
          </span>
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

.review-header-grid {
  display: flex;
  flex-direction: column;
  gap: 1.25rem;
}

.header-row {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 1.5rem;
}

.header-field {
  display: flex;
  flex-direction: column;
  gap: 0.375rem;
}

.field-label {
  font-size: 0.75rem;
  font-weight: 600;
  color: var(--color-gray-500, #6b7280);
  text-transform: uppercase;
  letter-spacing: 0.025em;
}

.field-value {
  font-size: 0.9375rem;
  color: var(--color-gray-900, #111827);
  font-weight: 500;
}

.date-value {
  font-family: 'Tahoma', sans-serif;
}

.field-input,
.field-select {
  font-family: inherit;
  font-size: 0.9375rem;
  padding: 0.5rem 0.75rem;
  border: 1px solid var(--color-gray-300, #d1d5db);
  border-radius: 6px;
  background-color: var(--color-white, #ffffff);
  color: var(--color-gray-900, #111827);
  transition: border-color 0.2s, box-shadow 0.2s;
}

.field-input:focus,
.field-select:focus {
  outline: none;
  border-color: var(--color-magenta, #CC0E70);
  box-shadow: 0 0 0 3px rgba(204, 14, 112, 0.1);
}

.field-input:disabled,
.field-select:disabled {
  background-color: var(--color-gray-50, #f9fafb);
  color: var(--color-gray-500, #6b7280);
  cursor: not-allowed;
}

.field-select {
  cursor: pointer;
}

.field-select:disabled {
  cursor: not-allowed;
}

/* Responsive adjustments */
@media (max-width: 768px) {
  .header-row {
    grid-template-columns: 1fr;
    gap: 1rem;
  }

  .editable-row {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (max-width: 480px) {
  .editable-row {
    grid-template-columns: 1fr;
  }
}
</style>
