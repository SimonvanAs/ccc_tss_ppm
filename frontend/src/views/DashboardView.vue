<script setup lang="ts">
import { useI18n } from 'vue-i18n'

const { t } = useI18n()
</script>

<template>
  <div class="dashboard">
    <h2>{{ t('dashboard.title') }}</h2>
    <p>{{ t('dashboard.welcome') }}</p>
  </div>
</template>

<style scoped>
.dashboard {
  max-width: 1200px;
  margin: 0 auto;
  padding: 2rem;
}

h2 {
  color: var(--color-navy);
  margin-bottom: 1rem;
}
</style>
