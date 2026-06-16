<script setup>
import { onMounted } from "vue";
import { useInventoryStore } from "./features/inventory/store/inventoryStore";
import PartsTable from "./features/inventory/components/PartsTable.vue";
import FilterBar from "./features/inventory/components/FilterBar.vue";
import BulkActionBar from "./features/inventory/components/BulkActionBar.vue";
import Pagination from "./features/inventory/components/Pagination.vue";

const store = useInventoryStore();

onMounted(() => {
  store.load();
});
</script>

<template>
  <main>
    <header class="page-header">
      <h1>PartsCloud</h1>
      <p class="subtitle">Stockout risk for spare-part inventory</p>
    </header>

    <p v-if="store.loading" class="state-message">Loading…</p>
    <p v-else-if="store.error" class="state-message error">
      Failed to load: {{ store.error }}
    </p>
    <template v-else>
      <p v-if="store.actionError" class="action-error">{{ store.actionError }}</p>
      <FilterBar />
      <BulkActionBar />
      <Pagination />
      <PartsTable />
      <Pagination />
    </template>
  </main>
</template>

<style>
* {
  box-sizing: border-box;
}
body {
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto,
    Helvetica, Arial, sans-serif;
  margin: 0;
  background: #f6f7f9;
  color: #111827;
}
main {
  max-width: 1080px;
  margin: 0 auto;
  padding: 2.5rem 1.5rem 4rem;
}
.page-header {
  margin-bottom: 1.75rem;
}
.page-header h1 {
  font-size: 1.6rem;
  font-weight: 700;
  margin: 0 0 0.2rem;
  letter-spacing: -0.01em;
}
.subtitle {
  margin: 0;
  color: #6b7280;
  font-size: 0.95rem;
}
.state-message {
  color: #6b7280;
}
.state-message.error {
  color: #991b1b;
}
.action-error {
  background: #fef2f2;
  border: 1px solid #fecaca;
  color: #991b1b;
  padding: 0.6rem 0.9rem;
  border-radius: 8px;
  font-size: 0.85rem;
  margin-bottom: 1rem;
}
</style>
