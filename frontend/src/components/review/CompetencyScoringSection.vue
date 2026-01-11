<script setup lang="ts">
// TSS PPM v3.0 - CompetencyScoringSection Integration Component
// Integrates CompetencyList, HOWScoreIndicator, and useCompetencyScoring

import { ref, watch, onMounted, onUnmounted } from 'vue'
import { useI18n } from 'vue-i18n'
import { useCompetencyScoring } from '../../composables/useCompetencyScoring'
import CompetencyList from './CompetencyList.vue'
import HOWScoreIndicator from './HOWScoreIndicator.vue'
import type { TovLevel } from '../../types/competency'

interface Props {
  reviewId: string
  tovLevel: TovLevel
  initialScores?: Record<string, number>
  initialNotes?: Record<string, string>
  disabled?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  initialScores: () => ({}),
  initialNotes: () => ({}),
  disabled: false,
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
    <!-- Header with HOW Score Indicator -->
    <div class="section-header">
      <h2 class="section-title">{{ t('competencies.how') }}</h2>

      <HOWScoreIndicator
        :how-score="howScore"
        :veto-active="vetoActive"
        :veto-competency-id="vetoCompetencyId"
        :grid-position="gridPosition"
        :scored-count="scoredCount"
      />
    </div>

    <!-- Competency List -->
    <CompetencyList
      :tov-level="tovLevel"
      :scores="getScoresRecord()"
      :notes="localNotes"
      :disabled="disabled"
      @score-change="handleScoreChange"
      @notes-change="handleNotesChange"
    />
  </div>
</template>

<style scoped>
.competency-scoring-section {
  margin-bottom: 2rem;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 2rem;
  margin-bottom: 1.5rem;
  flex-wrap: wrap;
}

.section-title {
  font-size: 1.25rem;
  font-weight: 600;
  color: var(--color-navy, #004A91);
  margin: 0;
}
</style>
