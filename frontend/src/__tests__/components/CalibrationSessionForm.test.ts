// TSS PPM v3.0 - CalibrationSessionForm Tests
import { describe, it, expect, vi, beforeEach } from 'vitest'
import { mount, flushPromises } from '@vue/test-utils'
import CalibrationSessionForm from '../../components/calibration/CalibrationSessionForm.vue'
import type { CalibrationSession } from '../../api/calibration'

// Mock vue-i18n
vi.mock('vue-i18n', () => ({
  useI18n: () => ({
    t: (key: string) => {
      const messages: Record<string, string> = {
        'calibration.form.title.create': 'Create Calibration Session',
        'calibration.form.title.edit': 'Edit Calibration Session',
        'calibration.form.name': 'Session Name',
        'calibration.form.namePlaceholder': 'Enter session name',
        'calibration.form.description': 'Description',
        'calibration.form.descriptionPlaceholder': 'Enter description',
        'calibration.form.reviewYear': 'Review Year',
        'calibration.form.scope': 'Scope',
        'calibration.form.scope.BUSINESS_UNIT': 'Business Unit',
        'calibration.form.scope.COMPANY_WIDE': 'Company Wide',
        'calibration.form.submit.create': 'Create Session',
        'calibration.form.submit.edit': 'Save Changes',
        'calibration.form.cancel': 'Cancel',
        'calibration.form.validation.nameRequired': 'Session name is required',
        'calibration.form.validation.yearRequired': 'Review year is required',
      }
      return messages[key] || key
    },
  }),
}))

// Mock the API
const mockCreateSession = vi.fn()
const mockUpdateSession = vi.fn()
vi.mock('../../api/calibration', () => ({
  createCalibrationSession: (data: unknown) => mockCreateSession(data),
  updateCalibrationSession: (id: string, data: unknown) => mockUpdateSession(id, data),
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

describe('CalibrationSessionForm', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    mockCreateSession.mockResolvedValue(createMockSession())
    mockUpdateSession.mockResolvedValue(createMockSession())
  })

  function createWrapper(props: { session?: CalibrationSession } = {}) {
    return mount(CalibrationSessionForm, {
      props,
    })
  }

  describe('form rendering', () => {
    it('should render name input field', () => {
      const wrapper = createWrapper()

      const nameInput = wrapper.find('input[name="name"]')
      expect(nameInput.exists()).toBe(true)
    })

    it('should render description textarea', () => {
      const wrapper = createWrapper()

      const descInput = wrapper.find('textarea[name="description"]')
      expect(descInput.exists()).toBe(true)
    })

    it('should render review year input', () => {
      const wrapper = createWrapper()

      const yearInput = wrapper.find('input[name="reviewYear"]')
      expect(yearInput.exists()).toBe(true)
    })

    it('should render scope select', () => {
      const wrapper = createWrapper()

      const scopeSelect = wrapper.find('select[name="scope"]')
      expect(scopeSelect.exists()).toBe(true)
    })

    it('should show create title when no session prop', () => {
      const wrapper = createWrapper()

      expect(wrapper.text()).toContain('Create Calibration Session')
    })

    it('should show edit title when session prop provided', () => {
      const wrapper = createWrapper({ session: createMockSession() })

      expect(wrapper.text()).toContain('Edit Calibration Session')
    })
  })

  describe('edit mode population', () => {
    it('should populate name from session prop', () => {
      const wrapper = createWrapper({
        session: createMockSession({ name: 'Test Session' }),
      })

      const nameInput = wrapper.find('input[name="name"]')
      expect((nameInput.element as HTMLInputElement).value).toBe('Test Session')
    })

    it('should populate description from session prop', () => {
      const wrapper = createWrapper({
        session: createMockSession({ description: 'Test description' }),
      })

      const descInput = wrapper.find('textarea[name="description"]')
      expect((descInput.element as HTMLTextAreaElement).value).toBe('Test description')
    })

    it('should populate review year from session prop', () => {
      const wrapper = createWrapper({
        session: createMockSession({ review_year: 2025 }),
      })

      const yearInput = wrapper.find('input[name="reviewYear"]')
      expect((yearInput.element as HTMLInputElement).value).toBe('2025')
    })

    it('should populate scope from session prop', () => {
      const wrapper = createWrapper({
        session: createMockSession({ scope: 'BUSINESS_UNIT' }),
      })

      const scopeSelect = wrapper.find('select[name="scope"]')
      expect((scopeSelect.element as HTMLSelectElement).value).toBe('BUSINESS_UNIT')
    })
  })

  describe('validation', () => {
    it('should show error when name is empty on submit', async () => {
      const wrapper = createWrapper()

      const form = wrapper.find('form')
      await form.trigger('submit')

      expect(wrapper.text()).toContain('Session name is required')
    })

    it('should show error when year is empty on submit', async () => {
      const wrapper = createWrapper()

      // Fill in name but not year
      await wrapper.find('input[name="name"]').setValue('Test Session')
      await wrapper.find('input[name="reviewYear"]').setValue('')

      const form = wrapper.find('form')
      await form.trigger('submit')

      expect(wrapper.text()).toContain('Review year is required')
    })

    it('should not submit when validation fails', async () => {
      const wrapper = createWrapper()

      const form = wrapper.find('form')
      await form.trigger('submit')

      expect(mockCreateSession).not.toHaveBeenCalled()
    })
  })

  describe('form submission - create mode', () => {
    it('should call createCalibrationSession with form data', async () => {
      const wrapper = createWrapper()

      await wrapper.find('input[name="name"]').setValue('New Session')
      await wrapper.find('textarea[name="description"]').setValue('Test description')
      await wrapper.find('input[name="reviewYear"]').setValue('2026')
      await wrapper.find('select[name="scope"]').setValue('COMPANY_WIDE')

      const form = wrapper.find('form')
      await form.trigger('submit')
      await flushPromises()

      expect(mockCreateSession).toHaveBeenCalledWith({
        name: 'New Session',
        description: 'Test description',
        review_year: 2026,
        scope: 'COMPANY_WIDE',
      })
    })

    it('should emit success event after successful create', async () => {
      const wrapper = createWrapper()

      await wrapper.find('input[name="name"]').setValue('New Session')
      await wrapper.find('input[name="reviewYear"]').setValue('2026')

      const form = wrapper.find('form')
      await form.trigger('submit')
      await flushPromises()

      expect(wrapper.emitted('success')).toHaveLength(1)
    })

    it('should show create button text in create mode', () => {
      const wrapper = createWrapper()

      const submitBtn = wrapper.find('button[type="submit"]')
      expect(submitBtn.text()).toContain('Create Session')
    })
  })

  describe('form submission - edit mode', () => {
    it('should call updateCalibrationSession with session id and form data', async () => {
      const session = createMockSession({ id: 'session-123', name: 'Old Name' })
      const wrapper = createWrapper({ session })

      await wrapper.find('input[name="name"]').setValue('Updated Name')

      const form = wrapper.find('form')
      await form.trigger('submit')
      await flushPromises()

      expect(mockUpdateSession).toHaveBeenCalledWith('session-123', expect.objectContaining({
        name: 'Updated Name',
      }))
    })

    it('should show save button text in edit mode', () => {
      const wrapper = createWrapper({ session: createMockSession() })

      const submitBtn = wrapper.find('button[type="submit"]')
      expect(submitBtn.text()).toContain('Save Changes')
    })
  })

  describe('cancel button', () => {
    it('should emit cancel event when cancel clicked', async () => {
      const wrapper = createWrapper()

      const cancelBtn = wrapper.find('.cancel-btn')
      await cancelBtn.trigger('click')

      expect(wrapper.emitted('cancel')).toHaveLength(1)
    })
  })

  describe('loading state', () => {
    it('should disable submit button while submitting', async () => {
      mockCreateSession.mockReturnValue(new Promise(() => {})) // Never resolves
      const wrapper = createWrapper()

      await wrapper.find('input[name="name"]').setValue('Test')
      await wrapper.find('input[name="reviewYear"]').setValue('2026')

      const form = wrapper.find('form')
      await form.trigger('submit')

      const submitBtn = wrapper.find('button[type="submit"]')
      expect((submitBtn.element as HTMLButtonElement).disabled).toBe(true)
    })
  })
})
