<script setup lang="ts">
import { computed, ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useScoring } from '../composables/useScoring'
import { submitScores as submitScoresApi } from '../api/scores'
import { calculateWhatScore, calculateHowScore } from '../services/scoring'
import GoalScoringSection from '../components/review/GoalScoringSection.vue'
import CompetencyScoringSection from '../components/review/CompetencyScoringSection.vue'
import NineGrid from '../components/review/NineGrid.vue'
import ScoreSummary from '../components/review/ScoreSummary.vue'
import SaveIndicator from '../components/common/SaveIndicator.vue'
import SubmitScoresButton from '../components/review/SubmitScoresButton.vue'
import { Card, SectionHeader } from '../components/layout'
import type { Goal } from '../components/review/GoalScoringSection.vue'
import type { Competency } from '../components/review/CompetencyScoringSection.vue'

interface Props {
  goals: Goal[]
  competencies: Competency[]
  readOnly?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  readOnly: false,
})

const route = useRoute()
const router = useRouter()
const reviewId = computed(() => route.params.reviewId as string)

// Submit state
const isSubmitting = ref(false)
const submitError = ref<string | null>(null)

const {
  goalScores,
  competencyScores,
  saveStatus,
  isLoading,
  loadError,
  allScoresComplete,
  setGoalScore,
  setGoalFeedback,
  setCompetencyScore,
  setRequiredGoals,
  setRequiredCompetencies,
  loadScores,
} = useScoring(reviewId.value)

// Calculate WHAT score from goals
const whatScoreResult = computed(() => {
  const goalScoreData = props.goals.map((g) => ({
    id: g.id,
    score: goalScores.value[g.id]?.score ?? 0,
    weight: g.weight,
    goalType: g.goal_type,
  }))

  // Only calculate if all goals have scores
  const allScored = goalScoreData.every((g) => g.score > 0)
  if (!allScored) return null

  return calculateWhatScore(goalScoreData)
})

// Calculate HOW score from competencies
const howScoreResult = computed(() => {
  const compScoreData = props.competencies.map((c) => ({
    id: c.id,
    score: competencyScores.value[c.id]?.score ?? 0,
  }))

  // Only calculate if all competencies have scores
  const allScored = compScoreData.every((c) => c.score > 0)
  if (!allScored) return null

  return calculateHowScore(compScoreData)
})

const whatScore = computed(() => whatScoreResult.value?.score ?? null)
const howScore = computed(() => howScoreResult.value?.score ?? null)
const whatVetoActive = computed(() => whatScoreResult.value?.vetoActive ?? false)
const whatVetoType = computed(() => whatScoreResult.value?.vetoReason ?? null)
const howVetoActive = computed(() => howScoreResult.value?.vetoActive ?? false)

// Event handlers
function handleGoalScoreChange(goalId: string, score: number) {
  setGoalScore(goalId, score)
}

function handleGoalFeedbackChange(goalId: string, feedback: string) {
  setGoalFeedback(goalId, feedback)
}

function handleCompetencyScoreChange(compId: string, score: number) {
  setCompetencyScore(compId, score)
}

async function handleSubmit() {
  if (isSubmitting.value) return

  isSubmitting.value = true
  submitError.value = null

  try {
    await submitScoresApi(reviewId.value)
    // Redirect to team dashboard on success
    router.push('/team')
  } catch (error) {
    submitError.value = error instanceof Error ? error.message : 'Submission failed'
  } finally {
    isSubmitting.value = false
  }
}

// Initialize
onMounted(async () => {
  setRequiredGoals(props.goals.map((g) => g.id))
  setRequiredCompetencies(props.competencies.map((c) => c.id))
  await loadScores()
})
</script>

<template>
  <div class="review-scoring-view">
    <!-- Page Header -->
    <SectionHeader title="Score Review">
      <template #actions>
        <SaveIndicator :status="saveStatus" />
      </template>
    </SectionHeader>

    <!-- Loading state -->
    <Card v-if="isLoading" class="state-card">
      <div class="loading-state">
        Loading scores...
      </div>
    </Card>

    <!-- Error state -->
    <Card v-else-if="loadError" class="state-card">
      <div class="error-state">
        {{ loadError }}
      </div>
    </Card>

    <div v-else class="scoring-layout">
      <main class="scoring-main">
        <GoalScoringSection
          :goals="goals"
          :scores="goalScores"
          :disabled="readOnly"
          @score-change="handleGoalScoreChange"
          @feedback-change="handleGoalFeedbackChange"
        />

        <CompetencyScoringSection
          :competencies="competencies"
          :scores="competencyScores"
          :disabled="readOnly"
          @score-change="handleCompetencyScoreChange"
        />

        <Card v-if="!readOnly" class="submit-card">
          <div class="submit-section">
            <SubmitScoresButton
              :all-scores-complete="allScoresComplete"
              :is-submitting="isSubmitting"
              :has-error="!!submitError"
              :error-message="submitError || ''"
              @submit="handleSubmit"
            />
          </div>
        </Card>
      </main>

      <aside class="scoring-sidebar">
        <Card class="sidebar-card" padding="md">
          <h3 class="sidebar-title">Performance Grid</h3>
          <NineGrid
            :what-score="whatScore"
            :how-score="howScore"
            :veto-active="whatVetoActive || howVetoActive"
            :veto-type="whatVetoType"
            compact
          />
        </Card>

        <Card class="sidebar-card" padding="md">
          <h3 class="sidebar-title">Score Summary</h3>
          <ScoreSummary
            :what-score="whatScore"
            :how-score="howScore"
            :what-veto-active="whatVetoActive"
            :what-veto-type="whatVetoType"
            :how-veto-active="howVetoActive"
            compact
          />
        </Card>
      </aside>
    </div>
  </div>
</template>

<style scoped>
.review-scoring-view {
  max-width: 1400px;
  margin: 0 auto;
}

.state-card {
  margin-top: 1rem;
}

.loading-state {
  text-align: center;
  padding: 2rem;
  color: var(--color-gray-600);
}

.error-state {
  text-align: center;
  padding: 2rem;
  color: var(--color-error);
}

.scoring-layout {
  display: grid;
  grid-template-columns: 1fr 280px;
  gap: 1.5rem;
  margin-top: 1rem;
}

@media (max-width: 1024px) {
  .scoring-layout {
    grid-template-columns: 1fr;
  }

  .scoring-sidebar {
    order: -1;
    display: flex;
    gap: 1rem;
  }

  .sidebar-card {
    flex: 1;
  }
}

@media (max-width: 768px) {
  .scoring-sidebar {
    flex-direction: column;
  }

  .sidebar-card {
    flex: none;
  }

  .scoring-main {
    gap: 1.5rem;
  }

  .submit-section {
    justify-content: center;
  }
}

@media (max-width: 480px) {
  .scoring-layout {
    gap: 1rem;
  }
}

.scoring-main {
  display: flex;
  flex-direction: column;
  gap: 2rem;
}

.submit-card {
  margin-top: 1rem;
}

.submit-section {
  display: flex;
  justify-content: flex-end;
}

.scoring-sidebar {
  display: flex;
  flex-direction: column;
  gap: 1rem;
  position: sticky;
  top: 1rem;
  align-self: start;
}

.sidebar-title {
  font-size: 0.875rem;
  font-weight: 600;
  color: var(--color-gray-600);
  margin: 0 0 1rem;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}
</style>
