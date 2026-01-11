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
  min-width: 80px;
  border: 2px solid var(--color-gray-200);
  border-radius: 8px;
  background: var(--color-white);
  cursor: pointer;
  transition: all 0.2s ease;
}

.score-option:hover:not(.selected) {
  border-color: var(--color-navy);
  background: var(--color-gray-100);
}

.score-option:focus {
  outline: 2px solid var(--color-navy);
  outline-offset: 2px;
}

.score-option.selected {
  border-width: 3px;
}

.score-option.score-1 {
  border-color: var(--color-gray-200);
}

.score-option.score-1.selected {
  border-color: var(--color-grid-red);
  background: #FEF2F2;
}

.score-option.score-2 {
  border-color: var(--color-gray-200);
}

.score-option.score-2.selected {
  border-color: var(--color-grid-orange);
  background: #FFFBEB;
}

.score-option.score-3 {
  border-color: var(--color-gray-200);
}

.score-option.score-3.selected {
  border-color: var(--color-grid-green);
  background: #F0FDF4;
}

.score-number {
  font-size: 1.5rem;
  font-weight: bold;
  color: var(--color-gray-900);
}

.score-option.score-1.selected .score-number {
  color: var(--color-grid-red);
}

.score-option.score-2.selected .score-number {
  color: var(--color-grid-orange);
}

.score-option.score-3.selected .score-number {
  color: var(--color-grid-green);
}

.score-label {
  font-size: 0.75rem;
  color: var(--color-gray-600);
  text-align: center;
  margin-top: 0.25rem;
  max-width: 100px;
}
</style>
