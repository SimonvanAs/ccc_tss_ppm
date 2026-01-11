<script setup lang="ts">
withDefaults(
  defineProps<{
    padding?: 'none' | 'sm' | 'md' | 'lg'
  }>(),
  {
    padding: 'md',
  }
)
</script>

<template>
  <div
    class="card"
    :class="{
      'card--no-padding': padding === 'none',
      'card--padding-sm': padding === 'sm',
      'card--padding-lg': padding === 'lg',
    }"
  >
    <slot />
  </div>
</template>

<style scoped>
.card {
  background-color: var(--color-white);
  border-radius: 8px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1), 0 1px 2px rgba(0, 0, 0, 0.06);
  padding: 1.5rem;
}

.card--no-padding {
  padding: 0;
}

.card--padding-sm {
  padding: 1rem;
}

.card--padding-lg {
  padding: 2rem;
}
</style>
