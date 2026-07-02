<script setup>
defineProps({
  padded: { type: Boolean, default: true },
  interactive: { type: Boolean, default: false },
});
</script>

<template>
  <div class="card" :class="{ 'card--padded': padded, 'card--interactive': interactive }">
    <slot />
  </div>
</template>

<style scoped>
.card {
  background: var(--c-surface);
  border: 1px solid var(--c-line);
  border-radius: var(--r-lg);
  box-shadow: var(--shadow-sm);
}
.card--padded {
  padding: var(--sp-5);
}
.card--interactive {
  cursor: pointer;
  transition: box-shadow var(--dur) var(--ease), transform var(--dur) var(--ease),
    border-color var(--dur) var(--ease);
}
.card--interactive:hover {
  box-shadow: var(--shadow-md);
  border-color: var(--c-purple);
  transform: translateY(-1px);
}
</style>
