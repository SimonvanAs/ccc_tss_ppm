<script setup lang="ts">
import { useI18n } from 'vue-i18n'
import { getCurrentUser, logout } from '../api/auth'
import { RouterLink } from 'vue-router'
import { Card, SectionHeader } from '../components/layout'

const { t } = useI18n()
const user = getCurrentUser()
</script>

<template>
  <div class="dashboard">
    <!-- Page Header -->
    <SectionHeader :title="t('dashboard.title')">
      <template #subtitle>
        {{ t('dashboard.welcome') }}
      </template>
    </SectionHeader>

    <!-- User Info Card -->
    <Card v-if="user" class="user-card">
      <h3 class="card-title">Logged in as:</h3>
      <p><strong>Email:</strong> {{ user.email }}</p>
      <p><strong>Name:</strong> {{ user.name }}</p>
      <p><strong>Roles:</strong> {{ user.roles.join(', ') }}</p>
      <button @click="logout" class="logout-btn">Logout</button>
    </Card>

    <!-- Quick Links Card -->
    <Card class="quick-links-card">
      <h3 class="card-title">Quick Links</h3>
      <RouterLink to="/reviews/33333333-3333-3333-3333-333333333333/goals" class="link-btn">
        Go to Goal Setting (Demo)
      </RouterLink>
    </Card>
  </div>
</template>

<style scoped>
.dashboard {
  max-width: 1200px;
  margin: 0 auto;
}

.user-card,
.quick-links-card {
  margin-top: 1rem;
}

.card-title {
  color: var(--color-navy);
  margin: 0 0 0.75rem;
  font-size: 1rem;
}

.user-card p {
  margin: 0.5rem 0;
}

.logout-btn {
  margin-top: 1rem;
  background: var(--color-magenta);
  color: white;
  border: none;
  padding: 0.5rem 1rem;
  border-radius: 4px;
  cursor: pointer;
  font-family: inherit;
}

.logout-btn:hover {
  opacity: 0.9;
}

.link-btn {
  display: inline-block;
  background: var(--color-navy);
  color: white;
  padding: 0.75rem 1.5rem;
  border-radius: 4px;
  text-decoration: none;
  margin-top: 0.5rem;
}

.link-btn:hover {
  opacity: 0.9;
}
</style>
