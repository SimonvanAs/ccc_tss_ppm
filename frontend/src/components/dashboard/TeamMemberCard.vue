<script setup lang="ts">
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'
import type { TeamMember } from '../../types'
import { ScoringStatus } from '../../types'

const props = defineProps<{
  member: TeamMember
}>()

defineEmits<{
  click: []
}>()

const { t } = useI18n()

const fullName = computed(() => {
  const parts = []
  if (props.member.first_name) parts.push(props.member.first_name)
  if (props.member.last_name) parts.push(props.member.last_name)
  return parts.join(' ') || props.member.email
})

const statusText = computed(() => {
  return t(`team.scoringStatus.${props.member.scoring_status}`)
})

const statusClass = computed(() => {
  switch (props.member.scoring_status) {
    case ScoringStatus.NOT_STARTED:
      return 'status-not-started'
    case ScoringStatus.IN_PROGRESS:
      return 'status-in-progress'
    case ScoringStatus.COMPLETE:
      return 'status-complete'
    default:
      return ''
  }
})
</script>

<template>
  <div class="team-member-card" @click="$emit('click')">
    <div class="card-header">
      <div class="member-info">
        <h3 class="member-name">{{ fullName }}</h3>
        <p class="member-title" v-if="member.function_title">{{ member.function_title }}</p>
        <p class="member-email">{{ member.email }}</p>
      </div>
      <div class="tov-level" v-if="member.tov_level">
        <span class="tov-badge">{{ member.tov_level }}</span>
      </div>
    </div>
    <div class="card-footer">
      <span :class="['status-badge', statusClass]">{{ statusText }}</span>
    </div>
  </div>
</template>

<style scoped>
.team-member-card {
  background: white;
  border-radius: 8px;
  padding: 1.25rem;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  cursor: pointer;
  transition: transform 0.2s, box-shadow 0.2s;
}

.team-member-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 1rem;
}

.member-info {
  flex: 1;
}

.member-name {
  margin: 0 0 0.25rem 0;
  font-size: 1.1rem;
  color: var(--color-navy);
}

.member-title {
  margin: 0 0 0.25rem 0;
  color: #666;
  font-size: 0.9rem;
}

.member-email {
  margin: 0;
  color: #999;
  font-size: 0.85rem;
}

.tov-level {
  margin-left: 1rem;
}

.tov-badge {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 28px;
  height: 28px;
  border-radius: 50%;
  background: var(--color-navy);
  color: white;
  font-weight: bold;
  font-size: 0.85rem;
}

.card-footer {
  border-top: 1px solid #eee;
  padding-top: 0.75rem;
}

.status-badge {
  display: inline-block;
  padding: 0.25rem 0.75rem;
  border-radius: 12px;
  font-size: 0.8rem;
  font-weight: 500;
}

.status-not-started {
  background: #f8d7da;
  color: #721c24;
}

.status-in-progress {
  background: #fff3cd;
  color: #856404;
}

.status-complete {
  background: #d4edda;
  color: #155724;
}
</style>
