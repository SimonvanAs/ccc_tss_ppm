<script setup lang="ts">
import { computed, ref } from 'vue'
import { useI18n } from 'vue-i18n'

interface TeamMember {
  id: string
  email: string
  first_name: string | null
  last_name: string | null
  review_id: string | null
  review_status: string | null
  what_score: number | null
  how_score: number | null
  grid_position_what: number | null
  grid_position_how: number | null
  what_veto_active: boolean
  how_veto_active: boolean
}

interface Props {
  employees: TeamMember[]
  maxMarkersPerCell?: number
}

const props = withDefaults(defineProps<Props>(), {
  maxMarkersPerCell: 5,
})

const emit = defineEmits<{
  (e: 'employee-click', employee: TeamMember): void
}>()

const { t } = useI18n()

// Grid values (3 = top/right, 1 = bottom/left)
const whatValues = [3, 2, 1] as const // Rows from top to bottom
const howValues = [1, 2, 3] as const // Columns from left to right

// Track hovered employee for tooltip
const hoveredEmployee = ref<TeamMember | null>(null)

// Filter employees that have grid positions
const employeesWithScores = computed(() =>
  props.employees.filter(
    (emp) => emp.grid_position_what !== null && emp.grid_position_how !== null
  )
)

// Check if any employees have scores
const hasEmployeesWithScores = computed(() => employeesWithScores.value.length > 0)

// Group employees by grid position
const employeesByCell = computed(() => {
  const map = new Map<string, TeamMember[]>()

  for (const emp of employeesWithScores.value) {
    const key = `${emp.grid_position_what}-${emp.grid_position_how}`
    if (!map.has(key)) {
      map.set(key, [])
    }
    map.get(key)!.push(emp)
  }

  return map
})

// Get employees for a specific cell
function getEmployeesInCell(what: number, how: number): TeamMember[] {
  const key = `${what}-${how}`
  return employeesByCell.value.get(key) || []
}

// Get count for a cell
function getCellCount(what: number, how: number): number {
  return getEmployeesInCell(what, how).length
}

// Get visible markers (limited by maxMarkersPerCell)
function getVisibleMarkers(what: number, how: number): TeamMember[] {
  const employees = getEmployeesInCell(what, how)
  return employees.slice(0, props.maxMarkersPerCell)
}

// Color mapping based on cell position
function getCellColor(what: number, how: number): string {
  const sum = what + how

  if (what === 3 && how === 3) return 'color-dark-green'
  if (sum >= 5) return 'color-green'
  if (sum >= 4 || (what === 2 && how === 2)) return 'color-orange'
  return 'color-red'
}

// Employee display name
function getEmployeeName(employee: TeamMember): string {
  if (employee.first_name && employee.last_name) {
    return `${employee.first_name} ${employee.last_name}`
  }
  if (employee.first_name) return employee.first_name
  if (employee.last_name) return employee.last_name
  return employee.email
}

// Get employee initials for marker
function getEmployeeInitials(employee: TeamMember): string {
  if (employee.first_name && employee.last_name) {
    return `${employee.first_name[0]}${employee.last_name[0]}`.toUpperCase()
  }
  if (employee.first_name) return employee.first_name[0].toUpperCase()
  if (employee.last_name) return employee.last_name[0].toUpperCase()
  return employee.email[0].toUpperCase()
}

// Handle marker click
function handleMarkerClick(employee: TeamMember) {
  emit('employee-click', employee)
}

// Handle keyboard navigation
function handleKeydown(event: KeyboardEvent, employee: TeamMember) {
  if (event.key === 'Enter' || event.key === ' ') {
    event.preventDefault()
    handleMarkerClick(employee)
  }
}

// Handle hover
function handleMouseEnter(employee: TeamMember) {
  hoveredEmployee.value = employee
}

function handleMouseLeave() {
  hoveredEmployee.value = null
}

// Check if marker has veto
function hasVeto(employee: TeamMember): boolean {
  return employee.what_veto_active || employee.how_veto_active
}

// Aria label for grid
const ariaLabel = computed(() => {
  const count = employeesWithScores.value.length
  return `Team 9-Grid performance matrix. ${count} employee${count !== 1 ? 's' : ''} displayed.`
})
</script>

<template>
  <div class="team-nine-grid">
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
            <!-- Markers container for multiple employees -->
            <div
              v-if="getEmployeesInCell(what, how).length > 0"
              class="markers-container"
              :class="{ 'has-multiple': getCellCount(what, how) > 1 }"
            >
              <button
                v-for="(employee, index) in getVisibleMarkers(what, how)"
                :key="employee.id"
                type="button"
                class="employee-marker"
                :class="{
                  'veto-active': hasVeto(employee),
                  [`marker-${index}`]: true,
                }"
                role="button"
                tabindex="0"
                :aria-label="`${getEmployeeName(employee)} - ${t('teamGrid.clickToView')}`"
                :title="getEmployeeName(employee)"
                @click="handleMarkerClick(employee)"
                @keydown="handleKeydown($event, employee)"
                @mouseenter="handleMouseEnter(employee)"
                @mouseleave="handleMouseLeave"
              >
                <span class="marker-initials">{{ getEmployeeInitials(employee) }}</span>
              </button>
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
      v-if="hoveredEmployee"
      class="employee-tooltip"
      role="tooltip"
    >
      <div class="tooltip-name">{{ getEmployeeName(hoveredEmployee) }}</div>
      <div class="tooltip-scores">
        <span>{{ t('teamGrid.whatScore') }}: {{ hoveredEmployee.what_score?.toFixed(2) || '-' }}</span>
        <span>{{ t('teamGrid.howScore') }}: {{ hoveredEmployee.how_score?.toFixed(2) || '-' }}</span>
      </div>
      <div class="tooltip-status">
        {{ t('teamGrid.status') }}: {{ hoveredEmployee.review_status || 'N/A' }}
      </div>
    </div>

    <!-- No scores message -->
    <div v-if="!hasEmployeesWithScores" class="no-scores-message">
      {{ t('teamGrid.noEmployees') }}
    </div>
  </div>
</template>

<style scoped>
.team-nine-grid {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.5rem;
  position: relative;
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
  width: 100px;
  text-align: center;
  font-size: 0.75rem;
  font-weight: 500;
  color: var(--color-gray-600);
}

.grid {
  display: grid;
  grid-template-columns: repeat(3, 100px);
  grid-template-rows: repeat(3, 100px);
  gap: 2px;
  background: var(--color-gray-200);
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
  background-color: var(--color-white);
  border: 2px solid var(--color-navy);
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
  outline: 2px solid var(--color-magenta);
  outline-offset: 2px;
}

.employee-marker.veto-active {
  border-color: var(--color-grid-red);
  background-color: #fef2f2;
}

.marker-initials {
  font-size: 0.625rem;
  font-weight: 600;
  color: var(--color-navy);
}

.cell-count {
  position: absolute;
  top: 2px;
  right: 2px;
  background-color: var(--color-navy);
  color: var(--color-white);
  font-size: 0.625rem;
  font-weight: 600;
  width: 18px;
  height: 18px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
}

.employee-tooltip {
  position: absolute;
  bottom: 100%;
  left: 50%;
  transform: translateX(-50%);
  background-color: var(--color-navy);
  color: var(--color-white);
  padding: 0.75rem;
  border-radius: 4px;
  font-size: 0.75rem;
  min-width: 160px;
  z-index: 100;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  margin-bottom: 0.5rem;
}

.employee-tooltip::after {
  content: '';
  position: absolute;
  top: 100%;
  left: 50%;
  transform: translateX(-50%);
  border: 6px solid transparent;
  border-top-color: var(--color-navy);
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

.tooltip-status {
  margin-top: 0.375rem;
  padding-top: 0.375rem;
  border-top: 1px solid rgba(255, 255, 255, 0.2);
  opacity: 0.9;
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
  color: var(--color-gray-600);
  text-align: center;
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
