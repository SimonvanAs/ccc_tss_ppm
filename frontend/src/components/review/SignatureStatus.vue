<script setup lang="ts">
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'

interface SignatureInfo {
  signedBy: string
  signedAt: Date
}

type ReviewStatus =
  | 'DRAFT'
  | 'PENDING_EMPLOYEE_SIGNATURE'
  | 'PENDING_MANAGER_SIGNATURE'
  | 'SIGNED'
  | 'ARCHIVED'

const props = withDefaults(
  defineProps<{
    status: ReviewStatus
    employeeSignature?: SignatureInfo
    managerSignature?: SignatureInfo
    wasRejected?: boolean
    compact?: boolean
  }>(),
  {
    wasRejected: false,
    compact: false,
  }
)

const { t, d } = useI18n()

const statusConfig = computed(() => {
  const configs: Record<
    ReviewStatus,
    { key: string; styleClass: string; icon: string }
  > = {
    DRAFT: {
      key: 'signature.status.draft',
      styleClass: 'draft',
      icon: 'draft',
    },
    PENDING_EMPLOYEE_SIGNATURE: {
      key: 'signature.status.awaitingEmployee',
      styleClass: 'pending',
      icon: 'pending',
    },
    PENDING_MANAGER_SIGNATURE: {
      key: 'signature.status.awaitingManager',
      styleClass: 'pending',
      icon: 'pending',
    },
    SIGNED: {
      key: 'signature.status.signed',
      styleClass: 'signed',
      icon: 'signed',
    },
    ARCHIVED: {
      key: 'signature.status.archived',
      styleClass: 'archived',
      icon: 'archived',
    },
  }
  return configs[props.status]
})

const statusClasses = computed(() => {
  const classes = [statusConfig.value.styleClass]
  if (props.compact) classes.push('compact')
  if (props.wasRejected && props.status === 'DRAFT') classes.push('rejected')
  return classes
})

function formatDate(date: Date): string {
  return d(date, 'short')
}
</script>

<template>
  <div class="signature-status" :class="statusClasses">
    <!-- Status Badge -->
    <div class="status-badge">
      <span class="status-icon" :class="statusConfig.icon">
        <template v-if="statusConfig.icon === 'signed'">
          <svg viewBox="0 0 20 20" fill="currentColor">
            <path
              fill-rule="evenodd"
              d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z"
              clip-rule="evenodd"
            />
          </svg>
        </template>
        <template v-else-if="statusConfig.icon === 'pending'">
          <svg viewBox="0 0 20 20" fill="currentColor">
            <path
              fill-rule="evenodd"
              d="M10 18a8 8 0 100-16 8 8 0 000 16zm1-12a1 1 0 10-2 0v4a1 1 0 00.293.707l2.828 2.829a1 1 0 101.415-1.415L11 9.586V6z"
              clip-rule="evenodd"
            />
          </svg>
        </template>
        <template v-else>
          <svg viewBox="0 0 20 20" fill="currentColor">
            <path
              d="M13.586 3.586a2 2 0 112.828 2.828l-.793.793-2.828-2.828.793-.793zM11.379 5.793L3 14.172V17h2.828l8.38-8.379-2.83-2.828z"
            />
          </svg>
        </template>
      </span>
      <span class="status-text">{{ t(statusConfig.key) }}</span>
    </div>

    <!-- Signature Details (hidden in compact mode) -->
    <div v-if="!compact && (employeeSignature || managerSignature)" class="signature-details">
      <!-- Employee Signature -->
      <div v-if="employeeSignature" class="signature-item">
        <span class="signature-role">{{ t('signature.employeeSigned') }}</span>
        <span class="signature-name">{{ employeeSignature.signedBy }}</span>
        <span class="signature-date">{{ formatDate(employeeSignature.signedAt) }}</span>
      </div>

      <!-- Manager Signature -->
      <div v-if="managerSignature" class="signature-item">
        <span class="signature-role">{{ t('signature.managerSigned') }}</span>
        <span class="signature-name">{{ managerSignature.signedBy }}</span>
        <span class="signature-date">{{ formatDate(managerSignature.signedAt) }}</span>
      </div>
    </div>
  </div>
</template>

<style scoped>
.signature-status {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.signature-status.compact {
  flex-direction: row;
  align-items: center;
}

.status-badge {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.375rem 0.75rem;
  border-radius: 9999px;
  font-size: 0.875rem;
  font-weight: 500;
  width: fit-content;
}

.status-icon {
  width: 1rem;
  height: 1rem;
  display: flex;
  align-items: center;
  justify-content: center;
}

.status-icon svg {
  width: 100%;
  height: 100%;
}

/* Draft status */
.signature-status.draft .status-badge {
  background: var(--color-gray-100, #f3f4f6);
  color: var(--color-gray-600, #4b5563);
}

.signature-status.draft .status-icon {
  color: var(--color-gray-500, #6b7280);
}

/* Pending status */
.signature-status.pending .status-badge {
  background: rgba(204, 14, 112, 0.1);
  color: var(--color-magenta, #CC0E70);
}

.signature-status.pending .status-icon {
  color: var(--color-magenta, #CC0E70);
}

/* Signed status */
.signature-status.signed .status-badge {
  background: rgba(16, 185, 129, 0.1);
  color: #059669;
}

.signature-status.signed .status-icon {
  color: #059669;
}

/* Archived status */
.signature-status.archived .status-badge {
  background: var(--color-gray-100, #f3f4f6);
  color: var(--color-gray-500, #6b7280);
}

/* Rejected (returned to draft) */
.signature-status.rejected .status-badge {
  background: rgba(245, 158, 11, 0.1);
  color: #d97706;
}

.signature-status.rejected .status-icon {
  color: #d97706;
}

.status-text {
  white-space: nowrap;
}

.signature-details {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
  padding-left: 0.25rem;
}

.signature-item {
  display: flex;
  flex-wrap: wrap;
  align-items: baseline;
  gap: 0.375rem;
  font-size: 0.8125rem;
  color: var(--color-gray-600, #4b5563);
}

.signature-role {
  color: var(--color-gray-500, #6b7280);
}

.signature-name {
  font-weight: 500;
  color: var(--color-gray-900, #111827);
}

.signature-date {
  color: var(--color-gray-500, #6b7280);
  font-size: 0.75rem;
}

/* Compact mode adjustments */
.signature-status.compact .status-badge {
  padding: 0.25rem 0.625rem;
  font-size: 0.8125rem;
}

.signature-status.compact .status-icon {
  width: 0.875rem;
  height: 0.875rem;
}
</style>
