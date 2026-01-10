// TSS PPM v3.0 - useAutoSave Composable Tests
import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'
import { ref, nextTick } from 'vue'
import { useAutoSave, SaveStatus } from '../../composables/useAutoSave'

describe('useAutoSave', () => {
  beforeEach(() => {
    vi.useFakeTimers()
  })

  afterEach(() => {
    vi.useRealTimers()
  })

  describe('initial state', () => {
    it('should initialize with idle status', () => {
      const saveFn = vi.fn()
      const { status } = useAutoSave(saveFn)
      expect(status.value).toBe(SaveStatus.IDLE)
    })

    it('should initialize with isDirty false', () => {
      const saveFn = vi.fn()
      const { isDirty } = useAutoSave(saveFn)
      expect(isDirty.value).toBe(false)
    })
  })

  describe('markDirty', () => {
    it('should set isDirty to true when called', () => {
      const saveFn = vi.fn()
      const { isDirty, markDirty } = useAutoSave(saveFn)

      markDirty()

      expect(isDirty.value).toBe(true)
    })

    it('should trigger save after debounce delay', async () => {
      const saveFn = vi.fn().mockResolvedValue(undefined)
      const { markDirty } = useAutoSave(saveFn, { debounceMs: 2500 })

      markDirty()

      // Should not be called immediately
      expect(saveFn).not.toHaveBeenCalled()

      // Advance time past debounce
      await vi.advanceTimersByTimeAsync(2500)

      expect(saveFn).toHaveBeenCalledTimes(1)
    })

    it('should reset debounce timer on subsequent calls', async () => {
      const saveFn = vi.fn().mockResolvedValue(undefined)
      const { markDirty } = useAutoSave(saveFn, { debounceMs: 2500 })

      markDirty()
      await vi.advanceTimersByTimeAsync(2000)

      // Mark dirty again before timeout
      markDirty()
      await vi.advanceTimersByTimeAsync(2000)

      // Should still not be called (timer was reset)
      expect(saveFn).not.toHaveBeenCalled()

      // Now advance past the second debounce
      await vi.advanceTimersByTimeAsync(500)

      expect(saveFn).toHaveBeenCalledTimes(1)
    })
  })

  describe('save status transitions', () => {
    it('should transition to SAVING when save starts', async () => {
      let resolvePromise: () => void
      const saveFn = vi.fn().mockReturnValue(
        new Promise<void>(resolve => {
          resolvePromise = resolve
        })
      )
      const { status, markDirty } = useAutoSave(saveFn, { debounceMs: 100 })

      markDirty()
      await vi.advanceTimersByTimeAsync(100)

      expect(status.value).toBe(SaveStatus.SAVING)

      resolvePromise!()
      await nextTick()
    })

    it('should transition to SAVED on successful save', async () => {
      const saveFn = vi.fn().mockResolvedValue(undefined)
      const { status, markDirty } = useAutoSave(saveFn, { debounceMs: 100 })

      markDirty()
      await vi.advanceTimersByTimeAsync(100)
      await nextTick()

      expect(status.value).toBe(SaveStatus.SAVED)
    })

    it('should transition to ERROR on save failure', async () => {
      const saveFn = vi.fn().mockRejectedValue(new Error('Save failed'))
      const { status, markDirty } = useAutoSave(saveFn, { debounceMs: 100 })

      markDirty()
      await vi.advanceTimersByTimeAsync(100)
      await nextTick()

      expect(status.value).toBe(SaveStatus.ERROR)
    })

    it('should clear isDirty on successful save', async () => {
      const saveFn = vi.fn().mockResolvedValue(undefined)
      const { isDirty, markDirty } = useAutoSave(saveFn, { debounceMs: 100 })

      markDirty()
      expect(isDirty.value).toBe(true)

      await vi.advanceTimersByTimeAsync(100)
      await nextTick()

      expect(isDirty.value).toBe(false)
    })

    it('should keep isDirty true on save failure', async () => {
      const saveFn = vi.fn().mockRejectedValue(new Error('Save failed'))
      const { isDirty, markDirty } = useAutoSave(saveFn, { debounceMs: 100 })

      markDirty()
      await vi.advanceTimersByTimeAsync(100)
      await nextTick()

      expect(isDirty.value).toBe(true)
    })

    it('should return to IDLE after saved delay', async () => {
      const saveFn = vi.fn().mockResolvedValue(undefined)
      const { status, markDirty } = useAutoSave(saveFn, { debounceMs: 100, savedDisplayMs: 2000 })

      markDirty()
      await vi.advanceTimersByTimeAsync(100)
      await nextTick()

      expect(status.value).toBe(SaveStatus.SAVED)

      await vi.advanceTimersByTimeAsync(2000)

      expect(status.value).toBe(SaveStatus.IDLE)
    })
  })

  describe('saveNow', () => {
    it('should save immediately without waiting for debounce', async () => {
      const saveFn = vi.fn().mockResolvedValue(undefined)
      const { markDirty, saveNow } = useAutoSave(saveFn, { debounceMs: 5000 })

      markDirty()

      // Don't advance timers, call saveNow directly
      await saveNow()

      expect(saveFn).toHaveBeenCalledTimes(1)
    })

    it('should cancel pending debounced save', async () => {
      const saveFn = vi.fn().mockResolvedValue(undefined)
      const { markDirty, saveNow } = useAutoSave(saveFn, { debounceMs: 100 })

      markDirty()
      await saveNow()

      // Advance past the debounce time
      await vi.advanceTimersByTimeAsync(100)

      // Should only have been called once (by saveNow, not by debounce)
      expect(saveFn).toHaveBeenCalledTimes(1)
    })

    it('should not save if not dirty', async () => {
      const saveFn = vi.fn().mockResolvedValue(undefined)
      const { saveNow } = useAutoSave(saveFn)

      await saveNow()

      expect(saveFn).not.toHaveBeenCalled()
    })
  })

  describe('cancel', () => {
    it('should cancel pending save', async () => {
      const saveFn = vi.fn().mockResolvedValue(undefined)
      const { markDirty, cancel } = useAutoSave(saveFn, { debounceMs: 100 })

      markDirty()
      cancel()

      await vi.advanceTimersByTimeAsync(200)

      expect(saveFn).not.toHaveBeenCalled()
    })

    it('should reset isDirty to false', () => {
      const saveFn = vi.fn()
      const { isDirty, markDirty, cancel } = useAutoSave(saveFn)

      markDirty()
      expect(isDirty.value).toBe(true)

      cancel()

      expect(isDirty.value).toBe(false)
    })
  })

  describe('error handling', () => {
    it('should expose lastError on save failure', async () => {
      const error = new Error('Network error')
      const saveFn = vi.fn().mockRejectedValue(error)
      const { lastError, markDirty } = useAutoSave(saveFn, { debounceMs: 100 })

      expect(lastError.value).toBeNull()

      markDirty()
      await vi.advanceTimersByTimeAsync(100)
      await nextTick()

      expect(lastError.value).toBe(error)
    })

    it('should clear lastError on successful save', async () => {
      const saveFn = vi.fn()
        .mockRejectedValueOnce(new Error('First error'))
        .mockResolvedValueOnce(undefined)
      const { lastError, markDirty } = useAutoSave(saveFn, { debounceMs: 100 })

      // First save fails
      markDirty()
      await vi.advanceTimersByTimeAsync(100)
      await nextTick()
      expect(lastError.value).not.toBeNull()

      // Second save succeeds
      markDirty()
      await vi.advanceTimersByTimeAsync(100)
      await nextTick()
      expect(lastError.value).toBeNull()
    })
  })

  describe('options', () => {
    it('should use default debounce of 2500ms', async () => {
      const saveFn = vi.fn().mockResolvedValue(undefined)
      const { markDirty } = useAutoSave(saveFn)

      markDirty()

      await vi.advanceTimersByTimeAsync(2400)
      expect(saveFn).not.toHaveBeenCalled()

      await vi.advanceTimersByTimeAsync(100)
      expect(saveFn).toHaveBeenCalledTimes(1)
    })

    it('should accept custom debounce time', async () => {
      const saveFn = vi.fn().mockResolvedValue(undefined)
      const { markDirty } = useAutoSave(saveFn, { debounceMs: 1000 })

      markDirty()

      await vi.advanceTimersByTimeAsync(900)
      expect(saveFn).not.toHaveBeenCalled()

      await vi.advanceTimersByTimeAsync(100)
      expect(saveFn).toHaveBeenCalledTimes(1)
    })
  })
})
