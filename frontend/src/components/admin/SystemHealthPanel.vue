<script setup lang="ts">
// TSS PPM v3.0 - System Health Panel Component
import { ref, onMounted, onUnmounted } from 'vue'
import { useI18n } from 'vue-i18n'
import { Card, SectionHeader } from '@/components/layout'
import { fetchSystemHealth, type SystemHealthResponse, type ServiceStatus } from '@/api/admin'

const { t } = useI18n()

const loading = ref(false)
const error = ref<string | null>(null)
const healthData = ref<SystemHealthResponse | null>(null)
const lastRefresh = ref<Date | null>(null)
let refreshInterval: ReturnType<typeof setInterval> | null = null

async function loadHealth() {
  loading.value = true
  error.value = null
  try {
    healthData.value = await fetchSystemHealth()
    lastRefresh.value = new Date()
  } catch (err) {
    error.value = err instanceof Error ? err.message : t('admin.system.loadError')
  } finally {
    loading.value = false
  }
}

function getStatusColor(status: string): string {
  switch (status) {
    case 'healthy':
      return 'status-healthy'
    case 'unhealthy':
      return 'status-unhealthy'
    default:
      return 'status-unknown'
  }
}

function getStatusIcon(status: string): string {
  switch (status) {
    case 'healthy':
      return '✓'
    case 'unhealthy':
      return '✗'
    default:
      return '?'
  }
}

function formatLatency(latencyMs: number | null): string {
  if (latencyMs === null) return '-'
  return `${latencyMs.toFixed(0)}ms`
}

function formatTimestamp(timestamp: string): string {
  return new Date(timestamp).toLocaleTimeString()
}

onMounted(() => {
  loadHealth()
  // Auto-refresh every 30 seconds
  refreshInterval = setInterval(loadHealth, 30000)
})

onUnmounted(() => {
  if (refreshInterval) {
    clearInterval(refreshInterval)
  }
})
</script>

<template>
  <Card>
    <SectionHeader
      :title="t('admin.system.healthTitle')"
      :description="t('admin.system.healthDescription')"
    >
      <template #actions>
        <button
          class="btn btn-secondary btn-sm"
          :disabled="loading"
          @click="loadHealth"
        >
          <svg
            :class="{ 'spin': loading }"
            xmlns="http://www.w3.org/2000/svg"
            width="16"
            height="16"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            stroke-width="2"
            stroke-linecap="round"
            stroke-linejoin="round"
          >
            <path d="M21.5 2v6h-6M2.5 22v-6h6M2 11.5a10 10 0 0 1 18.8-4.3M22 12.5a10 10 0 0 1-18.8 4.3"/>
          </svg>
          {{ t('admin.system.refresh') }}
        </button>
      </template>
    </SectionHeader>

    <!-- Loading State -->
    <div v-if="loading && !healthData" class="loading-state">
      <span class="spinner"></span>
      <span>{{ t('common.loading') }}</span>
    </div>

    <!-- Error State -->
    <div v-else-if="error" class="error-message">
      {{ error }}
      <button class="btn-link" @click="loadHealth">{{ t('common.retry') }}</button>
    </div>

    <!-- Health Data -->
    <template v-else-if="healthData">
      <!-- Overall Status -->
      <div class="overall-status" :class="getStatusColor(healthData.overall_status)">
        <span class="status-icon">{{ getStatusIcon(healthData.overall_status) }}</span>
        <div class="status-info">
          <span class="status-label">{{ t('admin.system.overallStatus') }}</span>
          <span class="status-value">{{ t(`admin.system.status.${healthData.overall_status}`) }}</span>
        </div>
        <span v-if="lastRefresh" class="last-refresh">
          {{ t('admin.system.lastRefresh', { time: formatTimestamp(healthData.timestamp) }) }}
        </span>
      </div>

      <!-- Service List -->
      <div class="service-list">
        <div
          v-for="(service, key) in healthData.services"
          :key="key"
          class="service-item"
        >
          <div class="service-status" :class="getStatusColor(service.status)">
            <span class="status-dot"></span>
          </div>
          <div class="service-info">
            <span class="service-name">{{ service.name }}</span>
            <span class="service-message">{{ service.message || '-' }}</span>
          </div>
          <div class="service-latency">
            {{ formatLatency(service.latency_ms) }}
          </div>
        </div>
      </div>
    </template>
  </Card>
</template>

<style scoped>
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

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

.spin {
  animation: spin 0.8s linear infinite;
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

.btn-secondary {
  background-color: white;
  color: var(--color-text);
  border: 1px solid var(--color-border);
}

.btn-secondary:hover:not(:disabled) {
  background-color: var(--color-bg-hover);
}

.overall-status {
  display: flex;
  align-items: center;
  gap: 1rem;
  padding: 1rem;
  border-radius: 0.5rem;
  margin-top: 1rem;
}

.overall-status.status-healthy {
  background-color: #dcfce7;
}

.overall-status.status-unhealthy {
  background-color: #fee2e2;
}

.overall-status.status-unknown {
  background-color: #fef3c7;
}

.status-icon {
  width: 2.5rem;
  height: 2.5rem;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 50%;
  font-size: 1.25rem;
  font-weight: bold;
}

.status-healthy .status-icon {
  background-color: #16a34a;
  color: white;
}

.status-unhealthy .status-icon {
  background-color: #dc2626;
  color: white;
}

.status-unknown .status-icon {
  background-color: #d97706;
  color: white;
}

.status-info {
  flex: 1;
  display: flex;
  flex-direction: column;
}

.status-label {
  font-size: 0.75rem;
  color: var(--color-text-muted);
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.status-value {
  font-size: 1.125rem;
  font-weight: 600;
}

.last-refresh {
  font-size: 0.75rem;
  color: var(--color-text-muted);
}

.service-list {
  margin-top: 1.5rem;
  border: 1px solid var(--color-border);
  border-radius: 0.5rem;
  overflow: hidden;
}

.service-item {
  display: flex;
  align-items: center;
  gap: 1rem;
  padding: 1rem;
  border-bottom: 1px solid var(--color-border);
}

.service-item:last-child {
  border-bottom: none;
}

.service-status {
  display: flex;
  align-items: center;
  justify-content: center;
}

.status-dot {
  width: 0.75rem;
  height: 0.75rem;
  border-radius: 50%;
}

.status-healthy .status-dot {
  background-color: #16a34a;
}

.status-unhealthy .status-dot {
  background-color: #dc2626;
}

.status-unknown .status-dot {
  background-color: #d97706;
}

.service-info {
  flex: 1;
  display: flex;
  flex-direction: column;
}

.service-name {
  font-weight: 500;
}

.service-message {
  font-size: 0.75rem;
  color: var(--color-text-muted);
}

.service-latency {
  font-size: 0.875rem;
  color: var(--color-text-muted);
  font-family: monospace;
}
</style>
