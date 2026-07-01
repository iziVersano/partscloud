<script setup>
import { onMounted } from "vue";
import { useInventoryStore } from "./features/inventory/store/inventoryStore";
import ErrorBoundary from "./components/ErrorBoundary.vue";
import ErrorBanner from "./features/inventory/components/ErrorBanner.vue";
import PartsTable from "./features/inventory/components/PartsTable.vue";
import FilterBar from "./features/inventory/components/FilterBar.vue";
import Pagination from "./features/inventory/components/Pagination.vue";

const store = useInventoryStore();

onMounted(() => {
  store.load();
});
</script>

<template>
  <ErrorBoundary>
    <main>
      <header class="page-header">
        <h1>PartsCloud</h1>
        <p class="subtitle">Stockout risk for spare-part inventory</p>
      </header>

      <ErrorBanner />

      <template v-if="!store.loading && !store.error">
        <FilterBar />
        <PartsTable />
        <Pagination />
      </template>
    </main>
  </ErrorBoundary>
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
</style>
