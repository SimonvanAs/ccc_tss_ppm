<script setup lang="ts">
import type { TeamMember } from '../../types'

defineProps<{
  member: TeamMember
}>()

defineEmits<{
  click: []
}>()
</script>

<template>
  <div class="team-member-card" @click="$emit('click')">
    <!-- Placeholder - will be implemented in Task 3 -->
    <slot />
  </div>
</template>

<style scoped>
.team-member-card {
  cursor: pointer;
}
</style>
