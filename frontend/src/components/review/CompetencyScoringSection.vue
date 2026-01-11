<script setup lang="ts">
import { computed } from 'vue'
import ScoreCard from './ScoreCard.vue'

export interface Competency {
  id: string
  name: string
  description?: string
  category: string
}

export interface CompetencyScore {
  score: number | null
}

interface Props {
  competencies: Competency[]
  scores: Record<string, CompetencyScore>
  disabled?: boolean
  compact?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  disabled: false,
  compact: false,
})

const emit = defineEmits<{
  (e: 'score-change', competencyId: string, score: number): void
}>()

// Group competencies by category
const groupedCompetencies = computed(() => {
  const groups: Record<string, Competency[]> = {}

  for (const comp of props.competencies) {
    if (!groups[comp.category]) {
      groups[comp.category] = []
    }
    groups[comp.category].push(comp)
  }

  return groups
})

const categories = computed(() => Object.keys(groupedCompetencies.value))

function getCompetencyScore(compId: string): number | null {
  return props.scores[compId]?.score ?? null
}

function handleScoreChange(compId: string, score: number) {
  emit('score-change', compId, score)
}

const scoreLabels = {
  1: 'Below',
  2: 'Meets',
  3: 'Exceeds',
}
</script>

<template>
  <div class="competency-scoring-section" :class="{ compact }">
    <h2 class="section-title">Competencies (HOW)</h2>

    <div v-if="competencies.length === 0" class="empty-state">
      No competencies defined for this review.
    </div>

    <div v-else class="category-list">
      <div
        v-for="category in categories"
        :key="category"
        class="category-group"
      >
        <h3 class="category-title">{{ category }}</h3>

        <div class="competency-list">
          <div
            v-for="comp in groupedCompetencies[category]"
            :key="comp.id"
            :data-competency-id="comp.id"
            class="competency-item"
          >
            <div class="competency-info">
              <h4 class="competency-name">{{ comp.name }}</h4>
              <p v-if="comp.description && !compact" class="competency-description">
                {{ comp.description }}
              </p>
            </div>

            <div class="competency-scoring">
              <ScoreCard
                :model-value="getCompetencyScore(comp.id)"
                :labels="compact ? {} : scoreLabels"
                :disabled="disabled"
                @update:model-value="handleScoreChange(comp.id, $event)"
              />
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.competency-scoring-section {
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

.category-list {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.category-group {
  background: var(--color-white);
  border: 1px solid var(--color-gray-200);
  border-radius: 8px;
  padding: 1rem;
}

.category-title {
  font-size: 1rem;
  font-weight: 600;
  color: var(--color-magenta);
  margin: 0 0 1rem;
  padding-bottom: 0.5rem;
  border-bottom: 1px solid var(--color-gray-200);
}

.competency-list {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.competency-item {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 1rem;
  padding: 0.75rem;
  background: var(--color-gray-100);
  border-radius: 4px;
}

.competency-info {
  flex: 1;
}

.competency-name {
  font-size: 0.875rem;
  font-weight: 600;
  margin: 0;
  color: var(--color-gray-900);
}

.competency-description {
  font-size: 0.75rem;
  color: var(--color-gray-600);
  margin: 0.25rem 0 0;
}

.competency-scoring {
  flex-shrink: 0;
}

/* Compact mode */
.compact .category-group {
  padding: 0.75rem;
}

.compact .category-title {
  font-size: 0.875rem;
  margin-bottom: 0.75rem;
}

.compact .competency-list {
  gap: 0.5rem;
}

.compact .competency-item {
  padding: 0.5rem;
  flex-direction: column;
  align-items: stretch;
  gap: 0.5rem;
}

.compact .competency-name {
  font-size: 0.75rem;
}

.compact .competency-scoring {
  display: flex;
  justify-content: center;
}
</style>
