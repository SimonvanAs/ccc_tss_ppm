<script setup lang="ts">
import ScoreCard from './ScoreCard.vue'
import VoiceInput from '../common/VoiceInput.vue'

export interface Goal {
  id: string
  title: string
  description?: string
  weight: number
  goal_type: 'STANDARD' | 'KAR' | 'SCF'
}

export interface GoalScore {
  score: number | null
  feedback?: string
}

interface Props {
  goals: Goal[]
  scores: Record<string, GoalScore>
  disabled?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  disabled: false,
})

const emit = defineEmits<{
  (e: 'score-change', goalId: string, score: number): void
  (e: 'feedback-change', goalId: string, feedback: string): void
}>()

function getGoalScore(goalId: string): number | null {
  return props.scores[goalId]?.score ?? null
}

function getGoalFeedback(goalId: string): string {
  return props.scores[goalId]?.feedback ?? ''
}

function handleScoreChange(goalId: string, score: number) {
  emit('score-change', goalId, score)
}

function handleFeedbackChange(goalId: string, event: Event) {
  const value = (event.target as HTMLTextAreaElement).value
  emit('feedback-change', goalId, value)
}

function handleVoiceTranscription(goalId: string, transcription: string) {
  const currentFeedback = getGoalFeedback(goalId)
  const newFeedback = currentFeedback + transcription
  emit('feedback-change', goalId, newFeedback)
}

const scoreLabels = {
  1: 'Does not meet',
  2: 'Meets',
  3: 'Exceeds',
}
</script>

<template>
  <div class="goal-scoring-section">
    <h2 class="section-title">Goals (WHAT)</h2>

    <div v-if="goals.length === 0" class="empty-state">
      No goals defined for this review.
    </div>

    <div v-else class="goal-list">
      <div
        v-for="goal in goals"
        :key="goal.id"
        :data-goal-id="goal.id"
        class="goal-item"
      >
        <div class="goal-header">
          <div class="goal-info">
            <h3 class="goal-title">{{ goal.title }}</h3>
            <span class="goal-weight">{{ goal.weight }}%</span>
            <span
              v-if="goal.goal_type !== 'STANDARD'"
              class="goal-type-badge"
              :class="goal.goal_type.toLowerCase()"
            >
              {{ goal.goal_type }}
            </span>
          </div>
          <p v-if="goal.description" class="goal-description">
            {{ goal.description }}
          </p>
        </div>

        <div class="goal-scoring">
          <ScoreCard
            :model-value="getGoalScore(goal.id)"
            :labels="scoreLabels"
            :disabled="disabled"
            @update:model-value="handleScoreChange(goal.id, $event)"
          />
        </div>

        <div class="goal-feedback">
          <label :for="`feedback-${goal.id}`" class="feedback-label">
            Manager Feedback
          </label>
          <div class="feedback-input-wrapper">
            <textarea
              :id="`feedback-${goal.id}`"
              :value="getGoalFeedback(goal.id)"
              :disabled="disabled"
              placeholder="Enter feedback for this goal..."
              rows="3"
              @input="handleFeedbackChange(goal.id, $event)"
            />
            <VoiceInput
              v-if="!disabled"
              @transcription="handleVoiceTranscription(goal.id, $event)"
            />
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.goal-scoring-section {
  margin-bottom: 2rem;
}

.section-title {
  font-size: 1.25rem;
  font-weight: 600;
  color: var(--color-navy);
  margin-bottom: 1rem;
  padding-bottom: 0.5rem;
  border-bottom: 2px solid var(--color-navy);
}

.empty-state {
  padding: 2rem;
  text-align: center;
  color: var(--color-gray-600);
  background: var(--color-gray-100);
  border-radius: 8px;
}

.goal-list {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.goal-item {
  background: var(--color-white);
  border: 1px solid var(--color-gray-200);
  border-radius: 8px;
  padding: 1.5rem;
}

.goal-header {
  margin-bottom: 1rem;
}

.goal-info {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  flex-wrap: wrap;
}

.goal-title {
  font-size: 1rem;
  font-weight: 600;
  margin: 0;
  color: var(--color-gray-900);
}

.goal-weight {
  font-size: 0.875rem;
  font-weight: 500;
  color: var(--color-gray-600);
  background: var(--color-gray-100);
  padding: 0.125rem 0.5rem;
  border-radius: 4px;
}

.goal-type-badge {
  font-size: 0.625rem;
  font-weight: 700;
  text-transform: uppercase;
  padding: 0.125rem 0.5rem;
  border-radius: 4px;
  letter-spacing: 0.05em;
}

.goal-type-badge.kar {
  background: #FEF3C7;
  color: #92400E;
}

.goal-type-badge.scf {
  background: #FEE2E2;
  color: #991B1B;
}

.goal-description {
  margin: 0.5rem 0 0;
  font-size: 0.875rem;
  color: var(--color-gray-600);
}

.goal-scoring {
  margin-bottom: 1rem;
}

.goal-feedback {
  border-top: 1px solid var(--color-gray-200);
  padding-top: 1rem;
}

.feedback-label {
  display: block;
  font-size: 0.875rem;
  font-weight: 500;
  color: var(--color-gray-600);
  margin-bottom: 0.5rem;
}

.feedback-input-wrapper {
  display: flex;
  gap: 0.5rem;
  align-items: flex-start;
}

.feedback-input-wrapper textarea {
  flex: 1;
  padding: 0.75rem;
  border: 1px solid var(--color-gray-200);
  border-radius: 4px;
  font-family: inherit;
  font-size: 0.875rem;
  resize: vertical;
  min-height: 80px;
}

.feedback-input-wrapper textarea:focus {
  outline: none;
  border-color: var(--color-navy);
  box-shadow: 0 0 0 2px rgba(0, 74, 145, 0.1);
}

.feedback-input-wrapper textarea:disabled {
  background: var(--color-gray-100);
  cursor: not-allowed;
}

/* Responsive styles */
@media (max-width: 768px) {
  .goal-item {
    padding: 1rem;
  }

  .goal-title {
    font-size: 0.9375rem;
  }

  .goal-scoring {
    display: flex;
    justify-content: center;
  }

  .feedback-input-wrapper {
    flex-direction: column;
  }

  .feedback-input-wrapper textarea {
    width: 100%;
  }
}

@media (max-width: 480px) {
  .section-title {
    font-size: 1.125rem;
  }

  .goal-list {
    gap: 1rem;
  }

  .goal-item {
    padding: 0.75rem;
  }

  .goal-info {
    flex-direction: column;
    align-items: flex-start;
    gap: 0.5rem;
  }

  .goal-description {
    font-size: 0.8125rem;
  }
}
</style>
