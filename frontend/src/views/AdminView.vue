<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useI18n } from 'vue-i18n'
import { getCurrentUser } from '../api/auth'
import { SectionHeader, Card } from '../components/layout'
import {
  fetchUsers,
  fetchManagers,
  updateUserRoles,
  updateUserManager,
  updateUserStatus,
  bulkOperation,
  type AdminUser,
  type ListUsersParams,
} from '../api/admin'

// User management components
import UserList from '../components/admin/UserList.vue'
import UserDetailModal from '../components/admin/UserDetailModal.vue'
import DeactivateUserModal from '../components/admin/DeactivateUserModal.vue'
import BulkActionBar from '../components/admin/BulkActionBar.vue'

// Placeholder components for later phases
const OpCoSettingsForm = { template: '<div class="stub-content">OpCo Settings - Coming in Phase 3</div>' }
const BusinessUnitList = { template: '<div class="stub-content">Business Units - Coming in Phase 3</div>' }
const SystemHealthPanel = { template: '<div class="stub-content">System Health - Coming in Phase 4</div>' }
const AuditLogList = { template: '<div class="stub-content">Audit Logs - Coming in Phase 5</div>' }

type AdminTab = 'users' | 'opcoSettings' | 'businessUnits' | 'system' | 'auditLogs'

const { t } = useI18n()
const user = getCurrentUser()

const activeTab = ref<AdminTab>('users')

const isAdmin = computed(() => {
  return user?.roles?.includes('admin') ?? false
})

const tabs: { key: AdminTab; label: string }[] = [
  { key: 'users', label: 'admin.tabs.users' },
  { key: 'opcoSettings', label: 'admin.tabs.opcoSettings' },
  { key: 'businessUnits', label: 'admin.tabs.businessUnits' },
  { key: 'system', label: 'admin.tabs.system' },
  { key: 'auditLogs', label: 'admin.tabs.auditLogs' },
]

function setActiveTab(tab: AdminTab) {
  activeTab.value = tab
}

// User management state
const users = ref<AdminUser[]>([])
const managers = ref<AdminUser[]>([])
const loading = ref(false)
const error = ref<string | null>(null)

// Pagination state
const currentPage = ref(1)
const totalPages = ref(1)
const pageSize = 50

// Filter state
const searchQuery = ref('')
const roleFilter = ref('')
const statusFilter = ref<boolean | null>(null)

// Selection state
const selectedUserIds = ref<string[]>([])

// Modal state
const showUserDetailModal = ref(false)
const showDeactivateModal = ref(false)
const editingUser = ref<AdminUser | null>(null)
const deactivatingUser = ref<AdminUser | null>(null)
const modalLoading = ref(false)
const modalError = ref<string | null>(null)

// Computed for selected count
const selectedCount = computed(() => selectedUserIds.value.length)

// Load users with current filters
async function loadUsers() {
  loading.value = true
  error.value = null

  try {
    const params: ListUsersParams = {
      first: (currentPage.value - 1) * pageSize,
      max_results: pageSize,
    }

    if (searchQuery.value) {
      params.search = searchQuery.value
    }
    if (roleFilter.value) {
      params.role = roleFilter.value
    }
    if (statusFilter.value !== null) {
      params.enabled = statusFilter.value
    }

    users.value = await fetchUsers(params)
    // Estimate total pages based on returned results
    totalPages.value = users.value.length < pageSize ? currentPage.value : currentPage.value + 1
  } catch (e) {
    error.value = t('admin.users.loadError')
    console.error('Failed to load users:', e)
  } finally {
    loading.value = false
  }
}

// Load managers for dropdown
async function loadManagers() {
  try {
    managers.value = await fetchManagers()
  } catch (e) {
    console.error('Failed to load managers:', e)
  }
}

// Initialize
onMounted(async () => {
  if (isAdmin.value) {
    await Promise.all([loadUsers(), loadManagers()])
  }
})

// Handle search
function handleSearch(query: string) {
  searchQuery.value = query
  currentPage.value = 1
  loadUsers()
}

// Handle role filter
function handleFilterRole(role: string) {
  roleFilter.value = role
  currentPage.value = 1
  loadUsers()
}

// Handle status filter
function handleFilterStatus(enabled: boolean | null) {
  statusFilter.value = enabled
  currentPage.value = 1
  loadUsers()
}

// Handle pagination
function handlePageChange(page: number) {
  currentPage.value = page
  loadUsers()
}

// Handle edit user
function handleEditUser(user: AdminUser) {
  editingUser.value = user
  modalError.value = null
  showUserDetailModal.value = true
}

// Handle toggle status
function handleToggleStatus(user: AdminUser) {
  deactivatingUser.value = user
  showDeactivateModal.value = true
}

// Handle selection
function handleSelect(ids: string[]) {
  selectedUserIds.value = ids
}

// Clear selection
function handleClearSelection() {
  selectedUserIds.value = []
}

// Save user changes
async function handleSaveUser(data: { roles: string[]; managerId: string | null }) {
  if (!editingUser.value) return

  modalLoading.value = true
  modalError.value = null

  try {
    // Update roles if changed
    const currentRoles = new Set(editingUser.value.roles)
    const newRoles = new Set(data.roles)
    const rolesChanged = currentRoles.size !== newRoles.size ||
      [...currentRoles].some(r => !newRoles.has(r))

    if (rolesChanged) {
      await updateUserRoles(editingUser.value.id, data.roles)
    }

    // Update manager if changed
    if (data.managerId !== editingUser.value.manager_id && data.managerId) {
      await updateUserManager(editingUser.value.id, data.managerId)
    }

    showUserDetailModal.value = false
    editingUser.value = null
    await loadUsers()
  } catch (e) {
    modalError.value = t('admin.users.saveError')
    console.error('Failed to save user:', e)
  } finally {
    modalLoading.value = false
  }
}

// Cancel user edit
function handleCancelEdit() {
  showUserDetailModal.value = false
  editingUser.value = null
  modalError.value = null
}

// Confirm status toggle
async function handleConfirmStatusToggle() {
  if (!deactivatingUser.value) return

  modalLoading.value = true

  try {
    await updateUserStatus(deactivatingUser.value.id, !deactivatingUser.value.enabled)
    showDeactivateModal.value = false
    deactivatingUser.value = null
    await loadUsers()
  } catch (e) {
    console.error('Failed to update user status:', e)
  } finally {
    modalLoading.value = false
  }
}

// Cancel status toggle
function handleCancelStatusToggle() {
  showDeactivateModal.value = false
  deactivatingUser.value = null
}

// Bulk assign role
async function handleBulkAssignRole(role: string) {
  if (selectedUserIds.value.length === 0) return

  loading.value = true
  try {
    await bulkOperation({
      user_ids: selectedUserIds.value,
      operation: 'assign_role',
      role,
    })
    selectedUserIds.value = []
    await loadUsers()
  } catch (e) {
    error.value = t('admin.users.bulkError')
    console.error('Failed to bulk assign role:', e)
  } finally {
    loading.value = false
  }
}

// Bulk assign manager
async function handleBulkAssignManager(managerId: string) {
  if (selectedUserIds.value.length === 0) return

  loading.value = true
  try {
    await bulkOperation({
      user_ids: selectedUserIds.value,
      operation: 'assign_manager',
      manager_id: managerId,
    })
    selectedUserIds.value = []
    await loadUsers()
  } catch (e) {
    error.value = t('admin.users.bulkError')
    console.error('Failed to bulk assign manager:', e)
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <div v-if="isAdmin" class="admin-view">
    <!-- Page Header -->
    <SectionHeader :title="t('admin.pageTitle')">
      <template #subtitle>
        {{ t('admin.pageSubtitle') }}
      </template>
    </SectionHeader>

    <!-- Tab Navigation -->
    <div class="tab-navigation" role="tablist">
      <button
        v-for="tab in tabs"
        :key="tab.key"
        class="tab-button"
        :class="{ 'is-active': activeTab === tab.key }"
        role="tab"
        :aria-selected="activeTab === tab.key"
        @click="setActiveTab(tab.key)"
      >
        {{ t(tab.label) }}
      </button>
    </div>

    <!-- Tab Content -->
    <div class="tab-content" role="tabpanel">
      <!-- Users Tab -->
      <template v-if="activeTab === 'users'">
        <!-- Bulk Action Bar -->
        <BulkActionBar
          :selected-count="selectedCount"
          :managers="managers"
          :loading="loading"
          @clear="handleClearSelection"
          @bulk-assign-role="handleBulkAssignRole"
          @bulk-assign-manager="handleBulkAssignManager"
        />

        <!-- Error Message -->
        <div v-if="error" class="error-banner">
          {{ error }}
        </div>

        <Card>
          <UserList
            :users="users"
            :loading="loading"
            :current-page="currentPage"
            :total-pages="totalPages"
            :selectable="true"
            :selected-ids="selectedUserIds"
            @search="handleSearch"
            @filter-role="handleFilterRole"
            @filter-status="handleFilterStatus"
            @page-change="handlePageChange"
            @edit="handleEditUser"
            @toggle-status="handleToggleStatus"
            @select="handleSelect"
          />
        </Card>

        <!-- User Detail Modal -->
        <UserDetailModal
          :show="showUserDetailModal"
          :user="editingUser"
          :managers="managers"
          :loading="modalLoading"
          :error="modalError ?? undefined"
          @save="handleSaveUser"
          @cancel="handleCancelEdit"
        />

        <!-- Deactivate/Activate Modal -->
        <DeactivateUserModal
          :show="showDeactivateModal"
          :user="deactivatingUser"
          :loading="modalLoading"
          @confirm="handleConfirmStatusToggle"
          @cancel="handleCancelStatusToggle"
        />
      </template>

      <!-- Other Tabs (Placeholders) -->
      <Card v-else>
        <component
          :is="
            activeTab === 'opcoSettings'
              ? OpCoSettingsForm
              : activeTab === 'businessUnits'
                ? BusinessUnitList
                : activeTab === 'system'
                  ? SystemHealthPanel
                  : AuditLogList
          "
        />
      </Card>
    </div>
  </div>

  <!-- Unauthorized State -->
  <div v-else class="unauthorized-view">
    <Card>
      <div class="unauthorized-message">
        {{ t('admin.unauthorized') }}
      </div>
    </Card>
  </div>
</template>

<style scoped>
.admin-view {
  max-width: 1200px;
  margin: 0 auto;
}

.tab-navigation {
  display: flex;
  gap: 0.25rem;
  border-bottom: 1px solid var(--color-gray-200);
  margin-top: 1.5rem;
  overflow-x: auto;
}

.tab-button {
  padding: 0.75rem 1.5rem;
  background: transparent;
  border: none;
  border-bottom: 3px solid transparent;
  font-size: 0.9375rem;
  font-weight: 500;
  color: var(--color-gray-600);
  cursor: pointer;
  transition: all 0.2s;
  white-space: nowrap;
  min-height: 44px;
}

.tab-button:hover {
  color: var(--color-navy);
  background-color: var(--color-gray-100);
}

.tab-button.is-active {
  color: var(--color-magenta);
  border-bottom-color: var(--color-magenta);
}

.tab-content {
  margin-top: 1.5rem;
}

.error-banner {
  background-color: #fee2e2;
  color: #991b1b;
  padding: 0.75rem 1rem;
  border-radius: 6px;
  margin-bottom: 1rem;
  font-size: 0.875rem;
}

.unauthorized-view {
  max-width: 600px;
  margin: 2rem auto;
}

.unauthorized-message {
  text-align: center;
  padding: 2rem;
  color: var(--color-error);
}

.stub-content {
  padding: 3rem;
  text-align: center;
  color: var(--color-gray-500);
  font-size: 0.875rem;
}
</style>
