<script setup lang="ts">
// TSS PPM v3.0 - PDFDownloadButton Component
import { ref, computed } from 'vue'
import { useI18n } from 'vue-i18n'
import { downloadReviewPdf } from '@/api/reviews'
import type { ReviewStatus } from '@/api/reviews'

const props = defineProps<{
  reviewId: string
  status: ReviewStatus
  employeeName?: string
  reviewYear?: number
}>()

const emit = defineEmits<{
  error: [error: Error]
}>()

const { t, locale } = useI18n()

const isDownloading = ref(false)

const isFinalReport = computed(() => {
  return props.status === 'SIGNED' || props.status === 'ARCHIVED'
})

const buttonLabel = computed(() => {
  if (isDownloading.value) {
    return t('pdf.downloading')
  }
  return isFinalReport.value ? t('pdf.downloadFinal') : t('pdf.downloadDraft')
})

function generateFilename(): string {
  const name = props.employeeName?.replace(/\s+/g, '_') || 'Review'
  const year = props.reviewYear || new Date().getFullYear()
  const suffix = isFinalReport.value ? 'Final' : 'Draft'
  return `${name}_${year}_${suffix}.pdf`
}

async function handleDownload() {
  if (isDownloading.value) return

  isDownloading.value = true

  try {
    const blob = await downloadReviewPdf(props.reviewId, locale.value)

    // Create download link
    const url = URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    link.download = generateFilename()
    document.body.appendChild(link)
    link.click()
    link.remove()
    URL.revokeObjectURL(url)
  } catch (error) {
    emit('error', error as Error)
  } finally {
    isDownloading.value = false
  }
}
</script>

<template>
  <button
    class="btn btn-secondary"
    :disabled="isDownloading"
    @click="handleDownload"
  >
    <svg
      v-if="isDownloading"
      class="spinner"
      viewBox="0 0 24 24"
      xmlns="http://www.w3.org/2000/svg"
    >
      <circle
        class="spinner-circle"
        cx="12"
        cy="12"
        r="10"
        fill="none"
        stroke="currentColor"
        stroke-width="2"
      />
    </svg>
    <svg
      v-else
      class="icon"
      viewBox="0 0 24 24"
      xmlns="http://www.w3.org/2000/svg"
    >
      <path
        fill="currentColor"
        d="M5 20h14v-2H5v2zm7-18L5.33 9h4.17v7h5v-7h4.17L12 2z"
      />
    </svg>
    {{ buttonLabel }}
  </button>
</template>

<style scoped>
.btn {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.5rem 1rem;
  font-family: Tahoma, Geneva, sans-serif;
  font-size: 0.875rem;
  font-weight: 500;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  transition: background-color 0.2s ease, opacity 0.2s ease;
}

.btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.btn-secondary {
  background-color: #f3f4f6;
  color: #374151;
  border: 1px solid #d1d5db;
}

.btn-secondary:hover:not(:disabled) {
  background-color: #e5e7eb;
}

.icon {
  width: 1rem;
  height: 1rem;
}

.spinner {
  width: 1rem;
  height: 1rem;
  animation: spin 1s linear infinite;
}

.spinner-circle {
  stroke-dasharray: 63;
  stroke-dashoffset: 50;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}
</style>
