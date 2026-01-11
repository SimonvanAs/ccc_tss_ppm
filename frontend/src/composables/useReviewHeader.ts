// TSS PPM v3.0 - useReviewHeader Composable
import { ref, computed } from 'vue'
import { useAutoSave, SaveStatus } from './useAutoSave'
import { fetchReview, updateReviewHeader, type ReviewDetails } from '../api/reviews'

/**
 * Composable for managing review header data with auto-save.
 *
 * @param reviewId - The review UUID
 */
export function useReviewHeader(reviewId: string) {
  const review = ref<ReviewDetails | null>(null)
  const loading = ref(false)
  const error = ref<string | null>(null)

  // Local state for pending changes (before save)
  const pendingJobTitle = ref<string | null>(null)
  const pendingTovLevel = ref<string | null>(null)

  /**
   * Save function for auto-save.
   * Only saves fields that have changed.
   */
  async function save(): Promise<void> {
    if (!review.value) return

    const updates: { job_title?: string; tov_level?: string } = {}

    if (pendingJobTitle.value !== null) {
      updates.job_title = pendingJobTitle.value
    }

    if (pendingTovLevel.value !== null) {
      updates.tov_level = pendingTovLevel.value
    }

    if (Object.keys(updates).length === 0) return

    const updatedReview = await updateReviewHeader(reviewId, updates)

    // Update local state with server response
    review.value = updatedReview

    // Clear pending changes
    pendingJobTitle.value = null
    pendingTovLevel.value = null
  }

  const { status, markDirty, saveNow } = useAutoSave(save, {
    debounceMs: 2500,
    savedDisplayMs: 2000,
  })

  const saveStatus = computed(() => status.value)

  /**
   * Load review data from API.
   */
  async function loadReview(): Promise<void> {
    loading.value = true
    error.value = null

    try {
      review.value = await fetchReview(reviewId)
    } catch (e) {
      error.value = e instanceof Error ? e.message : 'Failed to load review'
    } finally {
      loading.value = false
    }
  }

  /**
   * Update job title (triggers auto-save).
   */
  function updateJobTitle(value: string): void {
    pendingJobTitle.value = value
    markDirty()
  }

  /**
   * Update TOV level (triggers auto-save).
   */
  function updateTovLevel(value: string): void {
    pendingTovLevel.value = value
    markDirty()
  }

  /**
   * Save immediately without waiting for debounce.
   */
  async function saveImmediately(): Promise<void> {
    await saveNow()
  }

  return {
    review,
    loading,
    error,
    saveStatus,
    loadReview,
    updateJobTitle,
    updateTovLevel,
    saveImmediately,
  }
}
