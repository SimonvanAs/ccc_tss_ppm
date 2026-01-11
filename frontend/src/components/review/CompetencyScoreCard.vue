<script setup lang="ts">
// TSS PPM v3.0 - CompetencyScoreCard Component
// Score card for individual competency with magenta brand styling

interface Props {
  competencyId: string
  modelValue?: number | null
  labels?: Record<number, string>
  disabled?: boolean
  showVetoWarning?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  modelValue: null,
  labels: () => ({}),
  disabled: false,
  showVetoWarning: false,
})

const emit = defineEmits<{
  (e: 'update:modelValue', value: number): void
  (e: 'score-change', payload: { competencyId: string; score: number }): void
}>()

const scores = [1, 2, 3] as const

function selectScore(score: number) {
  if (props.disabled) return
  emit('update:modelValue', score)
  emit('score-change', { competencyId: props.competencyId, score })
}

function handleKeydown(score: number) {
  selectScore(score)
}

// Show VETO indicator when score is 1 and showVetoWarning is enabled
const showVeto = computed(() => props.showVetoWarning && props.modelValue === 1)
</script>

<script lang="ts">
import { computed } from 'vue'
</script>

<template>
  <div
    class="competency-score-card"
    :class="{ disabled }"
    role="radiogroup"
    aria-label="Competency score selection"
  >
    <div
      v-for="score in scores"
      :key="score"
      class="score-button"
      :class="[
        `score-${score}`,
        { selected: modelValue === score }
      ]"
      role="radio"
      :aria-checked="modelValue === score"
      tabindex="0"
      @click="selectScore(score)"
      @keydown.enter.prevent="handleKeydown(score)"
      @keydown.space.prevent="handleKeydown(score)"
    >
      <span class="score-number">{{ score }}</span>
      <span v-if="labels[score]" class="score-label">{{ labels[score] }}</span>
    </div>
    <div v-if="showVeto" class="veto-indicator">
      VETO
    </div>
  </div>
</template>

<style scoped>
.competency-score-card {
  display: flex;
  gap: 0.5rem;
  align-items: center;
}

.competency-score-card.disabled {
  opacity: 0.6;
  pointer-events: none;
}

.score-button {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 0.75rem 1rem;
  min-width: 60px;
  border: 2px solid var(--color-gray-200, #e5e7eb);
  border-radius: 8px;
  background: var(--color-white, #ffffff);
  cursor: pointer;
  transition: all 0.2s ease;
}

.score-button:hover:not(.selected) {
  border-color: var(--color-magenta, #CC0E70);
  background: var(--color-gray-100, #f3f4f6);
}

.score-button:focus {
  outline: 2px solid var(--color-magenta, #CC0E70);
  outline-offset: 2px;
}

.score-button.selected {
  border-width: 3px;
  border-color: var(--color-magenta, #CC0E70);
  background: #FDF2F7;
}

/* Score 1 (VETO potential) - use red for danger */
.score-button.score-1.selected {
  border-color: var(--color-grid-red, #dc2626);
  background: #FEF2F2;
}

.score-number {
  font-size: 1.25rem;
  font-weight: bold;
  color: var(--color-gray-900, #111827);
}

.score-button.selected .score-number {
  color: var(--color-magenta, #CC0E70);
}

.score-button.score-1.selected .score-number {
  color: var(--color-grid-red, #dc2626);
}

.score-label {
  font-size: 0.7rem;
  color: var(--color-gray-600, #4b5563);
  text-align: center;
  margin-top: 0.25rem;
  max-width: 80px;
}

.veto-indicator {
  display: inline-flex;
  align-items: center;
  padding: 0.25rem 0.5rem;
  margin-left: 0.5rem;
  font-size: 0.7rem;
  font-weight: bold;
  color: var(--color-white, #ffffff);
  background: var(--color-grid-red, #dc2626);
  border-radius: 4px;
  text-transform: uppercase;
}
</style>
