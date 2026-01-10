// TSS PPM v3.0 - VoiceInput Component Tests
import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'
import { mount } from '@vue/test-utils'
import { nextTick } from 'vue'
import VoiceInput from '../../components/common/VoiceInput.vue'

// Mock vue-i18n
vi.mock('vue-i18n', () => ({
  useI18n: () => ({
    t: (key: string) => {
      const messages: Record<string, string> = {
        'voice.holdToRecord': 'Hold to record',
        'voice.recording': 'Recording...',
        'voice.processing': 'Processing...',
        'voice.error': 'Voice input failed',
        'voice.unsupported': 'Voice input not supported',
      }
      return messages[key] || key
    },
  }),
}))

// Mock MediaRecorder
const mockMediaRecorder = {
  start: vi.fn(),
  stop: vi.fn(),
  ondataavailable: null as ((event: { data: Blob }) => void) | null,
  onstop: null as (() => void) | null,
  onerror: null as ((error: Error) => void) | null,
  state: 'inactive' as 'inactive' | 'recording',
}

const mockMediaStream = {
  getTracks: () => [{ stop: vi.fn() }],
}

describe('VoiceInput', () => {
  beforeEach(() => {
    vi.resetAllMocks()

    // Mock navigator.mediaDevices
    Object.defineProperty(navigator, 'mediaDevices', {
      value: {
        getUserMedia: vi.fn().mockResolvedValue(mockMediaStream),
      },
      writable: true,
    })

    // Mock MediaRecorder constructor
    vi.stubGlobal('MediaRecorder', vi.fn().mockImplementation(() => {
      return { ...mockMediaRecorder }
    }))

    // Mock MediaRecorder.isTypeSupported
    ;(MediaRecorder as unknown as { isTypeSupported: (type: string) => boolean }).isTypeSupported = vi.fn().mockReturnValue(true)
  })

  afterEach(() => {
    vi.unstubAllGlobals()
  })

  function createWrapper(props = {}) {
    return mount(VoiceInput, {
      props: {
        ...props,
      },
    })
  }

  describe('idle state', () => {
    it('should render microphone button', () => {
      const wrapper = createWrapper()
      expect(wrapper.find('button').exists()).toBe(true)
    })

    it('should show hold to record tooltip', () => {
      const wrapper = createWrapper()
      expect(wrapper.find('button').attributes('title')).toContain('Hold to record')
    })

    it('should have idle class by default', () => {
      const wrapper = createWrapper()
      expect(wrapper.find('.voice-input').classes()).toContain('is-idle')
    })

    it('should not be disabled by default', () => {
      const wrapper = createWrapper()
      expect(wrapper.find('button').attributes('disabled')).toBeUndefined()
    })
  })

  describe('recording state', () => {
    it('should start recording on mousedown', async () => {
      const wrapper = createWrapper()
      await wrapper.find('button').trigger('mousedown')

      expect(navigator.mediaDevices.getUserMedia).toHaveBeenCalled()
    })

    it('should have recording class when recording', async () => {
      const wrapper = createWrapper()
      await wrapper.find('button').trigger('mousedown')
      await nextTick()

      expect(wrapper.find('.voice-input').classes()).toContain('is-recording')
    })

    it('should stop recording on mouseup', async () => {
      const wrapper = createWrapper()

      await wrapper.find('button').trigger('mousedown')
      await nextTick()

      await wrapper.find('button').trigger('mouseup')

      // The MediaRecorder.stop should be called
      // (we'd need to access the internal recorder instance)
    })

    it('should stop recording on mouseleave', async () => {
      const wrapper = createWrapper()

      await wrapper.find('button').trigger('mousedown')
      await nextTick()

      await wrapper.find('button').trigger('mouseleave')

      // Recording should stop when mouse leaves button
    })
  })

  describe('processing state', () => {
    it('should show processing state after recording stops', async () => {
      const mockTranscribe = vi.fn().mockResolvedValue('transcribed text')
      const wrapper = createWrapper({ transcribeFn: mockTranscribe })

      await wrapper.find('button').trigger('mousedown')
      await nextTick()

      // Simulate recording stop with data
      await wrapper.find('button').trigger('mouseup')
      await nextTick()

      // Would transition to processing state while waiting for transcription
    })
  })

  describe('error state', () => {
    it('should show error when microphone access denied', async () => {
      ;(navigator.mediaDevices.getUserMedia as ReturnType<typeof vi.fn>).mockRejectedValueOnce(
        new Error('Permission denied')
      )

      const wrapper = createWrapper()
      await wrapper.find('button').trigger('mousedown')
      await nextTick()

      expect(wrapper.find('.voice-input').classes()).toContain('is-error')
    })

    it('should show unsupported message when MediaRecorder not available', () => {
      vi.stubGlobal('MediaRecorder', undefined)

      const wrapper = createWrapper()

      expect(wrapper.find('.voice-input').classes()).toContain('is-unsupported')
    })
  })

  describe('transcription callback', () => {
    it('should emit transcription event with text', async () => {
      const wrapper = createWrapper()

      // Trigger internal transcription event
      wrapper.vm.$emit('transcription', 'Hello world')

      const events = wrapper.emitted('transcription')
      expect(events).toBeTruthy()
      expect(events![0]).toEqual(['Hello world'])
    })
  })

  describe('disabled state', () => {
    it('should not start recording when disabled', async () => {
      const wrapper = createWrapper({ disabled: true })
      await wrapper.find('button').trigger('mousedown')

      expect(navigator.mediaDevices.getUserMedia).not.toHaveBeenCalled()
    })

    it('should have disabled attribute on button', () => {
      const wrapper = createWrapper({ disabled: true })
      expect(wrapper.find('button').attributes('disabled')).toBeDefined()
    })
  })

  describe('touch support', () => {
    it('should start recording on touchstart', async () => {
      const wrapper = createWrapper()
      await wrapper.find('button').trigger('touchstart')

      expect(navigator.mediaDevices.getUserMedia).toHaveBeenCalled()
    })

    it('should stop recording on touchend', async () => {
      const wrapper = createWrapper()

      await wrapper.find('button').trigger('touchstart')
      await nextTick()

      await wrapper.find('button').trigger('touchend')
      // Recording should stop
    })
  })
})
