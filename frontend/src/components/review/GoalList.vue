<script setup lang="ts">
import { ref } from 'vue'
import { useI18n } from 'vue-i18n'
import type { Goal } from '../../types'
import GoalItem from './GoalItem.vue'

const props = defineProps<{
  goals: Goal[]
  loading?: boolean
  readonly?: boolean
}>()

const emit = defineEmits<{
  edit: [goal: Goal]
  delete: [goal: Goal]
  reorder: [goalIds: string[]]
}>()

const { t } = useI18n()

// Drag state
const draggedIndex = ref<number | null>(null)
const dragOverIndex = ref<number | null>(null)

function handleDragStart(index: number) {
  if (props.readonly) return
  draggedIndex.value = index
}

function handleDragOver(event: DragEvent, index: number) {
  if (props.readonly) return
  event.preventDefault()
  dragOverIndex.value = index
}

function handleDragLeave() {
  dragOverIndex.value = null
}

function handleDrop(event: DragEvent, targetIndex: number) {
  event.preventDefault()
  if (props.readonly) return
  if (draggedIndex.value === null || draggedIndex.value === targetIndex) {
    resetDragState()
    return
  }

  // Calculate new order
  const newOrder = [...props.goals]
  const [draggedItem] = newOrder.splice(draggedIndex.value, 1)
  newOrder.splice(targetIndex, 0, draggedItem)

  // Emit the new order as an array of IDs
  emit('reorder', newOrder.map(g => g.id))
  resetDragState()
}

function handleDragEnd() {
  resetDragState()
}

function resetDragState() {
  draggedIndex.value = null
  dragOverIndex.value = null
}
</script>

<template>
  <div class="goal-list">
    <!-- Loading state -->
    <div v-if="loading" class="loading-state">
      <div class="spinner"></div>
      <p>{{ t('goals.loading') }}</p>
    </div>

    <!-- Empty state -->
    <div v-else-if="goals.length === 0" class="empty-state">
      <div class="empty-icon">📋</div>
      <h3>{{ t('goals.emptyTitle') }}</h3>
      <p>{{ t('goals.emptyDescription') }}</p>
    </div>

    <!-- Goal list with drag-drop support -->
    <div v-else class="goals">
      <div
        v-for="(goal, index) in goals"
        :key="goal.id"
        :class="[
          'goal-wrapper',
          {
            'is-dragging': draggedIndex === index,
            'is-drag-over': dragOverIndex === index && draggedIndex !== index,
          }
        ]"
        :draggable="!readonly"
        @dragstart="handleDragStart(index)"
        @dragover="handleDragOver($event, index)"
        @dragleave="handleDragLeave"
        @drop="handleDrop($event, index)"
        @dragend="handleDragEnd"
      >
        <div v-if="!readonly" class="drag-handle" :title="t('goals.dragToReorder')">
          <span class="drag-icon">⋮⋮</span>
        </div>
        <GoalItem
          :goal="goal"
          :readonly="readonly"
          @edit="emit('edit', $event)"
          @delete="emit('delete', $event)"
        />
      </div>
    </div>
  </div>
</template>

<style scoped>
.goal-list {
  min-height: 200px;
}

.loading-state,
.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 3rem 1rem;
  text-align: center;
  color: var(--color-gray-600);
}

.spinner {
  width: 40px;
  height: 40px;
  border: 3px solid var(--color-gray-200);
  border-top-color: var(--color-magenta);
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin-bottom: 1rem;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

.empty-icon {
  font-size: 3rem;
  margin-bottom: 1rem;
}

.empty-state h3 {
  margin: 0 0 0.5rem;
  color: var(--color-gray-900);
}

.empty-state p {
  margin: 0;
  font-size: 0.875rem;
}

.goals {
  display: flex;
  flex-direction: column;
}

.goal-wrapper {
  display: flex;
  align-items: stretch;
  margin-bottom: 0.75rem;
  border-radius: 8px;
  transition: transform 0.15s ease, box-shadow 0.15s ease, background-color 0.15s ease;
}

.goal-wrapper[draggable="true"] {
  cursor: grab;
}

.goal-wrapper[draggable="true"]:active {
  cursor: grabbing;
}

.goal-wrapper.is-dragging {
  opacity: 0.5;
  transform: scale(0.98);
}

.goal-wrapper.is-drag-over {
  background: var(--color-gray-100);
  box-shadow: 0 0 0 2px var(--color-magenta);
  border-radius: 8px;
}

.goal-wrapper :deep(.goal-item) {
  flex: 1;
  margin-bottom: 0;
}

.drag-handle {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 24px;
  background: var(--color-gray-100);
  border: 1px solid var(--color-gray-200);
  border-right: none;
  border-radius: 8px 0 0 8px;
  cursor: grab;
  user-select: none;
}

.drag-handle:active {
  cursor: grabbing;
}

.drag-icon {
  color: var(--color-gray-400);
  font-size: 0.875rem;
  letter-spacing: 1px;
}

.goal-wrapper:hover .drag-icon {
  color: var(--color-gray-600);
}
</style>
