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
    <button :disabled="store.page === 1" @click="prev">‹ Prev</button>
    <span class="page-indicator" aria-live="polite">
      Page {{ store.page }} of {{ store.totalPages }}
    </span>
    <button :disabled="store.page === store.totalPages" @click="next">Next ›</button>
  </div>
</template>

<style scoped>
.pagination {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 1rem;
  padding: 0.9rem 1rem;
  background: #f9fafb;
  border: 1px solid #e5e7eb;
  border-radius: 0 0 10px 10px;
}
.pagination button {
  padding: 0.4rem 0.9rem;
  border-radius: 6px;
  border: 1px solid #d1d5db;
  background: white;
  font-size: 0.85rem;
  cursor: pointer;
  color: #374151;
}
.pagination button:hover:not(:disabled) {
  background: #f3f4f6;
}
.pagination button:disabled {
  opacity: 0.4;
  cursor: default;
}
.page-indicator {
  font-size: 0.85rem;
  color: #6b7280;
}
</style>
