// TSS PPM v3.0 - Competency Preview Composable
import { ref } from 'vue'
import { getCompetencies } from '../api/competencies'
import type { Competency, TovLevel } from '../types/competency'

/**
 * Composable for loading and caching competencies by TOV level.
 * Used by CompetencyPreview component to display competencies based on selected TOV level.
 */
export function useCompetencyPreview() {
  const competencies = ref<Competency[]>([])
  const loading = ref(false)
  const error = ref<string | null>(null)

  // Cache to avoid redundant API calls
  const cache = new Map<TovLevel, Competency[]>()
  let currentLevel: TovLevel | null = null

  async function loadCompetencies(tovLevel: TovLevel | null) {
    // Clear competencies if no TOV level
    if (tovLevel === null) {
      competencies.value = []
      currentLevel = null
      return
    }

    // Use cache if available for the same level
    if (cache.has(tovLevel)) {
      competencies.value = cache.get(tovLevel)!
      currentLevel = tovLevel
      return
    }

    loading.value = true
    error.value = null

    try {
      const data = await getCompetencies(tovLevel)
      cache.set(tovLevel, data)
      competencies.value = data
      currentLevel = tovLevel
    } catch (e) {
      error.value = 'Failed to load competencies'
      competencies.value = []
    } finally {
      loading.value = false
    }
  }

  return {
    competencies,
    loading,
    error,
    loadCompetencies,
  }
}
