// TSS PPM v3.0 - BulkActionBar Component Tests
import { describe, it, expect, vi, beforeEach } from 'vitest'
import { mount } from '@vue/test-utils'
import BulkActionBar from '../../../components/admin/BulkActionBar.vue'
import type { AdminUser } from '../../../api/admin'

// Mock vue-i18n
vi.mock('vue-i18n', () => ({
  useI18n: () => ({
    t: (key: string, params?: Record<string, number>) => {
      const translations: Record<string, string> = {
        'admin.users.selectedCount': `${params?.count || 0} user(s) selected`,
        'admin.users.bulkAssignRole': 'Assign Role',
        'admin.users.bulkRemoveRole': 'Remove Role',
        'admin.users.bulkAssignManager': 'Assign Manager',
        'admin.users.clearSelection': 'Clear Selection',
        'admin.users.selectRole': 'Select role',
        'admin.users.selectManager': 'Select manager',
        'admin.users.apply': 'Apply',
        'roles.employee': 'Employee',
        'roles.manager': 'Manager',
        'roles.hr': 'HR',
        'roles.admin': 'Admin',
      }
      return translations[key] || key
    },
  }),
}))

const mockManagers: AdminUser[] = [
  {
    id: 'manager-1',
    email: 'alice@tss.eu',
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
    email: 'bob@tss.eu',
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

describe('BulkActionBar', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  describe('selection count display', () => {
    it('should not render when no users selected', () => {
      const wrapper = mount(BulkActionBar, {
        props: {
          selectedCount: 0,
          managers: mockManagers,
          loading: false,
        },
      })

      expect(wrapper.find('.bulk-action-bar').exists()).toBe(false)
    })

    it('should render when users are selected', () => {
      const wrapper = mount(BulkActionBar, {
        props: {
          selectedCount: 3,
          managers: mockManagers,
          loading: false,
        },
      })

      expect(wrapper.find('.bulk-action-bar').exists()).toBe(true)
    })

    it('should display selected count', () => {
      const wrapper = mount(BulkActionBar, {
        props: {
          selectedCount: 5,
          managers: mockManagers,
          loading: false,
        },
      })

      expect(wrapper.text()).toContain('5 user(s) selected')
    })

    it('should have clear selection button', () => {
      const wrapper = mount(BulkActionBar, {
        props: {
          selectedCount: 3,
          managers: mockManagers,
          loading: false,
        },
      })

      const clearButton = wrapper.find('[data-testid="clear-selection"]')
      expect(clearButton.exists()).toBe(true)
    })

    it('should emit clear event on clear button click', async () => {
      const wrapper = mount(BulkActionBar, {
        props: {
          selectedCount: 3,
          managers: mockManagers,
          loading: false,
        },
      })

      const clearButton = wrapper.find('[data-testid="clear-selection"]')
      await clearButton.trigger('click')

      expect(wrapper.emitted('clear')).toBeTruthy()
    })
  })

  describe('bulk role assignment', () => {
    it('should have assign role button', () => {
      const wrapper = mount(BulkActionBar, {
        props: {
          selectedCount: 3,
          managers: mockManagers,
          loading: false,
        },
      })

      const assignRoleButton = wrapper.find('[data-testid="assign-role-btn"]')
      expect(assignRoleButton.exists()).toBe(true)
    })

    it('should show role dropdown when assign role clicked', async () => {
      const wrapper = mount(BulkActionBar, {
        props: {
          selectedCount: 3,
          managers: mockManagers,
          loading: false,
        },
      })

      const assignRoleButton = wrapper.find('[data-testid="assign-role-btn"]')
      await assignRoleButton.trigger('click')

      const roleDropdown = wrapper.find('[data-testid="role-dropdown"]')
      expect(roleDropdown.exists()).toBe(true)
    })

    it('should emit bulk-assign-role with selected role', async () => {
      const wrapper = mount(BulkActionBar, {
        props: {
          selectedCount: 3,
          managers: mockManagers,
          loading: false,
        },
      })

      // Open dropdown
      const assignRoleButton = wrapper.find('[data-testid="assign-role-btn"]')
      await assignRoleButton.trigger('click')

      // Select a role
      const roleSelect = wrapper.find('[data-testid="role-select"]')
      await roleSelect.setValue('hr')

      // Click apply
      const applyButton = wrapper.find('[data-testid="apply-role"]')
      await applyButton.trigger('click')

      expect(wrapper.emitted('bulk-assign-role')).toBeTruthy()
      expect(wrapper.emitted('bulk-assign-role')![0]).toEqual(['hr'])
    })
  })

  describe('bulk manager assignment', () => {
    it('should have assign manager button', () => {
      const wrapper = mount(BulkActionBar, {
        props: {
          selectedCount: 3,
          managers: mockManagers,
          loading: false,
        },
      })

      const assignManagerButton = wrapper.find('[data-testid="assign-manager-btn"]')
      expect(assignManagerButton.exists()).toBe(true)
    })

    it('should show manager dropdown when assign manager clicked', async () => {
      const wrapper = mount(BulkActionBar, {
        props: {
          selectedCount: 3,
          managers: mockManagers,
          loading: false,
        },
      })

      const assignManagerButton = wrapper.find('[data-testid="assign-manager-btn"]')
      await assignManagerButton.trigger('click')

      const managerDropdown = wrapper.find('[data-testid="manager-dropdown"]')
      expect(managerDropdown.exists()).toBe(true)
    })

    it('should have options for each manager', async () => {
      const wrapper = mount(BulkActionBar, {
        props: {
          selectedCount: 3,
          managers: mockManagers,
          loading: false,
        },
      })

      // Open dropdown
      const assignManagerButton = wrapper.find('[data-testid="assign-manager-btn"]')
      await assignManagerButton.trigger('click')

      const options = wrapper.findAll('[data-testid="manager-select"] option')
      // placeholder + 2 managers
      expect(options.length).toBe(3)
    })

    it('should emit bulk-assign-manager with selected manager', async () => {
      const wrapper = mount(BulkActionBar, {
        props: {
          selectedCount: 3,
          managers: mockManagers,
          loading: false,
        },
      })

      // Open dropdown
      const assignManagerButton = wrapper.find('[data-testid="assign-manager-btn"]')
      await assignManagerButton.trigger('click')

      // Select a manager
      const managerSelect = wrapper.find('[data-testid="manager-select"]')
      await managerSelect.setValue('manager-2')

      // Click apply
      const applyButton = wrapper.find('[data-testid="apply-manager"]')
      await applyButton.trigger('click')

      expect(wrapper.emitted('bulk-assign-manager')).toBeTruthy()
      expect(wrapper.emitted('bulk-assign-manager')![0]).toEqual(['manager-2'])
    })
  })

  describe('loading state', () => {
    it('should disable buttons when loading', () => {
      const wrapper = mount(BulkActionBar, {
        props: {
          selectedCount: 3,
          managers: mockManagers,
          loading: true,
        },
      })

      const assignRoleButton = wrapper.find('[data-testid="assign-role-btn"]')
      const assignManagerButton = wrapper.find('[data-testid="assign-manager-btn"]')

      expect(assignRoleButton.attributes('disabled')).toBeDefined()
      expect(assignManagerButton.attributes('disabled')).toBeDefined()
    })
  })
})
