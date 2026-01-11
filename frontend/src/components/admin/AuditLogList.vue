<script setup lang="ts">
// TSS PPM v3.0 - Audit Log List Component
import { ref, computed, onMounted, watch } from 'vue'
import { useI18n } from 'vue-i18n'
import { Card, SectionHeader } from '@/components/layout'
import {
  fetchAuditLogs,
  fetchAuditLogFilters,
  getAuditLogExportUrl,
  type AuditLogEntry,
  type AuditLogListParams,
  type AuditLogFiltersResponse,
} from '@/api/admin'

const emit = defineEmits<{
  (e: 'view-details', log: AuditLogEntry): void
}>()

const { t } = useI18n()

// State
const logs = ref<AuditLogEntry[]>([])
const loading = ref(false)
const error = ref<string | null>(null)

// Pagination
const currentPage = ref(1)
const pageSize = ref(25)
const totalItems = ref(0)
const totalPages = computed(() => Math.ceil(totalItems.value / pageSize.value))

// Filters
const filterOptions = ref<AuditLogFiltersResponse>({ actions: [], entity_types: [] })
const startDate = ref('')
const endDate = ref('')
const selectedAction = ref('')
const selectedEntityType = ref('')

// Computed filter params
const filterParams = computed<AuditLogListParams>(() => ({
  page: currentPage.value,
  page_size: pageSize.value,
  start_date: startDate.value || undefined,
  end_date: endDate.value || undefined,
  action: selectedAction.value || undefined,
  entity_type: selectedEntityType.value || undefined,
}))

// Load audit logs
async function loadLogs() {
  loading.value = true
  error.value = null
  try {
    const response = await fetchAuditLogs(filterParams.value)
    logs.value = response.logs
    totalItems.value = response.total
  } catch (err) {
    error.value = err instanceof Error ? err.message : t('admin.auditLogs.loadError')
  } finally {
    loading.value = false
  }
}

// Load filter options
async function loadFilterOptions() {
  try {
    filterOptions.value = await fetchAuditLogFilters()
  } catch (err) {
    console.error('Failed to load filter options:', err)
  }
}

// Handle export
function handleExport() {
  const url = getAuditLogExportUrl(filterParams.value)
  window.open(url, '_blank')
}

// Handle page change
function goToPage(page: number) {
  if (page >= 1 && page <= totalPages.value) {
    currentPage.value = page
  }
}

// Handle filter changes
function applyFilters() {
  currentPage.value = 1
  loadLogs()
}

function clearFilters() {
  startDate.value = ''
  endDate.value = ''
  selectedAction.value = ''
  selectedEntityType.value = ''
  currentPage.value = 1
  loadLogs()
}

// Format date for display
function formatDate(dateString: string): string {
  return new Date(dateString).toLocaleString()
}

// Format action for display
function formatAction(action: string): string {
  return action.replace(/_/g, ' ').toLowerCase().replace(/\b\w/g, c => c.toUpperCase())
}

// View log details
function viewDetails(log: AuditLogEntry) {
  emit('view-details', log)
}

// Watch for page changes
watch(currentPage, loadLogs)

// Initialize
onMounted(() => {
  loadLogs()
  loadFilterOptions()
})
</script>

<template>
  <div class="audit-log-list">
    <Card>
      <SectionHeader
        :title="t('admin.auditLogs.title')"
        :description="t('admin.auditLogs.description')"
      />

      <!-- Filters -->
      <div class="filters">
        <div class="filter-row">
          <div class="filter-group">
            <label for="start-date">{{ t('admin.auditLogs.filters.startDate') }}</label>
            <input
              id="start-date"
              v-model="startDate"
              type="date"
              class="form-control"
            />
          </div>

          <div class="filter-group">
            <label for="end-date">{{ t('admin.auditLogs.filters.endDate') }}</label>
            <input
              id="end-date"
              v-model="endDate"
              type="date"
              class="form-control"
            />
          </div>

          <div class="filter-group">
            <label for="action-filter">{{ t('admin.auditLogs.filters.action') }}</label>
            <select
              id="action-filter"
              v-model="selectedAction"
              class="form-control"
            >
              <option value="">{{ t('admin.auditLogs.filters.allActions') }}</option>
              <option v-for="action in filterOptions.actions" :key="action" :value="action">
                {{ formatAction(action) }}
              </option>
            </select>
          </div>

          <div class="filter-group">
            <label for="entity-filter">{{ t('admin.auditLogs.filters.entityType') }}</label>
            <select
              id="entity-filter"
              v-model="selectedEntityType"
              class="form-control"
            >
              <option value="">{{ t('admin.auditLogs.filters.allEntities') }}</option>
              <option v-for="entityType in filterOptions.entity_types" :key="entityType" :value="entityType">
                {{ entityType }}
              </option>
            </select>
          </div>
        </div>

        <div class="filter-actions">
          <button class="btn btn-secondary" @click="clearFilters">
            {{ t('admin.auditLogs.filters.clear') }}
          </button>
          <button class="btn btn-primary" @click="applyFilters">
            {{ t('admin.auditLogs.filters.apply') }}
          </button>
          <button class="btn btn-outline" @click="handleExport">
            {{ t('admin.auditLogs.export') }}
          </button>
        </div>
      </div>

      <!-- Error State -->
      <div v-if="error" class="error-message">
        {{ error }}
        <button class="btn-link" @click="loadLogs">{{ t('common.retry') }}</button>
      </div>

      <!-- Loading State -->
      <div v-else-if="loading" class="loading-state">
        <span class="spinner"></span>
        <span>{{ t('common.loading') }}</span>
      </div>

      <!-- Empty State -->
      <div v-else-if="logs.length === 0" class="empty-state">
        {{ t('admin.auditLogs.empty') }}
      </div>

      <!-- Logs Table -->
      <div v-else class="table-container">
        <table class="audit-table">
          <thead>
            <tr>
              <th>{{ t('admin.auditLogs.columns.timestamp') }}</th>
              <th>{{ t('admin.auditLogs.columns.user') }}</th>
              <th>{{ t('admin.auditLogs.columns.action') }}</th>
              <th>{{ t('admin.auditLogs.columns.entityType') }}</th>
              <th>{{ t('admin.auditLogs.columns.details') }}</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="log in logs" :key="log.id">
              <td class="timestamp">{{ formatDate(log.created_at) }}</td>
              <td class="user">
                <span v-if="log.user_email">{{ log.user_email }}</span>
                <span v-else class="text-muted">{{ t('admin.auditLogs.systemAction') }}</span>
              </td>
              <td class="action">
                <span class="action-badge">{{ formatAction(log.action) }}</span>
              </td>
              <td class="entity-type">{{ log.entity_type }}</td>
              <td class="details">
                <button class="btn-link" @click="viewDetails(log)">
                  {{ t('admin.auditLogs.viewDetails') }}
                </button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      <!-- Pagination -->
      <div v-if="totalPages > 1" class="pagination">
        <button
          class="btn btn-sm"
          :disabled="currentPage === 1"
          @click="goToPage(1)"
        >
          &laquo;
        </button>
        <button
          class="btn btn-sm"
          :disabled="currentPage === 1"
          @click="goToPage(currentPage - 1)"
        >
          &lsaquo;
        </button>

        <span class="page-info">
          {{ t('admin.auditLogs.pageInfo', { current: currentPage, total: totalPages }) }}
        </span>

        <button
          class="btn btn-sm"
          :disabled="currentPage === totalPages"
          @click="goToPage(currentPage + 1)"
        >
          &rsaquo;
        </button>
        <button
          class="btn btn-sm"
          :disabled="currentPage === totalPages"
          @click="goToPage(totalPages)"
        >
          &raquo;
        </button>
      </div>

      <!-- Total count -->
      <div class="total-count">
        {{ t('admin.auditLogs.totalCount', { count: totalItems }) }}
      </div>
    </Card>
  </div>
</template>

<style scoped>
.audit-log-list {
  max-width: 100%;
}

.filters {
  margin-bottom: 1.5rem;
  padding-bottom: 1rem;
  border-bottom: 1px solid var(--color-border);
}

.filter-row {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
  gap: 1rem;
  margin-bottom: 1rem;
}

.filter-group {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.filter-group label {
  font-size: 0.75rem;
  font-weight: 500;
  color: var(--color-text-muted);
}

.form-control {
  padding: 0.5rem 0.75rem;
  border: 1px solid var(--color-border);
  border-radius: 0.375rem;
  font-size: 0.875rem;
}

.form-control:focus {
  outline: none;
  border-color: var(--color-primary);
  box-shadow: 0 0 0 2px rgba(204, 14, 112, 0.1);
}

.filter-actions {
  display: flex;
  gap: 0.75rem;
  flex-wrap: wrap;
}

.btn {
  padding: 0.5rem 1rem;
  border-radius: 0.375rem;
  font-weight: 500;
  font-size: 0.875rem;
  cursor: pointer;
  transition: all 0.15s ease;
}

.btn-sm {
  padding: 0.375rem 0.75rem;
  font-size: 0.8125rem;
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

.btn-outline {
  background-color: transparent;
  color: var(--color-primary);
  border: 1px solid var(--color-primary);
}

.btn-outline:hover:not(:disabled) {
  background-color: rgba(204, 14, 112, 0.05);
}

.btn-link {
  background: none;
  border: none;
  color: var(--color-primary);
  cursor: pointer;
  text-decoration: underline;
  font-size: 0.875rem;
  padding: 0;
}

.loading-state {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
  padding: 3rem;
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

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

.error-message {
  padding: 1rem;
  background-color: var(--color-error-bg, #fee2e2);
  color: var(--color-error, #dc2626);
  border-radius: 0.375rem;
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 0.875rem;
}

.empty-state {
  text-align: center;
  padding: 3rem;
  color: var(--color-text-muted);
}

.table-container {
  overflow-x: auto;
}

.audit-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 0.875rem;
}

.audit-table th,
.audit-table td {
  padding: 0.75rem 1rem;
  text-align: left;
  border-bottom: 1px solid var(--color-border);
}

.audit-table th {
  background-color: var(--color-bg-secondary, #f9fafb);
  font-weight: 600;
  color: var(--color-text-muted);
  font-size: 0.75rem;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.audit-table tbody tr:hover {
  background-color: var(--color-bg-hover, #f9fafb);
}

.timestamp {
  white-space: nowrap;
  font-variant-numeric: tabular-nums;
}

.user {
  max-width: 200px;
  overflow: hidden;
  text-overflow: ellipsis;
}

.text-muted {
  color: var(--color-text-muted);
  font-style: italic;
}

.action-badge {
  display: inline-block;
  padding: 0.25rem 0.5rem;
  background-color: var(--color-bg-secondary, #f3f4f6);
  border-radius: 0.25rem;
  font-size: 0.75rem;
  font-weight: 500;
}

.pagination {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
  margin-top: 1.5rem;
  padding-top: 1rem;
  border-top: 1px solid var(--color-border);
}

.page-info {
  padding: 0 1rem;
  font-size: 0.875rem;
  color: var(--color-text-muted);
}

.total-count {
  text-align: center;
  margin-top: 0.5rem;
  font-size: 0.75rem;
  color: var(--color-text-muted);
}

@media (max-width: 768px) {
  .filter-row {
    grid-template-columns: 1fr;
  }

  .audit-table th:nth-child(5),
  .audit-table td:nth-child(5) {
    display: none;
  }
}
</style>
