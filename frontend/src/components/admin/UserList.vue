<script setup lang="ts">
import { computed, ref, watch } from 'vue'
import { useI18n } from 'vue-i18n'
import type { AdminUser } from '../../api/admin'

const props = withDefaults(defineProps<{
  users: AdminUser[]
  loading: boolean
  currentPage?: number
  totalPages?: number
  selectable?: boolean
  selectedIds?: string[]
}>(), {
  currentPage: 1,
  totalPages: 1,
  selectable: false,
  selectedIds: () => [],
})

const emit = defineEmits<{
  (e: 'search', query: string): void
  (e: 'filter-role', role: string): void
  (e: 'filter-status', enabled: boolean | null): void
  (e: 'page-change', page: number): void
  (e: 'edit', user: AdminUser): void
  (e: 'toggle-status', user: AdminUser): void
  (e: 'select', ids: string[]): void
}>()

const { t } = useI18n()

// Local state for filters
const searchQuery = ref('')
const roleFilter = ref('')
const statusFilter = ref('')

// Debounced search
let searchTimeout: ReturnType<typeof setTimeout> | null = null
watch(searchQuery, (value) => {
  if (searchTimeout) clearTimeout(searchTimeout)
  searchTimeout = setTimeout(() => {
    emit('search', value)
  }, 300)
})

// Role filter change
function handleRoleFilterChange(event: Event) {
  const value = (event.target as HTMLSelectElement).value
  emit('filter-role', value)
}

// Status filter change
function handleStatusFilterChange(event: Event) {
  const value = (event.target as HTMLSelectElement).value
  if (value === '') {
    emit('filter-status', null)
  } else if (value === 'active') {
    emit('filter-status', true)
  } else {
    emit('filter-status', false)
  }
}

// Pagination
const showPagination = computed(() => props.totalPages > 1)

function handlePrevPage() {
  if (props.currentPage > 1) {
    emit('page-change', props.currentPage - 1)
  }
}

function handleNextPage() {
  if (props.currentPage < props.totalPages) {
    emit('page-change', props.currentPage + 1)
  }
}

// Selection
const allSelected = computed(() => {
  if (props.users.length === 0) return false
  return props.users.every(u => props.selectedIds.includes(u.id))
})

function handleSelectAll(event: Event) {
  const checked = (event.target as HTMLInputElement).checked
  if (checked) {
    emit('select', props.users.map(u => u.id))
  } else {
    emit('select', [])
  }
}

function handleSelectRow(userId: string, checked: boolean) {
  if (checked) {
    emit('select', [...props.selectedIds, userId])
  } else {
    emit('select', props.selectedIds.filter(id => id !== userId))
  }
}

// User display helpers
function getUserName(user: AdminUser): string {
  if (user.first_name && user.last_name) {
    return `${user.first_name} ${user.last_name}`
  }
  return user.email
}

function getRoleLabel(role: string): string {
  return t(`roles.${role}`, role)
}

// Available roles for filter
const availableRoles = ['employee', 'manager', 'hr', 'admin']
</script>

<template>
  <div class="user-list">
    <!-- Filters -->
    <div class="filters">
      <div class="search-wrapper">
        <input
          v-model="searchQuery"
          type="search"
          class="search-input"
          :placeholder="t('admin.users.search')"
        />
      </div>

      <select
        data-testid="role-filter"
        class="filter-select"
        :value="roleFilter"
        @change="handleRoleFilterChange"
      >
        <option value="">{{ t('admin.users.allRoles') }}</option>
        <option v-for="role in availableRoles" :key="role" :value="role">
          {{ getRoleLabel(role) }}
        </option>
      </select>

      <select
        data-testid="status-filter"
        class="filter-select"
        :value="statusFilter"
        @change="handleStatusFilterChange"
      >
        <option value="">{{ t('admin.users.allStatuses') }}</option>
        <option value="active">{{ t('admin.users.active') }}</option>
        <option value="inactive">{{ t('admin.users.inactive') }}</option>
      </select>
    </div>

    <!-- Loading state -->
    <div v-if="loading" class="loading-state">
      {{ t('admin.users.loading') }}
    </div>

    <!-- Empty state -->
    <div v-else-if="users.length === 0" class="empty-state">
      {{ t('admin.users.noUsers') }}
    </div>

    <!-- User table -->
    <table v-else class="user-table">
      <thead>
        <tr>
          <th v-if="selectable" class="checkbox-cell">
            <input
              type="checkbox"
              :checked="allSelected"
              @change="handleSelectAll"
            />
          </th>
          <th>{{ t('admin.users.name') }}</th>
          <th>{{ t('admin.users.email') }}</th>
          <th>{{ t('admin.users.roles') }}</th>
          <th>{{ t('admin.users.status') }}</th>
          <th>{{ t('admin.users.actions') }}</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="user in users" :key="user.id">
          <td v-if="selectable" class="checkbox-cell">
            <input
              type="checkbox"
              :checked="selectedIds.includes(user.id)"
              @change="(e) => handleSelectRow(user.id, (e.target as HTMLInputElement).checked)"
            />
          </td>
          <td>{{ getUserName(user) }}</td>
          <td>{{ user.email }}</td>
          <td>
            <span
              v-for="role in user.roles"
              :key="role"
              class="role-badge"
              :class="`role-${role}`"
            >
              {{ getRoleLabel(role) }}
            </span>
          </td>
          <td>
            <span
              class="status-badge"
              :class="user.enabled ? 'status-active' : 'status-inactive'"
            >
              {{ user.enabled ? t('admin.users.active') : t('admin.users.inactive') }}
            </span>
          </td>
          <td class="actions-cell">
            <button
              data-testid="edit-user"
              class="btn btn-sm btn-secondary"
              @click="emit('edit', user)"
            >
              {{ t('admin.users.edit') }}
            </button>
            <button
              data-testid="toggle-status"
              class="btn btn-sm"
              :class="user.enabled ? 'btn-danger' : 'btn-success'"
              @click="emit('toggle-status', user)"
            >
              {{ user.enabled ? t('admin.users.deactivate') : t('admin.users.activate') }}
            </button>
          </td>
        </tr>
      </tbody>
    </table>

    <!-- Pagination -->
    <div v-if="showPagination" class="pagination">
      <button
        data-testid="prev-page"
        class="btn btn-sm btn-secondary"
        :disabled="currentPage <= 1"
        @click="handlePrevPage"
      >
        {{ t('admin.users.previousPage') }}
      </button>
      <span class="page-info">
        {{ t('admin.users.pageInfo', { page: currentPage }) }}
      </span>
      <button
        data-testid="next-page"
        class="btn btn-sm btn-secondary"
        :disabled="currentPage >= totalPages"
        @click="handleNextPage"
      >
        {{ t('admin.users.nextPage') }}
      </button>
    </div>
  </div>
</template>

<style scoped>
.user-list {
  width: 100%;
}

.filters {
  display: flex;
  gap: 1rem;
  margin-bottom: 1rem;
  flex-wrap: wrap;
}

.search-wrapper {
  flex: 1;
  min-width: 200px;
}

.search-input {
  width: 100%;
  padding: 0.5rem 0.75rem;
  border: 1px solid var(--color-gray-300, #d1d5db);
  border-radius: 6px;
  font-size: 0.875rem;
}

.search-input:focus {
  outline: none;
  border-color: var(--color-navy, #004A91);
  box-shadow: 0 0 0 2px rgba(0, 74, 145, 0.1);
}

.filter-select {
  padding: 0.5rem 0.75rem;
  border: 1px solid var(--color-gray-300, #d1d5db);
  border-radius: 6px;
  font-size: 0.875rem;
  background-color: white;
  min-width: 150px;
}

.filter-select:focus {
  outline: none;
  border-color: var(--color-navy, #004A91);
}

.loading-state,
.empty-state {
  padding: 2rem;
  text-align: center;
  color: var(--color-gray-500, #6b7280);
}

.user-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 0.875rem;
}

.user-table th,
.user-table td {
  padding: 0.75rem;
  text-align: left;
  border-bottom: 1px solid var(--color-gray-200, #e5e7eb);
}

.user-table th {
  font-weight: 600;
  color: var(--color-gray-700, #374151);
  background-color: var(--color-gray-50, #f9fafb);
}

.user-table tbody tr:hover {
  background-color: var(--color-gray-50, #f9fafb);
}

.checkbox-cell {
  width: 40px;
  text-align: center;
}

.role-badge {
  display: inline-block;
  padding: 0.125rem 0.5rem;
  margin-right: 0.25rem;
  border-radius: 9999px;
  font-size: 0.75rem;
  font-weight: 500;
  background-color: var(--color-gray-100, #f3f4f6);
  color: var(--color-gray-700, #374151);
}

.role-admin {
  background-color: #fce7f3;
  color: #be185d;
}

.role-hr {
  background-color: #dbeafe;
  color: #1d4ed8;
}

.role-manager {
  background-color: #dcfce7;
  color: #166534;
}

.status-badge {
  display: inline-block;
  padding: 0.125rem 0.5rem;
  border-radius: 9999px;
  font-size: 0.75rem;
  font-weight: 500;
}

.status-active {
  background-color: #dcfce7;
  color: #166534;
}

.status-inactive {
  background-color: #fee2e2;
  color: #991b1b;
}

.actions-cell {
  display: flex;
  gap: 0.5rem;
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

.btn-sm {
  padding: 0.25rem 0.5rem;
  font-size: 0.75rem;
}

.btn-secondary {
  background-color: var(--color-gray-100, #f3f4f6);
  color: var(--color-gray-700, #374151);
}

.btn-secondary:hover:not(:disabled) {
  background-color: var(--color-gray-200, #e5e7eb);
}

.btn-danger {
  background-color: #fee2e2;
  color: #991b1b;
}

.btn-danger:hover:not(:disabled) {
  background-color: #fecaca;
}

.btn-success {
  background-color: #dcfce7;
  color: #166534;
}

.btn-success:hover:not(:disabled) {
  background-color: #bbf7d0;
}

.btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.pagination {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 1rem;
  margin-top: 1rem;
  padding-top: 1rem;
  border-top: 1px solid var(--color-gray-200, #e5e7eb);
}

.page-info {
  font-size: 0.875rem;
  color: var(--color-gray-600, #4b5563);
}

@media (max-width: 768px) {
  .filters {
    flex-direction: column;
  }

  .search-input {
    max-width: 100%;
  }

  .user-table th:nth-child(3),
  .user-table td:nth-child(3),
  .user-table th:nth-child(4),
  .user-table td:nth-child(4) {
    display: none;
  }

  .actions {
    flex-direction: column;
    gap: 0.25rem;
  }

  .actions .btn {
    width: 100%;
    justify-content: center;
  }
}

@media (max-width: 480px) {
  .user-table th:nth-child(2),
  .user-table td:nth-child(2) {
    display: none;
  }

  .pagination {
    flex-wrap: wrap;
    gap: 0.5rem;
  }
}
</style>
