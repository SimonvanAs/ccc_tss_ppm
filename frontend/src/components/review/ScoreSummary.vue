<script setup lang="ts">
import { computed } from 'vue'

type VetoType = 'SCF' | 'KAR' | 'COMPETENCY' | null

interface Props {
  whatScore?: number | null
  howScore?: number | null
  whatVetoActive?: boolean
  whatVetoType?: VetoType
  howVetoActive?: boolean
  compact?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  whatScore: null,
  howScore: null,
  whatVetoActive: false,
  whatVetoType: null,
  howVetoActive: false,
  compact: false,
})

function formatScore(score: number | null | undefined): string {
  if (score === null || score === undefined) return '-'
  return score.toFixed(2)
}

function getScoreClass(score: number | null | undefined): string {
  if (score === null || score === undefined) return ''
  if (score <= 1) return 'score-danger'
  if (score < 2) return 'score-warning'
  return 'score-success'
}

const whatScoreFormatted = computed(() => formatScore(props.whatScore))
const howScoreFormatted = computed(() => formatScore(props.howScore))

const whatScoreClass = computed(() => getScoreClass(props.whatScore))
const howScoreClass = computed(() => getScoreClass(props.howScore))

const whatAriaLabel = computed(() => {
  const value = props.whatScore !== null ? props.whatScore.toFixed(2) : 'not set'
  const veto = props.whatVetoActive ? `, ${props.whatVetoType} VETO active` : ''
  return `WHAT score: ${value}${veto}`
})

const howAriaLabel = computed(() => {
  const value = props.howScore !== null ? props.howScore.toFixed(2) : 'not set'
  const veto = props.howVetoActive ? ', Competency VETO active' : ''
  return `HOW score: ${value}${veto}`
})
</script>

<template>
  <div class="score-summary" :class="{ compact }">
    <div
      class="score-item what-score"
      :class="whatScoreClass"
      :aria-label="whatAriaLabel"
    >
      <span class="score-label">WHAT</span>
      <span class="score-value">{{ whatScoreFormatted }}</span>
      <span v-if="whatVetoActive" class="veto-badge">
        {{ whatVetoType }} VETO
      </span>
    </div>

    <div
      class="score-item how-score"
      :class="howScoreClass"
      :aria-label="howAriaLabel"
    >
      <span class="score-label">HOW</span>
      <span class="score-value">{{ howScoreFormatted }}</span>
      <span v-if="howVetoActive" class="veto-badge">
        VETO
      </span>
    </div>
  </div>
</template>

<style scoped>
.score-summary {
  display: flex;
  gap: 1.5rem;
}

.score-summary.compact {
  gap: 1rem;
}

.score-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 1rem;
  background: var(--color-white);
  border-radius: 8px;
  border: 2px solid var(--color-gray-200);
  min-width: 80px;
  position: relative;
}

.compact .score-item {
  padding: 0.5rem;
  min-width: 60px;
}

.score-label {
  font-size: 0.75rem;
  font-weight: 600;
  color: var(--color-gray-600);
  text-transform: uppercase;
  letter-spacing: 0.05em;
  margin-bottom: 0.25rem;
}

.compact .score-label {
  font-size: 0.625rem;
}

.score-value {
  font-size: 1.5rem;
  font-weight: 700;
  color: var(--color-gray-900);
}

.compact .score-value {
  font-size: 1.125rem;
}

/* Score status colors */
.score-danger {
  border-color: var(--color-grid-red);
  background: #FEF2F2;
}

.score-danger .score-value {
  color: var(--color-grid-red);
}

.score-warning {
  border-color: var(--color-grid-orange);
  background: #FFFBEB;
}

.score-warning .score-value {
  color: var(--color-grid-orange);
}

.score-success {
  border-color: var(--color-grid-green);
  background: #F0FDF4;
}

.score-success .score-value {
  color: var(--color-grid-green);
}

/* VETO badge */
.veto-badge {
  position: absolute;
  top: -0.5rem;
  right: -0.5rem;
  background-color: var(--color-grid-red);
  color: var(--color-white);
  font-size: 0.5rem;
  font-weight: 700;
  padding: 0.125rem 0.375rem;
  border-radius: 2px;
  text-transform: uppercase;
  white-space: nowrap;
}

.compact .veto-badge {
  font-size: 0.4375rem;
  padding: 0.0625rem 0.25rem;
}

/* Responsive styles */
@media (max-width: 480px) {
  .score-summary {
    justify-content: center;
  }

  .score-item {
    flex: 1;
    min-width: 0;
    max-width: 100px;
  }
}
</style>
