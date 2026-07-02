<script setup>
import { useInventoryStore } from "../store/inventoryStore";

const store = useInventoryStore();

function prev() {
  store.setPage(store.page - 1);
}

function next() {
  store.setPage(store.page + 1);
}
</script>

<template>
  <div v-if="store.totalPages > 1" class="pagination">
    <button :disabled="store.page === 1 || store.loading" @click="prev">‹ Prev</button>
    <span class="page-indicator" aria-live="polite">
      <span v-if="store.loading" class="page-spinner" aria-hidden="true" />
      Page {{ store.page }} of {{ store.totalPages }}
    </span>
    <button :disabled="store.page === store.totalPages || store.loading" @click="next">Next ›</button>
  </div>
</template>

<style scoped>
.pagination {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: var(--sp-4);
  padding: 0.9rem 1rem;
  background: var(--c-surface-2);
  border: 1px solid var(--c-line);
  border-radius: 0 0 var(--r-lg) var(--r-lg);
}
.pagination button {
  padding: 0.4rem 0.9rem;
  border-radius: var(--r-sm);
  border: 1px solid var(--c-line);
  background: var(--c-surface);
  font-size: var(--fs-sm);
  cursor: pointer;
  color: var(--c-ink-soft);
}
.pagination button:hover:not(:disabled) {
  background: var(--c-surface-2);
}
.pagination button:disabled {
  opacity: 0.4;
  cursor: default;
}
.page-indicator {
  display: inline-flex;
  align-items: center;
  gap: var(--sp-2);
  font-size: var(--fs-sm);
  color: var(--c-muted);
}
.page-spinner {
  display: inline-block;
  width: 10px;
  height: 10px;
  border: 2px solid currentColor;
  border-top-color: transparent;
  border-radius: 50%;
  animation: page-spin 0.6s linear infinite;
}
@keyframes page-spin {
  to {
    transform: rotate(360deg);
  }
}
</style>
