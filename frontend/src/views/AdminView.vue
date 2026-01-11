<script setup lang="ts">
import { ref, computed } from 'vue'
import { useI18n } from 'vue-i18n'
import { getCurrentUser } from '../api/auth'
import { SectionHeader, Card } from '../components/layout'

// Tab components - will be implemented in later phases
// For now, use placeholder components
const UserList = { template: '<div class="user-list-stub">User List placeholder</div>' }
const OpCoSettingsForm = { template: '<div class="opco-settings-stub">OpCo Settings placeholder</div>' }
const BusinessUnitList = { template: '<div class="business-unit-list-stub">Business Units placeholder</div>' }
const SystemHealthPanel = { template: '<div class="system-health-stub">System Health placeholder</div>' }
const AuditLogList = { template: '<div class="audit-log-list-stub">Audit Logs placeholder</div>' }

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
      <Card>
        <component
          :is="
            activeTab === 'users'
              ? UserList
              : activeTab === 'opcoSettings'
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

.unauthorized-view {
  max-width: 600px;
  margin: 2rem auto;
}

.unauthorized-message {
  text-align: center;
  padding: 2rem;
  color: var(--color-error);
}
</style>
