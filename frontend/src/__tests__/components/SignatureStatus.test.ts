// TSS PPM v3.0 - SignatureStatus Component Tests
import { describe, it, expect, vi } from 'vitest'
import { mount } from '@vue/test-utils'
import SignatureStatus from '../../components/review/SignatureStatus.vue'

// Mock vue-i18n
vi.mock('vue-i18n', () => ({
  useI18n: () => ({
    t: (key: string, params?: Record<string, unknown>) => {
      if (params) {
        return `${key}:${JSON.stringify(params)}`
      }
      return key
    },
    d: (date: Date) => date.toISOString().split('T')[0],
    locale: { value: 'en' },
  }),
}))

describe('SignatureStatus', () => {
  describe('awaiting employee signature', () => {
    it('should display Awaiting Employee Signature status', () => {
      const wrapper = mount(SignatureStatus, {
        props: {
          status: 'PENDING_EMPLOYEE_SIGNATURE',
        },
      })

      expect(wrapper.text()).toContain('signature.status.awaitingEmployee')
    })

    it('should use pending styling for awaiting states', () => {
      const wrapper = mount(SignatureStatus, {
        props: {
          status: 'PENDING_EMPLOYEE_SIGNATURE',
        },
      })

      expect(wrapper.find('.signature-status').classes()).toContain('pending')
    })

    it('should show pending icon', () => {
      const wrapper = mount(SignatureStatus, {
        props: {
          status: 'PENDING_EMPLOYEE_SIGNATURE',
        },
      })

      expect(wrapper.find('.status-icon.pending').exists()).toBe(true)
    })
  })

  describe('awaiting manager signature', () => {
    it('should display Awaiting Manager Signature status', () => {
      const wrapper = mount(SignatureStatus, {
        props: {
          status: 'PENDING_MANAGER_SIGNATURE',
        },
      })

      expect(wrapper.text()).toContain('signature.status.awaitingManager')
    })

    it('should show employee signature info when available', () => {
      const wrapper = mount(SignatureStatus, {
        props: {
          status: 'PENDING_MANAGER_SIGNATURE',
          employeeSignature: {
            signedBy: 'John Doe',
            signedAt: new Date('2024-01-15T10:30:00Z'),
          },
        },
      })

      expect(wrapper.text()).toContain('John Doe')
    })
  })

  describe('fully signed', () => {
    it('should display Signed status', () => {
      const wrapper = mount(SignatureStatus, {
        props: {
          status: 'SIGNED',
        },
      })

      expect(wrapper.text()).toContain('signature.status.signed')
    })

    it('should use signed styling', () => {
      const wrapper = mount(SignatureStatus, {
        props: {
          status: 'SIGNED',
        },
      })

      expect(wrapper.find('.signature-status').classes()).toContain('signed')
    })

    it('should show both signatures when fully signed', () => {
      const wrapper = mount(SignatureStatus, {
        props: {
          status: 'SIGNED',
          employeeSignature: {
            signedBy: 'Jane Employee',
            signedAt: new Date('2024-01-15T10:30:00Z'),
          },
          managerSignature: {
            signedBy: 'Bob Manager',
            signedAt: new Date('2024-01-16T14:00:00Z'),
          },
        },
      })

      expect(wrapper.text()).toContain('Jane Employee')
      expect(wrapper.text()).toContain('Bob Manager')
    })

    it('should show signed icon', () => {
      const wrapper = mount(SignatureStatus, {
        props: {
          status: 'SIGNED',
        },
      })

      expect(wrapper.find('.status-icon.signed').exists()).toBe(true)
    })
  })

  describe('draft status', () => {
    it('should display Draft status', () => {
      const wrapper = mount(SignatureStatus, {
        props: {
          status: 'DRAFT',
        },
      })

      expect(wrapper.text()).toContain('signature.status.draft')
    })

    it('should use draft styling', () => {
      const wrapper = mount(SignatureStatus, {
        props: {
          status: 'DRAFT',
        },
      })

      expect(wrapper.find('.signature-status').classes()).toContain('draft')
    })
  })

  describe('signature timestamps', () => {
    it('should display employee signature timestamp', () => {
      const wrapper = mount(SignatureStatus, {
        props: {
          status: 'PENDING_MANAGER_SIGNATURE',
          employeeSignature: {
            signedBy: 'John Doe',
            signedAt: new Date('2024-01-15T10:30:00Z'),
          },
        },
      })

      expect(wrapper.find('.signature-date').exists()).toBe(true)
    })

    it('should display manager signature timestamp', () => {
      const wrapper = mount(SignatureStatus, {
        props: {
          status: 'SIGNED',
          employeeSignature: {
            signedBy: 'Jane Employee',
            signedAt: new Date('2024-01-15T10:30:00Z'),
          },
          managerSignature: {
            signedBy: 'Bob Manager',
            signedAt: new Date('2024-01-16T14:00:00Z'),
          },
        },
      })

      const dates = wrapper.findAll('.signature-date')
      expect(dates.length).toBe(2)
    })
  })

  describe('compact mode', () => {
    it('should render in compact mode when prop is set', () => {
      const wrapper = mount(SignatureStatus, {
        props: {
          status: 'SIGNED',
          compact: true,
        },
      })

      expect(wrapper.find('.signature-status').classes()).toContain('compact')
    })

    it('should hide signature details in compact mode', () => {
      const wrapper = mount(SignatureStatus, {
        props: {
          status: 'SIGNED',
          compact: true,
          employeeSignature: {
            signedBy: 'Jane Employee',
            signedAt: new Date('2024-01-15T10:30:00Z'),
          },
          managerSignature: {
            signedBy: 'Bob Manager',
            signedAt: new Date('2024-01-16T14:00:00Z'),
          },
        },
      })

      expect(wrapper.find('.signature-details').exists()).toBe(false)
    })
  })

  describe('signer information', () => {
    it('should show signer name for employee signature', () => {
      const wrapper = mount(SignatureStatus, {
        props: {
          status: 'PENDING_MANAGER_SIGNATURE',
          employeeSignature: {
            signedBy: 'John Smith',
            signedAt: new Date('2024-01-15T10:30:00Z'),
          },
        },
      })

      expect(wrapper.text()).toContain('John Smith')
    })

    it('should show signer name for manager signature', () => {
      const wrapper = mount(SignatureStatus, {
        props: {
          status: 'SIGNED',
          managerSignature: {
            signedBy: 'Alice Manager',
            signedAt: new Date('2024-01-16T14:00:00Z'),
          },
        },
      })

      expect(wrapper.text()).toContain('Alice Manager')
    })
  })

  describe('styling', () => {
    it('should apply brand colors based on status', () => {
      const wrapper = mount(SignatureStatus, {
        props: {
          status: 'SIGNED',
        },
      })

      // Signed should have success/green styling
      expect(wrapper.find('.signature-status.signed').exists()).toBe(true)
    })

    it('should show warning style for rejected', () => {
      const wrapper = mount(SignatureStatus, {
        props: {
          status: 'DRAFT',
          wasRejected: true,
        },
      })

      expect(wrapper.find('.signature-status').classes()).toContain('rejected')
    })
  })
})
