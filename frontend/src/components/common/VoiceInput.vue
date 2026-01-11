<script setup lang="ts">
import { ref, computed, onUnmounted } from 'vue'
import { useI18n } from 'vue-i18n'
import { getToken } from '../../api/auth'

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1'

const props = defineProps<{
  disabled?: boolean
  transcribeFn?: (audioBlob: Blob) => Promise<string>
}>()

const emit = defineEmits<{
  transcription: [text: string]
  error: [error: Error]
}>()

const { t } = useI18n()

// Voice input states
type VoiceState = 'idle' | 'recording' | 'processing' | 'error' | 'unsupported'

const state = ref<VoiceState>('idle')
const errorMessage = ref<string | null>(null)

// Check for browser support
const isSupported = computed(() => {
  return typeof MediaRecorder !== 'undefined' && navigator.mediaDevices?.getUserMedia
})

// Update state if unsupported
if (!isSupported.value) {
  state.value = 'unsupported'
}

// Recording state
let mediaRecorder: MediaRecorder | null = null
let mediaStream: MediaStream | null = null
let audioChunks: Blob[] = []
let recordingStartTime: number | null = null

// Minimum recording duration in milliseconds (3 seconds)
const MIN_RECORDING_DURATION_MS = 3000

const stateClass = computed(() => `is-${state.value}`)

const tooltipText = computed(() => {
  switch (state.value) {
    case 'recording':
      return t('voice.recording')
    case 'processing':
      return t('voice.processing')
    case 'error':
      return errorMessage.value || t('voice.error')
    case 'unsupported':
      return t('voice.unsupported')
    default:
      return t('voice.holdToRecord')
  }
})

async function startRecording() {
  if (props.disabled || !isSupported.value || state.value === 'recording') {
    return
  }

  audioChunks = []
  errorMessage.value = null

  try {
    mediaStream = await navigator.mediaDevices.getUserMedia({
      audio: {
        echoCancellation: true,
        noiseSuppression: true,
      },
    })

    mediaRecorder = new MediaRecorder(mediaStream, {
      mimeType: MediaRecorder.isTypeSupported('audio/webm') ? 'audio/webm' : 'audio/mp4',
    })

    mediaRecorder.ondataavailable = (event) => {
      if (event.data.size > 0) {
        audioChunks.push(event.data)
      }
    }

    mediaRecorder.onstop = async () => {
      // Stop all tracks to release microphone
      if (mediaStream) {
        mediaStream.getTracks().forEach(track => track.stop())
        mediaStream = null
      }

      // Check recording duration - ignore if too short (accidental click)
      const recordingDuration = recordingStartTime ? Date.now() - recordingStartTime : 0
      recordingStartTime = null

      if (recordingDuration < MIN_RECORDING_DURATION_MS) {
        // Recording too short, silently ignore
        state.value = 'idle'
        audioChunks = []
        return
      }

      if (audioChunks.length > 0) {
        await processAudio()
      }
    }

    mediaRecorder.onerror = () => {
      handleError(new Error('Recording failed'))
    }

    mediaRecorder.start()
    recordingStartTime = Date.now()
    state.value = 'recording'
  } catch (error) {
    handleError(error instanceof Error ? error : new Error('Microphone access denied'))
  }
}

function stopRecording() {
  if (mediaRecorder && mediaRecorder.state === 'recording') {
    mediaRecorder.stop()
  }
}

async function processAudio() {
  if (audioChunks.length === 0) {
    state.value = 'idle'
    return
  }

  state.value = 'processing'

  try {
    const audioBlob = new Blob(audioChunks, { type: 'audio/webm' })

    if (props.transcribeFn) {
      const text = await props.transcribeFn(audioBlob)
      emit('transcription', text)
    } else {
      // Default: use the API endpoint for transcription
      const formData = new FormData()
      formData.append('audio', audioBlob, 'recording.webm')

      // Get auth token
      const token = await getToken()
      const headers: HeadersInit = {}
      if (token) {
        headers['Authorization'] = `Bearer ${token}`
      }

      const response = await fetch(`${API_BASE_URL}/voice/transcribe`, {
        method: 'POST',
        headers,
        body: formData,
      })

      if (!response.ok) {
        const errorText = await response.text()
        throw new Error(`Transcription failed: ${errorText}`)
      }

      const result = await response.json()
      emit('transcription', result.text)
    }

    state.value = 'idle'
  } catch (error) {
    handleError(error instanceof Error ? error : new Error('Transcription failed'))
  }
}

function handleError(error: Error) {
  state.value = 'error'
  errorMessage.value = error.message
  emit('error', error)

  // Reset to idle after 3 seconds
  setTimeout(() => {
    if (state.value === 'error') {
      state.value = 'idle'
      errorMessage.value = null
    }
  }, 3000)
}

// Handle mouse/touch events
function handlePointerDown(event: MouseEvent | TouchEvent) {
  event.preventDefault()
  startRecording()
}

function handlePointerUp() {
  stopRecording()
}

function handlePointerLeave() {
  stopRecording()
}

// Cleanup on unmount
onUnmounted(() => {
  if (mediaRecorder && mediaRecorder.state === 'recording') {
    mediaRecorder.stop()
  }
  if (mediaStream) {
    mediaStream.getTracks().forEach(track => track.stop())
  }
})
</script>

<template>
  <div :class="['voice-input', stateClass]">
    <button
      type="button"
      class="voice-button"
      :title="tooltipText"
      :disabled="disabled || state === 'unsupported' || state === 'processing'"
      @mousedown="handlePointerDown"
      @mouseup="handlePointerUp"
      @mouseleave="handlePointerLeave"
      @touchstart="handlePointerDown"
      @touchend="handlePointerUp"
    >
      <!-- Microphone icon -->
      <svg
        class="mic-icon"
        viewBox="0 0 24 24"
        fill="none"
        stroke="currentColor"
        stroke-width="2"
        stroke-linecap="round"
        stroke-linejoin="round"
      >
        <path d="M12 1a3 3 0 0 0-3 3v8a3 3 0 0 0 6 0V4a3 3 0 0 0-3-3z" />
        <path d="M19 10v2a7 7 0 0 1-14 0v-2" />
        <line x1="12" y1="19" x2="12" y2="23" />
        <line x1="8" y1="23" x2="16" y2="23" />
      </svg>

      <!-- Recording pulse animation -->
      <span v-if="state === 'recording'" class="pulse-ring" />

      <!-- Processing spinner -->
      <span v-if="state === 'processing'" class="processing-spinner" />
    </button>
  </div>
</template>

<style scoped>
.voice-input {
  display: inline-flex;
  position: relative;
}

.voice-button {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 40px;
  height: 40px;
  padding: 0;
  border: none;
  border-radius: 50%;
  background: var(--color-gray-200);
  color: var(--color-gray-600);
  cursor: pointer;
  transition: all 0.2s;
  position: relative;
}

.voice-button:hover:not(:disabled) {
  background: var(--color-gray-300);
}

.voice-button:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

/* Idle state */
.is-idle .voice-button {
  background: var(--color-gray-200);
  color: var(--color-gray-600);
}

/* Recording state - magenta pulse */
.is-recording .voice-button {
  background: var(--color-magenta);
  color: white;
  animation: pulse 1s ease-in-out infinite;
}

@keyframes pulse {
  0%, 100% {
    transform: scale(1);
  }
  50% {
    transform: scale(1.05);
  }
}

.pulse-ring {
  position: absolute;
  inset: -4px;
  border: 2px solid var(--color-magenta);
  border-radius: 50%;
  animation: pulse-ring 1.5s ease-out infinite;
}

@keyframes pulse-ring {
  0% {
    transform: scale(1);
    opacity: 1;
  }
  100% {
    transform: scale(1.5);
    opacity: 0;
  }
}

/* Processing state - blue spinner */
.is-processing .voice-button {
  background: var(--color-navy);
  color: white;
}

.processing-spinner {
  position: absolute;
  inset: -4px;
  border: 2px solid transparent;
  border-top-color: var(--color-navy);
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

/* Error state - red */
.is-error .voice-button {
  background: #FEE2E2;
  color: #991B1B;
  animation: shake 0.5s ease-in-out;
}

@keyframes shake {
  0%, 100% {
    transform: translateX(0);
  }
  25% {
    transform: translateX(-4px);
  }
  75% {
    transform: translateX(4px);
  }
}

/* Unsupported state */
.is-unsupported .voice-button {
  background: var(--color-gray-100);
  color: var(--color-gray-400);
}

.mic-icon {
  width: 20px;
  height: 20px;
}
</style>
