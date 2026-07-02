<script setup>
import { useInventoryStore } from "../store/inventoryStore";

const store = useInventoryStore();
</script>

<template>
  <p v-if="store.loading" class="state-message" aria-live="polite">Loading…</p>
  <p v-else-if="store.error" class="state-message error" role="alert">
    Failed to load: {{ store.error }}
  </p>
  <p v-else-if="store.actionError" class="action-error" role="alert">
    {{ store.actionError }}
    <button class="dismiss" @click="store.dismissActionError()" aria-label="Dismiss error">×</button>
  </p>
</template>

<style scoped>
.state-message {
  color: var(--c-muted);
}
.state-message.error {
  color: var(--c-critical);
}
.action-error {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: var(--sp-3);
  background: var(--c-critical-bg);
  border: 1px solid var(--c-critical-bg);
  color: var(--c-critical);
  padding: 0.6rem 0.9rem;
  border-radius: var(--r-md);
  font-size: var(--fs-sm);
  margin-bottom: var(--sp-4);
}
.action-error .dismiss {
  background: none;
  border: none;
  color: inherit;
  font-size: 1.1rem;
  line-height: 1;
  cursor: pointer;
  padding: 0 0.2rem;
}
</style>
