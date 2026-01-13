<script setup lang="ts">
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'
import type { Competency } from '../../types/competency'

const props = withDefaults(
  defineProps<{
    competencies: Competency[]
    loading: boolean
    showSelectMessage?: boolean
  }>(),
  {
    showSelectMessage: false,
  }
)

const { t, locale } = useI18n()

// Get competency title based on locale
function getTitle(comp: Competency): string {
  const lang = locale.value
  if (lang === 'nl' && comp.title_nl) return comp.title_nl
  if (lang === 'es' && comp.title_es) return comp.title_es
  return comp.title_en
}

// Group competencies by category
const groupedCompetencies = computed(() => {
  const groups: Record<string, Competency[]> = {
    Dedicated: [],
    Entrepreneurial: [],
    Innovative: [],
  }

  for (const comp of props.competencies) {
    if (groups[comp.category]) {
      groups[comp.category].push(comp)
    }
  }

  // Sort by display_order within each group
  for (const category of Object.keys(groups)) {
    groups[category].sort((a, b) => a.display_order - b.display_order)
  }

  return groups
})

const hasCompetencies = computed(() => props.competencies.length > 0)

const categories = ['Dedicated', 'Entrepreneurial', 'Innovative'] as const
</script>

<template>
  <div class="competency-preview">
    <!-- Header -->
    <div class="preview-header">
      <h3 class="preview-title">{{ t('competencyPreview.title') }}</h3>
    </div>

    <!-- Loading state -->
    <div v-if="loading" data-testid="loading-state" class="loading-state">
      <span class="loading-spinner"></span>
      <span>{{ t('common.loading') }}</span>
    </div>

    <!-- Empty state -->
    <div
      v-else-if="!hasCompetencies"
      data-testid="empty-state"
      class="empty-state"
    >
      <p v-if="showSelectMessage">{{ t('competencyPreview.selectTovLevel') }}</p>
      <p v-else>{{ t('competencyPreview.emptyState') }}</p>
    </div>

    <!-- Competencies grouped by category -->
    <div v-else class="competency-categories">
      <div
        v-for="category in categories"
        :key="category"
        :data-testid="`category-${category}`"
        class="category-group competency-category"
      >
        <h4 class="category-title">
          {{ t(`competencies.categories.${category}`) }}
        </h4>
        <div class="category-items">
          <div
            v-for="competency in groupedCompetencies[category]"
            :key="competency.id"
            data-testid="competency-item"
            class="competency-item"
          >
            <div class="competency-header">
              <span class="competency-title">{{ getTitle(competency) }}</span>
              <span class="competency-subcategory">{{ t(`competencies.subcategories.${competency.subcategory}`) }}</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.competency-preview {
  background-color: var(--color-white, #ffffff);
  border-radius: 8px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1), 0 1px 2px rgba(0, 0, 0, 0.06);
  padding: 1.5rem;
}

.preview-header {
  margin-bottom: 1.25rem;
  padding-bottom: 0.75rem;
  border-bottom: 1px solid var(--color-gray-200, #e5e7eb);
}

.preview-title {
  font-size: 1rem;
  font-weight: 600;
  color: var(--color-gray-900, #111827);
  margin: 0;
}

.loading-state {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.75rem;
  padding: 2rem;
  color: var(--color-gray-500, #6b7280);
}

.loading-spinner {
  width: 20px;
  height: 20px;
  border: 2px solid var(--color-gray-300, #d1d5db);
  border-top-color: var(--color-magenta, #CC0E70);
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

.empty-state {
  padding: 2rem;
  text-align: center;
  color: var(--color-gray-500, #6b7280);
}

.empty-state p {
  margin: 0;
  font-size: 0.9375rem;
}

.competency-categories {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.category-group {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.category-title {
  font-size: 0.8125rem;
  font-weight: 600;
  color: var(--color-magenta, #CC0E70);
  text-transform: uppercase;
  letter-spacing: 0.05em;
  margin: 0;
}

.category-items {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 0.75rem;
  align-items: stretch;
}

.competency-item {
  background-color: var(--color-gray-50, #f9fafb);
  border-radius: 6px;
  padding: 0.75rem 1rem;
  border: 1px solid var(--color-gray-200, #e5e7eb);
  min-height: 120px;
  display: flex;
  flex-direction: column;
}

.competency-header {
  display: flex;
  flex-direction: column;
  flex: 1;
}

.competency-title {
  font-size: 0.875rem;
  font-weight: 500;
  color: var(--color-gray-900, #111827);
  flex: 1;
}

.competency-subcategory {
  font-size: 0.75rem;
  color: var(--color-gray-500, #6b7280);
  margin-top: auto;
  padding-top: 0.5rem;
}

/* Responsive */
@media (max-width: 640px) {
  .category-items {
    grid-template-columns: 1fr;
  }
}
</style>
