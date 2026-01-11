<script setup lang="ts">
// TSS PPM v3.0 - CalibrationSessionList Component
import { ref, computed, onMounted } from 'vue'
import { useI18n } from 'vue-i18n'
import {
  fetchCalibrationSessions,
  type CalibrationSession,
  type CalibrationSessionStatus,
} from '../../api/calibration'

const { t } = useI18n()

const emit = defineEmits<{
  (e: 'create'): void
  (e: 'select', session: CalibrationSession): void
}>()

const sessions = ref<CalibrationSession[]>([])
const loading = ref(true)
const error = ref<string | null>(null)
const statusFilter = ref<CalibrationSessionStatus | ''>('')

const filteredSessions = computed(() => {
  if (!statusFilter.value) return sessions.value
  return sessions.value.filter((s) => s.status === statusFilter.value)
})

const statusOptions: CalibrationSessionStatus[] = [
  'PREPARATION',
  'IN_PROGRESS',
  'PENDING_APPROVAL',
  'COMPLETED',
  'CANCELLED',
]

function getStatusClass(status: CalibrationSessionStatus): string {
  return `status-${status.toLowerCase().replace('_', '-')}`
}

function formatDate(dateString: string): string {
  const date = new Date(dateString)
  return date.toLocaleDateString(undefined, {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
  })
}

function handleCreateClick() {
  emit('create')
}

function handleSessionClick(session: CalibrationSession) {
  emit('select', session)
}

onMounted(async () => {
  try {
    sessions.value = await fetchCalibrationSessions()
  } catch (e) {
    error.value = e instanceof Error ? e.message : 'Failed to load sessions'
  } finally {
    loading.value = false
  }
})
</script>

<template>
  <div class="calibration-session-list">
    <div class="list-header">
      <h2>{{ t('calibration.sessions.title') }}</h2>
      <div class="header-actions">
        <select
          v-model="statusFilter"
          class="status-filter"
          :aria-label="t('calibration.sessions.filterByStatus')"
        >
          <option value="">{{ t('calibration.sessions.allStatuses') }}</option>
          <option v-for="status in statusOptions" :key="status" :value="status">
            {{ t(`calibration.status.${status}`) }}
          </option>
        </select>
        <button class="create-session-btn" @click="handleCreateClick">
          {{ t('calibration.sessions.createNew') }}
        </button>
      </div>
    </div>

    <div v-if="loading" class="loading-state">
      {{ t('calibration.sessions.loading') }}
    </div>

    <div v-else-if="error" class="error-state">
      {{ error }}
    </div>

    <div v-else-if="filteredSessions.length === 0" class="empty-state">
      {{ t('calibration.sessions.noSessions') }}
    </div>

    <div v-else class="sessions-grid">
      <div
        v-for="session in filteredSessions"
        :key="session.id"
        class="session-card"
        @click="handleSessionClick(session)"
      >
        <div class="card-header">
          <h3 class="session-name">{{ session.name }}</h3>
          <span class="status-badge" :class="getStatusClass(session.status)">
            {{ t(`calibration.status.${session.status}`) }}
          </span>
        </div>

        <div class="card-body">
          <p v-if="session.description" class="session-description">
            {{ session.description }}
          </p>

          <div class="session-meta">
            <span class="meta-item">
              <span class="meta-label">Year:</span>
              <span class="meta-value">{{ session.review_year }}</span>
            </span>
            <span class="meta-item">
              <span class="meta-label">Scope:</span>
              <span class="meta-value">{{ session.scope }}</span>
            </span>
            <span class="meta-item">
              <span class="meta-label">Created:</span>
              <span class="meta-value">{{ formatDate(session.created_at) }}</span>
            </span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.calibration-session-list {
  padding: 1rem;
}

.list-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.5rem;
}

.list-header h2 {
  margin: 0;
  color: var(--navy, #004a91);
  font-family: Tahoma, sans-serif;
}

.header-actions {
  display: flex;
  gap: 1rem;
  align-items: center;
}

.status-filter {
  padding: 0.5rem 1rem;
  border: 1px solid #ccc;
  border-radius: 4px;
  font-family: Tahoma, sans-serif;
  min-width: 150px;
}

.create-session-btn {
  padding: 0.5rem 1rem;
  background-color: var(--magenta, #cc0e70);
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-family: Tahoma, sans-serif;
  font-weight: bold;
}

.create-session-btn:hover {
  background-color: #a00b5a;
}

.loading-state,
.error-state,
.empty-state {
  text-align: center;
  padding: 3rem;
  color: #666;
  font-family: Tahoma, sans-serif;
}

.error-state {
  color: #c00;
}

.sessions-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
  gap: 1rem;
}

.session-card {
  background: white;
  border: 1px solid #e0e0e0;
  border-radius: 8px;
  padding: 1rem;
  cursor: pointer;
  transition: box-shadow 0.2s, border-color 0.2s;
}

.session-card:hover {
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  border-color: var(--navy, #004a91);
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 0.75rem;
}

.session-name {
  margin: 0;
  font-size: 1.1rem;
  color: var(--navy, #004a91);
  font-family: Tahoma, sans-serif;
}

.status-badge {
  padding: 0.25rem 0.5rem;
  border-radius: 4px;
  font-size: 0.75rem;
  font-weight: bold;
  text-transform: uppercase;
}

.status-preparation {
  background-color: #e3f2fd;
  color: #1565c0;
}

.status-in-progress {
  background-color: #fff3e0;
  color: #e65100;
}

.status-pending-approval {
  background-color: #fce4ec;
  color: #c2185b;
}

.status-completed {
  background-color: #e8f5e9;
  color: #2e7d32;
}

.status-cancelled {
  background-color: #fafafa;
  color: #616161;
}

.session-description {
  margin: 0 0 0.75rem;
  color: #666;
  font-size: 0.9rem;
  line-height: 1.4;
}

.session-meta {
  display: flex;
  flex-wrap: wrap;
  gap: 1rem;
  font-size: 0.85rem;
}

.meta-item {
  display: flex;
  gap: 0.25rem;
}

.meta-label {
  color: #999;
}

.meta-value {
  color: #333;
  font-weight: 500;
}
</style>
