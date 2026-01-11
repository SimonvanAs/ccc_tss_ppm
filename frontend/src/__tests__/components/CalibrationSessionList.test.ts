// TSS PPM v3.0 - CalibrationSessionList Tests
import { describe, it, expect, vi, beforeEach } from 'vitest'
import { mount, flushPromises } from '@vue/test-utils'
import CalibrationSessionList from '../../components/calibration/CalibrationSessionList.vue'
import type { CalibrationSession } from '../../api/calibration'

// Mock vue-i18n
vi.mock('vue-i18n', () => ({
  useI18n: () => ({
    t: (key: string) => {
      const messages: Record<string, string> = {
        'calibration.sessions.title': 'Calibration Sessions',
        'calibration.sessions.createNew': 'Create New Session',
        'calibration.sessions.filterByStatus': 'Filter by Status',
        'calibration.sessions.allStatuses': 'All Statuses',
        'calibration.sessions.noSessions': 'No calibration sessions found',
        'calibration.sessions.loading': 'Loading sessions...',
        'calibration.status.PREPARATION': 'Preparation',
        'calibration.status.IN_PROGRESS': 'In Progress',
        'calibration.status.PENDING_APPROVAL': 'Pending Approval',
        'calibration.status.COMPLETED': 'Completed',
        'calibration.status.CANCELLED': 'Cancelled',
      }
      return messages[key] || key
    },
  }),
}))

// Mock the API
const mockFetchSessions = vi.fn()
vi.mock('../../api/calibration', () => ({
  fetchCalibrationSessions: () => mockFetchSessions(),
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

describe('CalibrationSessionList', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    mockFetchSessions.mockResolvedValue([])
  })

  function createWrapper() {
    return mount(CalibrationSessionList, {
      global: {
        stubs: {
          RouterLink: {
            template: '<a><slot /></a>',
            props: ['to'],
          },
        },
      },
    })
  }

  describe('loading state', () => {
    it('should show loading indicator while fetching', () => {
      mockFetchSessions.mockReturnValue(new Promise(() => {})) // Never resolves
      const wrapper = createWrapper()

      expect(wrapper.text()).toContain('Loading sessions...')
    })

    it('should hide loading indicator after fetch completes', async () => {
      mockFetchSessions.mockResolvedValue([])
      const wrapper = createWrapper()

      await flushPromises()

      expect(wrapper.text()).not.toContain('Loading sessions...')
    })
  })

  describe('session list rendering', () => {
    it('should display list of sessions', async () => {
      const sessions = [
        createMockSession({ id: '1', name: 'Session 1' }),
        createMockSession({ id: '2', name: 'Session 2' }),
      ]
      mockFetchSessions.mockResolvedValue(sessions)

      const wrapper = createWrapper()
      await flushPromises()

      expect(wrapper.text()).toContain('Session 1')
      expect(wrapper.text()).toContain('Session 2')
    })

    it('should show empty state when no sessions', async () => {
      mockFetchSessions.mockResolvedValue([])
      const wrapper = createWrapper()

      await flushPromises()

      expect(wrapper.text()).toContain('No calibration sessions found')
    })

    it('should display session review year', async () => {
      mockFetchSessions.mockResolvedValue([createMockSession({ review_year: 2026 })])
      const wrapper = createWrapper()

      await flushPromises()

      expect(wrapper.text()).toContain('2026')
    })

    it('should display session scope', async () => {
      mockFetchSessions.mockResolvedValue([createMockSession({ scope: 'COMPANY_WIDE' })])
      const wrapper = createWrapper()

      await flushPromises()

      expect(wrapper.text()).toContain('COMPANY_WIDE')
    })
  })

  describe('status badge rendering', () => {
    it('should show PREPARATION status badge', async () => {
      mockFetchSessions.mockResolvedValue([createMockSession({ status: 'PREPARATION' })])
      const wrapper = createWrapper()

      await flushPromises()

      const badge = wrapper.find('.status-badge')
      expect(badge.exists()).toBe(true)
      expect(badge.text()).toContain('Preparation')
      expect(badge.classes()).toContain('status-preparation')
    })

    it('should show IN_PROGRESS status badge', async () => {
      mockFetchSessions.mockResolvedValue([createMockSession({ status: 'IN_PROGRESS' })])
      const wrapper = createWrapper()

      await flushPromises()

      const badge = wrapper.find('.status-badge')
      expect(badge.text()).toContain('In Progress')
      expect(badge.classes()).toContain('status-in-progress')
    })

    it('should show COMPLETED status badge', async () => {
      mockFetchSessions.mockResolvedValue([createMockSession({ status: 'COMPLETED' })])
      const wrapper = createWrapper()

      await flushPromises()

      const badge = wrapper.find('.status-badge')
      expect(badge.text()).toContain('Completed')
      expect(badge.classes()).toContain('status-completed')
    })
  })

  describe('status filter', () => {
    it('should render status filter dropdown', async () => {
      mockFetchSessions.mockResolvedValue([])
      const wrapper = createWrapper()

      await flushPromises()

      const select = wrapper.find('select.status-filter')
      expect(select.exists()).toBe(true)
    })

    it('should filter sessions when status selected', async () => {
      mockFetchSessions.mockResolvedValue([
        createMockSession({ id: '1', status: 'PREPARATION' }),
        createMockSession({ id: '2', status: 'COMPLETED' }),
      ])
      const wrapper = createWrapper()

      await flushPromises()

      // Initially shows both
      expect(wrapper.findAll('.session-card')).toHaveLength(2)

      // Filter by PREPARATION
      const select = wrapper.find('select.status-filter')
      await select.setValue('PREPARATION')

      // Should only show PREPARATION sessions
      expect(wrapper.findAll('.session-card')).toHaveLength(1)
    })

    it('should show all sessions when filter cleared', async () => {
      mockFetchSessions.mockResolvedValue([
        createMockSession({ id: '1', status: 'PREPARATION' }),
        createMockSession({ id: '2', status: 'COMPLETED' }),
      ])
      const wrapper = createWrapper()

      await flushPromises()

      const select = wrapper.find('select.status-filter')
      await select.setValue('PREPARATION')
      expect(wrapper.findAll('.session-card')).toHaveLength(1)

      await select.setValue('')
      expect(wrapper.findAll('.session-card')).toHaveLength(2)
    })
  })

  describe('create session button', () => {
    it('should render create new session button', async () => {
      mockFetchSessions.mockResolvedValue([])
      const wrapper = createWrapper()

      await flushPromises()

      const button = wrapper.find('.create-session-btn')
      expect(button.exists()).toBe(true)
      expect(button.text()).toContain('Create New Session')
    })

    it('should emit create event when button clicked', async () => {
      mockFetchSessions.mockResolvedValue([])
      const wrapper = createWrapper()

      await flushPromises()

      const button = wrapper.find('.create-session-btn')
      await button.trigger('click')

      expect(wrapper.emitted('create')).toHaveLength(1)
    })
  })

  describe('session card click', () => {
    it('should emit select event with session when card clicked', async () => {
      const session = createMockSession({ id: 'session-1' })
      mockFetchSessions.mockResolvedValue([session])
      const wrapper = createWrapper()

      await flushPromises()

      const card = wrapper.find('.session-card')
      await card.trigger('click')

      expect(wrapper.emitted('select')).toHaveLength(1)
      expect(wrapper.emitted('select')![0]).toEqual([session])
    })
  })

  describe('date formatting', () => {
    it('should display formatted created date', async () => {
      mockFetchSessions.mockResolvedValue([
        createMockSession({ created_at: '2026-01-10T10:30:00Z' }),
      ])
      const wrapper = createWrapper()

      await flushPromises()

      // Should contain some date representation
      expect(wrapper.text()).toMatch(/2026|Jan|10/)
    })
  })
})
