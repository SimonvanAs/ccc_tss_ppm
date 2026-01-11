<script setup lang="ts">
// TSS PPM v3.0 - Calibration View
import { ref } from 'vue'
import { useI18n } from 'vue-i18n'
import { SectionHeader } from '../components/layout'
import CalibrationSessionList from '../components/calibration/CalibrationSessionList.vue'
import CalibrationSessionForm from '../components/calibration/CalibrationSessionForm.vue'
import CalibrationSessionDetail from '../components/calibration/CalibrationSessionDetail.vue'
import type { CalibrationSession } from '../api/calibration'

const { t } = useI18n()

type ViewMode = 'list' | 'create' | 'detail'

const viewMode = ref<ViewMode>('list')
const selectedSession = ref<CalibrationSession | null>(null)

function handleCreate() {
  viewMode.value = 'create'
}

function handleSelectSession(session: CalibrationSession) {
  selectedSession.value = session
  viewMode.value = 'detail'
}

function handleFormCancel() {
  viewMode.value = 'list'
}

function handleFormSubmit() {
  viewMode.value = 'list'
}

function handleBackToList() {
  selectedSession.value = null
  viewMode.value = 'list'
}
</script>

<template>
  <div class="calibration-view">
    <SectionHeader :title="t('calibration.title')">
      <template #actions>
        <button
          v-if="viewMode !== 'list'"
          class="back-btn"
          @click="handleBackToList"
        >
          <svg width="20" height="20" viewBox="0 0 20 20" fill="currentColor">
            <path fill-rule="evenodd" d="M9.707 16.707a1 1 0 01-1.414 0l-6-6a1 1 0 010-1.414l6-6a1 1 0 011.414 1.414L5.414 9H17a1 1 0 110 2H5.414l4.293 4.293a1 1 0 010 1.414z" clip-rule="evenodd" />
          </svg>
          {{ t('common.back') }}
        </button>
      </template>
    </SectionHeader>

    <CalibrationSessionList
      v-if="viewMode === 'list'"
      @create="handleCreate"
      @select="handleSelectSession"
    />

    <CalibrationSessionForm
      v-else-if="viewMode === 'create'"
      @cancel="handleFormCancel"
      @submit="handleFormSubmit"
    />

    <CalibrationSessionDetail
      v-else-if="viewMode === 'detail' && selectedSession"
      :session-id="selectedSession.id"
      @back="handleBackToList"
    />
  </div>
</template>

<style scoped>
.calibration-view {
  max-width: 1400px;
  margin: 0 auto;
}

.view-header {
  display: flex;
  align-items: center;
  gap: 1rem;
  margin-bottom: 1.5rem;
}

.view-header h1 {
  margin: 0;
  color: var(--color-navy, #004a91);
  font-size: 1.5rem;
}

.back-btn {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.5rem 1rem;
  background: transparent;
  border: 1px solid var(--color-gray-300, #ccc);
  border-radius: 4px;
  cursor: pointer;
  color: var(--color-navy, #004a91);
  font-size: 0.875rem;
  transition: all 0.2s;
}

.back-btn:hover {
  background-color: var(--color-gray-100, #f5f5f5);
  border-color: var(--color-navy, #004a91);
}
</style>
