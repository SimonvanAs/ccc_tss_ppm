// TSS PPM v3.0 - Competency Preview Composable
import { ref } from 'vue'
import { getCompetencies } from '../api/competencies'
import type { Competency, TovLevel } from '../types/competency'

// Cache TTL in milliseconds (15 minutes)
const CACHE_TTL = 15 * 60 * 1000

interface CacheEntry {
  data: Competency[]
  timestamp: number
}

// Cache to avoid redundant API calls (with TTL)
const cache = new Map<TovLevel, CacheEntry>()

/**
 * Check if a cache entry is still valid based on TTL.
 */
function isCacheValid(entry: CacheEntry): boolean {
  return Date.now() - entry.timestamp < CACHE_TTL
}

/**
 * Composable for loading and caching competencies by TOV level.
 * Used by CompetencyPreview component to display competencies based on selected TOV level.
 * Cache entries expire after 15 minutes.
 */
export function useCompetencyPreview() {
  const competencies = ref<Competency[]>([])
  const loading = ref(false)
  const error = ref<string | null>(null)

  let currentLevel: TovLevel | null = null

  async function loadCompetencies(tovLevel: TovLevel | null) {
    // Clear competencies if no TOV level
    if (tovLevel === null) {
      competencies.value = []
      currentLevel = null
      return
    }

    // Use cache if available and still valid
    const cached = cache.get(tovLevel)
    if (cached && isCacheValid(cached)) {
      competencies.value = cached.data
      currentLevel = tovLevel
      return
    }

    loading.value = true
    error.value = null

    try {
      const data = await getCompetencies(tovLevel)
      cache.set(tovLevel, { data, timestamp: Date.now() })
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

/**
 * Clear the competency cache. Exported for testing purposes.
 */
export function clearCompetencyCache(): void {
  cache.clear()
}
