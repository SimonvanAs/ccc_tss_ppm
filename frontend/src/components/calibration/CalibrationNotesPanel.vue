<script setup lang="ts">
// TSS PPM v3.0 - CalibrationNotesPanel Component
import { ref, computed, onMounted, watch } from 'vue'
import { useI18n } from 'vue-i18n'
import {
  fetchSessionNotes,
  addNote,
  type CalibrationNote,
} from '../../api/calibration'

const { t } = useI18n()

const props = defineProps<{
  sessionId: string
  reviewId?: string
}>()

// State
const notes = ref<CalibrationNote[]>([])
const loading = ref(true)
const error = ref<string | null>(null)
const showAddForm = ref(false)
const newNoteContent = ref('')
const addError = ref<string | null>(null)
const contentError = ref(false)
const submitting = ref(false)

// Computed
const isReviewLevel = computed(() => !!props.reviewId)

const sortedNotes = computed(() => {
  return [...notes.value].sort((a, b) => {
    return new Date(b.created_at).getTime() - new Date(a.created_at).getTime()
  })
})

// Format date for display
function formatDate(dateString: string): string {
  const date = new Date(dateString)
  return date.toLocaleDateString(undefined, {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  })
}

// Get author display name
function getAuthorName(note: CalibrationNote): string {
  if (note.first_name && note.last_name) {
    return `${note.first_name} ${note.last_name}`
  }
  if (note.first_name) return note.first_name
  if (note.last_name) return note.last_name
  return 'Unknown'
}

// Load notes
async function loadNotes() {
  loading.value = true
  error.value = null

  try {
    notes.value = await fetchSessionNotes(props.sessionId, props.reviewId)
  } catch (e) {
    error.value = t('calibration.notes.error')
    console.error('Failed to load notes:', e)
  } finally {
    loading.value = false
  }
}

// Handle add note
function handleAddClick() {
  showAddForm.value = true
  newNoteContent.value = ''
  addError.value = null
  contentError.value = false
}

function handleCancel() {
  showAddForm.value = false
  newNoteContent.value = ''
  addError.value = null
  contentError.value = false
}

async function handleSubmit() {
  addError.value = null
  contentError.value = false

  if (!newNoteContent.value.trim()) {
    contentError.value = true
    return
  }

  submitting.value = true

  try {
    const newNote = await addNote(
      props.sessionId,
      newNoteContent.value.trim(),
      props.reviewId
    )

    notes.value.push(newNote)
    showAddForm.value = false
    newNoteContent.value = ''
  } catch (e) {
    addError.value = t('calibration.notes.addError')
    console.error('Failed to add note:', e)
  } finally {
    submitting.value = false
  }
}

// Watch for content changes to clear error
watch(newNoteContent, () => {
  if (newNoteContent.value.trim()) {
    contentError.value = false
  }
})

// Reload notes when reviewId changes
watch(
  () => props.reviewId,
  () => {
    loadNotes()
  }
)

onMounted(loadNotes)
</script>

<template>
  <div class="calibration-notes-panel">
    <div class="panel-header">
      <h3 class="panel-title">
        {{ isReviewLevel ? t('calibration.notes.reviewNotes') : t('calibration.notes.sessionNotes') }}
      </h3>
      <button
        v-if="!showAddForm && !loading"
        class="add-note-btn"
        @click="handleAddClick"
      >
        {{ t('calibration.notes.addNote') }}
      </button>
    </div>

    <div v-if="loading" class="loading-state">
      {{ t('calibration.notes.loading') }}
    </div>

    <div v-else-if="error" class="error-state">
      {{ error }}
    </div>

    <template v-else>
      <!-- Add Note Form -->
      <form v-if="showAddForm" class="add-note-form" @submit.prevent="handleSubmit">
        <textarea
          v-model="newNoteContent"
          name="noteContent"
          rows="3"
          :placeholder="t('calibration.notes.placeholder')"
          :class="{ 'has-error': contentError }"
        />
        <span v-if="contentError" class="error-message">
          {{ t('calibration.notes.contentRequired') }}
        </span>
        <div v-if="addError" class="add-error">
          {{ addError }}
        </div>
        <div class="form-actions">
          <button type="button" class="cancel-btn" @click="handleCancel">
            {{ t('calibration.notes.cancel') }}
          </button>
          <button type="submit" class="submit-btn" :disabled="submitting">
            {{ t('calibration.notes.submit') }}
          </button>
        </div>
      </form>

      <!-- Notes List -->
      <div v-if="sortedNotes.length === 0" class="empty-state">
        {{ t('calibration.notes.noNotes') }}
      </div>

      <div v-else class="notes-list">
        <div
          v-for="note in sortedNotes"
          :key="note.id"
          class="note-item"
        >
          <div class="note-header">
            <span class="note-author">{{ getAuthorName(note) }}</span>
            <span class="note-date">{{ formatDate(note.created_at) }}</span>
          </div>
          <div class="note-content">{{ note.content }}</div>
        </div>
      </div>
    </template>
  </div>
</template>

<style scoped>
.calibration-notes-panel {
  background: white;
  border: 1px solid #e0e0e0;
  border-radius: 8px;
  padding: 1rem;
}

.panel-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
}

.panel-title {
  margin: 0;
  font-size: 1rem;
  color: var(--navy, #004a91);
  font-family: Tahoma, sans-serif;
}

.add-note-btn {
  padding: 0.5rem 1rem;
  background-color: var(--magenta, #cc0e70);
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-family: Tahoma, sans-serif;
  font-size: 0.85rem;
  font-weight: bold;
}

.add-note-btn:hover {
  background-color: #a00b5a;
}

.loading-state,
.error-state,
.empty-state {
  text-align: center;
  padding: 2rem;
  color: #666;
  font-family: Tahoma, sans-serif;
}

.error-state {
  color: #c00;
}

.add-note-form {
  margin-bottom: 1rem;
  padding: 1rem;
  background: #f9f9f9;
  border-radius: 4px;
}

.add-note-form textarea {
  width: 100%;
  padding: 0.75rem;
  border: 1px solid #ccc;
  border-radius: 4px;
  font-family: Tahoma, sans-serif;
  font-size: 0.9rem;
  resize: vertical;
  box-sizing: border-box;
}

.add-note-form textarea:focus {
  outline: none;
  border-color: var(--magenta, #cc0e70);
  box-shadow: 0 0 0 2px rgba(204, 14, 112, 0.1);
}

.add-note-form textarea.has-error {
  border-color: #c00;
}

.error-message {
  display: block;
  margin-top: 0.25rem;
  color: #c00;
  font-size: 0.85rem;
  font-family: Tahoma, sans-serif;
}

.add-error {
  margin-top: 0.5rem;
  padding: 0.5rem;
  background-color: #ffebee;
  color: #c00;
  border-radius: 4px;
  font-size: 0.85rem;
  font-family: Tahoma, sans-serif;
}

.form-actions {
  display: flex;
  justify-content: flex-end;
  gap: 0.5rem;
  margin-top: 0.75rem;
}

.cancel-btn {
  padding: 0.5rem 1rem;
  background: white;
  color: #333;
  border: 1px solid #ccc;
  border-radius: 4px;
  cursor: pointer;
  font-family: Tahoma, sans-serif;
  font-size: 0.85rem;
}

.cancel-btn:hover {
  background: #f5f5f5;
}

.submit-btn {
  padding: 0.5rem 1rem;
  background-color: var(--magenta, #cc0e70);
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-family: Tahoma, sans-serif;
  font-size: 0.85rem;
  font-weight: bold;
}

.submit-btn:hover:not(:disabled) {
  background-color: #a00b5a;
}

.submit-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.notes-list {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.note-item {
  padding: 0.75rem;
  background: #f9f9f9;
  border-radius: 4px;
  border-left: 3px solid var(--navy, #004a91);
}

.note-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 0.5rem;
}

.note-author {
  font-weight: 600;
  color: var(--navy, #004a91);
  font-family: Tahoma, sans-serif;
  font-size: 0.85rem;
}

.note-date {
  font-size: 0.75rem;
  color: #999;
  font-family: Tahoma, sans-serif;
}

.note-content {
  font-family: Tahoma, sans-serif;
  font-size: 0.9rem;
  color: #333;
  line-height: 1.5;
  white-space: pre-wrap;
}
</style>
