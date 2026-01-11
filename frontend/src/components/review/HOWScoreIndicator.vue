<script setup lang="ts">
// TSS PPM v3.0 - HOWScoreIndicator Component
// Displays the calculated HOW score with VETO warning and grid position

import { computed } from 'vue'
import { useI18n } from 'vue-i18n'

interface Props {
  howScore: number | null
  vetoActive: boolean
  vetoCompetencyId?: string
  gridPosition: number | null
  scoredCount: number
}

const props = defineProps<Props>()

const { t } = useI18n()

// Computed: formatted HOW score
const formattedScore = computed(() => {
  if (props.howScore === null) return '-'
  return props.howScore.toFixed(2)
})

// Computed: formatted grid position
const formattedGridPosition = computed(() => {
  if (props.gridPosition === null) return '-'
  return props.gridPosition.toString()
})

// Computed: grid position label
const gridPositionLabel = computed(() => {
  if (props.gridPosition === null) return ''
  return t(`scoring.gridLabels.how.${props.gridPosition}`)
})

// Computed: is scoring complete
const isComplete = computed(() => props.scoredCount >= 6)

// Computed: progress text
const progressText = computed(() => {
  return t('competencies.scoreComplete', { count: props.scoredCount })
})
</script>

<template>
  <div
    class="how-score-indicator"
    :class="{ 'is-incomplete': !isComplete }"
    aria-label="HOW Score Indicator"
  >
    <!-- VETO Warning Banner -->
    <div v-if="vetoActive" class="veto-banner">
      <span class="veto-icon">⚠️</span>
      <span class="veto-text">{{ t('competencies.veto') }}</span>
      <span class="veto-message">{{ t('competencies.vetoWarning') }}</span>
    </div>

    <!-- Score Card -->
    <div class="score-card">
      <!-- HOW Score -->
      <div class="score-section">
        <span class="score-label">{{ t('competencies.howScoreLabel') }}</span>
        <span
          class="how-score-value"
          :class="{ 'is-veto': vetoActive }"
        >
          {{ formattedScore }}
        </span>
      </div>

      <!-- Grid Position -->
      <div class="score-section">
        <span class="score-label">{{ t('scoring.gridPosition') }}</span>
        <div class="grid-position">
          <span class="grid-position-value">{{ formattedGridPosition }}</span>
          <span v-if="gridPosition !== null" class="grid-position-label">
            {{ gridPositionLabel }}
          </span>
        </div>
      </div>

      <!-- Progress Indicator -->
      <div class="progress-indicator">
        <span class="progress-text">{{ progressText }}</span>
        <div class="progress-bar">
          <div
            class="progress-fill"
            :style="{ width: `${(scoredCount / 6) * 100}%` }"
          />
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.how-score-indicator {
  padding: 1rem;
  border-radius: 8px;
  background: var(--color-white, #ffffff);
  border: 1px solid var(--color-gray-200);
}

.how-score-indicator.is-incomplete {
  border-color: var(--color-gray-300);
  background: var(--color-gray-50, #f9fafb);
}

.veto-banner {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.75rem;
  margin-bottom: 1rem;
  border-radius: 6px;
  background: #FEF2F2;
  border: 1px solid var(--color-grid-red, #dc2626);
  color: #991B1B;
}

.veto-icon {
  font-size: 1.25rem;
}

.veto-text {
  font-weight: 700;
  text-transform: uppercase;
  font-size: 0.875rem;
}

.veto-message {
  font-size: 0.8rem;
  opacity: 0.8;
}

.score-card {
  display: flex;
  flex-wrap: wrap;
  gap: 1.5rem;
  align-items: flex-start;
}

.score-section {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.score-label {
  font-size: 0.75rem;
  font-weight: 500;
  color: var(--color-gray-600);
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.how-score-value {
  font-size: 2rem;
  font-weight: 700;
  color: var(--color-navy, #004A91);
  font-family: 'Tahoma', sans-serif;
}

.how-score-value.is-veto {
  color: var(--color-grid-red, #dc2626);
}

.grid-position {
  display: flex;
  align-items: baseline;
  gap: 0.5rem;
}

.grid-position-value {
  font-size: 2rem;
  font-weight: 700;
  color: var(--color-magenta, #CC0E70);
  font-family: 'Tahoma', sans-serif;
}

.grid-position-label {
  font-size: 0.875rem;
  color: var(--color-gray-600);
}

.progress-indicator {
  flex: 1;
  min-width: 150px;
}

.progress-text {
  font-size: 0.8rem;
  color: var(--color-gray-600);
  display: block;
  margin-bottom: 0.5rem;
}

.progress-bar {
  height: 8px;
  background: var(--color-gray-200);
  border-radius: 4px;
  overflow: hidden;
}

.progress-fill {
  height: 100%;
  background: var(--color-magenta, #CC0E70);
  border-radius: 4px;
  transition: width 0.3s ease;
}

.is-incomplete .how-score-value {
  color: var(--color-gray-400);
}

.is-incomplete .grid-position-value {
  color: var(--color-gray-400);
}
</style>
