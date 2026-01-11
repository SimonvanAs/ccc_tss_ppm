<script setup lang="ts">
// TSS PPM v3.0 - System Configuration Form Component
import { ref, onMounted, computed } from 'vue'
import { useI18n } from 'vue-i18n'
import { Card, SectionHeader } from '@/components/layout'
import {
  fetchVoiceConfig,
  updateVoiceConfig,
  fetchReviewPeriods,
  toggleReviewPeriod,
  type VoiceConfig,
  type ReviewPeriod,
} from '@/api/admin'

const { t } = useI18n()

// Voice config state
const voiceLoading = ref(false)
const voiceSaving = ref(false)
const voiceError = ref<string | null>(null)
const voiceSuccess = ref<string | null>(null)
const voiceConfig = ref<VoiceConfig | null>(null)
const voiceForm = ref({
  voice_service_url: '',
  voice_service_enabled: true,
  voice_model: 'whisper-small',
})

// Review periods state
const periodsLoading = ref(false)
const periodsError = ref<string | null>(null)
const reviewPeriods = ref<ReviewPeriod[]>([])
const togglingPeriod = ref<string | null>(null)

const voiceModels = [
  { value: 'whisper-tiny', label: 'Whisper Tiny (Fast)' },
  { value: 'whisper-small', label: 'Whisper Small (Balanced)' },
  { value: 'whisper-medium', label: 'Whisper Medium (Accurate)' },
  { value: 'whisper-large', label: 'Whisper Large (Most Accurate)' },
]

const stageLabels: Record<string, string> = {
  GOAL_SETTING: 'Goal Setting',
  MID_YEAR_REVIEW: 'Mid-Year Review',
  END_YEAR_REVIEW: 'End-Year Review',
}

const voiceHasChanges = computed(() => {
  if (!voiceConfig.value) return false
  return (
    voiceForm.value.voice_service_url !== voiceConfig.value.voice_service_url ||
    voiceForm.value.voice_service_enabled !== voiceConfig.value.voice_service_enabled ||
    voiceForm.value.voice_model !== voiceConfig.value.voice_model
  )
})

async function loadVoiceConfig() {
  voiceLoading.value = true
  voiceError.value = null
  try {
    voiceConfig.value = await fetchVoiceConfig()
    voiceForm.value = {
      voice_service_url: voiceConfig.value.voice_service_url,
      voice_service_enabled: voiceConfig.value.voice_service_enabled,
      voice_model: voiceConfig.value.voice_model,
    }
  } catch (err) {
    voiceError.value = err instanceof Error ? err.message : t('admin.system.voice.loadError')
  } finally {
    voiceLoading.value = false
  }
}

async function saveVoiceConfig() {
  voiceSaving.value = true
  voiceError.value = null
  voiceSuccess.value = null
  try {
    voiceConfig.value = await updateVoiceConfig(voiceForm.value)
    voiceSuccess.value = t('admin.system.voice.saveSuccess')
    setTimeout(() => {
      voiceSuccess.value = null
    }, 3000)
  } catch (err) {
    voiceError.value = err instanceof Error ? err.message : t('admin.system.voice.saveError')
  } finally {
    voiceSaving.value = false
  }
}

function resetVoiceForm() {
  if (voiceConfig.value) {
    voiceForm.value = {
      voice_service_url: voiceConfig.value.voice_service_url,
      voice_service_enabled: voiceConfig.value.voice_service_enabled,
      voice_model: voiceConfig.value.voice_model,
    }
  }
}

async function loadReviewPeriods() {
  periodsLoading.value = true
  periodsError.value = null
  try {
    reviewPeriods.value = await fetchReviewPeriods()
  } catch (err) {
    periodsError.value = err instanceof Error ? err.message : t('admin.system.periods.loadError')
  } finally {
    periodsLoading.value = false
  }
}

async function handleTogglePeriod(period: ReviewPeriod) {
  if (!period.id) return
  togglingPeriod.value = period.id
  try {
    const updated = await toggleReviewPeriod(period.id, !period.is_open)
    const index = reviewPeriods.value.findIndex(p => p.id === period.id)
    if (index !== -1) {
      reviewPeriods.value[index] = updated
    }
  } catch (err) {
    periodsError.value = err instanceof Error ? err.message : t('admin.system.periods.toggleError')
  } finally {
    togglingPeriod.value = null
  }
}

function formatDate(dateString: string): string {
  return new Date(dateString).toLocaleDateString()
}

onMounted(() => {
  loadVoiceConfig()
  loadReviewPeriods()
})
</script>

<template>
  <div class="system-config-form">
    <!-- Voice Configuration -->
    <Card>
      <SectionHeader
        :title="t('admin.system.voice.title')"
        :description="t('admin.system.voice.description')"
      />

      <!-- Loading State -->
      <div v-if="voiceLoading" class="loading-state">
        <span class="spinner"></span>
        <span>{{ t('common.loading') }}</span>
      </div>

      <!-- Error State -->
      <div v-else-if="voiceError && !voiceConfig" class="error-message">
        {{ voiceError }}
        <button class="btn-link" @click="loadVoiceConfig">{{ t('common.retry') }}</button>
      </div>

      <!-- Form -->
      <template v-else-if="voiceConfig">
        <div v-if="voiceSuccess" class="success-message">{{ voiceSuccess }}</div>
        <div v-if="voiceError" class="error-message">{{ voiceError }}</div>

        <div class="form-group">
          <label class="checkbox-label">
            <input
              v-model="voiceForm.voice_service_enabled"
              type="checkbox"
              class="checkbox"
            />
            <span>{{ t('admin.system.voice.enabled') }}</span>
          </label>
          <small class="help-text">{{ t('admin.system.voice.enabledHelp') }}</small>
        </div>

        <div class="form-group">
          <label for="voice-url">{{ t('admin.system.voice.serviceUrl') }}</label>
          <input
            id="voice-url"
            v-model="voiceForm.voice_service_url"
            type="url"
            class="form-control"
            :placeholder="t('admin.system.voice.serviceUrlPlaceholder')"
          />
        </div>

        <div class="form-group">
          <label for="voice-model">{{ t('admin.system.voice.model') }}</label>
          <select
            id="voice-model"
            v-model="voiceForm.voice_model"
            class="form-control"
          >
            <option v-for="model in voiceModels" :key="model.value" :value="model.value">
              {{ model.label }}
            </option>
          </select>
        </div>

        <div class="form-actions">
          <button
            class="btn btn-secondary"
            :disabled="!voiceHasChanges || voiceSaving"
            @click="resetVoiceForm"
          >
            {{ t('common.reset') }}
          </button>
          <button
            class="btn btn-primary"
            :disabled="!voiceHasChanges || voiceSaving"
            @click="saveVoiceConfig"
          >
            <span v-if="voiceSaving" class="spinner-small"></span>
            {{ voiceSaving ? t('common.saving') : t('common.save') }}
          </button>
        </div>
      </template>
    </Card>

    <!-- Review Periods -->
    <Card class="mt-4">
      <SectionHeader
        :title="t('admin.system.periods.title')"
        :description="t('admin.system.periods.description')"
      />

      <!-- Loading State -->
      <div v-if="periodsLoading" class="loading-state">
        <span class="spinner"></span>
        <span>{{ t('common.loading') }}</span>
      </div>

      <!-- Error State -->
      <div v-else-if="periodsError && reviewPeriods.length === 0" class="error-message">
        {{ periodsError }}
        <button class="btn-link" @click="loadReviewPeriods">{{ t('common.retry') }}</button>
      </div>

      <!-- Empty State -->
      <div v-else-if="reviewPeriods.length === 0" class="empty-state">
        {{ t('admin.system.periods.empty') }}
      </div>

      <!-- Periods List -->
      <div v-else class="periods-list">
        <div v-if="periodsError" class="error-message mb-2">{{ periodsError }}</div>

        <div
          v-for="period in reviewPeriods"
          :key="period.id"
          class="period-item"
        >
          <div class="period-info">
            <span class="period-stage">{{ stageLabels[period.stage] || period.stage }}</span>
            <span class="period-year">{{ period.year }}</span>
          </div>
          <div class="period-dates">
            <span>{{ formatDate(period.start_date) }} - {{ formatDate(period.end_date) }}</span>
          </div>
          <div class="period-status">
            <span
              class="status-badge"
              :class="period.is_open ? 'status-open' : 'status-closed'"
            >
              {{ period.is_open ? t('admin.system.periods.open') : t('admin.system.periods.closed') }}
            </span>
          </div>
          <div class="period-actions">
            <button
              class="btn btn-sm"
              :class="period.is_open ? 'btn-warning' : 'btn-success'"
              :disabled="togglingPeriod === period.id"
              @click="handleTogglePeriod(period)"
            >
              <span v-if="togglingPeriod === period.id" class="spinner-small"></span>
              {{ period.is_open ? t('admin.system.periods.close') : t('admin.system.periods.openAction') }}
            </button>
          </div>
        </div>
      </div>
    </Card>
  </div>
</template>

<style scoped>
.system-config-form {
  max-width: 800px;
}

.mt-4 {
  margin-top: 1.5rem;
}

.mb-2 {
  margin-bottom: 0.5rem;
}

.loading-state {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
  padding: 2rem;
  color: var(--color-text-muted);
}

.spinner {
  width: 1.5rem;
  height: 1.5rem;
  border: 2px solid var(--color-border);
  border-top-color: var(--color-primary);
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
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

.error-message {
  padding: 0.75rem 1rem;
  background-color: var(--color-error-bg, #fee2e2);
  color: var(--color-error, #dc2626);
  border-radius: 0.375rem;
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 0.875rem;
}

.success-message {
  padding: 0.75rem 1rem;
  background-color: var(--color-success-bg, #dcfce7);
  color: var(--color-success, #16a34a);
  border-radius: 0.375rem;
  margin-bottom: 1rem;
  font-size: 0.875rem;
}

.btn-link {
  background: none;
  border: none;
  color: var(--color-primary);
  cursor: pointer;
  text-decoration: underline;
}

.empty-state {
  text-align: center;
  padding: 2rem;
  color: var(--color-text-muted);
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

.checkbox-label {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  cursor: pointer;
}

.checkbox {
  width: 1.125rem;
  height: 1.125rem;
  cursor: pointer;
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

.form-actions {
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

.btn-sm {
  padding: 0.375rem 0.75rem;
  font-size: 0.8125rem;
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

.btn-success {
  background-color: #16a34a;
  color: white;
  border: none;
}

.btn-success:hover:not(:disabled) {
  background-color: #15803d;
}

.btn-warning {
  background-color: #d97706;
  color: white;
  border: none;
}

.btn-warning:hover:not(:disabled) {
  background-color: #b45309;
}

.periods-list {
  margin-top: 1rem;
  border: 1px solid var(--color-border);
  border-radius: 0.5rem;
  overflow: hidden;
}

.period-item {
  display: grid;
  grid-template-columns: 1fr 1fr auto auto;
  gap: 1rem;
  align-items: center;
  padding: 1rem;
  border-bottom: 1px solid var(--color-border);
}

.period-item:last-child {
  border-bottom: none;
}

.period-info {
  display: flex;
  flex-direction: column;
}

.period-stage {
  font-weight: 500;
}

.period-year {
  font-size: 0.75rem;
  color: var(--color-text-muted);
}

.period-dates {
  font-size: 0.875rem;
  color: var(--color-text-muted);
}

.period-status {
  text-align: center;
}

.status-badge {
  display: inline-block;
  padding: 0.25rem 0.5rem;
  border-radius: 9999px;
  font-size: 0.75rem;
  font-weight: 500;
}

.status-open {
  background-color: #dcfce7;
  color: #16a34a;
}

.status-closed {
  background-color: #f3f4f6;
  color: #6b7280;
}

@media (max-width: 640px) {
  .period-item {
    grid-template-columns: 1fr;
    gap: 0.5rem;
  }

  .period-actions {
    margin-top: 0.5rem;
  }
}
</style>
