// TSS PPM v3.0 - Auto-save Composable
import { ref, onUnmounted, getCurrentInstance } from 'vue'

/**
 * Save status states for UI feedback.
 */
export enum SaveStatus {
  IDLE = 'idle',
  SAVING = 'saving',
  SAVED = 'saved',
  ERROR = 'error',
}

/**
 * Options for useAutoSave.
 */
export interface UseAutoSaveOptions {
  /** Debounce delay in milliseconds before triggering save. Default: 2500ms */
  debounceMs?: number
  /** How long to display "Saved" status before returning to idle. Default: 2000ms */
  savedDisplayMs?: number
}

/**
 * Composable for auto-saving form data with debounce.
 *
 * @param saveFn - Async function to call when saving
 * @param options - Configuration options
 */
export function useAutoSave(
  saveFn: () => Promise<void>,
  options: UseAutoSaveOptions = {}
) {
  const { debounceMs = 2500, savedDisplayMs = 2000 } = options

  const status = ref<SaveStatus>(SaveStatus.IDLE)
  const isDirty = ref(false)
  const lastError = ref<Error | null>(null)

  let debounceTimer: ReturnType<typeof setTimeout> | null = null
  let savedDisplayTimer: ReturnType<typeof setTimeout> | null = null

  /**
   * Clear any pending timers.
   */
  function clearTimers() {
    if (debounceTimer !== null) {
      clearTimeout(debounceTimer)
      debounceTimer = null
    }
    if (savedDisplayTimer !== null) {
      clearTimeout(savedDisplayTimer)
      savedDisplayTimer = null
    }
  }

  /**
   * Execute the save function.
   */
  async function doSave(): Promise<void> {
    if (!isDirty.value) return

    status.value = SaveStatus.SAVING
    lastError.value = null

    try {
      await saveFn()
      isDirty.value = false
      status.value = SaveStatus.SAVED

      // Return to idle after display time
      savedDisplayTimer = setTimeout(() => {
        if (status.value === SaveStatus.SAVED) {
          status.value = SaveStatus.IDLE
        }
      }, savedDisplayMs)
    } catch (error) {
      status.value = SaveStatus.ERROR
      lastError.value = error instanceof Error ? error : new Error(String(error))
    }
  }

  /**
   * Mark content as dirty and schedule a debounced save.
   */
  function markDirty(): void {
    isDirty.value = true

    // Clear existing debounce timer
    if (debounceTimer !== null) {
      clearTimeout(debounceTimer)
    }

    // Schedule new save
    debounceTimer = setTimeout(() => {
      debounceTimer = null
      doSave()
    }, debounceMs)
  }

  /**
   * Save immediately without waiting for debounce.
   */
  async function saveNow(): Promise<void> {
    // Cancel any pending debounced save
    if (debounceTimer !== null) {
      clearTimeout(debounceTimer)
      debounceTimer = null
    }

    await doSave()
  }

  /**
   * Cancel any pending save and reset dirty state.
   */
  function cancel(): void {
    clearTimers()
    isDirty.value = false
    status.value = SaveStatus.IDLE
  }

  // Clean up timers on unmount (only if inside a component)
  if (getCurrentInstance()) {
    onUnmounted(() => {
      clearTimers()
    })
  }

  return {
    status,
    isDirty,
    lastError,
    markDirty,
    saveNow,
    cancel,
  }
}
