<script setup lang="ts">
import { useSlots } from 'vue'

defineProps<{
  title: string
  subtitle?: string
}>()

const slots = useSlots()
</script>

<template>
  <div class="section-header">
    <div class="section-header__content">
      <h2 class="section-header__title">{{ title }}</h2>
      <p v-if="slots.subtitle || subtitle" class="section-header__subtitle">
        <slot name="subtitle">{{ subtitle }}</slot>
      </p>
    </div>
    <div v-if="slots.actions" class="section-header__actions">
      <slot name="actions" />
    </div>
  </div>
</template>

<style scoped>
.section-header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 1rem;
  margin-bottom: 1rem;
}

.section-header__content {
  flex: 1;
}

.section-header__title {
  color: var(--color-navy);
  font-family: Tahoma, sans-serif;
  font-size: 1.25rem;
  font-weight: bold;
  margin: 0;
  line-height: 1.4;
}

.section-header__subtitle {
  color: var(--color-gray-600);
  font-size: 0.875rem;
  margin: 0.25rem 0 0 0;
  line-height: 1.5;
}

.section-header__actions {
  flex-shrink: 0;
}
</style>
