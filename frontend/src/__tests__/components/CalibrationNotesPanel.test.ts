// TSS PPM v3.0 - CalibrationNotesPanel Tests
import { describe, it, expect, vi, beforeEach } from 'vitest'
import { mount, flushPromises } from '@vue/test-utils'
import CalibrationNotesPanel from '../../components/calibration/CalibrationNotesPanel.vue'
import type { CalibrationNote } from '../../api/calibration'

// Mock vue-i18n
vi.mock('vue-i18n', () => ({
  useI18n: () => ({
    t: (key: string) => {
      const messages: Record<string, string> = {
        'calibration.notes.title': 'Notes',
        'calibration.notes.sessionNotes': 'Session Notes',
        'calibration.notes.reviewNotes': 'Review Notes',
        'calibration.notes.addNote': 'Add Note',
        'calibration.notes.placeholder': 'Enter your note...',
        'calibration.notes.submit': 'Add',
        'calibration.notes.cancel': 'Cancel',
        'calibration.notes.noNotes': 'No notes yet',
        'calibration.notes.loading': 'Loading notes...',
        'calibration.notes.error': 'Failed to load notes',
        'calibration.notes.addError': 'Failed to add note',
        'calibration.notes.contentRequired': 'Note content is required',
      }
      return messages[key] || key
    },
  }),
}))

// Mock the API
const mockFetchNotes = vi.fn()
const mockAddNote = vi.fn()
vi.mock('../../api/calibration', () => ({
  fetchSessionNotes: (sessionId: string, reviewId?: string) => mockFetchNotes(sessionId, reviewId),
  addNote: (sessionId: string, content: string, reviewId?: string) =>
    mockAddNote(sessionId, content, reviewId),
}))

function createMockNote(overrides: Partial<CalibrationNote> = {}): CalibrationNote {
  return {
    id: 'note-1',
    session_id: 'session-1',
    review_id: null,
    content: 'This is a test note',
    created_by: 'user-1',
    first_name: 'Jane',
    last_name: 'Doe',
    created_at: '2026-01-10T10:00:00Z',
    ...overrides,
  }
}

describe('CalibrationNotesPanel', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    mockFetchNotes.mockResolvedValue([])
    mockAddNote.mockResolvedValue(createMockNote())
  })

  function createWrapper(props: { sessionId: string; reviewId?: string }) {
    return mount(CalibrationNotesPanel, {
      props,
    })
  }

  describe('loading state', () => {
    it('should show loading indicator while fetching', () => {
      mockFetchNotes.mockReturnValue(new Promise(() => {})) // Never resolves
      const wrapper = createWrapper({ sessionId: 'session-1' })

      expect(wrapper.text()).toContain('Loading notes...')
    })

    it('should hide loading after notes load', async () => {
      mockFetchNotes.mockResolvedValue([])
      const wrapper = createWrapper({ sessionId: 'session-1' })

      await flushPromises()

      expect(wrapper.text()).not.toContain('Loading notes...')
    })
  })

  describe('notes display', () => {
    it('should display list of notes', async () => {
      const notes = [
        createMockNote({ id: 'n1', content: 'First note' }),
        createMockNote({ id: 'n2', content: 'Second note' }),
      ]
      mockFetchNotes.mockResolvedValue(notes)

      const wrapper = createWrapper({ sessionId: 'session-1' })
      await flushPromises()

      expect(wrapper.text()).toContain('First note')
      expect(wrapper.text()).toContain('Second note')
    })

    it('should display author name for each note', async () => {
      mockFetchNotes.mockResolvedValue([
        createMockNote({ first_name: 'Jane', last_name: 'Doe' }),
      ])

      const wrapper = createWrapper({ sessionId: 'session-1' })
      await flushPromises()

      expect(wrapper.text()).toContain('Jane Doe')
    })

    it('should display formatted timestamp for each note', async () => {
      mockFetchNotes.mockResolvedValue([
        createMockNote({ created_at: '2026-01-10T10:30:00Z' }),
      ])

      const wrapper = createWrapper({ sessionId: 'session-1' })
      await flushPromises()

      // Should contain some date/time representation
      expect(wrapper.text()).toMatch(/2026|Jan|10/)
    })

    it('should show empty state when no notes', async () => {
      mockFetchNotes.mockResolvedValue([])

      const wrapper = createWrapper({ sessionId: 'session-1' })
      await flushPromises()

      expect(wrapper.text()).toContain('No notes yet')
    })
  })

  describe('session vs review notes', () => {
    it('should fetch session-level notes when no reviewId', async () => {
      const wrapper = createWrapper({ sessionId: 'session-123' })
      await flushPromises()

      expect(mockFetchNotes).toHaveBeenCalledWith('session-123', undefined)
    })

    it('should fetch review-level notes when reviewId provided', async () => {
      const wrapper = createWrapper({ sessionId: 'session-123', reviewId: 'review-456' })
      await flushPromises()

      expect(mockFetchNotes).toHaveBeenCalledWith('session-123', 'review-456')
    })

    it('should show session notes title for session-level notes', async () => {
      mockFetchNotes.mockResolvedValue([])
      const wrapper = createWrapper({ sessionId: 'session-1' })
      await flushPromises()

      expect(wrapper.text()).toContain('Session Notes')
    })

    it('should show review notes title for review-level notes', async () => {
      mockFetchNotes.mockResolvedValue([])
      const wrapper = createWrapper({ sessionId: 'session-1', reviewId: 'review-1' })
      await flushPromises()

      expect(wrapper.text()).toContain('Review Notes')
    })
  })

  describe('add note form', () => {
    it('should render add note button', async () => {
      const wrapper = createWrapper({ sessionId: 'session-1' })
      await flushPromises()

      const addBtn = wrapper.find('.add-note-btn')
      expect(addBtn.exists()).toBe(true)
    })

    it('should show note form when add button clicked', async () => {
      const wrapper = createWrapper({ sessionId: 'session-1' })
      await flushPromises()

      const addBtn = wrapper.find('.add-note-btn')
      await addBtn.trigger('click')

      const textarea = wrapper.find('textarea[name="noteContent"]')
      expect(textarea.exists()).toBe(true)
    })

    it('should hide form when cancel clicked', async () => {
      const wrapper = createWrapper({ sessionId: 'session-1' })
      await flushPromises()

      await wrapper.find('.add-note-btn').trigger('click')
      expect(wrapper.find('textarea[name="noteContent"]').exists()).toBe(true)

      await wrapper.find('.cancel-btn').trigger('click')
      expect(wrapper.find('textarea[name="noteContent"]').exists()).toBe(false)
    })

    it('should show validation error when content is empty', async () => {
      const wrapper = createWrapper({ sessionId: 'session-1' })
      await flushPromises()

      await wrapper.find('.add-note-btn').trigger('click')
      await wrapper.find('form').trigger('submit')

      expect(wrapper.text()).toContain('Note content is required')
    })

    it('should not submit when content is empty', async () => {
      const wrapper = createWrapper({ sessionId: 'session-1' })
      await flushPromises()

      await wrapper.find('.add-note-btn').trigger('click')
      await wrapper.find('form').trigger('submit')

      expect(mockAddNote).not.toHaveBeenCalled()
    })
  })

  describe('add note submission', () => {
    it('should call addNote API with correct params for session note', async () => {
      const wrapper = createWrapper({ sessionId: 'session-123' })
      await flushPromises()

      await wrapper.find('.add-note-btn').trigger('click')
      await wrapper.find('textarea[name="noteContent"]').setValue('My new note')
      await wrapper.find('form').trigger('submit')
      await flushPromises()

      expect(mockAddNote).toHaveBeenCalledWith('session-123', 'My new note', undefined)
    })

    it('should call addNote API with reviewId for review note', async () => {
      const wrapper = createWrapper({ sessionId: 'session-123', reviewId: 'review-456' })
      await flushPromises()

      await wrapper.find('.add-note-btn').trigger('click')
      await wrapper.find('textarea[name="noteContent"]').setValue('My review note')
      await wrapper.find('form').trigger('submit')
      await flushPromises()

      expect(mockAddNote).toHaveBeenCalledWith('session-123', 'My review note', 'review-456')
    })

    it('should add new note to list after successful submission', async () => {
      const newNote = createMockNote({ id: 'new-note', content: 'New note content' })
      mockAddNote.mockResolvedValue(newNote)

      const wrapper = createWrapper({ sessionId: 'session-1' })
      await flushPromises()

      await wrapper.find('.add-note-btn').trigger('click')
      await wrapper.find('textarea[name="noteContent"]').setValue('New note content')
      await wrapper.find('form').trigger('submit')
      await flushPromises()

      expect(wrapper.text()).toContain('New note content')
    })

    it('should clear form after successful submission', async () => {
      const wrapper = createWrapper({ sessionId: 'session-1' })
      await flushPromises()

      await wrapper.find('.add-note-btn').trigger('click')
      await wrapper.find('textarea[name="noteContent"]').setValue('Test note')
      await wrapper.find('form').trigger('submit')
      await flushPromises()

      // Form should be hidden
      expect(wrapper.find('textarea[name="noteContent"]').exists()).toBe(false)
    })

    it('should show error on API failure', async () => {
      mockAddNote.mockRejectedValue(new Error('API error'))

      const wrapper = createWrapper({ sessionId: 'session-1' })
      await flushPromises()

      await wrapper.find('.add-note-btn').trigger('click')
      await wrapper.find('textarea[name="noteContent"]').setValue('Test note')
      await wrapper.find('form').trigger('submit')
      await flushPromises()

      expect(wrapper.text()).toContain('Failed to add note')
    })
  })

  describe('error state', () => {
    it('should show error message on fetch failure', async () => {
      mockFetchNotes.mockRejectedValue(new Error('Fetch error'))

      const wrapper = createWrapper({ sessionId: 'session-1' })
      await flushPromises()

      expect(wrapper.text()).toContain('Failed to load notes')
    })
  })

  describe('notes ordering', () => {
    it('should display notes in reverse chronological order (newest first)', async () => {
      const notes = [
        createMockNote({ id: 'n1', content: 'Older note', created_at: '2026-01-10T10:00:00Z' }),
        createMockNote({ id: 'n2', content: 'Newer note', created_at: '2026-01-11T10:00:00Z' }),
      ]
      mockFetchNotes.mockResolvedValue(notes)

      const wrapper = createWrapper({ sessionId: 'session-1' })
      await flushPromises()

      const noteItems = wrapper.findAll('.note-item')
      // Newer note should appear first
      expect(noteItems[0].text()).toContain('Newer note')
      expect(noteItems[1].text()).toContain('Older note')
    })
  })

  describe('refresh on reviewId change', () => {
    it('should refetch notes when reviewId changes', async () => {
      const wrapper = createWrapper({ sessionId: 'session-1' })
      await flushPromises()

      expect(mockFetchNotes).toHaveBeenCalledTimes(1)

      await wrapper.setProps({ reviewId: 'review-123' })
      await flushPromises()

      expect(mockFetchNotes).toHaveBeenCalledTimes(2)
      expect(mockFetchNotes).toHaveBeenLastCalledWith('session-1', 'review-123')
    })
  })
})
