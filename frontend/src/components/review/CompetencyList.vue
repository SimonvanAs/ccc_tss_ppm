<script setup lang="ts">
// TSS PPM v3.0 - CompetencyList Component
// Displays 6 competencies grouped by category for scoring

import { ref, computed, watch, onMounted } from 'vue'
import { useI18n } from 'vue-i18n'
import { getCompetencies } from '../../api/competencies'
import type { Competency, TovLevel } from '../../types/competency'
import CompetencyScoreCard from './CompetencyScoreCard.vue'
import VoiceInput from '../common/VoiceInput.vue'

interface Props {
  tovLevel: TovLevel
  scores?: Record<string, number>
  notes?: Record<string, string>
  disabled?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  scores: () => ({}),
  notes: () => ({}),
  disabled: false,
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

// Computed: group competencies by category
const groupedCompetencies = computed(() => {
  const groups: Record<string, Competency[]> = {
    Dedicated: [],
    Entrepreneurial: [],
    Innovative: [],
  }

  for (const comp of competencies.value) {
    if (groups[comp.category]) {
      groups[comp.category].push(comp)
    }
  }

  return groups
})

// Computed: category order
const categories = computed(() => ['Dedicated', 'Entrepreneurial', 'Innovative'])

// Fetch competencies
async function fetchCompetencies() {
  loading.value = true
  try {
    competencies.value = await getCompetencies(props.tovLevel)
  } catch (error) {
    console.error('Failed to fetch competencies:', error)
    competencies.value = []
  } finally {
    loading.value = false
  }
}

// Watch for tovLevel changes
watch(
  () => props.tovLevel,
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

// Check if competency has VETO (score = 1)
function hasVeto(competencyId: string): boolean {
  return props.scores[competencyId] === 1
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

// Handle score change from score card
function handleScoreChange(payload: { competencyId: string; score: number }) {
  emit('score-change', payload)
}

// Handle notes change
function handleNotesChange(competencyId: string, notes: string) {
  localNotes.value[competencyId] = notes
  emit('notes-change', { competencyId, notes })
}

// Handle voice transcription
function handleTranscription(competencyId: string, text: string) {
  const currentNotes = localNotes.value[competencyId] || ''
  const newNotes = currentNotes ? `${currentNotes} ${text}` : text
  handleNotesChange(competencyId, newNotes)
}
</script>

<template>
  <div class="competency-list">
    <!-- Loading state -->
    <div v-if="loading" class="loading-state">
      <div class="spinner"></div>
      <p>{{ t('common.loading') }}</p>
    </div>

    <!-- Competency list -->
    <div v-else class="competencies">
      <div
        v-for="category in categories"
        :key="category"
        class="category-group"
        :data-category="category"
      >
        <h3 class="category-title">
          {{ t(`competencies.categories.${category}`) }}
        </h3>

        <div
          v-for="comp in groupedCompetencies[category]"
          :key="comp.id"
          class="competency-item"
          :class="{ 'veto-warning': hasVeto(comp.id) }"
          :data-competency-id="comp.id"
        >
          <div class="competency-header">
            <div class="competency-info">
              <span class="category-badge">{{ comp.subcategory }}</span>
              <h4 class="competency-title">{{ getTitle(comp) }}</h4>
            </div>

            <CompetencyScoreCard
              :competency-id="comp.id"
              :model-value="scores[comp.id] ?? null"
              :labels="{
                1: t('competencies.scores.1'),
                2: t('competencies.scores.2'),
                3: t('competencies.scores.3'),
              }"
              :disabled="disabled"
              :show-veto-warning="true"
              @score-change="handleScoreChange"
            />
          </div>

          <!-- VETO indicator -->
          <div v-if="hasVeto(comp.id)" class="veto-indicator">
            {{ t('competencies.veto') }}
          </div>

          <!-- Behavioral indicators toggle -->
          <button
            v-if="comp.indicators_en && comp.indicators_en.length > 0"
            class="indicators-toggle"
            @click="toggleIndicators(comp.id)"
          >
            {{
              expandedIndicators.has(comp.id)
                ? t('competencies.hideIndicators')
                : t('competencies.showIndicators')
            }}
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

          <!-- Notes section -->
          <div class="notes-section">
            <label class="notes-label">{{ t('competencies.notes') }}</label>
            <div class="notes-input-wrapper">
              <textarea
                class="notes-textarea"
                :value="localNotes[comp.id] || ''"
                :disabled="disabled"
                rows="2"
                @input="handleNotesChange(comp.id, ($event.target as HTMLTextAreaElement).value)"
                @blur="handleNotesChange(comp.id, localNotes[comp.id] || '')"
              />
              <VoiceInput
                :disabled="disabled"
                @transcription="handleTranscription(comp.id, $event)"
              />
            </div>
          </div>
        </div>
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

.category-group {
  margin-bottom: 2rem;
}

.category-title {
  font-size: 1rem;
  font-weight: 600;
  color: var(--color-navy, #004A91);
  margin: 0 0 1rem;
  padding-bottom: 0.5rem;
  border-bottom: 2px solid var(--color-gray-200);
}

.competency-item {
  padding: 1rem;
  margin-bottom: 1rem;
  border: 1px solid var(--color-gray-200);
  border-radius: 8px;
  background: var(--color-white, #ffffff);
  transition: all 0.2s ease;
}

.competency-item:hover {
  border-color: var(--color-gray-300);
}

.competency-item.veto-warning {
  border-color: var(--color-grid-red, #dc2626);
  background: #FEF2F2;
}

.competency-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 1rem;
  flex-wrap: wrap;
}

.competency-info {
  flex: 1;
  min-width: 200px;
}

.category-badge {
  display: inline-block;
  padding: 0.25rem 0.5rem;
  font-size: 0.7rem;
  font-weight: 600;
  color: var(--color-white, #ffffff);
  background: var(--color-navy, #004A91);
  border-radius: 4px;
  text-transform: uppercase;
  margin-bottom: 0.5rem;
}

.competency-title {
  margin: 0;
  font-size: 0.95rem;
  font-weight: 500;
  color: var(--color-gray-900);
}

.veto-indicator {
  display: inline-block;
  padding: 0.25rem 0.5rem;
  margin-top: 0.5rem;
  font-size: 0.7rem;
  font-weight: bold;
  color: var(--color-white, #ffffff);
  background: var(--color-grid-red, #dc2626);
  border-radius: 4px;
  text-transform: uppercase;
}

.indicators-toggle {
  display: inline-block;
  margin-top: 0.5rem;
  padding: 0;
  font-size: 0.8rem;
  color: var(--color-navy, #004A91);
  background: none;
  border: none;
  cursor: pointer;
  text-decoration: underline;
}

.indicators-toggle:hover {
  color: var(--color-magenta, #CC0E70);
}

.indicators-list {
  margin: 0.75rem 0 0;
  padding-left: 1.5rem;
  font-size: 0.85rem;
  color: var(--color-gray-700);
}

.indicators-list li {
  margin-bottom: 0.25rem;
}

.notes-section {
  margin-top: 1rem;
  padding-top: 1rem;
  border-top: 1px solid var(--color-gray-200);
}

.notes-label {
  display: block;
  font-size: 0.8rem;
  font-weight: 500;
  color: var(--color-gray-600);
  margin-bottom: 0.5rem;
}

.notes-input-wrapper {
  display: flex;
  gap: 0.5rem;
  align-items: flex-start;
}

.notes-textarea {
  flex: 1;
  padding: 0.5rem;
  font-size: 0.875rem;
  font-family: inherit;
  border: 1px solid var(--color-gray-300);
  border-radius: 6px;
  resize: vertical;
  min-height: 60px;
}

.notes-textarea:focus {
  outline: none;
  border-color: var(--color-magenta, #CC0E70);
  box-shadow: 0 0 0 2px rgba(204, 14, 112, 0.1);
}

.notes-textarea:disabled {
  background: var(--color-gray-100);
  cursor: not-allowed;
}
</style>
