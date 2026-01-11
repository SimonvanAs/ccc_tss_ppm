// TSS PPM v3.0 - PDFDownloadButton Tests
import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'
import { mount } from '@vue/test-utils'
import { ref } from 'vue'
import PDFDownloadButton from '@/components/review/PDFDownloadButton.vue'

// Mock the api
vi.mock('@/api/reviews', () => ({
  downloadReviewPdf: vi.fn(),
}))

// Mock i18n
const mockT = vi.fn((key: string) => {
  const translations: Record<string, string> = {
    'pdf.downloadDraft': 'Download Draft PDF',
    'pdf.downloadFinal': 'Download Final Report',
    'pdf.downloading': 'Downloading...',
    'pdf.error': 'Failed to download PDF',
  }
  return translations[key] || key
})

vi.mock('vue-i18n', () => ({
  useI18n: () => ({
    t: mockT,
    locale: ref('en'),
  }),
}))

describe('PDFDownloadButton', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    // Mock URL.createObjectURL and URL.revokeObjectURL
    global.URL.createObjectURL = vi.fn(() => 'blob:test-url')
    global.URL.revokeObjectURL = vi.fn()
  })

  afterEach(() => {
    vi.restoreAllMocks()
  })

  describe('Button Label', () => {
    it('shows "Download Draft PDF" for DRAFT status', () => {
      const wrapper = mount(PDFDownloadButton, {
        props: {
          reviewId: 'test-review-id',
          status: 'DRAFT',
        },
      })

      expect(wrapper.text()).toContain('Download Draft PDF')
    })

    it('shows "Download Draft PDF" for PENDING_EMPLOYEE_SIGNATURE status', () => {
      const wrapper = mount(PDFDownloadButton, {
        props: {
          reviewId: 'test-review-id',
          status: 'PENDING_EMPLOYEE_SIGNATURE',
        },
      })

      expect(wrapper.text()).toContain('Download Draft PDF')
    })

    it('shows "Download Draft PDF" for PENDING_MANAGER_SIGNATURE status', () => {
      const wrapper = mount(PDFDownloadButton, {
        props: {
          reviewId: 'test-review-id',
          status: 'PENDING_MANAGER_SIGNATURE',
        },
      })

      expect(wrapper.text()).toContain('Download Draft PDF')
    })

    it('shows "Download Final Report" for SIGNED status', () => {
      const wrapper = mount(PDFDownloadButton, {
        props: {
          reviewId: 'test-review-id',
          status: 'SIGNED',
        },
      })

      expect(wrapper.text()).toContain('Download Final Report')
    })

    it('shows "Download Final Report" for ARCHIVED status', () => {
      const wrapper = mount(PDFDownloadButton, {
        props: {
          reviewId: 'test-review-id',
          status: 'ARCHIVED',
        },
      })

      expect(wrapper.text()).toContain('Download Final Report')
    })
  })

  describe('Loading State', () => {
    it('shows loading text when downloading', async () => {
      const { downloadReviewPdf } = await import('@/api/reviews')
      const mockDownload = downloadReviewPdf as ReturnType<typeof vi.fn>

      // Create a promise that we can control
      let resolveDownload: (value: Blob) => void
      mockDownload.mockImplementation(() => new Promise((resolve) => {
        resolveDownload = resolve
      }))

      const wrapper = mount(PDFDownloadButton, {
        props: {
          reviewId: 'test-review-id',
          status: 'SIGNED',
        },
      })

      // Click the button to start download
      await wrapper.find('button').trigger('click')
      await wrapper.vm.$nextTick()

      expect(wrapper.text()).toContain('Downloading...')

      // Resolve the promise
      resolveDownload!(new Blob(['%PDF-1.4'], { type: 'application/pdf' }))
    })

    it('disables button while downloading', async () => {
      const { downloadReviewPdf } = await import('@/api/reviews')
      const mockDownload = downloadReviewPdf as ReturnType<typeof vi.fn>

      let resolveDownload: (value: Blob) => void
      mockDownload.mockImplementation(() => new Promise((resolve) => {
        resolveDownload = resolve
      }))

      const wrapper = mount(PDFDownloadButton, {
        props: {
          reviewId: 'test-review-id',
          status: 'SIGNED',
        },
      })

      await wrapper.find('button').trigger('click')
      await wrapper.vm.$nextTick()

      expect(wrapper.find('button').attributes('disabled')).toBeDefined()

      resolveDownload!(new Blob(['%PDF-1.4'], { type: 'application/pdf' }))
    })

    it('re-enables button after download completes', async () => {
      const { downloadReviewPdf } = await import('@/api/reviews')
      const mockDownload = downloadReviewPdf as ReturnType<typeof vi.fn>
      mockDownload.mockResolvedValue(new Blob(['%PDF-1.4'], { type: 'application/pdf' }))

      const wrapper = mount(PDFDownloadButton, {
        props: {
          reviewId: 'test-review-id',
          status: 'SIGNED',
        },
      })

      await wrapper.find('button').trigger('click')
      await wrapper.vm.$nextTick()
      await vi.waitFor(() => {
        return wrapper.find('button').attributes('disabled') === undefined
      })

      expect(wrapper.find('button').attributes('disabled')).toBeUndefined()
    })
  })

  describe('Download Behavior', () => {
    it('calls API with correct review ID', async () => {
      const { downloadReviewPdf } = await import('@/api/reviews')
      const mockDownload = downloadReviewPdf as ReturnType<typeof vi.fn>
      mockDownload.mockResolvedValue(new Blob(['%PDF-1.4'], { type: 'application/pdf' }))

      const wrapper = mount(PDFDownloadButton, {
        props: {
          reviewId: 'test-review-123',
          status: 'SIGNED',
        },
      })

      await wrapper.find('button').trigger('click')
      await wrapper.vm.$nextTick()

      expect(mockDownload).toHaveBeenCalledWith('test-review-123', 'en')
    })

    it('passes locale to API', async () => {
      const { downloadReviewPdf } = await import('@/api/reviews')
      const mockDownload = downloadReviewPdf as ReturnType<typeof vi.fn>
      mockDownload.mockResolvedValue(new Blob(['%PDF-1.4'], { type: 'application/pdf' }))

      const wrapper = mount(PDFDownloadButton, {
        props: {
          reviewId: 'test-review-id',
          status: 'SIGNED',
        },
      })

      await wrapper.find('button').trigger('click')

      expect(mockDownload).toHaveBeenCalledWith('test-review-id', 'en')
    })

    it('triggers file download on success', async () => {
      const { downloadReviewPdf } = await import('@/api/reviews')
      const mockDownload = downloadReviewPdf as ReturnType<typeof vi.fn>
      mockDownload.mockResolvedValue(new Blob(['%PDF-1.4'], { type: 'application/pdf' }))

      const wrapper = mount(PDFDownloadButton, {
        props: {
          reviewId: 'test-review-id',
          status: 'SIGNED',
          employeeName: 'John Doe',
          reviewYear: 2024,
        },
      })

      await wrapper.find('button').trigger('click')
      await vi.waitFor(() => !wrapper.find('button').attributes('disabled'))

      // Verify the download was called successfully
      expect(mockDownload).toHaveBeenCalledWith('test-review-id', 'en')
      // URL.createObjectURL should have been called with the blob
      expect(URL.createObjectURL).toHaveBeenCalled()
    })
  })

  describe('Error Handling', () => {
    it('emits error event on download failure', async () => {
      const { downloadReviewPdf } = await import('@/api/reviews')
      const mockDownload = downloadReviewPdf as ReturnType<typeof vi.fn>
      mockDownload.mockRejectedValue(new Error('Network error'))

      const wrapper = mount(PDFDownloadButton, {
        props: {
          reviewId: 'test-review-id',
          status: 'SIGNED',
        },
      })

      await wrapper.find('button').trigger('click')
      await vi.waitFor(() => wrapper.emitted('error'))

      expect(wrapper.emitted('error')).toBeTruthy()
    })

    it('re-enables button after error', async () => {
      const { downloadReviewPdf } = await import('@/api/reviews')
      const mockDownload = downloadReviewPdf as ReturnType<typeof vi.fn>
      mockDownload.mockRejectedValue(new Error('Network error'))

      const wrapper = mount(PDFDownloadButton, {
        props: {
          reviewId: 'test-review-id',
          status: 'SIGNED',
        },
      })

      await wrapper.find('button').trigger('click')
      await vi.waitFor(() => wrapper.emitted('error'))

      expect(wrapper.find('button').attributes('disabled')).toBeUndefined()
    })
  })

  describe('Styling', () => {
    it('has button element', () => {
      const wrapper = mount(PDFDownloadButton, {
        props: {
          reviewId: 'test-review-id',
          status: 'SIGNED',
        },
      })

      expect(wrapper.find('button').exists()).toBe(true)
    })

    it('applies secondary styling', () => {
      const wrapper = mount(PDFDownloadButton, {
        props: {
          reviewId: 'test-review-id',
          status: 'SIGNED',
        },
      })

      const button = wrapper.find('button')
      expect(button.classes()).toContain('btn-secondary')
    })
  })
})
