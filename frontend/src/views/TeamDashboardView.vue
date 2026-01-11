<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useI18n } from 'vue-i18n'
import { useRouter } from 'vue-router'
import { fetchTeamMembers } from '../api/team'
import type { TeamMember } from '../types'
import TeamMemberCard from '../components/dashboard/TeamMemberCard.vue'

const { t } = useI18n()
const router = useRouter()

const teamMembers = ref<TeamMember[]>([])
const loading = ref(true)
const error = ref<string | null>(null)

async function loadTeam() {
  loading.value = true
  error.value = null
  try {
    teamMembers.value = await fetchTeamMembers()
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

onMounted(() => {
  loadTeam()
})
</script>

<template>
  <div class="team-dashboard">
    <header class="page-header">
      <h1>{{ t('team.pageTitle') }}</h1>
      <p class="subtitle">{{ t('team.pageSubtitle') }}</p>
    </header>

    <div v-if="loading" class="loading-state">
      {{ t('team.loading') }}
    </div>

    <div v-else-if="error" class="error-state">
      {{ error }}
    </div>

    <div v-else-if="teamMembers.length === 0" class="empty-state">
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
  </div>
</template>

<style scoped>
.team-dashboard {
  max-width: 1200px;
  margin: 0 auto;
  padding: 2rem;
}

.page-header {
  margin-bottom: 2rem;
}

.page-header h1 {
  color: var(--color-navy);
  margin: 0 0 0.5rem 0;
}

.subtitle {
  color: #666;
  margin: 0;
}

.loading-state,
.error-state,
.empty-state {
  text-align: center;
  padding: 3rem;
  color: #666;
}

.error-state {
  color: #dc3545;
}

.team-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 1.5rem;
}
</style>
