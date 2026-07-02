<script setup>
import { watch } from "vue";
import { useInventoryStore } from "../store/inventoryStore";
import { useDebouncedRef } from "../../../shared/composables/useDebouncedRef";

const store = useInventoryStore();

// `immediate` keeps the input responsive; `debounced` fires the search 300ms
// after typing stops, so we don't hit the API on every keystroke.
const { immediate: query, debounced } = useDebouncedRef(store.search, 300);

watch(debounced, (term) => {
  if (term !== store.search) store.setSearch(term);
});

function clear() {
  // Setting `query` alone would still search after the debounce delay;
  // searching immediately here is the whole point of a clear button.
  query.value = "";
  if (store.search !== "") store.setSearch("");
}
</script>

<template>
  <div class="search">
    <span v-if="store.loading" class="search__spinner" aria-hidden="true" />
    <svg v-else class="search__icon" width="16" height="16" viewBox="0 0 20 20" aria-hidden="true">
      <circle cx="9" cy="9" r="6" fill="none" stroke="currentColor" stroke-width="2" />
      <path d="M14 14l4 4" stroke="currentColor" stroke-width="2" stroke-linecap="round" />
    </svg>
    <input
      v-model="query"
      type="search"
      class="search__input"
      placeholder="Search SKU or name…"
      aria-label="Search parts"
    />
    <button v-if="query" class="search__clear" aria-label="Clear search" @click="clear">×</button>
  </div>
</template>

<style scoped>
.search {
  display: flex;
  align-items: center;
  gap: var(--sp-2);
  padding: 0 0.7rem;
  background: var(--c-surface);
  border: 1px solid var(--c-line);
  border-radius: var(--r-pill);
  height: 2.25rem;
  width: 220px;
  max-width: 100%;
}
.search:focus-within {
  border-color: var(--c-purple);
  box-shadow: 0 0 0 3px var(--c-purple-bg);
}
.search__icon {
  color: var(--c-muted);
  flex-shrink: 0;
}
.search__spinner {
  display: inline-block;
  flex-shrink: 0;
  width: 12px;
  height: 12px;
  border: 2px solid var(--c-purple);
  border-top-color: transparent;
  border-radius: 50%;
  animation: search-spin 0.6s linear infinite;
}
@keyframes search-spin {
  to {
    transform: rotate(360deg);
  }
}
.search__input {
  border: none;
  background: none;
  outline: none;
  font-size: var(--fs-sm);
  color: var(--c-ink);
  width: 100%;
}
.search__input::placeholder {
  color: var(--c-muted);
}
/* Hide the native search clear (we render our own). */
.search__input::-webkit-search-cancel-button {
  display: none;
}
.search__clear {
  background: none;
  border: none;
  color: var(--c-muted);
  font-size: 1.2rem;
  line-height: 1;
  cursor: pointer;
  padding: 0;
}
.search__clear:hover {
  color: var(--c-ink);
}
</style>
