<script setup>
import { useInventoryStore } from "../store/inventoryStore";

const store = useInventoryStore();
</script>

<template>
  <p v-if="store.loading" class="state-message">Loading…</p>
  <p v-else-if="store.error" class="state-message error">
    Failed to load: {{ store.error }}
  </p>
  <p v-else-if="store.actionError" class="action-error">
    {{ store.actionError }}
    <button class="dismiss" @click="store.dismissActionError()">×</button>
  </p>
</template>

<style scoped>
.state-message {
  color: #6b7280;
}
.state-message.error {
  color: #991b1b;
}
.action-error {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 0.75rem;
  background: #fef2f2;
  border: 1px solid #fecaca;
  color: #991b1b;
  padding: 0.6rem 0.9rem;
  border-radius: 8px;
  font-size: 0.85rem;
  margin-bottom: 1rem;
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
