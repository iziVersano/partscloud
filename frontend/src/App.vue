<script setup>
import InventoryView from "./features/inventory/InventoryView.vue";
</script>

<template>
  <main>
    <header class="page-header">
      <h1>PartsCloud</h1>
      <p class="subtitle">Stockout risk for spare-part inventory</p>
    </header>
    <InventoryView />
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
</style>
