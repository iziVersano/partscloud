<script setup>
import { onMounted } from "vue";
import { useInventoryStore } from "./features/inventory/store/inventoryStore";
import PartsTable from "./features/inventory/components/PartsTable.vue";

const store = useInventoryStore();

onMounted(() => {
  store.load();
});
</script>

<template>
  <main>
    <h1>PartsCloud — Stockout Risk</h1>
    <p v-if="store.loading">Loading…</p>
    <p v-else-if="store.error">Failed to load: {{ store.error }}</p>
    <PartsTable v-else />
  </main>
</template>

<style>
body {
  font-family: system-ui, sans-serif;
  margin: 2rem;
  color: #1a1a1a;
}
</style>
