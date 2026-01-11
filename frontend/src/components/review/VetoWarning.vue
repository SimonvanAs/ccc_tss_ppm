<script setup lang="ts">
import { computed } from 'vue'

type VetoType = 'SCF' | 'KAR' | 'COMPETENCY' | null

interface Props {
  vetoType: VetoType
  vetoActive?: boolean
  goalName?: string
  competencyName?: string
  compensated?: boolean
  compensatingGoalName?: string
  showCompensationHint?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  vetoActive: false,
  compensated: false,
  showCompensationHint: false,
})

const vetoTitle = computed(() => {
  switch (props.vetoType) {
    case 'SCF':
      return 'SCF VETO'
    case 'KAR':
      return 'KAR VETO'
    case 'COMPETENCY':
      return 'Competency VETO'
    default:
      return ''
  }
})

const vetoClass = computed(() => {
  switch (props.vetoType) {
    case 'SCF':
      return 'scf-veto'
    case 'KAR':
      return 'kar-veto'
    case 'COMPETENCY':
      return 'competency-veto'
    default:
      return ''
  }
})

const triggeringName = computed(() => {
  if (props.vetoType === 'COMPETENCY' && props.competencyName) {
    return props.competencyName
  }
  return props.goalName
})

const showWarning = computed(() => {
  return props.vetoActive && props.vetoType !== null
})

const showCompensated = computed(() => {
  return !props.vetoActive && props.compensated && props.vetoType === 'KAR'
})
</script>

<template>
  <div
    v-if="showWarning"
    class="veto-warning veto-active"
    :class="vetoClass"
    role="alert"
    aria-live="polite"
  >
    <span class="veto-icon">⚠️</span>
    <div class="veto-content">
      <strong class="veto-title">{{ vetoTitle }}</strong>
      <span class="veto-message">
        Score reduced to 1.00
        <template v-if="triggeringName">
          due to "{{ triggeringName }}"
        </template>
      </span>
      <span v-if="showCompensationHint && vetoType === 'KAR'" class="veto-hint">
        This can be offset by compensation from another KAR goal scoring 3.
      </span>
    </div>
  </div>

  <div
    v-else-if="showCompensated"
    class="veto-compensated veto-success"
    :class="vetoClass"
  >
    <span class="veto-icon">✓</span>
    <div class="veto-content">
      <strong class="veto-title">Compensated</strong>
      <span class="veto-message">
        KAR VETO was offset
        <template v-if="compensatingGoalName">
          by "{{ compensatingGoalName }}"
        </template>
      </span>
    </div>
  </div>
</template>

<style scoped>
.veto-warning,
.veto-compensated {
  display: flex;
  align-items: flex-start;
  gap: 0.75rem;
  padding: 1rem;
  border-radius: 8px;
  margin: 0.5rem 0;
}

.veto-warning.veto-active {
  background-color: #FEF2F2;
  border: 1px solid var(--color-grid-red);
  color: #991B1B;
}

.veto-compensated.veto-success {
  background-color: #F0FDF4;
  border: 1px solid var(--color-grid-green);
  color: #166534;
}

.veto-icon {
  font-size: 1.25rem;
  flex-shrink: 0;
}

.veto-content {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.veto-title {
  font-weight: 600;
}

.veto-message {
  font-size: 0.875rem;
}

.veto-hint {
  font-size: 0.75rem;
  opacity: 0.8;
  margin-top: 0.25rem;
}

/* Type-specific styling */
.scf-veto.veto-active {
  border-left: 4px solid var(--color-grid-red);
}

.kar-veto.veto-active {
  border-left: 4px solid var(--color-grid-orange);
  background-color: #FFFBEB;
  color: #92400E;
}

.kar-veto.veto-success {
  border-left: 4px solid var(--color-grid-green);
}

.competency-veto.veto-active {
  border-left: 4px solid var(--color-grid-red);
}
</style>
