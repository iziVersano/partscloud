<script setup>
import { onMounted, defineAsyncComponent } from "vue";
import { useInventoryStore } from "./features/inventory/store/inventoryStore";
import ErrorBoundary from "./components/ErrorBoundary.vue";
import ErrorBanner from "./features/inventory/components/ErrorBanner.vue";
import PartsTable from "./features/inventory/components/PartsTable.vue";
import FilterBar from "./features/inventory/components/FilterBar.vue";
import Pagination from "./features/inventory/components/Pagination.vue";
import StatCards from "./features/inventory/components/StatCards.vue";
import TopBar from "./shared/ui/TopBar.vue";
import ToastHost from "./shared/ui/ToastHost.vue";

// The drawer and its SVG chart aren't needed until a row is clicked, so we
// code-split them out of the initial bundle.
const SkuDrawer = defineAsyncComponent(() =>
  import("./features/inventory/components/SkuDrawer.vue")
);

const store = useInventoryStore();

onMounted(() => {
  store.load();
  store.loadStats();
});
</script>

<template>
  <ErrorBoundary>
    <main>
      <TopBar />

      <ErrorBanner />

      <StatCards v-if="!store.error" />

      <template v-if="!store.error">
        <FilterBar />
        <PartsTable />
        <Pagination />
      </template>
    </main>
    <SkuDrawer />
    <ToastHost />
  </ErrorBoundary>
</template>

<style>
* {
  box-sizing: border-box;
}
html {
  /* Always reserve the scrollbar gutter so content doesn't shift sideways
     when a page is short enough to hide the scrollbar. */
  scrollbar-gutter: stable;
  overflow-y: scroll;
}
body {
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto,
    Helvetica, Arial, sans-serif;
  margin: 0;
  background: var(--c-app-bg);
  color: var(--c-ink);
  transition: background var(--dur) var(--ease), color var(--dur) var(--ease);
}
main {
  max-width: 1080px;
  margin: 0 auto;
  padding: 2.5rem 1.5rem 4rem;
}
</style>
