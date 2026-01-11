<script setup lang="ts">
// TSS PPM v3.0 - Audit Log Detail Modal Component
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'
import { type AuditLogEntry } from '@/api/admin'

const props = defineProps<{
  show: boolean
  log: AuditLogEntry | null
}>()

const emit = defineEmits<{
  (e: 'close'): void
}>()

const { t } = useI18n()

// Format date for display
function formatDate(dateString: string): string {
  return new Date(dateString).toLocaleString()
}

// Format action for display
function formatAction(action: string): string {
  return action.replace(/_/g, ' ').toLowerCase().replace(/\b\w/g, c => c.toUpperCase())
}

// Format changes as readable JSON
const formattedChanges = computed(() => {
  if (!props.log?.changes) return null
  return JSON.stringify(props.log.changes, null, 2)
})

// Check if changes has before/after structure
const hasDiff = computed(() => {
  if (!props.log?.changes) return false
  return 'before' in props.log.changes && 'after' in props.log.changes
})

function close() {
  emit('close')
}
</script>

<template>
  <Teleport to="body">
    <div v-if="show" class="modal-overlay" @click.self="close">
      <div class="modal-container" role="dialog" aria-modal="true">
        <div class="modal-header">
          <h2>{{ t('admin.auditLogs.detail.title') }}</h2>
          <button class="close-button" @click="close" :aria-label="t('common.close')">
            &times;
          </button>
        </div>

        <div v-if="log" class="modal-body">
          <!-- Basic Info -->
          <div class="info-section">
            <div class="info-row">
              <span class="info-label">{{ t('admin.auditLogs.detail.timestamp') }}</span>
              <span class="info-value">{{ formatDate(log.created_at) }}</span>
            </div>

            <div class="info-row">
              <span class="info-label">{{ t('admin.auditLogs.detail.action') }}</span>
              <span class="info-value">
                <span class="action-badge">{{ formatAction(log.action) }}</span>
              </span>
            </div>

            <div class="info-row">
              <span class="info-label">{{ t('admin.auditLogs.detail.entityType') }}</span>
              <span class="info-value">{{ log.entity_type }}</span>
            </div>

            <div v-if="log.entity_id" class="info-row">
              <span class="info-label">{{ t('admin.auditLogs.detail.entityId') }}</span>
              <span class="info-value mono">{{ log.entity_id }}</span>
            </div>
          </div>

          <!-- User Info -->
          <div class="info-section">
            <h3 class="section-title">{{ t('admin.auditLogs.detail.performedBy') }}</h3>
            <div v-if="log.user_email" class="info-row">
              <span class="info-label">{{ t('admin.auditLogs.detail.userEmail') }}</span>
              <span class="info-value">{{ log.user_email }}</span>
            </div>
            <div v-if="log.user_name" class="info-row">
              <span class="info-label">{{ t('admin.auditLogs.detail.userName') }}</span>
              <span class="info-value">{{ log.user_name }}</span>
            </div>
            <div v-if="log.user_id" class="info-row">
              <span class="info-label">{{ t('admin.auditLogs.detail.userId') }}</span>
              <span class="info-value mono">{{ log.user_id }}</span>
            </div>
            <div v-if="!log.user_email && !log.user_name" class="info-row">
              <span class="text-muted">{{ t('admin.auditLogs.systemAction') }}</span>
            </div>
          </div>

          <!-- Request Info -->
          <div v-if="log.ip_address || log.user_agent" class="info-section">
            <h3 class="section-title">{{ t('admin.auditLogs.detail.requestInfo') }}</h3>
            <div v-if="log.ip_address" class="info-row">
              <span class="info-label">{{ t('admin.auditLogs.detail.ipAddress') }}</span>
              <span class="info-value mono">{{ log.ip_address }}</span>
            </div>
            <div v-if="log.user_agent" class="info-row">
              <span class="info-label">{{ t('admin.auditLogs.detail.userAgent') }}</span>
              <span class="info-value user-agent">{{ log.user_agent }}</span>
            </div>
          </div>

          <!-- Changes -->
          <div v-if="log.changes" class="info-section">
            <h3 class="section-title">{{ t('admin.auditLogs.detail.changes') }}</h3>

            <!-- Diff view for before/after -->
            <template v-if="hasDiff">
              <div class="diff-container">
                <div class="diff-column">
                  <h4 class="diff-label">{{ t('admin.auditLogs.detail.before') }}</h4>
                  <pre class="diff-content before">{{ JSON.stringify(log.changes.before, null, 2) }}</pre>
                </div>
                <div class="diff-column">
                  <h4 class="diff-label">{{ t('admin.auditLogs.detail.after') }}</h4>
                  <pre class="diff-content after">{{ JSON.stringify(log.changes.after, null, 2) }}</pre>
                </div>
              </div>
            </template>

            <!-- Raw JSON for other formats -->
            <template v-else>
              <pre class="json-content">{{ formattedChanges }}</pre>
            </template>
          </div>
        </div>

        <div class="modal-footer">
          <button class="btn btn-secondary" @click="close">
            {{ t('common.close') }}
          </button>
        </div>
      </div>
    </div>
  </Teleport>
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
  align-items: center;
  justify-content: center;
  z-index: 1000;
  padding: 1rem;
}

.modal-container {
  background: white;
  border-radius: 0.5rem;
  width: 100%;
  max-width: 700px;
  max-height: 90vh;
  display: flex;
  flex-direction: column;
  box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.1);
}

.modal-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 1rem 1.5rem;
  border-bottom: 1px solid var(--color-border);
}

.modal-header h2 {
  margin: 0;
  font-size: 1.125rem;
  font-weight: 600;
}

.close-button {
  background: none;
  border: none;
  font-size: 1.5rem;
  cursor: pointer;
  color: var(--color-text-muted);
  line-height: 1;
  padding: 0.25rem;
}

.close-button:hover {
  color: var(--color-text);
}

.modal-body {
  padding: 1.5rem;
  overflow-y: auto;
  flex: 1;
}

.info-section {
  margin-bottom: 1.5rem;
  padding-bottom: 1rem;
  border-bottom: 1px solid var(--color-border);
}

.info-section:last-child {
  margin-bottom: 0;
  padding-bottom: 0;
  border-bottom: none;
}

.section-title {
  font-size: 0.875rem;
  font-weight: 600;
  color: var(--color-text-muted);
  margin: 0 0 0.75rem 0;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.info-row {
  display: flex;
  gap: 1rem;
  margin-bottom: 0.5rem;
}

.info-label {
  flex: 0 0 120px;
  font-weight: 500;
  color: var(--color-text-muted);
  font-size: 0.875rem;
}

.info-value {
  flex: 1;
  font-size: 0.875rem;
  word-break: break-word;
}

.mono {
  font-family: monospace;
  font-size: 0.8125rem;
  background-color: var(--color-bg-secondary, #f3f4f6);
  padding: 0.125rem 0.375rem;
  border-radius: 0.25rem;
}

.text-muted {
  color: var(--color-text-muted);
  font-style: italic;
}

.action-badge {
  display: inline-block;
  padding: 0.25rem 0.5rem;
  background-color: var(--color-primary, #cc0e70);
  color: white;
  border-radius: 0.25rem;
  font-size: 0.75rem;
  font-weight: 500;
}

.user-agent {
  font-size: 0.75rem;
  color: var(--color-text-muted);
}

.diff-container {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1rem;
}

.diff-column {
  min-width: 0;
}

.diff-label {
  font-size: 0.75rem;
  font-weight: 500;
  margin: 0 0 0.5rem 0;
  color: var(--color-text-muted);
}

.diff-content {
  margin: 0;
  padding: 0.75rem;
  border-radius: 0.375rem;
  font-size: 0.75rem;
  font-family: monospace;
  overflow-x: auto;
  white-space: pre-wrap;
  word-break: break-word;
}

.diff-content.before {
  background-color: #fef2f2;
  border: 1px solid #fecaca;
}

.diff-content.after {
  background-color: #f0fdf4;
  border: 1px solid #bbf7d0;
}

.json-content {
  margin: 0;
  padding: 0.75rem;
  background-color: var(--color-bg-secondary, #f3f4f6);
  border-radius: 0.375rem;
  font-size: 0.75rem;
  font-family: monospace;
  overflow-x: auto;
  white-space: pre-wrap;
  word-break: break-word;
}

.modal-footer {
  display: flex;
  justify-content: flex-end;
  padding: 1rem 1.5rem;
  border-top: 1px solid var(--color-border);
}

.btn {
  padding: 0.5rem 1rem;
  border-radius: 0.375rem;
  font-weight: 500;
  font-size: 0.875rem;
  cursor: pointer;
  transition: all 0.15s ease;
}

.btn-secondary {
  background-color: white;
  color: var(--color-text);
  border: 1px solid var(--color-border);
}

.btn-secondary:hover {
  background-color: var(--color-bg-hover);
}

@media (max-width: 640px) {
  .modal-container {
    max-height: 100vh;
    border-radius: 0;
  }

  .diff-container {
    grid-template-columns: 1fr;
  }

  .info-row {
    flex-direction: column;
    gap: 0.25rem;
  }

  .info-label {
    flex: none;
  }
}
</style>
