<script setup lang="ts">
// TSS PPM v3.0 - CompetencyList Component
// Displays 6 competencies grouped by category for scoring

import { ref, computed, watch, onMounted } from 'vue'
import { useI18n } from 'vue-i18n'
import { getCompetencies } from '../../api/competencies'
import type { Competency, TovLevel } from '../../types/competency'

interface Props {
  tovLevel: TovLevel
  scores?: Record<string, number>
  notes?: Record<string, string>
  disabled?: boolean
  previewMode?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  scores: () => ({}),
  notes: () => ({}),
  disabled: false,
  previewMode: false,
})

const emit = defineEmits<{
  (e: 'score-change', payload: { competencyId: string; score: number }): void
  (e: 'notes-change', payload: { competencyId: string; notes: string }): void
}>()

const { t, locale } = useI18n()

// State
const competencies = ref<Competency[]>([])
const loading = ref(true)
const expandedIndicators = ref<Set<string>>(new Set())
const localNotes = ref<Record<string, string>>({})

// Fetch competencies with current locale
async function fetchCompetencies() {
  loading.value = true
  try {
    competencies.value = await getCompetencies(props.tovLevel, locale.value)
    // In preview mode, expand all indicators by default
    if (props.previewMode) {
      expandedIndicators.value = new Set(competencies.value.map((c) => c.id))
    }
  } catch (error) {
    console.error('Failed to fetch competencies:', error)
    competencies.value = []
  } finally {
    loading.value = false
  }
}

// Watch for tovLevel or locale changes
watch(
  [() => props.tovLevel, locale],
  () => {
    fetchCompetencies()
  }
)

// Initialize notes from props
watch(
  () => props.notes,
  (newNotes) => {
    localNotes.value = { ...newNotes }
  },
  { immediate: true }
)

onMounted(() => {
  fetchCompetencies()
})

// Get competency title based on locale
function getTitle(comp: Competency): string {
  const lang = locale.value
  if (lang === 'nl' && comp.title_nl) return comp.title_nl
  if (lang === 'es' && comp.title_es) return comp.title_es
  return comp.title_en
}

// Toggle indicators visibility
function toggleIndicators(competencyId: string) {
  if (expandedIndicators.value.has(competencyId)) {
    expandedIndicators.value.delete(competencyId)
  } else {
    expandedIndicators.value.add(competencyId)
  }
  // Trigger reactivity
  expandedIndicators.value = new Set(expandedIndicators.value)
}

// Handle score selection
function selectScore(competencyId: string, score: number) {
  if (props.disabled) return
  emit('score-change', { competencyId, score })
}

// Handle notes change
function handleNotesChange(competencyId: string, event: Event) {
  const target = event.target as HTMLTextAreaElement
  localNotes.value[competencyId] = target.value
  emit('notes-change', { competencyId, notes: target.value })
}

// Score options
const scoreOptions = [1, 2, 3] as const
</script>

<template>
  <div class="competency-list">
    <!-- Loading state -->
    <div v-if="loading" class="loading-state">
      <div class="spinner"></div>
      <p>{{ t('common.loading') }}</p>
    </div>

    <!-- Competency cards -->
    <div v-else class="competency-cards">
      <div
        v-for="comp in competencies"
        :key="comp.id"
        class="competency-card"
        :data-competency-id="comp.id"
      >
        <!-- Category breadcrumb -->
        <div class="competency-breadcrumb">
          <span class="category-name">{{ t(`competencies.categories.${comp.category}`) }}</span>
          <span class="breadcrumb-separator">›</span>
          <span class="subcategory-name">{{ t(`competencies.subcategories.${comp.subcategory}`) }}</span>
        </div>

        <!-- Description -->
        <p class="competency-description">{{ getTitle(comp) }}</p>

        <!-- Behavioral Indicators Toggle -->
        <button
          v-if="comp.indicators_en && comp.indicators_en.length > 0"
          class="indicators-toggle"
          :aria-expanded="expandedIndicators.has(comp.id)"
          @click="toggleIndicators(comp.id)"
        >
          <span class="toggle-arrow" :class="{ expanded: expandedIndicators.has(comp.id) }">
            {{ expandedIndicators.has(comp.id) ? '▼' : '▶' }}
          </span>
          {{ t('competencies.behavioralIndicators') }}
        </button>

        <!-- Indicators list -->
        <ul
          v-if="expandedIndicators.has(comp.id) && comp.indicators_en"
          class="indicators-list"
        >
          <li v-for="(indicator, idx) in comp.indicators_en" :key="idx">
            {{ indicator }}
          </li>
        </ul>

        <!-- Scoring section (hidden in preview mode) -->
        <template v-if="!previewMode">
          <!-- Divider -->
          <div class="card-divider"></div>

          <!-- Score section -->
          <div class="score-section">
            <span class="score-label">{{ t('goals.score') }}:</span>
            <div class="score-buttons">
              <button
                v-for="score in scoreOptions"
                :key="score"
                class="score-btn"
                :class="{ selected: scores[comp.id] === score }"
                :disabled="disabled"
                @click="selectScore(comp.id, score)"
              >
                {{ score }}
              </button>
            </div>
          </div>

          <!-- Explanation textarea -->
          <textarea
            class="explanation-textarea"
            :value="localNotes[comp.id] || ''"
            :disabled="disabled"
            :placeholder="t('competencies.explanationPlaceholder')"
            rows="2"
            @input="handleNotesChange(comp.id, $event)"
          />
        </template>
      </div>
    </div>
  </div>
</template>

<style scoped>
.competency-list {
  min-height: 200px;
}

.loading-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 3rem 1rem;
  text-align: center;
  color: var(--color-gray-600);
}

.spinner {
  width: 40px;
  height: 40px;
  border: 3px solid var(--color-gray-200);
  border-top-color: var(--color-magenta);
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin-bottom: 1rem;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

.competency-cards {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.competency-card {
  padding: 1.25rem;
  border: 1px solid var(--color-gray-200);
  border-radius: 8px;
  background: var(--color-white, #ffffff);
}

.competency-breadcrumb {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  margin-bottom: 0.75rem;
}

.category-name {
  font-size: 0.875rem;
  font-weight: 600;
  color: var(--color-navy, #004A91);
}

.breadcrumb-separator {
  color: var(--color-gray-400);
  font-size: 0.875rem;
}

.subcategory-name {
  font-size: 0.875rem;
  color: var(--color-gray-600);
}

.competency-description {
  font-size: 0.9375rem;
  color: var(--color-gray-900);
  line-height: 1.5;
  margin: 0 0 1rem;
}

.indicators-toggle {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0;
  font-size: 0.875rem;
  font-weight: 500;
  color: var(--color-navy, #004A91);
  background: none;
  border: none;
  cursor: pointer;
  margin-bottom: 0.75rem;
}

.indicators-toggle:hover {
  color: var(--color-magenta, #CC0E70);
}

.toggle-arrow {
  font-size: 0.625rem;
  transition: transform 0.2s;
}

.indicators-list {
  margin: 0 0 1rem;
  padding-left: 1.5rem;
  font-size: 0.875rem;
  color: var(--color-gray-700);
  line-height: 1.6;
}

.indicators-list li {
  margin-bottom: 0.25rem;
}

.card-divider {
  height: 1px;
  background-color: var(--color-gray-200);
  margin: 1rem 0;
}

.score-section {
  display: flex;
  align-items: center;
  gap: 1rem;
  margin-bottom: 1rem;
}

.score-label {
  font-size: 0.875rem;
  font-weight: 500;
  color: var(--color-gray-700);
}

.score-buttons {
  display: flex;
  gap: 0.5rem;
}

.score-btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 40px;
  height: 40px;
  font-size: 1rem;
  font-weight: 600;
  color: var(--color-gray-700);
  background: var(--color-white);
  border: 2px solid var(--color-gray-300);
  border-radius: 50%;
  cursor: pointer;
  transition: all 0.2s;
}

.score-btn:hover:not(:disabled):not(.selected) {
  border-color: var(--color-gray-400);
  background: var(--color-gray-50);
}

.score-btn.selected {
  color: var(--color-white);
  background: var(--color-gray-700);
  border-color: var(--color-gray-700);
}

.score-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.explanation-textarea {
  width: 100%;
  padding: 0.75rem;
  font-size: 0.875rem;
  font-family: inherit;
  border: 1px solid var(--color-gray-300);
  border-radius: 6px;
  resize: vertical;
  min-height: 60px;
}

.explanation-textarea::placeholder {
  color: var(--color-gray-400);
}

.explanation-textarea:focus {
  outline: none;
  border-color: var(--color-navy, #004A91);
  box-shadow: 0 0 0 3px rgba(0, 74, 145, 0.1);
}

.explanation-textarea:disabled {
  background: var(--color-gray-100);
  cursor: not-allowed;
}
</style>
