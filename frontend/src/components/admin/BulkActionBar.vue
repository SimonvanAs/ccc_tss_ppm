<script setup lang="ts">
import { ref } from 'vue'
import { useI18n } from 'vue-i18n'
import type { AdminUser } from '../../api/admin'

const props = defineProps<{
  selectedCount: number
  managers: AdminUser[]
  loading: boolean
}>()

const emit = defineEmits<{
  (e: 'clear'): void
  (e: 'bulk-assign-role', role: string): void
  (e: 'bulk-assign-manager', managerId: string): void
}>()

const { t } = useI18n()

// Dropdown visibility
const showRoleDropdown = ref(false)
const showManagerDropdown = ref(false)

// Selected values
const selectedRole = ref('')
const selectedManagerId = ref('')

// Available roles
const availableRoles = ['employee', 'manager', 'hr', 'admin']

// Toggle role dropdown
function toggleRoleDropdown() {
  showRoleDropdown.value = !showRoleDropdown.value
  showManagerDropdown.value = false
  selectedRole.value = ''
}

// Toggle manager dropdown
function toggleManagerDropdown() {
  showManagerDropdown.value = !showManagerDropdown.value
  showRoleDropdown.value = false
  selectedManagerId.value = ''
}

// Apply role assignment
function applyRoleAssignment() {
  if (selectedRole.value) {
    emit('bulk-assign-role', selectedRole.value)
    showRoleDropdown.value = false
    selectedRole.value = ''
  }
}

// Apply manager assignment
function applyManagerAssignment() {
  if (selectedManagerId.value) {
    emit('bulk-assign-manager', selectedManagerId.value)
    showManagerDropdown.value = false
    selectedManagerId.value = ''
  }
}

// Get manager display name
function getManagerName(manager: AdminUser): string {
  if (manager.first_name && manager.last_name) {
    return `${manager.first_name} ${manager.last_name}`
  }
  return manager.email
}

// Get role label
function getRoleLabel(role: string): string {
  return t(`roles.${role}`, role)
}
</script>

<template>
  <div v-if="selectedCount > 0" class="bulk-action-bar">
    <div class="selection-info">
      <span class="selected-count">
        {{ t('admin.users.selectedCount', { count: selectedCount }) }}
      </span>
      <button
        data-testid="clear-selection"
        class="btn-link"
        @click="emit('clear')"
      >
        {{ t('admin.users.clearSelection') }}
      </button>
    </div>

    <div class="actions">
      <!-- Assign Role -->
      <div class="action-group">
        <button
          data-testid="assign-role-btn"
          class="btn btn-secondary"
          :disabled="loading"
          @click="toggleRoleDropdown"
        >
          {{ t('admin.users.bulkAssignRole') }}
        </button>

        <div v-if="showRoleDropdown" data-testid="role-dropdown" class="dropdown">
          <select
            v-model="selectedRole"
            data-testid="role-select"
            class="dropdown-select"
          >
            <option value="">{{ t('admin.users.selectRole') }}</option>
            <option v-for="role in availableRoles" :key="role" :value="role">
              {{ getRoleLabel(role) }}
            </option>
          </select>
          <button
            data-testid="apply-role"
            class="btn btn-primary btn-sm"
            :disabled="!selectedRole"
            @click="applyRoleAssignment"
          >
            {{ t('admin.users.apply') }}
          </button>
        </div>
      </div>

      <!-- Assign Manager -->
      <div class="action-group">
        <button
          data-testid="assign-manager-btn"
          class="btn btn-secondary"
          :disabled="loading"
          @click="toggleManagerDropdown"
        >
          {{ t('admin.users.bulkAssignManager') }}
        </button>

        <div v-if="showManagerDropdown" data-testid="manager-dropdown" class="dropdown">
          <select
            v-model="selectedManagerId"
            data-testid="manager-select"
            class="dropdown-select"
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
          <button
            data-testid="apply-manager"
            class="btn btn-primary btn-sm"
            :disabled="!selectedManagerId"
            @click="applyManagerAssignment"
          >
            {{ t('admin.users.apply') }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.bulk-action-bar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.75rem 1rem;
  background-color: var(--color-navy, #004A91);
  color: white;
  border-radius: 8px;
  margin-bottom: 1rem;
}

.selection-info {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.selected-count {
  font-size: 0.875rem;
  font-weight: 500;
}

.btn-link {
  background: none;
  border: none;
  color: rgba(255, 255, 255, 0.8);
  font-size: 0.875rem;
  cursor: pointer;
  text-decoration: underline;
}

.btn-link:hover {
  color: white;
}

.actions {
  display: flex;
  gap: 0.5rem;
}

.action-group {
  position: relative;
}

.dropdown {
  position: absolute;
  top: 100%;
  right: 0;
  margin-top: 0.5rem;
  padding: 0.75rem;
  background: white;
  border-radius: 8px;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
  display: flex;
  gap: 0.5rem;
  z-index: 10;
}

.dropdown-select {
  padding: 0.375rem 0.5rem;
  border: 1px solid var(--color-gray-300, #d1d5db);
  border-radius: 4px;
  font-size: 0.875rem;
  min-width: 150px;
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
  background-color: rgba(255, 255, 255, 0.2);
  color: white;
}

.btn-secondary:hover:not(:disabled) {
  background-color: rgba(255, 255, 255, 0.3);
}

.btn-primary {
  background-color: var(--color-navy, #004A91);
  color: white;
}

.btn-primary:hover:not(:disabled) {
  background-color: #003570;
}

.btn-sm {
  padding: 0.375rem 0.75rem;
  font-size: 0.75rem;
}
</style>
