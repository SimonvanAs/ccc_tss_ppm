<script setup lang="ts">
import { computed } from 'vue'

interface Props {
  modelValue?: number | null
  labels?: Record<number, string>
  disabled?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  modelValue: null,
  labels: () => ({}),
  disabled: false,
})

const emit = defineEmits<{
  (e: 'update:modelValue', value: number): void
  (e: 'change', value: number): void
}>()

const scores = [1, 2, 3] as const

function selectScore(score: number) {
  if (props.disabled) return
  emit('update:modelValue', score)
  emit('change', score)
}

function handleKeydown(score: number) {
  selectScore(score)
}
</script>

<template>
  <div
    class="score-card"
    :class="{ disabled }"
    role="radiogroup"
  >
    <div
      v-for="score in scores"
      :key="score"
      class="score-option"
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
  </div>
</template>

<style scoped>
.score-card {
  display: flex;
  gap: 0.75rem;
}

.score-card.disabled {
  opacity: 0.6;
  pointer-events: none;
}

.score-option {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 1rem;
  width: 90px;
  min-height: 70px;
  border: 2px solid var(--color-gray-200);
  border-radius: 8px;
  background: var(--color-white);
  cursor: pointer;
  transition: all 0.2s ease;
  box-sizing: border-box;
}

.score-option:hover:not(.selected) {
  border-color: var(--color-magenta);
  background: var(--color-gray-100);
}

.score-option:focus {
  outline: 2px solid var(--color-magenta);
  outline-offset: 2px;
}

/* Selected state - magenta for all scores */
.score-option.selected {
  border-color: var(--color-magenta);
  background: rgba(204, 14, 112, 0.08);
}

.score-number {
  font-size: 1.5rem;
  font-weight: bold;
  color: var(--color-gray-900);
}

.score-option.selected .score-number {
  color: var(--color-magenta);
}

.score-label {
  font-size: 0.75rem;
  color: var(--color-gray-600);
  text-align: center;
  margin-top: 0.25rem;
  max-width: 80px;
}

.score-option.selected .score-label {
  color: var(--color-magenta);
}
</style>
