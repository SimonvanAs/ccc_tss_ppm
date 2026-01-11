<script setup lang="ts">
// TSS PPM v3.0 - CalibrationNineGrid Component
import { computed, ref } from 'vue'
import { useI18n } from 'vue-i18n'
import type { CalibrationReview } from '../../api/calibration'

interface Props {
  reviews: CalibrationReview[]
  selectedReviewId?: string
  maxMarkersPerCell?: number
}

const props = withDefaults(defineProps<Props>(), {
  maxMarkersPerCell: 5,
})

const emit = defineEmits<{
  (e: 'select', review: CalibrationReview): void
}>()

const { t } = useI18n()

// Grid values (3 = top/right, 1 = bottom/left)
const whatValues = [3, 2, 1] as const // Rows from top to bottom
const howValues = [1, 2, 3] as const // Columns from left to right

// Track hovered review for tooltip
const hoveredReview = ref<CalibrationReview | null>(null)

// Filter reviews that have grid positions
const reviewsWithScores = computed(() =>
  props.reviews.filter(
    (review) => review.grid_position_what !== null && review.grid_position_how !== null
  )
)

// Check if any reviews have scores
const hasReviewsWithScores = computed(() => reviewsWithScores.value.length > 0)

// Group reviews by grid position
const reviewsByCell = computed(() => {
  const map = new Map<string, CalibrationReview[]>()

  for (const review of reviewsWithScores.value) {
    const key = `${review.grid_position_what}-${review.grid_position_how}`
    if (!map.has(key)) {
      map.set(key, [])
    }
    map.get(key)!.push(review)
  }

  return map
})

// Get reviews for a specific cell
function getReviewsInCell(what: number, how: number): CalibrationReview[] {
  const key = `${what}-${how}`
  return reviewsByCell.value.get(key) || []
}

// Get count for a cell
function getCellCount(what: number, how: number): number {
  return getReviewsInCell(what, how).length
}

// Get visible markers (limited by maxMarkersPerCell)
function getVisibleMarkers(what: number, how: number): CalibrationReview[] {
  const reviews = getReviewsInCell(what, how)
  return reviews.slice(0, props.maxMarkersPerCell)
}

// Check if cell has overflow
function hasOverflow(what: number, how: number): boolean {
  return getCellCount(what, how) > props.maxMarkersPerCell
}

// Color mapping based on cell position
function getCellColor(what: number, how: number): string {
  const sum = what + how

  if (what === 3 && how === 3) return 'color-dark-green'
  if (sum >= 5) return 'color-green'
  if (sum >= 4 || (what === 2 && how === 2)) return 'color-orange'
  return 'color-red'
}

// Get employee initials for marker
function getEmployeeInitials(review: CalibrationReview): string {
  const name = review.employee_name
  if (!name) return '?'

  const parts = name.split(' ')
  if (parts.length >= 2) {
    return `${parts[0][0]}${parts[parts.length - 1][0]}`.toUpperCase()
  }
  return name[0].toUpperCase()
}

// Format score for display
function formatScore(score: number | null): string {
  if (score === null) return '-'
  return score.toFixed(2)
}

// Get manager display name
function getManagerName(review: CalibrationReview): string {
  if (review.manager_first_name && review.manager_last_name) {
    return `${review.manager_first_name} ${review.manager_last_name}`
  }
  if (review.manager_first_name) return review.manager_first_name
  if (review.manager_last_name) return review.manager_last_name
  return '-'
}

// Handle marker click
function handleMarkerClick(review: CalibrationReview) {
  emit('select', review)
}

// Handle keyboard navigation
function handleKeydown(event: KeyboardEvent, review: CalibrationReview) {
  if (event.key === 'Enter' || event.key === ' ') {
    event.preventDefault()
    handleMarkerClick(review)
  }
}

// Handle hover
function handleMouseEnter(review: CalibrationReview) {
  hoveredReview.value = review
}

function handleMouseLeave() {
  hoveredReview.value = null
}

// Check if review has veto
function hasVeto(review: CalibrationReview): boolean {
  return review.what_veto_active || review.how_veto_active
}

// Check if review is selected
function isSelected(review: CalibrationReview): boolean {
  return review.review_id === props.selectedReviewId
}

// Aria label for grid
const ariaLabel = computed(() => {
  const count = reviewsWithScores.value.length
  return `Calibration 9-Grid. ${count} review${count !== 1 ? 's' : ''} displayed.`
})
</script>

<template>
  <div class="calibration-nine-grid">
    <!-- Y-axis label (WHAT) -->
    <div class="axis-title y-axis-title">WHAT</div>

    <div class="grid-container">
      <!-- Row labels -->
      <div class="row-labels">
        <div v-for="what in whatValues" :key="what" class="row-label">{{ what }}</div>
      </div>

      <!-- Grid -->
      <div class="grid" role="grid" :aria-label="ariaLabel">
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
            <!-- Markers container for multiple reviews -->
            <div
              v-if="getReviewsInCell(what, how).length > 0"
              class="markers-container"
              :class="{ 'has-multiple': getCellCount(what, how) > 1 }"
            >
              <button
                v-for="(review, index) in getVisibleMarkers(what, how)"
                :key="review.review_id"
                type="button"
                class="employee-marker"
                :class="{
                  'veto-active': hasVeto(review),
                  'selected': isSelected(review),
                  [`marker-${index}`]: true,
                }"
                role="button"
                tabindex="0"
                :aria-label="`${review.employee_name} - ${t('calibration.grid.clickToSelect')}`"
                :title="review.employee_name"
                @click="handleMarkerClick(review)"
                @keydown="handleKeydown($event, review)"
                @mouseenter="handleMouseEnter(review)"
                @mouseleave="handleMouseLeave"
              >
                <span class="marker-initials">{{ getEmployeeInitials(review) }}</span>
              </button>

              <!-- Overflow indicator -->
              <div v-if="hasOverflow(what, how)" class="overflow-indicator">
                +{{ getCellCount(what, how) - maxMarkersPerCell }}
              </div>
            </div>

            <!-- Count badge for multiple employees -->
            <div v-if="getCellCount(what, how) > 1" class="cell-count">
              {{ getCellCount(what, how) }}
            </div>
          </div>
        </template>
      </div>

      <!-- Column labels -->
      <div class="col-labels">
        <div v-for="how in howValues" :key="how" class="col-label">{{ how }}</div>
      </div>
    </div>

    <!-- X-axis label (HOW) -->
    <div class="axis-title x-axis-title">HOW</div>

    <!-- Tooltip -->
    <div
      v-if="hoveredReview"
      class="employee-tooltip"
      role="tooltip"
    >
      <div class="tooltip-name">{{ hoveredReview.employee_name }}</div>
      <div class="tooltip-scores">
        <span>{{ t('calibration.grid.whatScore') }}: {{ formatScore(hoveredReview.what_score) }}</span>
        <span>{{ t('calibration.grid.howScore') }}: {{ formatScore(hoveredReview.how_score) }}</span>
      </div>
      <div class="tooltip-manager">
        {{ t('calibration.grid.manager') }}: {{ getManagerName(hoveredReview) }}
      </div>
      <div v-if="hasVeto(hoveredReview)" class="tooltip-veto">
        {{ t('calibration.grid.veto') }}
      </div>
    </div>

    <!-- No scores message -->
    <div v-if="!hasReviewsWithScores" class="no-scores-message">
      {{ t('calibration.grid.noReviews') }}
    </div>
  </div>
</template>

<style scoped>
.calibration-nine-grid {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.5rem;
  position: relative;
}

.axis-title {
  font-size: 0.75rem;
  font-weight: 600;
  color: var(--navy, #004a91);
  text-transform: uppercase;
  letter-spacing: 0.05em;
  font-family: Tahoma, sans-serif;
}

.y-axis-title {
  writing-mode: vertical-rl;
  text-orientation: mixed;
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
  color: #666;
  width: 1rem;
  font-family: Tahoma, sans-serif;
}

.col-labels {
  display: flex;
  margin-top: 0.25rem;
}

.col-label {
  width: 100px;
  text-align: center;
  font-size: 0.75rem;
  font-weight: 500;
  color: #666;
  font-family: Tahoma, sans-serif;
}

.grid {
  display: grid;
  grid-template-columns: repeat(3, 100px);
  grid-template-rows: repeat(3, 100px);
  gap: 2px;
  background: #e0e0e0;
  padding: 2px;
  border-radius: 4px;
}

.grid-cell {
  position: relative;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 2px;
}

.color-red {
  background-color: #ffcdd2;
}

.color-orange {
  background-color: #ffe0b2;
}

.color-green {
  background-color: #c8e6c9;
}

.color-dark-green {
  background-color: #a5d6a7;
}

.markers-container {
  display: flex;
  flex-wrap: wrap;
  gap: 4px;
  justify-content: center;
  align-items: center;
  padding: 4px;
}

.markers-container.has-multiple {
  justify-content: flex-start;
  align-content: flex-start;
}

.employee-marker {
  width: 28px;
  height: 28px;
  background-color: white;
  border: 2px solid var(--navy, #004a91);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all 0.2s ease;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
  padding: 0;
}

.employee-marker:hover {
  transform: scale(1.1);
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.3);
  z-index: 10;
}

.employee-marker:focus {
  outline: 2px solid var(--magenta, #cc0e70);
  outline-offset: 2px;
}

.employee-marker.selected {
  border-color: var(--magenta, #cc0e70);
  border-width: 3px;
  background-color: #fce4ec;
}

.employee-marker.veto-active {
  border-color: #c00;
  background-color: #fef2f2;
}

.marker-initials {
  font-size: 0.625rem;
  font-weight: 600;
  color: var(--navy, #004a91);
  font-family: Tahoma, sans-serif;
}

.overflow-indicator {
  font-size: 0.625rem;
  font-weight: 600;
  color: #666;
  font-family: Tahoma, sans-serif;
}

.cell-count {
  position: absolute;
  top: 2px;
  right: 2px;
  background-color: var(--navy, #004a91);
  color: white;
  font-size: 0.625rem;
  font-weight: 600;
  width: 18px;
  height: 18px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-family: Tahoma, sans-serif;
}

.employee-tooltip {
  position: absolute;
  bottom: 100%;
  left: 50%;
  transform: translateX(-50%);
  background-color: var(--navy, #004a91);
  color: white;
  padding: 0.75rem;
  border-radius: 4px;
  font-size: 0.75rem;
  min-width: 180px;
  z-index: 100;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  margin-bottom: 0.5rem;
  font-family: Tahoma, sans-serif;
}

.employee-tooltip::after {
  content: '';
  position: absolute;
  top: 100%;
  left: 50%;
  transform: translateX(-50%);
  border: 6px solid transparent;
  border-top-color: var(--navy, #004a91);
}

.tooltip-name {
  font-weight: 600;
  margin-bottom: 0.375rem;
}

.tooltip-scores {
  display: flex;
  flex-direction: column;
  gap: 0.125rem;
  opacity: 0.9;
}

.tooltip-manager {
  margin-top: 0.375rem;
  padding-top: 0.375rem;
  border-top: 1px solid rgba(255, 255, 255, 0.2);
  opacity: 0.9;
}

.tooltip-veto {
  margin-top: 0.375rem;
  padding: 0.25rem 0.5rem;
  background-color: #c00;
  border-radius: 2px;
  font-weight: 600;
  text-align: center;
}

.no-scores-message {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  background-color: rgba(255, 255, 255, 0.9);
  padding: 1rem 1.5rem;
  border-radius: 4px;
  font-size: 0.875rem;
  color: #666;
  text-align: center;
  font-family: Tahoma, sans-serif;
}

/* Responsive styles */
@media (max-width: 480px) {
  .grid {
    grid-template-columns: repeat(3, 80px);
    grid-template-rows: repeat(3, 80px);
  }

  .col-label {
    width: 80px;
  }

  .employee-marker {
    width: 24px;
    height: 24px;
  }

  .marker-initials {
    font-size: 0.5rem;
  }
}
</style>
