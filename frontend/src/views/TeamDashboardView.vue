<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useI18n } from 'vue-i18n'
import { useRouter } from 'vue-router'
import { fetchTeamMembers, fetchTeamGrid } from '../api/team'
import type { TeamMember, TeamMemberGrid } from '../types'
import TeamMemberCard from '../components/dashboard/TeamMemberCard.vue'
import TeamNineGrid from '../components/review/TeamNineGrid.vue'
import { Card, SectionHeader } from '../components/layout'

const { t } = useI18n()
const router = useRouter()

const teamMembers = ref<TeamMember[]>([])
const gridMembers = ref<TeamMemberGrid[]>([])
const loading = ref(true)
const error = ref<string | null>(null)

async function loadTeam() {
  loading.value = true
  error.value = null
  try {
    // Fetch both team members and grid data in parallel
    const [members, grid] = await Promise.all([
      fetchTeamMembers(),
      fetchTeamGrid(),
    ])
    teamMembers.value = members
    gridMembers.value = grid
  } catch (e) {
    error.value = t('team.error')
  } finally {
    loading.value = false
  }
}

function handleMemberClick(member: TeamMember) {
  if (member.review_id) {
    router.push({ name: 'ReviewScoring', params: { reviewId: member.review_id } })
  }
}

function handleGridClick(member: TeamMemberGrid) {
  if (member.review_id) {
    router.push({ name: 'ReviewScoring', params: { reviewId: member.review_id } })
  }
}

onMounted(() => {
  loadTeam()
})
</script>

<template>
  <div class="team-dashboard">
    <!-- Page Header -->
    <SectionHeader :title="t('team.pageTitle')">
      <template #subtitle>
        {{ t('team.pageSubtitle') }}
      </template>
    </SectionHeader>

    <!-- Loading state -->
    <Card v-if="loading" class="state-card">
      <div class="loading-state">
        {{ t('team.loading') }}
      </div>
    </Card>

    <!-- Error state -->
    <Card v-else-if="error" class="state-card">
      <div class="error-state">
        {{ error }}
      </div>
    </Card>

    <!-- Content when loaded -->
    <template v-else>
      <!-- 9-Grid Overview Section -->
      <section class="nine-grid-section">
        <SectionHeader :title="t('teamGrid.title')" />
        <Card>
          <TeamNineGrid
            v-if="gridMembers.length > 0"
            :employees="gridMembers"
            @employee-click="handleGridClick"
          />
          <div v-else class="empty-grid-state">
            {{ t('teamGrid.noEmployees') }}
          </div>
        </Card>
      </section>

      <!-- Team Members List Section -->
      <section class="team-members-section">
        <SectionHeader :title="t('team.directReports')" />
        <div v-if="teamMembers.length === 0" class="empty-state">
          {{ t('team.emptyState') }}
        </div>
        <div v-else class="team-grid">
          <TeamMemberCard
            v-for="member in teamMembers"
            :key="member.id"
            :member="member"
            @click="handleMemberClick(member)"
          />
        </div>
      </section>
    </template>
  </div>
</template>

<style scoped>
.team-dashboard {
  max-width: 1200px;
  margin: 0 auto;
}

.state-card {
  margin-top: 1rem;
}

.loading-state,
.error-state,
.empty-state {
  text-align: center;
  padding: 2rem;
  color: var(--color-gray-600);
}

.error-state {
  color: var(--color-error);
}

.nine-grid-section {
  margin-top: 1.5rem;
}

.team-members-section {
  margin-top: 2rem;
}

.empty-grid-state {
  text-align: center;
  padding: 2rem;
  color: var(--color-gray-600);
}

.team-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 1.5rem;
  margin-top: 1rem;
}
</style>
