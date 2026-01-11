// TSS PPM v3.0 - UserDetailModal Component Tests
import { describe, it, expect, vi, beforeEach } from 'vitest'
import { mount, flushPromises } from '@vue/test-utils'
import UserDetailModal from '../../../components/admin/UserDetailModal.vue'
import type { AdminUser } from '../../../api/admin'

// Mock vue-i18n
vi.mock('vue-i18n', () => ({
  useI18n: () => ({
    t: (key: string) => {
      const translations: Record<string, string> = {
        'admin.users.editUser': 'Edit User',
        'admin.users.name': 'Name',
        'admin.users.email': 'Email',
        'admin.users.functionTitle': 'Function Title',
        'admin.users.tovLevel': 'TOV Level',
        'admin.users.roles': 'Roles',
        'admin.users.manager': 'Manager',
        'admin.users.selectManager': 'Select a manager',
        'admin.users.save': 'Save',
        'admin.users.cancel': 'Cancel',
        'admin.users.saving': 'Saving...',
        'roles.employee': 'Employee',
        'roles.manager': 'Manager',
        'roles.hr': 'HR',
        'roles.admin': 'Admin',
      }
      return translations[key] || key
    },
  }),
}))

const mockUser: AdminUser = {
  id: 'user-1',
  email: 'john.doe@tss.eu',
  first_name: 'John',
  last_name: 'Doe',
  enabled: true,
  roles: ['employee', 'manager'],
  function_title: 'Software Engineer',
  tov_level: 'B',
  manager_id: 'manager-1',
  opco_id: 'opco-1',
}

const mockManagers: AdminUser[] = [
  {
    id: 'manager-1',
    email: 'alice.manager@tss.eu',
    first_name: 'Alice',
    last_name: 'Manager',
    enabled: true,
    roles: ['manager'],
    function_title: 'Team Lead',
    tov_level: 'A',
    manager_id: null,
    opco_id: 'opco-1',
  },
  {
    id: 'manager-2',
    email: 'bob.manager@tss.eu',
    first_name: 'Bob',
    last_name: 'Manager',
    enabled: true,
    roles: ['manager'],
    function_title: 'Director',
    tov_level: 'A',
    manager_id: null,
    opco_id: 'opco-1',
  },
]

describe('UserDetailModal', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  describe('modal rendering', () => {
    it('should not render when show is false', () => {
      const wrapper = mount(UserDetailModal, {
        props: {
          show: false,
          user: mockUser,
          managers: mockManagers,
          loading: false,
        },
      })

      expect(wrapper.find('.modal-overlay').exists()).toBe(false)
    })

    it('should render when show is true', () => {
      const wrapper = mount(UserDetailModal, {
        props: {
          show: true,
          user: mockUser,
          managers: mockManagers,
          loading: false,
        },
      })

      expect(wrapper.find('.modal-overlay').exists()).toBe(true)
    })

    it('should display user name in header', () => {
      const wrapper = mount(UserDetailModal, {
        props: {
          show: true,
          user: mockUser,
          managers: mockManagers,
          loading: false,
        },
      })

      expect(wrapper.text()).toContain('John Doe')
    })

    it('should display user email', () => {
      const wrapper = mount(UserDetailModal, {
        props: {
          show: true,
          user: mockUser,
          managers: mockManagers,
          loading: false,
        },
      })

      expect(wrapper.text()).toContain('john.doe@tss.eu')
    })

    it('should display function title', () => {
      const wrapper = mount(UserDetailModal, {
        props: {
          show: true,
          user: mockUser,
          managers: mockManagers,
          loading: false,
        },
      })

      expect(wrapper.text()).toContain('Software Engineer')
    })

    it('should display TOV level', () => {
      const wrapper = mount(UserDetailModal, {
        props: {
          show: true,
          user: mockUser,
          managers: mockManagers,
          loading: false,
        },
      })

      expect(wrapper.text()).toContain('B')
    })
  })

  describe('role checkboxes', () => {
    it('should render checkboxes for each role', () => {
      const wrapper = mount(UserDetailModal, {
        props: {
          show: true,
          user: mockUser,
          managers: mockManagers,
          loading: false,
        },
      })

      const checkboxes = wrapper.findAll('input[type="checkbox"]')
      expect(checkboxes.length).toBe(4) // employee, manager, hr, admin
    })

    it('should have checked checkboxes for user roles', () => {
      const wrapper = mount(UserDetailModal, {
        props: {
          show: true,
          user: mockUser,
          managers: mockManagers,
          loading: false,
        },
      })

      const employeeCheckbox = wrapper.find('input[value="employee"]')
      const managerCheckbox = wrapper.find('input[value="manager"]')
      const hrCheckbox = wrapper.find('input[value="hr"]')

      expect((employeeCheckbox.element as HTMLInputElement).checked).toBe(true)
      expect((managerCheckbox.element as HTMLInputElement).checked).toBe(true)
      expect((hrCheckbox.element as HTMLInputElement).checked).toBe(false)
    })

    it('should toggle role when checkbox clicked', async () => {
      const wrapper = mount(UserDetailModal, {
        props: {
          show: true,
          user: mockUser,
          managers: mockManagers,
          loading: false,
        },
      })

      const hrCheckbox = wrapper.find('input[value="hr"]')
      await hrCheckbox.setValue(true)

      expect((hrCheckbox.element as HTMLInputElement).checked).toBe(true)
    })
  })

  describe('manager dropdown', () => {
    it('should render manager dropdown', () => {
      const wrapper = mount(UserDetailModal, {
        props: {
          show: true,
          user: mockUser,
          managers: mockManagers,
          loading: false,
        },
      })

      const managerSelect = wrapper.find('[data-testid="manager-select"]')
      expect(managerSelect.exists()).toBe(true)
    })

    it('should have options for each manager', () => {
      const wrapper = mount(UserDetailModal, {
        props: {
          show: true,
          user: mockUser,
          managers: mockManagers,
          loading: false,
        },
      })

      const options = wrapper.findAll('[data-testid="manager-select"] option')
      // placeholder + 2 managers
      expect(options.length).toBe(3)
    })

    it('should have current manager selected', () => {
      const wrapper = mount(UserDetailModal, {
        props: {
          show: true,
          user: mockUser,
          managers: mockManagers,
          loading: false,
        },
      })

      const managerSelect = wrapper.find('[data-testid="manager-select"]')
      expect((managerSelect.element as HTMLSelectElement).value).toBe('manager-1')
    })

    it('should allow changing manager', async () => {
      const wrapper = mount(UserDetailModal, {
        props: {
          show: true,
          user: mockUser,
          managers: mockManagers,
          loading: false,
        },
      })

      const managerSelect = wrapper.find('[data-testid="manager-select"]')
      await managerSelect.setValue('manager-2')

      expect((managerSelect.element as HTMLSelectElement).value).toBe('manager-2')
    })
  })

  describe('save action', () => {
    it('should have save button', () => {
      const wrapper = mount(UserDetailModal, {
        props: {
          show: true,
          user: mockUser,
          managers: mockManagers,
          loading: false,
        },
      })

      const saveButton = wrapper.find('[data-testid="save-button"]')
      expect(saveButton.exists()).toBe(true)
    })

    it('should emit save event with updated data on save', async () => {
      const wrapper = mount(UserDetailModal, {
        props: {
          show: true,
          user: mockUser,
          managers: mockManagers,
          loading: false,
        },
      })

      // Add HR role
      const hrCheckbox = wrapper.find('input[value="hr"]')
      await hrCheckbox.setValue(true)

      // Change manager
      const managerSelect = wrapper.find('[data-testid="manager-select"]')
      await managerSelect.setValue('manager-2')

      // Click save
      const saveButton = wrapper.find('[data-testid="save-button"]')
      await saveButton.trigger('click')

      expect(wrapper.emitted('save')).toBeTruthy()
      const emittedData = wrapper.emitted('save')![0][0] as {
        roles: string[]
        managerId: string
      }
      expect(emittedData.roles).toContain('hr')
      expect(emittedData.managerId).toBe('manager-2')
    })

    it('should disable save button when loading', () => {
      const wrapper = mount(UserDetailModal, {
        props: {
          show: true,
          user: mockUser,
          managers: mockManagers,
          loading: true,
        },
      })

      const saveButton = wrapper.find('[data-testid="save-button"]')
      expect(saveButton.attributes('disabled')).toBeDefined()
    })

    it('should show saving text when loading', () => {
      const wrapper = mount(UserDetailModal, {
        props: {
          show: true,
          user: mockUser,
          managers: mockManagers,
          loading: true,
        },
      })

      const saveButton = wrapper.find('[data-testid="save-button"]')
      expect(saveButton.text()).toContain('Saving')
    })
  })

  describe('cancel action', () => {
    it('should have cancel button', () => {
      const wrapper = mount(UserDetailModal, {
        props: {
          show: true,
          user: mockUser,
          managers: mockManagers,
          loading: false,
        },
      })

      const cancelButton = wrapper.find('[data-testid="cancel-button"]')
      expect(cancelButton.exists()).toBe(true)
    })

    it('should emit cancel event on cancel', async () => {
      const wrapper = mount(UserDetailModal, {
        props: {
          show: true,
          user: mockUser,
          managers: mockManagers,
          loading: false,
        },
      })

      const cancelButton = wrapper.find('[data-testid="cancel-button"]')
      await cancelButton.trigger('click')

      expect(wrapper.emitted('cancel')).toBeTruthy()
    })

    it('should emit cancel on overlay click', async () => {
      const wrapper = mount(UserDetailModal, {
        props: {
          show: true,
          user: mockUser,
          managers: mockManagers,
          loading: false,
        },
      })

      const overlay = wrapper.find('.modal-overlay')
      await overlay.trigger('click')

      expect(wrapper.emitted('cancel')).toBeTruthy()
    })

    it('should not emit cancel when clicking modal content', async () => {
      const wrapper = mount(UserDetailModal, {
        props: {
          show: true,
          user: mockUser,
          managers: mockManagers,
          loading: false,
        },
      })

      const content = wrapper.find('.modal-content')
      await content.trigger('click')

      expect(wrapper.emitted('cancel')).toBeFalsy()
    })
  })

  describe('error display', () => {
    it('should display error message when provided', () => {
      const wrapper = mount(UserDetailModal, {
        props: {
          show: true,
          user: mockUser,
          managers: mockManagers,
          loading: false,
          error: 'Failed to save user',
        },
      })

      expect(wrapper.text()).toContain('Failed to save user')
    })
  })
})
