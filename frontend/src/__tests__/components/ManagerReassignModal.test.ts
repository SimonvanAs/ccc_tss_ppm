// TSS PPM v3.0 - ManagerReassignModal Component Tests
import { describe, it, expect, vi, beforeEach } from 'vitest'
import { mount } from '@vue/test-utils'
import ManagerReassignModal from '../../components/review/ManagerReassignModal.vue'

// Mock vue-i18n
vi.mock('vue-i18n', () => ({
  useI18n: () => ({
    t: (key: string) => key,
  }),
}))

const mockManagers = [
  { id: 'manager-1', name: 'John Smith' },
  { id: 'manager-2', name: 'Jane Doe' },
  { id: 'manager-3', name: 'Bob Wilson' },
]

describe('ManagerReassignModal', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  describe('modal rendering with manager dropdown', () => {
    it('should render modal when show is true', () => {
      const wrapper = mount(ManagerReassignModal, {
        props: {
          show: true,
          managers: mockManagers,
          currentManagerId: 'manager-1',
          loading: false,
        },
      })

      expect(wrapper.find('[data-testid="reassign-modal"]').exists()).toBe(true)
    })

    it('should not render modal when show is false', () => {
      const wrapper = mount(ManagerReassignModal, {
        props: {
          show: false,
          managers: mockManagers,
          currentManagerId: 'manager-1',
          loading: false,
        },
      })

      expect(wrapper.find('[data-testid="reassign-modal"]').exists()).toBe(false)
    })

    it('should render manager dropdown with all managers except current', () => {
      const wrapper = mount(ManagerReassignModal, {
        props: {
          show: true,
          managers: mockManagers,
          currentManagerId: 'manager-1',
          loading: false,
        },
      })

      const select = wrapper.find('[data-testid="manager-select"]')
      expect(select.exists()).toBe(true)

      const options = select.findAll('option')
      // Should have placeholder + 2 managers (excluding current)
      expect(options.length).toBe(3) // placeholder + 2 other managers
    })

    it('should exclude current manager from dropdown options', () => {
      const wrapper = mount(ManagerReassignModal, {
        props: {
          show: true,
          managers: mockManagers,
          currentManagerId: 'manager-1',
          loading: false,
        },
      })

      const select = wrapper.find('[data-testid="manager-select"]')
      const optionValues = select.findAll('option').map((o) => o.element.value)

      expect(optionValues).not.toContain('manager-1')
      expect(optionValues).toContain('manager-2')
      expect(optionValues).toContain('manager-3')
    })
  })

  describe('optional reason field', () => {
    it('should render reason textarea', () => {
      const wrapper = mount(ManagerReassignModal, {
        props: {
          show: true,
          managers: mockManagers,
          currentManagerId: 'manager-1',
          loading: false,
        },
      })

      expect(wrapper.find('[data-testid="reason-input"]').exists()).toBe(true)
    })

    it('should allow entering reason text', async () => {
      const wrapper = mount(ManagerReassignModal, {
        props: {
          show: true,
          managers: mockManagers,
          currentManagerId: 'manager-1',
          loading: false,
        },
      })

      const textarea = wrapper.find('[data-testid="reason-input"]')
      await textarea.setValue('Manager is on extended leave')

      expect((textarea.element as HTMLTextAreaElement).value).toBe(
        'Manager is on extended leave'
      )
    })
  })

  describe('submit and cancel actions', () => {
    it('should emit cancel event when cancel button clicked', async () => {
      const wrapper = mount(ManagerReassignModal, {
        props: {
          show: true,
          managers: mockManagers,
          currentManagerId: 'manager-1',
          loading: false,
        },
      })

      await wrapper.find('[data-testid="cancel-button"]').trigger('click')

      expect(wrapper.emitted('cancel')).toBeTruthy()
    })

    it('should disable submit button when no manager selected', () => {
      const wrapper = mount(ManagerReassignModal, {
        props: {
          show: true,
          managers: mockManagers,
          currentManagerId: 'manager-1',
          loading: false,
        },
      })

      const submitButton = wrapper.find('[data-testid="submit-button"]')
      expect(submitButton.attributes('disabled')).toBeDefined()
    })

    it('should enable submit button when manager is selected', async () => {
      const wrapper = mount(ManagerReassignModal, {
        props: {
          show: true,
          managers: mockManagers,
          currentManagerId: 'manager-1',
          loading: false,
        },
      })

      await wrapper.find('[data-testid="manager-select"]').setValue('manager-2')

      const submitButton = wrapper.find('[data-testid="submit-button"]')
      expect(submitButton.attributes('disabled')).toBeUndefined()
    })

    it('should emit submit event with manager id and reason when submitted', async () => {
      const wrapper = mount(ManagerReassignModal, {
        props: {
          show: true,
          managers: mockManagers,
          currentManagerId: 'manager-1',
          loading: false,
        },
      })

      await wrapper.find('[data-testid="manager-select"]').setValue('manager-2')
      await wrapper.find('[data-testid="reason-input"]').setValue('Transfer request')
      await wrapper.find('[data-testid="submit-button"]').trigger('click')

      expect(wrapper.emitted('submit')).toBeTruthy()
      expect(wrapper.emitted('submit')![0]).toEqual([
        { managerId: 'manager-2', reason: 'Transfer request' },
      ])
    })

    it('should emit submit with empty reason if not provided', async () => {
      const wrapper = mount(ManagerReassignModal, {
        props: {
          show: true,
          managers: mockManagers,
          currentManagerId: 'manager-1',
          loading: false,
        },
      })

      await wrapper.find('[data-testid="manager-select"]').setValue('manager-2')
      await wrapper.find('[data-testid="submit-button"]').trigger('click')

      expect(wrapper.emitted('submit')![0]).toEqual([
        { managerId: 'manager-2', reason: '' },
      ])
    })
  })

  describe('loading and error states', () => {
    it('should disable form controls when loading', () => {
      const wrapper = mount(ManagerReassignModal, {
        props: {
          show: true,
          managers: mockManagers,
          currentManagerId: 'manager-1',
          loading: true,
        },
      })

      expect(wrapper.find('[data-testid="manager-select"]').attributes('disabled')).toBeDefined()
      expect(wrapper.find('[data-testid="reason-input"]').attributes('disabled')).toBeDefined()
      expect(wrapper.find('[data-testid="cancel-button"]').attributes('disabled')).toBeDefined()
    })

    it('should show loading text on submit button when loading', async () => {
      const wrapper = mount(ManagerReassignModal, {
        props: {
          show: true,
          managers: mockManagers,
          currentManagerId: 'manager-1',
          loading: true,
        },
      })

      expect(wrapper.find('[data-testid="submit-button"]').text()).toContain(
        'managerReassign.submitting'
      )
    })

    it('should display error message when error prop is set', () => {
      const wrapper = mount(ManagerReassignModal, {
        props: {
          show: true,
          managers: mockManagers,
          currentManagerId: 'manager-1',
          loading: false,
          error: 'Failed to reassign manager',
        },
      })

      expect(wrapper.find('[data-testid="error-message"]').exists()).toBe(true)
      expect(wrapper.text()).toContain('Failed to reassign manager')
    })

    it('should not display error message when error prop is empty', () => {
      const wrapper = mount(ManagerReassignModal, {
        props: {
          show: true,
          managers: mockManagers,
          currentManagerId: 'manager-1',
          loading: false,
        },
      })

      expect(wrapper.find('[data-testid="error-message"]').exists()).toBe(false)
    })
  })

  describe('modal close behavior', () => {
    it('should emit cancel when clicking close button', async () => {
      const wrapper = mount(ManagerReassignModal, {
        props: {
          show: true,
          managers: mockManagers,
          currentManagerId: 'manager-1',
          loading: false,
        },
      })

      await wrapper.find('[data-testid="close-button"]').trigger('click')

      expect(wrapper.emitted('cancel')).toBeTruthy()
    })

    it('should reset form when modal is closed and reopened', async () => {
      const wrapper = mount(ManagerReassignModal, {
        props: {
          show: true,
          managers: mockManagers,
          currentManagerId: 'manager-1',
          loading: false,
        },
      })

      // Fill form
      await wrapper.find('[data-testid="manager-select"]').setValue('manager-2')
      await wrapper.find('[data-testid="reason-input"]').setValue('Some reason')

      // Close modal
      await wrapper.setProps({ show: false })

      // Reopen modal
      await wrapper.setProps({ show: true })

      // Check form is reset
      const select = wrapper.find('[data-testid="manager-select"]')
      expect((select.element as HTMLSelectElement).value).toBe('')
    })
  })
})
