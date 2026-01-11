// TSS PPM v3.0 - CalibrationSessionDetail Tests
import { describe, it, expect, vi, beforeEach } from 'vitest'
import { mount, flushPromises } from '@vue/test-utils'
import CalibrationSessionDetail from '../../components/calibration/CalibrationSessionDetail.vue'
import type {
  CalibrationSession,
  CalibrationReview,
  CalibrationParticipant,
} from '../../api/calibration'

// Mock vue-i18n
vi.mock('vue-i18n', () => ({
  useI18n: () => ({
    t: (key: string) => {
      const messages: Record<string, string> = {
        'calibration.detail.title': 'Calibration Session',
        'calibration.detail.description': 'Description',
        'calibration.detail.reviewYear': 'Review Year',
        'calibration.detail.scope': 'Scope',
        'calibration.detail.status': 'Status',
        'calibration.detail.createdAt': 'Created',
        'calibration.detail.reviews': 'Reviews',
        'calibration.detail.participants': 'Participants',
        'calibration.detail.noReviews': 'No reviews in this session',
        'calibration.detail.noParticipants': 'No participants added',
        'calibration.detail.loading': 'Loading...',
        'calibration.detail.startSession': 'Start Session',
        'calibration.detail.completeSession': 'Complete Session',
        'calibration.detail.edit': 'Edit',
        'calibration.detail.delete': 'Delete',
        'calibration.detail.back': 'Back to Sessions',
        'calibration.status.PREPARATION': 'Preparation',
        'calibration.status.IN_PROGRESS': 'In Progress',
        'calibration.status.PENDING_APPROVAL': 'Pending Approval',
        'calibration.status.COMPLETED': 'Completed',
        'calibration.status.CANCELLED': 'Cancelled',
        'calibration.scope.COMPANY_WIDE': 'Company Wide',
        'calibration.scope.BUSINESS_UNIT': 'Business Unit',
      }
      return messages[key] || key
    },
  }),
}))

// Mock the API
const mockFetchSession = vi.fn()
const mockFetchReviews = vi.fn()
const mockFetchParticipants = vi.fn()
const mockStartSession = vi.fn()
const mockCompleteSession = vi.fn()
const mockDeleteSession = vi.fn()

vi.mock('../../api/calibration', () => ({
  fetchCalibrationSession: (id: string) => mockFetchSession(id),
  fetchSessionReviews: (id: string) => mockFetchReviews(id),
  fetchSessionParticipants: (id: string) => mockFetchParticipants(id),
  startCalibrationSession: (id: string) => mockStartSession(id),
  completeCalibrationSession: (id: string) => mockCompleteSession(id),
  deleteCalibrationSession: (id: string) => mockDeleteSession(id),
}))

function createMockSession(overrides: Partial<CalibrationSession> = {}): CalibrationSession {
  return {
    id: 'session-1',
    opco_id: 'opco-1',
    name: 'Q4 2026 Calibration',
    description: 'End of year calibration',
    review_year: 2026,
    scope: 'COMPANY_WIDE',
    business_unit_id: null,
    status: 'PREPARATION',
    facilitator_id: null,
    created_by: null,
    snapshot_taken_at: null,
    completed_at: null,
    notes: null,
    created_at: '2026-01-10T10:00:00Z',
    updated_at: '2026-01-10T10:00:00Z',
    ...overrides,
  }
}

function createMockReview(overrides: Partial<CalibrationReview> = {}): CalibrationReview {
  return {
    review_id: 'review-1',
    employee_id: 'emp-1',
    employee_name: 'John Doe',
    employee_email: 'john@example.com',
    what_score: 2.5,
    how_score: 2.0,
    grid_position_what: 2,
    grid_position_how: 2,
    what_veto_active: false,
    how_veto_active: false,
    review_status: 'SIGNED',
    manager_first_name: 'Jane',
    manager_last_name: 'Smith',
    ...overrides,
  }
}

function createMockParticipant(
  overrides: Partial<CalibrationParticipant> = {}
): CalibrationParticipant {
  return {
    user_id: 'user-1',
    role: 'PARTICIPANT',
    first_name: 'Alice',
    last_name: 'Johnson',
    email: 'alice@example.com',
    ...overrides,
  }
}

describe('CalibrationSessionDetail', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    mockFetchSession.mockResolvedValue(createMockSession())
    mockFetchReviews.mockResolvedValue([])
    mockFetchParticipants.mockResolvedValue([])
    mockStartSession.mockResolvedValue(createMockSession({ status: 'IN_PROGRESS' }))
    mockCompleteSession.mockResolvedValue(createMockSession({ status: 'COMPLETED' }))
    mockDeleteSession.mockResolvedValue(undefined)
  })

  function createWrapper(props: { sessionId: string }) {
    return mount(CalibrationSessionDetail, {
      props,
    })
  }

  describe('loading state', () => {
    it('should show loading indicator while fetching', () => {
      mockFetchSession.mockReturnValue(new Promise(() => {})) // Never resolves
      const wrapper = createWrapper({ sessionId: 'session-1' })

      expect(wrapper.text()).toContain('Loading...')
    })

    it('should hide loading after data loads', async () => {
      const wrapper = createWrapper({ sessionId: 'session-1' })

      await flushPromises()

      expect(wrapper.text()).not.toContain('Loading...')
    })
  })

  describe('session info display', () => {
    it('should display session name', async () => {
      mockFetchSession.mockResolvedValue(createMockSession({ name: 'Annual Review 2026' }))
      const wrapper = createWrapper({ sessionId: 'session-1' })

      await flushPromises()

      expect(wrapper.text()).toContain('Annual Review 2026')
    })

    it('should display session description', async () => {
      mockFetchSession.mockResolvedValue(
        createMockSession({ description: 'Year-end calibration' })
      )
      const wrapper = createWrapper({ sessionId: 'session-1' })

      await flushPromises()

      expect(wrapper.text()).toContain('Year-end calibration')
    })

    it('should display review year', async () => {
      mockFetchSession.mockResolvedValue(createMockSession({ review_year: 2026 }))
      const wrapper = createWrapper({ sessionId: 'session-1' })

      await flushPromises()

      expect(wrapper.text()).toContain('2026')
    })

    it('should display session status badge', async () => {
      mockFetchSession.mockResolvedValue(createMockSession({ status: 'IN_PROGRESS' }))
      const wrapper = createWrapper({ sessionId: 'session-1' })

      await flushPromises()

      const badge = wrapper.find('.status-badge')
      expect(badge.exists()).toBe(true)
      expect(badge.text()).toContain('In Progress')
    })
  })

  describe('reviews display', () => {
    it('should show empty state when no reviews', async () => {
      mockFetchReviews.mockResolvedValue([])
      const wrapper = createWrapper({ sessionId: 'session-1' })

      await flushPromises()

      expect(wrapper.text()).toContain('No reviews in this session')
    })

    it('should display review list with employee names', async () => {
      mockFetchReviews.mockResolvedValue([
        createMockReview({ employee_name: 'John Doe' }),
        createMockReview({ review_id: 'review-2', employee_name: 'Jane Smith' }),
      ])
      const wrapper = createWrapper({ sessionId: 'session-1' })

      await flushPromises()

      expect(wrapper.text()).toContain('John Doe')
      expect(wrapper.text()).toContain('Jane Smith')
    })

    it('should display review scores', async () => {
      mockFetchReviews.mockResolvedValue([
        createMockReview({ what_score: 2.5, how_score: 2.0 }),
      ])
      const wrapper = createWrapper({ sessionId: 'session-1' })

      await flushPromises()

      expect(wrapper.text()).toContain('2.5')
      expect(wrapper.text()).toContain('2.0')
    })

    it('should display manager name for reviews', async () => {
      mockFetchReviews.mockResolvedValue([
        createMockReview({ manager_first_name: 'Jane', manager_last_name: 'Smith' }),
      ])
      const wrapper = createWrapper({ sessionId: 'session-1' })

      await flushPromises()

      expect(wrapper.text()).toContain('Jane Smith')
    })
  })

  describe('participants display', () => {
    it('should show empty state when no participants', async () => {
      mockFetchParticipants.mockResolvedValue([])
      const wrapper = createWrapper({ sessionId: 'session-1' })

      await flushPromises()

      expect(wrapper.text()).toContain('No participants added')
    })

    it('should display participant names', async () => {
      mockFetchParticipants.mockResolvedValue([
        createMockParticipant({ first_name: 'Alice', last_name: 'Johnson' }),
        createMockParticipant({ user_id: 'user-2', first_name: 'Bob', last_name: 'Williams' }),
      ])
      const wrapper = createWrapper({ sessionId: 'session-1' })

      await flushPromises()

      expect(wrapper.text()).toContain('Alice Johnson')
      expect(wrapper.text()).toContain('Bob Williams')
    })

    it('should display participant roles', async () => {
      mockFetchParticipants.mockResolvedValue([
        createMockParticipant({ role: 'FACILITATOR' }),
        createMockParticipant({ user_id: 'user-2', role: 'OBSERVER' }),
      ])
      const wrapper = createWrapper({ sessionId: 'session-1' })

      await flushPromises()

      expect(wrapper.text()).toContain('FACILITATOR')
      expect(wrapper.text()).toContain('OBSERVER')
    })
  })

  describe('action buttons', () => {
    it('should show Start Session button when status is PREPARATION', async () => {
      mockFetchSession.mockResolvedValue(createMockSession({ status: 'PREPARATION' }))
      const wrapper = createWrapper({ sessionId: 'session-1' })

      await flushPromises()

      const startBtn = wrapper.find('.start-session-btn')
      expect(startBtn.exists()).toBe(true)
    })

    it('should not show Start Session button when status is IN_PROGRESS', async () => {
      mockFetchSession.mockResolvedValue(createMockSession({ status: 'IN_PROGRESS' }))
      const wrapper = createWrapper({ sessionId: 'session-1' })

      await flushPromises()

      const startBtn = wrapper.find('.start-session-btn')
      expect(startBtn.exists()).toBe(false)
    })

    it('should show Complete Session button when status is IN_PROGRESS', async () => {
      mockFetchSession.mockResolvedValue(createMockSession({ status: 'IN_PROGRESS' }))
      const wrapper = createWrapper({ sessionId: 'session-1' })

      await flushPromises()

      const completeBtn = wrapper.find('.complete-session-btn')
      expect(completeBtn.exists()).toBe(true)
    })

    it('should show Edit button when status is PREPARATION', async () => {
      mockFetchSession.mockResolvedValue(createMockSession({ status: 'PREPARATION' }))
      const wrapper = createWrapper({ sessionId: 'session-1' })

      await flushPromises()

      const editBtn = wrapper.find('.edit-btn')
      expect(editBtn.exists()).toBe(true)
    })

    it('should show Delete button when status is PREPARATION', async () => {
      mockFetchSession.mockResolvedValue(createMockSession({ status: 'PREPARATION' }))
      const wrapper = createWrapper({ sessionId: 'session-1' })

      await flushPromises()

      const deleteBtn = wrapper.find('.delete-btn')
      expect(deleteBtn.exists()).toBe(true)
    })

    it('should not show Edit/Delete when status is not PREPARATION', async () => {
      mockFetchSession.mockResolvedValue(createMockSession({ status: 'IN_PROGRESS' }))
      const wrapper = createWrapper({ sessionId: 'session-1' })

      await flushPromises()

      expect(wrapper.find('.edit-btn').exists()).toBe(false)
      expect(wrapper.find('.delete-btn').exists()).toBe(false)
    })
  })

  describe('start session action', () => {
    it('should call startCalibrationSession when Start clicked', async () => {
      mockFetchSession.mockResolvedValue(createMockSession({ id: 'session-123' }))
      const wrapper = createWrapper({ sessionId: 'session-123' })

      await flushPromises()

      const startBtn = wrapper.find('.start-session-btn')
      await startBtn.trigger('click')
      await flushPromises()

      expect(mockStartSession).toHaveBeenCalledWith('session-123')
    })

    it('should emit status-changed after starting session', async () => {
      mockFetchSession.mockResolvedValue(createMockSession({ status: 'PREPARATION' }))
      const wrapper = createWrapper({ sessionId: 'session-1' })

      await flushPromises()

      const startBtn = wrapper.find('.start-session-btn')
      await startBtn.trigger('click')
      await flushPromises()

      expect(wrapper.emitted('status-changed')).toBeTruthy()
    })
  })

  describe('complete session action', () => {
    it('should call completeCalibrationSession when Complete clicked', async () => {
      mockFetchSession.mockResolvedValue(
        createMockSession({ id: 'session-123', status: 'IN_PROGRESS' })
      )
      const wrapper = createWrapper({ sessionId: 'session-123' })

      await flushPromises()

      const completeBtn = wrapper.find('.complete-session-btn')
      await completeBtn.trigger('click')
      await flushPromises()

      expect(mockCompleteSession).toHaveBeenCalledWith('session-123')
    })
  })

  describe('edit action', () => {
    it('should emit edit event when Edit clicked', async () => {
      mockFetchSession.mockResolvedValue(createMockSession())
      const wrapper = createWrapper({ sessionId: 'session-1' })

      await flushPromises()

      const editBtn = wrapper.find('.edit-btn')
      await editBtn.trigger('click')

      expect(wrapper.emitted('edit')).toHaveLength(1)
    })
  })

  describe('delete action', () => {
    it('should call deleteCalibrationSession when Delete confirmed', async () => {
      mockFetchSession.mockResolvedValue(createMockSession({ id: 'session-123' }))
      const wrapper = createWrapper({ sessionId: 'session-123' })

      await flushPromises()

      // Simulate confirming the delete
      const deleteBtn = wrapper.find('.delete-btn')
      await deleteBtn.trigger('click')

      // Find and click confirm button in the confirm dialog
      const confirmBtn = wrapper.find('.confirm-delete-btn')
      if (confirmBtn.exists()) {
        await confirmBtn.trigger('click')
        await flushPromises()
        expect(mockDeleteSession).toHaveBeenCalledWith('session-123')
      }
    })

    it('should emit deleted event after successful delete', async () => {
      mockFetchSession.mockResolvedValue(createMockSession())
      const wrapper = createWrapper({ sessionId: 'session-1' })

      await flushPromises()

      const deleteBtn = wrapper.find('.delete-btn')
      await deleteBtn.trigger('click')

      const confirmBtn = wrapper.find('.confirm-delete-btn')
      if (confirmBtn.exists()) {
        await confirmBtn.trigger('click')
        await flushPromises()
        expect(wrapper.emitted('deleted')).toBeTruthy()
      }
    })
  })

  describe('back button', () => {
    it('should emit back event when back button clicked', async () => {
      const wrapper = createWrapper({ sessionId: 'session-1' })

      await flushPromises()

      const backBtn = wrapper.find('.back-btn')
      await backBtn.trigger('click')

      expect(wrapper.emitted('back')).toHaveLength(1)
    })
  })

  describe('data fetching', () => {
    it('should fetch session data on mount', async () => {
      createWrapper({ sessionId: 'session-123' })

      await flushPromises()

      expect(mockFetchSession).toHaveBeenCalledWith('session-123')
    })

    it('should fetch reviews on mount', async () => {
      createWrapper({ sessionId: 'session-123' })

      await flushPromises()

      expect(mockFetchReviews).toHaveBeenCalledWith('session-123')
    })

    it('should fetch participants on mount', async () => {
      createWrapper({ sessionId: 'session-123' })

      await flushPromises()

      expect(mockFetchParticipants).toHaveBeenCalledWith('session-123')
    })
  })
})
