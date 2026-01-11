<script setup lang="ts">
import { ref, watch, computed } from 'vue'
import { useI18n } from 'vue-i18n'
import type { AdminUser } from '../../api/admin'

const props = defineProps<{
  show: boolean
  user: AdminUser | null
  managers: AdminUser[]
  loading: boolean
  error?: string
}>()

const emit = defineEmits<{
  (e: 'save', data: { roles: string[]; managerId: string | null }): void
  (e: 'cancel'): void
}>()

const { t } = useI18n()

// Local state for editing
const selectedRoles = ref<string[]>([])
const selectedManagerId = ref<string | null>(null)

// Available roles
const availableRoles = ['employee', 'manager', 'hr', 'admin']

// Reset form when user changes
watch(() => props.user, (newUser) => {
  if (newUser) {
    selectedRoles.value = [...newUser.roles]
    selectedManagerId.value = newUser.manager_id
  }
}, { immediate: true })

// User display name
const userName = computed(() => {
  if (!props.user) return ''
  if (props.user.first_name && props.user.last_name) {
    return `${props.user.first_name} ${props.user.last_name}`
  }
  return props.user.email
})

// Handle role toggle
function toggleRole(role: string, checked: boolean) {
  if (checked) {
    selectedRoles.value = [...selectedRoles.value, role]
  } else {
    selectedRoles.value = selectedRoles.value.filter(r => r !== role)
  }
}

// Handle save
function handleSave() {
  emit('save', {
    roles: selectedRoles.value,
    managerId: selectedManagerId.value,
  })
}

// Handle cancel (overlay click)
function handleOverlayClick(event: MouseEvent) {
  if (event.target === event.currentTarget) {
    emit('cancel')
  }
}

// Get role label
function getRoleLabel(role: string): string {
  return t(`roles.${role}`, role)
}

// Get manager display name
function getManagerName(manager: AdminUser): string {
  if (manager.first_name && manager.last_name) {
    return `${manager.first_name} ${manager.last_name}`
  }
  return manager.email
}
</script>

<template>
  <div v-if="show" class="modal-overlay" @click="handleOverlayClick">
    <div class="modal-content" @click.stop>
      <div class="modal-header">
        <h2 class="modal-title">{{ t('admin.users.editUser') }}: {{ userName }}</h2>
      </div>

      <div class="modal-body">
        <!-- Error message -->
        <div v-if="error" class="error-message">
          {{ error }}
        </div>

        <!-- User info (read-only) -->
        <div class="form-section">
          <div class="info-row">
            <span class="info-label">{{ t('admin.users.email') }}:</span>
            <span class="info-value">{{ user?.email }}</span>
          </div>
          <div class="info-row">
            <span class="info-label">{{ t('admin.users.functionTitle') }}:</span>
            <span class="info-value">{{ user?.function_title || '-' }}</span>
          </div>
          <div class="info-row">
            <span class="info-label">{{ t('admin.users.tovLevel') }}:</span>
            <span class="info-value">{{ user?.tov_level || '-' }}</span>
          </div>
        </div>

        <!-- Roles -->
        <div class="form-section">
          <label class="section-label">{{ t('admin.users.roles') }}</label>
          <div class="roles-grid">
            <label
              v-for="role in availableRoles"
              :key="role"
              class="role-checkbox"
            >
              <input
                type="checkbox"
                :value="role"
                :checked="selectedRoles.includes(role)"
                @change="(e) => toggleRole(role, (e.target as HTMLInputElement).checked)"
              />
              <span class="role-label">{{ getRoleLabel(role) }}</span>
            </label>
          </div>
        </div>

        <!-- Manager selection -->
        <div class="form-section">
          <label class="section-label" for="manager-select">
            {{ t('admin.users.manager') }}
          </label>
          <select
            id="manager-select"
            v-model="selectedManagerId"
            data-testid="manager-select"
            class="manager-select"
          >
            <option value="">{{ t('admin.users.selectManager') }}</option>
            <option
              v-for="manager in managers"
              :key="manager.id"
              :value="manager.id"
            >
              {{ getManagerName(manager) }}
            </option>
          </select>
        </div>
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
          data-testid="save-button"
          class="btn btn-primary"
          :disabled="loading"
          @click="handleSave"
        >
          {{ loading ? t('admin.users.saving') : t('admin.users.save') }}
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
  max-width: 500px;
  max-height: 90vh;
  overflow-y: auto;
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

.error-message {
  background-color: #fee2e2;
  color: #991b1b;
  padding: 0.75rem 1rem;
  border-radius: 6px;
  margin-bottom: 1rem;
  font-size: 0.875rem;
}

.form-section {
  margin-bottom: 1.5rem;
}

.form-section:last-child {
  margin-bottom: 0;
}

.section-label {
  display: block;
  font-size: 0.875rem;
  font-weight: 600;
  color: var(--color-gray-700, #374151);
  margin-bottom: 0.5rem;
}

.info-row {
  display: flex;
  padding: 0.5rem 0;
  border-bottom: 1px solid var(--color-gray-100, #f3f4f6);
}

.info-row:last-child {
  border-bottom: none;
}

.info-label {
  font-size: 0.875rem;
  color: var(--color-gray-500, #6b7280);
  width: 120px;
  flex-shrink: 0;
}

.info-value {
  font-size: 0.875rem;
  color: var(--color-gray-900, #111827);
}

.roles-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 0.75rem;
}

.role-checkbox {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  cursor: pointer;
}

.role-checkbox input {
  width: 16px;
  height: 16px;
  cursor: pointer;
}

.role-label {
  font-size: 0.875rem;
  color: var(--color-gray-700, #374151);
}

.manager-select {
  width: 100%;
  padding: 0.5rem 0.75rem;
  border: 1px solid var(--color-gray-300, #d1d5db);
  border-radius: 6px;
  font-size: 0.875rem;
  background-color: white;
}

.manager-select:focus {
  outline: none;
  border-color: var(--color-navy, #004A91);
  box-shadow: 0 0 0 2px rgba(0, 74, 145, 0.1);
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

.btn-primary {
  background-color: var(--color-navy, #004A91);
  color: white;
}

.btn-primary:hover:not(:disabled) {
  background-color: #003570;
}
</style>
