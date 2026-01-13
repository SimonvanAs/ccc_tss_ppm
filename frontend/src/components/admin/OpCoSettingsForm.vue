<script setup lang="ts">
// TSS PPM v3.0 - OpCo Settings Form Component
import { ref, onMounted, computed } from 'vue'
import { useI18n } from 'vue-i18n'
import { Card, SectionHeader } from '@/components/layout'
import {
  fetchOpCoSettings,
  updateOpCoSettings,
  uploadOpCoLogo,
  deleteOpCoLogo,
  type OpCoResponse,
  type OpCoUpdateRequest,
} from '@/api/admin'

const { t } = useI18n()

const loading = ref(false)
const saving = ref(false)
const error = ref<string | null>(null)
const successMessage = ref<string | null>(null)
const opco = ref<OpCoResponse | null>(null)

// Logo upload state
const logoUploading = ref(false)
const logoError = ref<string | null>(null)
const fileInputRef = ref<HTMLInputElement | null>(null)

// Form state
const formData = ref<OpCoUpdateRequest>({
  name: '',
  code: '',
  default_language: 'en',
  settings: {
    review_cycle: {
      goal_setting_start: '',
      goal_setting_end: '',
      mid_year_start: '',
      mid_year_end: '',
      end_year_start: '',
      end_year_end: '',
    },
  },
})

const languages = [
  { value: 'en', label: 'English' },
  { value: 'nl', label: 'Nederlands' },
  { value: 'es', label: 'Español' },
]

const hasChanges = computed(() => {
  if (!opco.value) return false
  // Note: logo_url is not included - logo is uploaded immediately, not as part of form save
  return (
    formData.value.name !== opco.value.name ||
    formData.value.code !== opco.value.code ||
    formData.value.default_language !== opco.value.default_language ||
    JSON.stringify(formData.value.settings) !== JSON.stringify(opco.value.settings)
  )
})

async function loadSettings() {
  loading.value = true
  error.value = null
  try {
    opco.value = await fetchOpCoSettings()
    formData.value = {
      name: opco.value.name,
      code: opco.value.code,
      logo_url: opco.value.logo_url,
      default_language: opco.value.default_language,
      settings: {
        review_cycle: {
          goal_setting_start: opco.value.settings?.review_cycle?.goal_setting_start || '',
          goal_setting_end: opco.value.settings?.review_cycle?.goal_setting_end || '',
          mid_year_start: opco.value.settings?.review_cycle?.mid_year_start || '',
          mid_year_end: opco.value.settings?.review_cycle?.mid_year_end || '',
          end_year_start: opco.value.settings?.review_cycle?.end_year_start || '',
          end_year_end: opco.value.settings?.review_cycle?.end_year_end || '',
        },
      },
    }
  } catch (err) {
    error.value = err instanceof Error ? err.message : t('admin.opco.loadError')
  } finally {
    loading.value = false
  }
}

async function saveSettings() {
  saving.value = true
  error.value = null
  successMessage.value = null
  try {
    opco.value = await updateOpCoSettings(formData.value)
    successMessage.value = t('admin.opco.saveSuccess')
    setTimeout(() => {
      successMessage.value = null
    }, 3000)
  } catch (err) {
    error.value = err instanceof Error ? err.message : t('admin.opco.saveError')
  } finally {
    saving.value = false
  }
}

function resetForm() {
  if (opco.value) {
    formData.value = {
      name: opco.value.name,
      code: opco.value.code,
      logo_url: opco.value.logo_url,
      default_language: opco.value.default_language,
      settings: {
        review_cycle: {
          goal_setting_start: opco.value.settings?.review_cycle?.goal_setting_start || '',
          goal_setting_end: opco.value.settings?.review_cycle?.goal_setting_end || '',
          mid_year_start: opco.value.settings?.review_cycle?.mid_year_start || '',
          mid_year_end: opco.value.settings?.review_cycle?.mid_year_end || '',
          end_year_start: opco.value.settings?.review_cycle?.end_year_start || '',
          end_year_end: opco.value.settings?.review_cycle?.end_year_end || '',
        },
      },
    }
  }
}

// Logo upload handlers
function triggerFileInput() {
  fileInputRef.value?.click()
}

async function handleLogoSelect(event: Event) {
  const input = event.target as HTMLInputElement
  const file = input.files?.[0]
  if (!file) return

  // Validate file type
  const allowedTypes = ['image/png', 'image/jpeg', 'image/gif', 'image/svg+xml', 'image/webp']
  if (!allowedTypes.includes(file.type)) {
    logoError.value = t('admin.opco.logoInvalidType')
    return
  }

  // Validate file size (5MB max)
  if (file.size > 5 * 1024 * 1024) {
    logoError.value = t('admin.opco.logoTooLarge')
    return
  }

  logoError.value = null
  logoUploading.value = true

  try {
    const response = await uploadOpCoLogo(file)
    // Update both opco and formData with new logo URL
    if (opco.value) {
      opco.value.logo_url = response.logo_url
    }
    formData.value.logo_url = response.logo_url
    successMessage.value = t('admin.opco.logoUploadSuccess')
    setTimeout(() => {
      successMessage.value = null
    }, 3000)
  } catch (err) {
    logoError.value = err instanceof Error ? err.message : t('admin.opco.logoUploadError')
  } finally {
    logoUploading.value = false
    // Reset file input
    if (input) input.value = ''
  }
}

async function handleLogoDelete() {
  if (!opco.value?.logo_url) return

  logoUploading.value = true
  logoError.value = null

  try {
    await deleteOpCoLogo()
    if (opco.value) {
      opco.value.logo_url = null
    }
    formData.value.logo_url = null
    successMessage.value = t('admin.opco.logoDeleteSuccess')
    setTimeout(() => {
      successMessage.value = null
    }, 3000)
  } catch (err) {
    logoError.value = err instanceof Error ? err.message : t('admin.opco.logoDeleteError')
  } finally {
    logoUploading.value = false
  }
}

onMounted(() => {
  loadSettings()
})
</script>

<template>
  <div class="opco-settings-form">
    <!-- Loading State -->
    <div v-if="loading" class="loading-state">
      <span class="spinner"></span>
      <span>{{ t('common.loading') }}</span>
    </div>

    <!-- Error State -->
    <div v-else-if="error" class="error-message">
      {{ error }}
      <button class="btn-link" @click="loadSettings">{{ t('common.retry') }}</button>
    </div>

    <!-- Form -->
    <template v-else-if="opco">
      <!-- Success Message -->
      <div v-if="successMessage" class="success-message">
        {{ successMessage }}
      </div>

      <!-- General Settings -->
      <Card>
        <SectionHeader
          :title="t('admin.opco.generalSettings')"
          :description="t('admin.opco.generalSettingsDescription')"
        />

        <div class="form-grid">
          <div class="form-group">
            <label for="opco-name">{{ t('admin.opco.name') }}</label>
            <input
              id="opco-name"
              v-model="formData.name"
              type="text"
              class="form-control"
              :placeholder="t('admin.opco.namePlaceholder')"
            />
          </div>

          <div class="form-group">
            <label for="opco-code">{{ t('admin.opco.code') }}</label>
            <input
              id="opco-code"
              v-model="formData.code"
              type="text"
              class="form-control"
              :placeholder="t('admin.opco.codePlaceholder')"
            />
          </div>

          <div class="form-group">
            <label for="opco-language">{{ t('admin.opco.defaultLanguage') }}</label>
            <select
              id="opco-language"
              v-model="formData.default_language"
              class="form-control"
            >
              <option v-for="lang in languages" :key="lang.value" :value="lang.value">
                {{ lang.label }}
              </option>
            </select>
          </div>

          <!-- Logo Upload -->
          <div class="form-group form-group-full">
            <label>{{ t('admin.opco.logo') }}</label>
            <div class="logo-upload-container">
              <!-- Current Logo Preview -->
              <div v-if="opco?.logo_url" class="logo-preview">
                <img :src="opco.logo_url" :alt="t('admin.opco.logoAlt')" />
                <button
                  type="button"
                  class="btn-delete-logo"
                  :disabled="logoUploading"
                  @click="handleLogoDelete"
                  :title="t('admin.opco.deleteLogo')"
                >
                  <span v-if="logoUploading" class="spinner-small"></span>
                  <span v-else>&times;</span>
                </button>
              </div>

              <!-- Upload Button -->
              <div class="logo-upload-actions">
                <input
                  ref="fileInputRef"
                  type="file"
                  accept="image/png,image/jpeg,image/gif,image/svg+xml,image/webp"
                  class="hidden-input"
                  @change="handleLogoSelect"
                />
                <button
                  type="button"
                  class="btn btn-secondary"
                  :disabled="logoUploading"
                  @click="triggerFileInput"
                >
                  <span v-if="logoUploading" class="spinner-small"></span>
                  {{ opco?.logo_url ? t('admin.opco.changeLogo') : t('admin.opco.uploadLogo') }}
                </button>
                <span class="logo-hint">{{ t('admin.opco.logoHint') }}</span>
              </div>

              <!-- Logo Error -->
              <div v-if="logoError" class="logo-error">
                {{ logoError }}
              </div>
            </div>
          </div>
        </div>
      </Card>

      <!-- Review Cycle Settings -->
      <Card class="mt-4">
        <SectionHeader
          :title="t('admin.opco.reviewCycle')"
          :description="t('admin.opco.reviewCycleDescription')"
        />

        <div class="review-cycle-grid">
          <!-- Goal Setting Period -->
          <div class="period-section">
            <h4>{{ t('admin.opco.goalSettingPeriod') }}</h4>
            <div class="date-range">
              <div class="form-group">
                <label for="goal-start">{{ t('admin.opco.startDate') }}</label>
                <input
                  id="goal-start"
                  v-model="formData.settings!.review_cycle!.goal_setting_start"
                  type="date"
                  class="form-control"
                />
              </div>
              <div class="form-group">
                <label for="goal-end">{{ t('admin.opco.endDate') }}</label>
                <input
                  id="goal-end"
                  v-model="formData.settings!.review_cycle!.goal_setting_end"
                  type="date"
                  class="form-control"
                />
              </div>
            </div>
          </div>

          <!-- Mid-Year Review Period -->
          <div class="period-section">
            <h4>{{ t('admin.opco.midYearPeriod') }}</h4>
            <div class="date-range">
              <div class="form-group">
                <label for="midyear-start">{{ t('admin.opco.startDate') }}</label>
                <input
                  id="midyear-start"
                  v-model="formData.settings!.review_cycle!.mid_year_start"
                  type="date"
                  class="form-control"
                />
              </div>
              <div class="form-group">
                <label for="midyear-end">{{ t('admin.opco.endDate') }}</label>
                <input
                  id="midyear-end"
                  v-model="formData.settings!.review_cycle!.mid_year_end"
                  type="date"
                  class="form-control"
                />
              </div>
            </div>
          </div>

          <!-- End-Year Review Period -->
          <div class="period-section">
            <h4>{{ t('admin.opco.endYearPeriod') }}</h4>
            <div class="date-range">
              <div class="form-group">
                <label for="endyear-start">{{ t('admin.opco.startDate') }}</label>
                <input
                  id="endyear-start"
                  v-model="formData.settings!.review_cycle!.end_year_start"
                  type="date"
                  class="form-control"
                />
              </div>
              <div class="form-group">
                <label for="endyear-end">{{ t('admin.opco.endDate') }}</label>
                <input
                  id="endyear-end"
                  v-model="formData.settings!.review_cycle!.end_year_end"
                  type="date"
                  class="form-control"
                />
              </div>
            </div>
          </div>
        </div>
      </Card>

      <!-- Form Actions -->
      <div class="form-actions">
        <button
          class="btn btn-secondary"
          :disabled="!hasChanges || saving"
          @click="resetForm"
        >
          {{ t('common.reset') }}
        </button>
        <button
          class="btn btn-primary"
          :disabled="!hasChanges || saving"
          @click="saveSettings"
        >
          <span v-if="saving" class="spinner-small"></span>
          {{ saving ? t('common.saving') : t('common.save') }}
        </button>
      </div>
    </template>
  </div>
</template>

<style scoped>
.opco-settings-form {
  max-width: 800px;
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
  padding: 1rem;
  background-color: var(--color-error-bg, #fee2e2);
  color: var(--color-error, #dc2626);
  border-radius: 0.5rem;
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.success-message {
  padding: 1rem;
  background-color: var(--color-success-bg, #dcfce7);
  color: var(--color-success, #16a34a);
  border-radius: 0.5rem;
  margin-bottom: 1rem;
}

.btn-link {
  background: none;
  border: none;
  color: var(--color-primary);
  cursor: pointer;
  text-decoration: underline;
}

.form-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 1rem;
}

.form-group-full {
  grid-column: 1 / -1;
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

.mt-4 {
  margin-top: 1.5rem;
}

.review-cycle-grid {
  display: grid;
  gap: 1.5rem;
}

.period-section h4 {
  margin: 0 0 0.75rem;
  font-size: 0.875rem;
  font-weight: 600;
  color: var(--color-text);
}

.date-range {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 1rem;
}

.form-actions {
  display: flex;
  justify-content: flex-end;
  gap: 0.75rem;
  margin-top: 1.5rem;
  padding-top: 1.5rem;
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

/* Logo Upload Styles */
.logo-upload-container {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.logo-preview {
  position: relative;
  display: inline-block;
  max-width: 200px;
}

.logo-preview img {
  max-width: 100%;
  max-height: 100px;
  object-fit: contain;
  border: 1px solid var(--color-border);
  border-radius: 0.375rem;
  padding: 0.5rem;
  background: white;
}

.btn-delete-logo {
  position: absolute;
  top: -0.5rem;
  right: -0.5rem;
  width: 1.5rem;
  height: 1.5rem;
  border-radius: 50%;
  border: none;
  background-color: var(--color-error, #dc2626);
  color: white;
  font-size: 1rem;
  line-height: 1;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: background-color 0.15s ease;
}

.btn-delete-logo:hover:not(:disabled) {
  background-color: #b91c1c;
}

.btn-delete-logo:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.logo-upload-actions {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  flex-wrap: wrap;
}

.hidden-input {
  display: none;
}

.logo-hint {
  font-size: 0.75rem;
  color: var(--color-text-muted);
}

.logo-error {
  color: var(--color-error, #dc2626);
  font-size: 0.875rem;
}

@media (max-width: 640px) {
  .form-grid,
  .date-range {
    grid-template-columns: 1fr;
  }
}
</style>
