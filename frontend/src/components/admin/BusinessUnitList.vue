<script setup lang="ts">
// TSS PPM v3.0 - Business Unit List Component
import { ref, computed, onMounted } from 'vue'
import { useI18n } from 'vue-i18n'
import { Card, SectionHeader } from '@/components/layout'
import BusinessUnitModal from './BusinessUnitModal.vue'
import {
  fetchBusinessUnits,
  deleteBusinessUnit,
  type BusinessUnit,
} from '@/api/admin'

const { t } = useI18n()

const loading = ref(false)
const error = ref<string | null>(null)
const businessUnits = ref<BusinessUnit[]>([])
const selectedUnit = ref<BusinessUnit | null>(null)
const showModal = ref(false)
const deleteConfirm = ref<BusinessUnit | null>(null)
const deleting = ref(false)

// Build tree structure for display
const unitTree = computed(() => {
  const roots: (BusinessUnit & { children: BusinessUnit[] })[] = []
  const unitMap = new Map<string, BusinessUnit & { children: BusinessUnit[] }>()

  // Create map with children arrays
  businessUnits.value.forEach(unit => {
    unitMap.set(unit.id, { ...unit, children: [] })
  })

  // Build tree
  unitMap.forEach(unit => {
    if (unit.parent_id && unitMap.has(unit.parent_id)) {
      unitMap.get(unit.parent_id)!.children.push(unit)
    } else {
      roots.push(unit)
    }
  })

  return roots
})

async function loadBusinessUnits() {
  loading.value = true
  error.value = null
  try {
    businessUnits.value = await fetchBusinessUnits()
  } catch (err) {
    error.value = err instanceof Error ? err.message : t('admin.businessUnits.loadError')
  } finally {
    loading.value = false
  }
}

function openCreateModal() {
  selectedUnit.value = null
  showModal.value = true
}

function openEditModal(unit: BusinessUnit) {
  selectedUnit.value = unit
  showModal.value = true
}

function handleModalClose() {
  showModal.value = false
  selectedUnit.value = null
}

function handleModalSave() {
  showModal.value = false
  selectedUnit.value = null
  loadBusinessUnits()
}

function confirmDelete(unit: BusinessUnit) {
  deleteConfirm.value = unit
}

function cancelDelete() {
  deleteConfirm.value = null
}

async function executeDelete() {
  if (!deleteConfirm.value) return

  deleting.value = true
  error.value = null
  try {
    await deleteBusinessUnit(deleteConfirm.value.id)
    deleteConfirm.value = null
    await loadBusinessUnits()
  } catch (err) {
    error.value = err instanceof Error ? err.message : t('admin.businessUnits.deleteError')
  } finally {
    deleting.value = false
  }
}

function getParentName(parentId: string | null): string {
  if (!parentId) return '-'
  const parent = businessUnits.value.find(u => u.id === parentId)
  return parent ? parent.name : '-'
}

onMounted(() => {
  loadBusinessUnits()
})
</script>

<template>
  <div class="business-unit-list">
    <Card>
      <SectionHeader
        :title="t('admin.businessUnits.title')"
        :description="t('admin.businessUnits.description')"
      >
        <template #actions>
          <button class="btn btn-primary btn-sm" @click="openCreateModal">
            <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
              <line x1="12" y1="5" x2="12" y2="19"></line>
              <line x1="5" y1="12" x2="19" y2="12"></line>
            </svg>
            {{ t('admin.businessUnits.create') }}
          </button>
        </template>
      </SectionHeader>

      <!-- Loading State -->
      <div v-if="loading" class="loading-state">
        <span class="spinner"></span>
        <span>{{ t('common.loading') }}</span>
      </div>

      <!-- Error State -->
      <div v-else-if="error" class="error-message">
        {{ error }}
        <button class="btn-link" @click="loadBusinessUnits">{{ t('common.retry') }}</button>
      </div>

      <!-- Empty State -->
      <div v-else-if="businessUnits.length === 0" class="empty-state">
        <p>{{ t('admin.businessUnits.empty') }}</p>
        <button class="btn btn-primary" @click="openCreateModal">
          {{ t('admin.businessUnits.createFirst') }}
        </button>
      </div>

      <!-- Business Units Table -->
      <table v-else class="table">
        <thead>
          <tr>
            <th>{{ t('admin.businessUnits.name') }}</th>
            <th>{{ t('admin.businessUnits.code') }}</th>
            <th>{{ t('admin.businessUnits.parent') }}</th>
            <th class="actions-col">{{ t('common.actions') }}</th>
          </tr>
        </thead>
        <tbody>
          <template v-for="unit in unitTree" :key="unit.id">
            <!-- Parent unit -->
            <tr>
              <td class="name-cell">
                <span class="unit-name">{{ unit.name }}</span>
              </td>
              <td>
                <code class="unit-code">{{ unit.code }}</code>
              </td>
              <td>{{ getParentName(unit.parent_id) }}</td>
              <td class="actions-col">
                <button
                  class="btn-icon"
                  :title="t('common.edit')"
                  @click="openEditModal(unit)"
                >
                  <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                    <path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"></path>
                    <path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"></path>
                  </svg>
                </button>
                <button
                  class="btn-icon btn-icon-danger"
                  :title="t('common.delete')"
                  @click="confirmDelete(unit)"
                >
                  <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                    <polyline points="3 6 5 6 21 6"></polyline>
                    <path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"></path>
                  </svg>
                </button>
              </td>
            </tr>
            <!-- Child units -->
            <tr v-for="child in unit.children" :key="child.id" class="child-row">
              <td class="name-cell">
                <span class="indent"></span>
                <span class="unit-name">{{ child.name }}</span>
              </td>
              <td>
                <code class="unit-code">{{ child.code }}</code>
              </td>
              <td>{{ unit.name }}</td>
              <td class="actions-col">
                <button
                  class="btn-icon"
                  :title="t('common.edit')"
                  @click="openEditModal(child)"
                >
                  <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                    <path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"></path>
                    <path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"></path>
                  </svg>
                </button>
                <button
                  class="btn-icon btn-icon-danger"
                  :title="t('common.delete')"
                  @click="confirmDelete(child)"
                >
                  <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                    <polyline points="3 6 5 6 21 6"></polyline>
                    <path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"></path>
                  </svg>
                </button>
              </td>
            </tr>
          </template>
        </tbody>
      </table>
    </Card>

    <!-- Delete Confirmation -->
    <div v-if="deleteConfirm" class="modal-overlay">
      <div class="modal-content delete-modal">
        <h3>{{ t('admin.businessUnits.deleteTitle') }}</h3>
        <p>
          {{ t('admin.businessUnits.deleteConfirm', { name: deleteConfirm.name }) }}
        </p>
        <div class="modal-actions">
          <button class="btn btn-secondary" :disabled="deleting" @click="cancelDelete">
            {{ t('common.cancel') }}
          </button>
          <button class="btn btn-danger" :disabled="deleting" @click="executeDelete">
            <span v-if="deleting" class="spinner-small"></span>
            {{ deleting ? t('common.deleting') : t('common.delete') }}
          </button>
        </div>
      </div>
    </div>

    <!-- Create/Edit Modal -->
    <BusinessUnitModal
      v-if="showModal"
      :unit="selectedUnit"
      :available-parents="businessUnits.filter(u => u.id !== selectedUnit?.id)"
      @close="handleModalClose"
      @save="handleModalSave"
    />
  </div>
</template>

<style scoped>
.business-unit-list {
  max-width: 900px;
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

.empty-state p {
  margin-bottom: 1rem;
}

.table {
  width: 100%;
  border-collapse: collapse;
  margin-top: 1rem;
}

.table th,
.table td {
  padding: 0.75rem;
  text-align: left;
  border-bottom: 1px solid var(--color-border);
}

.table th {
  font-weight: 600;
  color: var(--color-text-muted);
  font-size: 0.75rem;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.child-row {
  background-color: var(--color-bg-subtle, #f9fafb);
}

.name-cell {
  display: flex;
  align-items: center;
}

.indent {
  display: inline-block;
  width: 1.5rem;
  margin-right: 0.5rem;
  border-left: 2px solid var(--color-border);
  height: 1rem;
}

.unit-name {
  font-weight: 500;
}

.unit-code {
  font-size: 0.75rem;
  background-color: var(--color-bg-subtle, #f3f4f6);
  padding: 0.125rem 0.375rem;
  border-radius: 0.25rem;
}

.actions-col {
  width: 100px;
  text-align: right;
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
  gap: 0.25rem;
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

.btn-danger {
  background-color: var(--color-error, #dc2626);
  color: white;
  border: none;
}

.btn-danger:hover:not(:disabled) {
  background-color: #b91c1c;
}

.btn-icon {
  background: none;
  border: none;
  padding: 0.375rem;
  cursor: pointer;
  color: var(--color-text-muted);
  border-radius: 0.25rem;
  transition: all 0.15s ease;
}

.btn-icon:hover {
  background-color: var(--color-bg-hover);
  color: var(--color-text);
}

.btn-icon-danger:hover {
  background-color: var(--color-error-bg, #fee2e2);
  color: var(--color-error, #dc2626);
}

.modal-overlay {
  position: fixed;
  inset: 0;
  background-color: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.modal-content {
  background: white;
  border-radius: 0.5rem;
  padding: 1.5rem;
  max-width: 400px;
  width: 90%;
}

.delete-modal h3 {
  margin: 0 0 0.75rem;
  color: var(--color-error, #dc2626);
}

.delete-modal p {
  margin: 0 0 1.5rem;
  color: var(--color-text-muted);
}

.modal-actions {
  display: flex;
  justify-content: flex-end;
  gap: 0.75rem;
}
</style>
