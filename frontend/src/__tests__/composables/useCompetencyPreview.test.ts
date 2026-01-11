// TSS PPM v3.0 - useCompetencyPreview Composable Tests
import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'
import { useCompetencyPreview } from '../../composables/useCompetencyPreview'
import * as competenciesApi from '../../api/competencies'
import type { Competency } from '../../types/competency'

// Mock the competencies API
vi.mock('../../api/competencies', () => ({
  getCompetencies: vi.fn(),
}))

const mockCompetencies: Competency[] = [
  {
    id: 'comp-1',
    level: 'B',
    category: 'Dedicated',
    subcategory: 'Result driven',
    title_en: 'Achieves Results',
    indicators_en: ['Delivers on commitments'],
    display_order: 1,
  },
  {
    id: 'comp-2',
    level: 'B',
    category: 'Entrepreneurial',
    subcategory: 'Entrepreneurial',
    title_en: 'Takes Initiative',
    indicators_en: ['Identifies opportunities'],
    display_order: 2,
  },
]

describe('useCompetencyPreview', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  afterEach(() => {
    vi.restoreAllMocks()
  })

  describe('fetching competencies by TOV level', () => {
    it('should fetch competencies when TOV level is provided', async () => {
      vi.mocked(competenciesApi.getCompetencies).mockResolvedValue(mockCompetencies)

      const { competencies, loading, loadCompetencies } = useCompetencyPreview()

      expect(competencies.value).toEqual([])
      expect(loading.value).toBe(false)

      await loadCompetencies('B')

      expect(competenciesApi.getCompetencies).toHaveBeenCalledWith('B')
      expect(competencies.value).toEqual(mockCompetencies)
    })

    it('should set loading state during fetch', async () => {
      let resolvePromise: (value: Competency[]) => void
      const promise = new Promise<Competency[]>((resolve) => {
        resolvePromise = resolve
      })
      vi.mocked(competenciesApi.getCompetencies).mockReturnValue(promise)

      const { loading, loadCompetencies } = useCompetencyPreview()

      const loadPromise = loadCompetencies('B')
      expect(loading.value).toBe(true)

      resolvePromise!(mockCompetencies)
      await loadPromise

      expect(loading.value).toBe(false)
    })

    it('should handle API errors gracefully', async () => {
      vi.mocked(competenciesApi.getCompetencies).mockRejectedValue(new Error('API Error'))

      const { competencies, error, loadCompetencies } = useCompetencyPreview()

      await loadCompetencies('B')

      expect(competencies.value).toEqual([])
      expect(error.value).toBe('Failed to load competencies')
    })
  })

  describe('caching to avoid redundant API calls', () => {
    it('should cache results for the same TOV level', async () => {
      vi.mocked(competenciesApi.getCompetencies).mockResolvedValue(mockCompetencies)

      const { loadCompetencies } = useCompetencyPreview()

      await loadCompetencies('B')
      await loadCompetencies('B')

      expect(competenciesApi.getCompetencies).toHaveBeenCalledTimes(1)
    })

    it('should fetch again for different TOV level', async () => {
      vi.mocked(competenciesApi.getCompetencies).mockResolvedValue(mockCompetencies)

      const { loadCompetencies } = useCompetencyPreview()

      await loadCompetencies('B')
      await loadCompetencies('C')

      expect(competenciesApi.getCompetencies).toHaveBeenCalledTimes(2)
      expect(competenciesApi.getCompetencies).toHaveBeenNthCalledWith(1, 'B')
      expect(competenciesApi.getCompetencies).toHaveBeenNthCalledWith(2, 'C')
    })

    it('should use cached data when requesting same level again', async () => {
      vi.mocked(competenciesApi.getCompetencies).mockResolvedValue(mockCompetencies)

      const { competencies, loadCompetencies } = useCompetencyPreview()

      await loadCompetencies('B')
      const firstResult = competencies.value

      await loadCompetencies('B')

      expect(competencies.value).toBe(firstResult)
    })
  })

  describe('loading state management', () => {
    it('should start with loading false', () => {
      const { loading } = useCompetencyPreview()
      expect(loading.value).toBe(false)
    })

    it('should start with empty competencies', () => {
      const { competencies } = useCompetencyPreview()
      expect(competencies.value).toEqual([])
    })

    it('should clear error when fetch succeeds', async () => {
      vi.mocked(competenciesApi.getCompetencies)
        .mockRejectedValueOnce(new Error('API Error'))
        .mockResolvedValueOnce(mockCompetencies)

      const { error, loadCompetencies } = useCompetencyPreview()

      await loadCompetencies('B')
      expect(error.value).toBe('Failed to load competencies')

      // Use different level to bypass cache
      await loadCompetencies('C')
      expect(error.value).toBeNull()
    })

    it('should clear competencies when TOV level is null', async () => {
      vi.mocked(competenciesApi.getCompetencies).mockResolvedValue(mockCompetencies)

      const { competencies, loadCompetencies } = useCompetencyPreview()

      await loadCompetencies('B')
      expect(competencies.value).toEqual(mockCompetencies)

      await loadCompetencies(null)
      expect(competencies.value).toEqual([])
    })
  })
})
