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
    <button :disabled="store.page === 1" @click="store.setPage(1)">« First</button>
    <button :disabled="store.page === 1" @click="prev">‹ Prev</button>
    <span class="page-indicator">Page {{ store.page }} of {{ store.totalPages }}</span>
    <button :disabled="store.page === store.totalPages" @click="next">Next ›</button>
    <button :disabled="store.page === store.totalPages" @click="store.setPage(store.totalPages)">Last »</button>
  </div>
</template>

<style scoped>
.pagination {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 1rem;
  padding: 0.6rem 1rem;
  background: #f9fafb;
  border: 1px solid #e5e7eb;
  border-radius: 8px;
  margin: 0.5rem 0;
}
.pagination button {
  padding: 0.4rem 1rem;
  border-radius: 6px;
  border: 1px solid #d1d5db;
  background: white;
  font-size: 0.85rem;
  font-weight: 500;
  cursor: pointer;
  color: #374151;
  box-shadow: 0 1px 2px rgba(0,0,0,0.05);
}
.pagination button:hover:not(:disabled) {
  background: #e5e7eb;
  border-color: #9ca3af;
}
.pagination button:disabled {
  opacity: 0.35;
  cursor: default;
  box-shadow: none;
}
.page-indicator {
  font-size: 0.875rem;
  font-weight: 600;
  color: #374151;
}
</style>
