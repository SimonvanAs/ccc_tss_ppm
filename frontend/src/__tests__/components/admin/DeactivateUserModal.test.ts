// TSS PPM v3.0 - DeactivateUserModal Component Tests
import { describe, it, expect, vi, beforeEach } from 'vitest'
import { mount } from '@vue/test-utils'
import DeactivateUserModal from '../../../components/admin/DeactivateUserModal.vue'
import type { AdminUser } from '../../../api/admin'

// Mock vue-i18n
vi.mock('vue-i18n', () => ({
  useI18n: () => ({
    t: (key: string, params?: Record<string, string>) => {
      const translations: Record<string, string> = {
        'admin.users.deactivateUser': 'Deactivate User',
        'admin.users.activateUser': 'Activate User',
        'admin.users.deactivateConfirm': `Are you sure you want to deactivate ${params?.name || 'this user'}?`,
        'admin.users.activateConfirm': `Are you sure you want to activate ${params?.name || 'this user'}?`,
        'admin.users.deactivateWarning': 'This user will no longer be able to log in.',
        'admin.users.activateWarning': 'This user will be able to log in again.',
        'admin.users.confirm': 'Confirm',
        'admin.users.cancel': 'Cancel',
        'admin.users.processing': 'Processing...',
      }
      return translations[key] || key
    },
  }),
}))

const mockActiveUser: AdminUser = {
  id: 'user-1',
  email: 'john.doe@tss.eu',
  first_name: 'John',
  last_name: 'Doe',
  enabled: true,
  roles: ['employee'],
  function_title: 'Software Engineer',
  tov_level: 'B',
  manager_id: 'manager-1',
  opco_id: 'opco-1',
}

const mockInactiveUser: AdminUser = {
  ...mockActiveUser,
  id: 'user-2',
  enabled: false,
}

describe('DeactivateUserModal', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  describe('modal rendering', () => {
    it('should not render when show is false', () => {
      const wrapper = mount(DeactivateUserModal, {
        props: {
          show: false,
          user: mockActiveUser,
          loading: false,
        },
      })

      expect(wrapper.find('.modal-overlay').exists()).toBe(false)
    })

    it('should render when show is true', () => {
      const wrapper = mount(DeactivateUserModal, {
        props: {
          show: true,
          user: mockActiveUser,
          loading: false,
        },
      })

      expect(wrapper.find('.modal-overlay').exists()).toBe(true)
    })

    it('should show deactivate title for active user', () => {
      const wrapper = mount(DeactivateUserModal, {
        props: {
          show: true,
          user: mockActiveUser,
          loading: false,
        },
      })

      expect(wrapper.text()).toContain('Deactivate User')
    })

    it('should show activate title for inactive user', () => {
      const wrapper = mount(DeactivateUserModal, {
        props: {
          show: true,
          user: mockInactiveUser,
          loading: false,
        },
      })

      expect(wrapper.text()).toContain('Activate User')
    })

    it('should show user name in confirmation message', () => {
      const wrapper = mount(DeactivateUserModal, {
        props: {
          show: true,
          user: mockActiveUser,
          loading: false,
        },
      })

      expect(wrapper.text()).toContain('John Doe')
    })

    it('should show warning about login access', () => {
      const wrapper = mount(DeactivateUserModal, {
        props: {
          show: true,
          user: mockActiveUser,
          loading: false,
        },
      })

      expect(wrapper.text()).toContain('will no longer be able to log in')
    })
  })

  describe('confirm action', () => {
    it('should have confirm button', () => {
      const wrapper = mount(DeactivateUserModal, {
        props: {
          show: true,
          user: mockActiveUser,
          loading: false,
        },
      })

      const confirmButton = wrapper.find('[data-testid="confirm-button"]')
      expect(confirmButton.exists()).toBe(true)
    })

    it('should emit confirm event on confirm click', async () => {
      const wrapper = mount(DeactivateUserModal, {
        props: {
          show: true,
          user: mockActiveUser,
          loading: false,
        },
      })

      const confirmButton = wrapper.find('[data-testid="confirm-button"]')
      await confirmButton.trigger('click')

      expect(wrapper.emitted('confirm')).toBeTruthy()
    })

    it('should disable confirm button when loading', () => {
      const wrapper = mount(DeactivateUserModal, {
        props: {
          show: true,
          user: mockActiveUser,
          loading: true,
        },
      })

      const confirmButton = wrapper.find('[data-testid="confirm-button"]')
      expect(confirmButton.attributes('disabled')).toBeDefined()
    })

    it('should show processing text when loading', () => {
      const wrapper = mount(DeactivateUserModal, {
        props: {
          show: true,
          user: mockActiveUser,
          loading: true,
        },
      })

      const confirmButton = wrapper.find('[data-testid="confirm-button"]')
      expect(confirmButton.text()).toContain('Processing')
    })
  })

  describe('cancel action', () => {
    it('should have cancel button', () => {
      const wrapper = mount(DeactivateUserModal, {
        props: {
          show: true,
          user: mockActiveUser,
          loading: false,
        },
      })

      const cancelButton = wrapper.find('[data-testid="cancel-button"]')
      expect(cancelButton.exists()).toBe(true)
    })

    it('should emit cancel event on cancel click', async () => {
      const wrapper = mount(DeactivateUserModal, {
        props: {
          show: true,
          user: mockActiveUser,
          loading: false,
        },
      })

      const cancelButton = wrapper.find('[data-testid="cancel-button"]')
      await cancelButton.trigger('click')

      expect(wrapper.emitted('cancel')).toBeTruthy()
    })

    it('should emit cancel on overlay click', async () => {
      const wrapper = mount(DeactivateUserModal, {
        props: {
          show: true,
          user: mockActiveUser,
          loading: false,
        },
      })

      const overlay = wrapper.find('.modal-overlay')
      await overlay.trigger('click')

      expect(wrapper.emitted('cancel')).toBeTruthy()
    })
  })
})
