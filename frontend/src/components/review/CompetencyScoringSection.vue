<script setup lang="ts">
// TSS PPM v3.0 - CompetencyScoringSection Integration Component
// Integrates CompetencyList, HOWScoreIndicator, and useCompetencyScoring

import { ref, watch, onMounted, onUnmounted, computed } from 'vue'
import { useI18n } from 'vue-i18n'
import { useCompetencyScoring } from '../../composables/useCompetencyScoring'
import CompetencyList from './CompetencyList.vue'
import type { TovLevel } from '../../types/competency'

interface Props {
  reviewId: string
  tovLevel: TovLevel
  initialScores?: Record<string, number>
  initialNotes?: Record<string, string>
  disabled?: boolean
  previewMode?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  initialScores: () => ({}),
  initialNotes: () => ({}),
  disabled: false,
  previewMode: false,
})

const emit = defineEmits<{
  (e: 'score-change', payload: { competencyId: string; score: number }): void
  (e: 'notes-change', payload: { competencyId: string; notes: string }): void
  (e: 'score-save', payload: { scores: { competency_id: string; score: number }[]; notes: Record<string, string> }): void
  (e: 'how-score-change', payload: { howScore: number | null; gridPosition: number | null; vetoActive: boolean }): void
}>()

const { t } = useI18n()

// Composable for HOW score calculation
const {
  scores,
  scoredCount,
  isComplete,
  vetoActive,
  vetoCompetencyId,
  howScore,
  gridPosition,
  setScore,
  initializeScores,
  getScoresArray,
} = useCompetencyScoring()

// Local notes state
const localNotes = ref<Record<string, string>>({})

// Auto-save debounce timer
let saveTimer: ReturnType<typeof setTimeout> | null = null
const DEBOUNCE_MS = 1000

// Level descriptions
const levelDescriptions: Record<TovLevel, string> = {
  A: 'Entry level - Learns and applies basic skills under guidance',
  B: 'Professional level - Sets ambitious goals independently and proactively adds value',
  C: 'Senior level - Leads and coaches others while driving strategic initiatives',
  D: 'Leadership level - Shapes organization direction and develops talent',
}

const levelDescription = computed(() => levelDescriptions[props.tovLevel] || '')

// Initialize from props
onMounted(() => {
  if (props.initialScores && Object.keys(props.initialScores).length > 0) {
    const scoreArray = Object.entries(props.initialScores).map(([id, score]) => ({
      id,
      score,
    }))
    initializeScores(scoreArray)
  }

  if (props.initialNotes) {
    localNotes.value = { ...props.initialNotes }
  }
})

// Cleanup on unmount
onUnmounted(() => {
  if (saveTimer) {
    clearTimeout(saveTimer)
  }
})

// Watch for HOW score changes and emit to parent
watch(
  [howScore, gridPosition, vetoActive],
  ([newHowScore, newGridPosition, newVetoActive]) => {
    emit('how-score-change', {
      howScore: newHowScore,
      gridPosition: newGridPosition,
      vetoActive: newVetoActive,
    })
  }
)

// Handle score change from CompetencyList
function handleScoreChange(payload: { competencyId: string; score: number }) {
  setScore(payload.competencyId, payload.score)
  emit('score-change', payload)
  scheduleSave()
}

// Handle notes change from CompetencyList
function handleNotesChange(payload: { competencyId: string; notes: string }) {
  localNotes.value[payload.competencyId] = payload.notes
  emit('notes-change', payload)
  scheduleSave()
}

// Debounced auto-save
function scheduleSave() {
  if (saveTimer) {
    clearTimeout(saveTimer)
  }

  saveTimer = setTimeout(() => {
    emit('score-save', {
      scores: getScoresArray(),
      notes: localNotes.value,
    })
  }, DEBOUNCE_MS)
}

// Convert scores Map to Record for CompetencyList
function getScoresRecord(): Record<string, number> {
  const record: Record<string, number> = {}
  for (const [id, score] of scores.value.entries()) {
    record[id] = score
  }
  return record
}
</script>

<template>
  <div class="competency-scoring-section">
    <!-- Section Header -->
    <div class="section-header">
      <h2 class="section-title">{{ t('competencies.howAxisTitle') }}</h2>
      <div class="section-divider"></div>
    </div>

    <!-- Selected Level Indicator -->
    <div class="level-indicator">
      <span class="level-label">{{ t('competencies.selectedLevel') }}:</span>
      <span class="level-badge">{{ tovLevel }}</span>
      <span class="level-description">{{ levelDescription }}</span>
    </div>

    <!-- VETO Warning Banner (hidden in preview mode) -->
    <div v-if="!previewMode" class="veto-warning-banner">
      <span class="warning-icon">⚠</span>
      <span>{{ t('competencies.vetoWarning') }}</span>
    </div>

    <!-- Competency List -->
    <CompetencyList
      :tov-level="tovLevel"
      :scores="getScoresRecord()"
      :notes="localNotes"
      :disabled="disabled"
      :preview-mode="previewMode"
      @score-change="handleScoreChange"
      @notes-change="handleNotesChange"
    />
  </div>
</template>

<style scoped>
.competency-scoring-section {
  background-color: var(--color-white, #ffffff);
  border-radius: 8px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1), 0 1px 2px rgba(0, 0, 0, 0.06);
  padding: 1.5rem;
  margin-bottom: 1.5rem;
}

.section-header {
  margin-bottom: 1.5rem;
}

.section-title {
  font-size: 1.125rem;
  font-weight: 700;
  color: var(--color-magenta, #CC0E70);
  margin: 0 0 0.75rem 0;
}

.section-divider {
  height: 2px;
  background-color: var(--color-magenta, #CC0E70);
}

.level-indicator {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 1rem;
  background-color: var(--color-gray-50, #f9fafb);
  border-radius: 8px;
  border-left: 4px solid var(--color-navy, #004A91);
  margin-bottom: 1rem;
}

.level-label {
  font-size: 0.875rem;
  color: var(--color-gray-600, #6b7280);
}

.level-badge {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 32px;
  height: 32px;
  font-size: 1rem;
  font-weight: 700;
  color: var(--color-navy, #004A91);
  background-color: var(--color-white, #ffffff);
  border: 2px solid var(--color-navy, #004A91);
  border-radius: 50%;
}

.level-description {
  flex: 1;
  font-size: 0.875rem;
  color: var(--color-gray-700, #374151);
}

.veto-warning-banner {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.875rem 1rem;
  background-color: #FEF3C7;
  border-radius: 8px;
  border-left: 4px solid #F59E0B;
  margin-bottom: 1.5rem;
  font-size: 0.875rem;
  color: #92400E;
}

.warning-icon {
  font-size: 1.125rem;
}

/* Responsive styles */
@media (max-width: 640px) {
  .level-indicator {
    flex-wrap: wrap;
  }

  .level-description {
    flex-basis: 100%;
    margin-top: 0.5rem;
  }
}
</style>
