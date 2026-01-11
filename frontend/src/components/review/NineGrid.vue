<script setup lang="ts">
import { computed } from 'vue'

type VetoType = 'SCF' | 'KAR' | 'COMPETENCY' | null

interface Props {
  whatScore?: number | null
  howScore?: number | null
  vetoActive?: boolean
  vetoType?: VetoType
  compact?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  whatScore: null,
  howScore: null,
  vetoActive: false,
  vetoType: null,
  compact: false,
})

// Grid values (3 = top/right, 1 = bottom/left)
const whatValues = [3, 2, 1] as const // Rows from top to bottom
const howValues = [1, 2, 3] as const // Columns from left to right

// Color mapping based on cell position
// Red: Low performance (1,1), (1,2), (2,1)
// Orange: Developing (1,3), (2,2), (3,1)
// Green: Solid performers (2,3), (3,2)
// Dark Green: Top performers (3,3)
function getCellColor(what: number, how: number): string {
  const sum = what + how

  if (what === 3 && how === 3) return 'color-dark-green'
  if (sum >= 5) return 'color-green'
  if (sum >= 4 || (what === 2 && how === 2)) return 'color-orange'
  return 'color-red'
}

// Calculate the rounded cell position
const cellPosition = computed(() => {
  if (props.whatScore === null || props.howScore === null) {
    return null
  }

  // Round and clamp to 1-3
  const what = Math.min(3, Math.max(1, Math.round(props.whatScore)))
  const how = Math.min(3, Math.max(1, Math.round(props.howScore)))

  return { what, how }
})

// Check if marker should be in this cell
function hasMarker(what: number, how: number): boolean {
  if (!cellPosition.value) return false
  return cellPosition.value.what === what && cellPosition.value.how === how
}

// Aria label for the grid
const ariaLabel = computed(() => {
  if (!cellPosition.value) {
    return '9-Grid performance matrix. No scores entered.'
  }
  return `9-Grid performance matrix. Current position: WHAT: ${props.whatScore}, HOW: ${props.howScore}`
})
</script>

<template>
  <div class="nine-grid" :class="{ compact }">
    <!-- Y-axis label (WHAT) -->
    <div v-if="!compact" class="axis-title y-axis-title">WHAT</div>

    <div class="grid-container">
      <!-- Row labels -->
      <div class="row-labels">
        <div v-for="what in whatValues" :key="what" class="row-label">{{ what }}</div>
      </div>

      <!-- Grid -->
      <div
        class="grid"
        role="grid"
        :aria-label="ariaLabel"
      >
        <template v-for="what in whatValues" :key="`row-${what}`">
          <div
            v-for="how in howValues"
            :key="`cell-${what}-${how}`"
            class="grid-cell"
            :class="getCellColor(what, how)"
            :data-what="what"
            :data-how="how"
            role="gridcell"
          >
            <div v-if="hasMarker(what, how)" class="position-marker" />
          </div>
        </template>
      </div>

      <!-- Column labels -->
      <div class="col-labels">
        <div v-for="how in howValues" :key="how" class="col-label">{{ how }}</div>
      </div>
    </div>

    <!-- X-axis label (HOW) -->
    <div v-if="!compact" class="axis-title x-axis-title">HOW</div>

    <!-- VETO indicator -->
    <div v-if="vetoActive" class="veto-indicator">
      VETO Active
    </div>
  </div>
</template>

<style scoped>
.nine-grid {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.5rem;
}

.nine-grid.compact {
  gap: 0.25rem;
}

.axis-title {
  font-size: 0.75rem;
  font-weight: 600;
  color: var(--color-gray-600);
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.y-axis-title {
  writing-mode: vertical-rl;
  text-orientation: mixed;
  transform: rotate(180deg);
  position: absolute;
  left: -1.5rem;
  top: 50%;
  transform: rotate(180deg) translateY(50%);
}

.x-axis-title {
  margin-top: 0.25rem;
}

.grid-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  position: relative;
}

.row-labels {
  position: absolute;
  left: -1.5rem;
  top: 0;
  height: 100%;
  display: flex;
  flex-direction: column;
}

.row-label {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 0.75rem;
  font-weight: 500;
  color: var(--color-gray-600);
  width: 1rem;
}

.col-labels {
  display: flex;
  margin-top: 0.25rem;
}

.col-label {
  width: 60px;
  text-align: center;
  font-size: 0.75rem;
  font-weight: 500;
  color: var(--color-gray-600);
}

.compact .col-label {
  width: 40px;
}

.grid {
  display: grid;
  grid-template-columns: repeat(3, 60px);
  grid-template-rows: repeat(3, 60px);
  gap: 2px;
  background: var(--color-gray-200);
  padding: 2px;
  border-radius: 4px;
}

.compact .grid {
  grid-template-columns: repeat(3, 40px);
  grid-template-rows: repeat(3, 40px);
}

.grid-cell {
  position: relative;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 2px;
}

.color-red {
  background-color: var(--color-grid-red);
}

.color-orange {
  background-color: var(--color-grid-orange);
}

.color-green {
  background-color: var(--color-grid-green);
}

.color-dark-green {
  background-color: var(--color-grid-dark-green);
}

.position-marker {
  width: 20px;
  height: 20px;
  background-color: var(--color-white);
  border: 3px solid var(--color-navy);
  border-radius: 50%;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.3);
}

.compact .position-marker {
  width: 14px;
  height: 14px;
  border-width: 2px;
}

.veto-indicator {
  position: absolute;
  top: 0;
  right: 0;
  background-color: var(--color-grid-red);
  color: var(--color-white);
  font-size: 0.625rem;
  font-weight: 600;
  padding: 0.125rem 0.375rem;
  border-radius: 2px;
  text-transform: uppercase;
}

/* Responsive styles */
@media (max-width: 480px) {
  .grid {
    grid-template-columns: repeat(3, 50px);
    grid-template-rows: repeat(3, 50px);
  }

  .col-label {
    width: 50px;
    font-size: 0.625rem;
  }

  .row-label {
    font-size: 0.625rem;
  }

  .position-marker {
    width: 16px;
    height: 16px;
  }

  .row-labels {
    left: -1.25rem;
  }
}
</style>
