<script setup>
import { onMounted } from "vue";
import { useInventoryStore } from "./store/inventoryStore";
import FilterBar from "./components/FilterBar.vue";
import BulkActionBar from "./components/BulkActionBar.vue";
import Pagination from "./components/Pagination.vue";
import PartsTable from "./components/PartsTable.vue";

const store = useInventoryStore();

onMounted(() => {
  store.load();
});
</script>

<template>
  <div>
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
  </div>
</template>

<style scoped>
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
