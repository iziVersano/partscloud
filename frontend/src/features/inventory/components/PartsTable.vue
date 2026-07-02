<script setup>
import { computed, ref, onMounted, onBeforeUnmount } from "vue";
import { useInventoryStore } from "../store/inventoryStore";
import RiskBadge from "./RiskBadge.vue";
import StatusIcon from "./StatusIcon.vue";
import BaseSkeleton from "../../../shared/ui/BaseSkeleton.vue";

const store = useInventoryStore();

const columns = [
  { label: "SKU", field: "sku" },
  { label: "Name", field: "name" },
  { label: "Category", field: "category" },
  { label: "On hand", field: "on_hand" },
  { label: "Risk", field: "risk_score" },
  { label: "Status", field: "action_status" },
];

function onCheckboxChange(sku) {
  store.toggleSelected(sku);
}

function accept(sku) {
  store.act(sku, "accepted");
}

function decline(sku) {
  store.act(sku, "declined");
}

function sortBy(field) {
  store.setSort(field);
}

function ariaSortFor(field) {
  if (store.sortField !== field) return "none";
  return store.sortDir === "asc" ? "ascending" : "descending";
}

// Select-all operates on the current page, not every filtered row across
// all pages — selection itself is still tracked globally, so checking
// boxes on page 1, then page 2, accumulates correctly.
const allOnPageSelected = computed(() =>
  store.skus.length > 0 &&
  store.skus.every((row) => store.selected.includes(row.sku))
);

function toggleSelectAll() {
  store.toggleSelectAll();
}

const dropdownOpen = ref(false);
const selectWrap = ref(null);

function selectAll() {
  store.skus.forEach((row) => {
    if (!store.selected.includes(row.sku)) store.toggleSelected(row.sku);
  });
  dropdownOpen.value = false;
}

function selectNone() {
  store.clearSelection();
  dropdownOpen.value = false;
}

function onClickOutside(e) {
  if (dropdownOpen.value && selectWrap.value && !selectWrap.value.contains(e.target)) {
    dropdownOpen.value = false;
  }
}

onMounted(() => document.addEventListener("click", onClickOutside));
onBeforeUnmount(() => document.removeEventListener("click", onClickOutside));
</script>

<template>
  <div class="table-card">
    <table class="parts-table">
      <caption class="visually-hidden">
        Spare parts inventory, sorted by {{ columns.find(c => c.field === store.sortField)?.label }}
      </caption>
      <thead>
        <tr>
          <th scope="col" class="checkbox-col">
            <div class="select-all-wrap" ref="selectWrap">
              <input
                type="checkbox"
                :checked="allOnPageSelected"
                @change="toggleSelectAll"
                aria-label="Select all rows on this page"
              />
              <button
                class="chevron-btn"
                @click="dropdownOpen = !dropdownOpen"
                aria-label="Selection options"
              >▾</button>
              <div v-if="dropdownOpen" class="select-dropdown">
                <button @click="selectAll">All</button>
                <button @click="selectNone">None</button>
              </div>
            </div>
          </th>
          <th
            v-for="col in columns"
            :key="col.field"
            scope="col"
            class="sortable"
            tabindex="0"
            :aria-sort="ariaSortFor(col.field)"
            @click="sortBy(col.field)"
            @keydown.enter="sortBy(col.field)"
            @keydown.space.prevent="sortBy(col.field)"
          >
            {{ col.label }}
            <span v-if="store.sortField === col.field" class="sort-arrow" aria-hidden="true">
              {{ store.sortDir === "asc" ? "▲" : "▼" }}
            </span>
          </th>
          <th scope="col">Action</th>
        </tr>
      </thead>
      <tbody v-if="store.loading">
        <tr v-for="n in 10" :key="`sk-${n}`" class="skeleton-row">
          <td class="checkbox-col"><BaseSkeleton width="16px" height="16px" /></td>
          <td><BaseSkeleton width="70%" /></td>
          <td><BaseSkeleton width="90%" /></td>
          <td><BaseSkeleton width="60%" /></td>
          <td><BaseSkeleton width="40%" /></td>
          <td><BaseSkeleton width="55px" height="1.3rem" radius="var(--r-pill)" /></td>
          <td><BaseSkeleton width="60%" /></td>
          <td><BaseSkeleton width="80%" /></td>
        </tr>
      </tbody>

      <tbody v-else class="row-list">
        <tr
          v-for="row in store.skus"
          :key="row.sku"
          class="row"
          @click="store.openSku(row.sku)"
        >
          <td class="checkbox-col" data-label="Select" @click.stop>
            <input
              type="checkbox"
              :checked="store.selected.includes(row.sku)"
              @change="onCheckboxChange(row.sku)"
              :aria-label="`Select ${row.sku}`"
            />
          </td>
          <td class="mono" data-label="SKU">{{ row.sku }}</td>
          <td data-label="Name">{{ row.name }}</td>
          <td class="muted" data-label="Category">{{ row.category }}</td>
          <td class="mono" data-label="On hand">{{ row.on_hand }}</td>
          <td data-label="Risk"><RiskBadge :risk="row.risk" /></td>
          <td data-label="Status"><StatusIcon :status="row.action_status" :risk="row.risk" /></td>
          <td class="actions" data-label="Action" @click.stop>
            <button
              class="btn accept"
              @click="accept(row.sku)"
              :disabled="row.action_status === 'accepted' || store.isPending(row.sku) || store.bulkPending"
            >
              <span v-if="store.isPending(row.sku)" class="spinner" aria-hidden="true"></span>
              {{ store.isPending(row.sku) ? "Saving…" : "Accept" }}
            </button>
            <button
              class="btn decline"
              @click="decline(row.sku)"
              :disabled="row.action_status === 'declined' || store.isPending(row.sku) || store.bulkPending"
            >
              <span v-if="store.isPending(row.sku)" class="spinner" aria-hidden="true"></span>
              {{ store.isPending(row.sku) ? "Saving…" : "Decline" }}
            </button>
          </td>
        </tr>
      </tbody>
    </table>

    <div v-if="!store.loading && store.skus.length === 0" class="empty-state">
      <svg width="40" height="40" viewBox="0 0 24 24" aria-hidden="true">
        <circle cx="11" cy="11" r="7" fill="none" stroke="currentColor" stroke-width="2" />
        <path d="M16 16l4 4" stroke="currentColor" stroke-width="2" stroke-linecap="round" />
      </svg>
      <p class="empty-state__title">No parts match your filters</p>
      <p class="empty-state__hint">Try a different risk filter or clear your search.</p>
    </div>
  </div>
</template>

<style scoped>
.table-card {
  background: var(--c-surface);
  border: 1px solid var(--c-line);
  border-radius: var(--r-lg);
  overflow: hidden;
  box-shadow: var(--shadow-sm);
  /* Reserve height for a full page (header + 10 rows) so a short last page
     or an emptied filter doesn't collapse the layout and cause a jump. */
  min-height: 517px;
}
.parts-table {
  width: 100%;
  border-collapse: collapse;
  font-size: var(--fs-md);
}
.parts-table th,
.parts-table td {
  padding: 0.7rem 0.9rem;
  text-align: left;
  vertical-align: middle;
}
.parts-table thead th {
  background: var(--c-surface-2);
  font-size: var(--fs-xs);
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.03em;
  color: var(--c-muted);
  border-bottom: 1px solid var(--c-line);
}
.parts-table tbody tr {
  border-bottom: 1px solid var(--c-line);
}
.parts-table tbody tr:last-child {
  border-bottom: none;
}
.parts-table tbody tr:hover {
  background: var(--c-surface-2);
}
.parts-table tbody tr.row {
  cursor: pointer;
}
.skeleton-row td {
  padding: 0.8rem 0.9rem;
}

/* Rows fade in on filter/sort/paginate. Plain keyframes rather than
   TransitionGroup: Vue's move animation applies position:absolute to
   leaving elements, which breaks <tr> layout inside a <table>. */
.row-list .row {
  animation: row-fade-in var(--dur) var(--ease);
}
@keyframes row-fade-in {
  from {
    opacity: 0;
  }
  to {
    opacity: 1;
  }
}

.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: var(--sp-7) var(--sp-4);
  color: var(--c-muted);
  text-align: center;
}
.empty-state__title {
  margin: var(--sp-3) 0 0;
  font-size: var(--fs-md);
  font-weight: 600;
  color: var(--c-ink-soft);
}
.empty-state__hint {
  margin: var(--sp-1) 0 0;
  font-size: var(--fs-sm);
}
.parts-table th.sortable {
  cursor: pointer;
  user-select: none;
}
.parts-table th.sortable:hover {
  color: var(--c-ink-soft);
}
.parts-table th.sortable:focus-visible {
  outline: 2px solid var(--c-purple);
  outline-offset: -2px;
}
.visually-hidden {
  position: absolute;
  width: 1px;
  height: 1px;
  padding: 0;
  margin: -1px;
  overflow: hidden;
  clip: rect(0, 0, 0, 0);
  white-space: nowrap;
  border: 0;
}
.sort-arrow {
  font-size: 0.7rem;
}
.checkbox-col {
  width: 4rem;
}
.select-all-wrap {
  position: relative;
  display: flex;
  align-items: center;
  gap: 2px;
}
.chevron-btn {
  background: none;
  border: none;
  padding: 0 2px;
  cursor: pointer;
  font-size: 0.75rem;
  color: var(--c-muted);
  line-height: 1;
}
.chevron-btn:hover {
  color: var(--c-ink);
}
.select-dropdown {
  position: absolute;
  top: calc(100% + 4px);
  left: 0;
  background: var(--c-surface);
  border: 1px solid var(--c-line);
  border-radius: var(--r-sm);
  box-shadow: var(--shadow-md);
  z-index: 10;
  min-width: 80px;
  overflow: hidden;
}
.select-dropdown button {
  display: block;
  width: 100%;
  padding: 0.45rem 0.85rem;
  background: none;
  border: none;
  text-align: left;
  font-size: var(--fs-sm);
  cursor: pointer;
  color: var(--c-ink);
}
.select-dropdown button:hover {
  background: var(--c-surface-2);
}
.parts-table input[type="checkbox"] {
  accent-color: var(--c-purple);
  width: 16px;
  height: 16px;
  cursor: pointer;
}
.mono {
  font-family: "SF Mono", "Roboto Mono", Consolas, monospace;
  font-size: 0.88rem;
  color: var(--c-ink-soft);
}
.muted {
  color: var(--c-muted);
}
.actions {
  white-space: nowrap;
}
.btn {
  padding: 0.35rem 0.75rem;
  border-radius: 6px;
  font-size: 0.82rem;
  font-weight: 500;
  cursor: pointer;
  border: 1px solid transparent;
  margin-right: 0.4rem;
  min-width: 4.5rem;
  white-space: nowrap;
}
.btn.accept {
  background: var(--c-ok-bg);
  border-color: transparent;
  color: var(--c-ok);
}
.btn.accept:hover:not(:disabled) {
  filter: brightness(0.97);
}
.btn.decline {
  background: var(--c-critical-bg);
  border-color: transparent;
  color: var(--c-critical);
}
.btn.decline:hover:not(:disabled) {
  filter: brightness(0.97);
}
.btn:disabled {
  opacity: 0.6;
  cursor: default;
}
.spinner {
  display: inline-block;
  width: 10px;
  height: 10px;
  border: 2px solid currentColor;
  border-top-color: transparent;
  border-radius: 50%;
  animation: spin 0.6s linear infinite;
  vertical-align: middle;
  margin-right: 4px;
}
@keyframes spin {
  to { transform: rotate(360deg); }
}

@media (max-width: 640px) {
  .parts-table thead {
    position: absolute;
    width: 1px;
    height: 1px;
    overflow: hidden;
    clip: rect(0, 0, 0, 0);
  }
  .parts-table,
  .parts-table tbody,
  .parts-table tr {
    display: block;
    width: 100%;
  }
  .parts-table tbody tr {
    padding: 0.75rem 0.9rem;
  }
  .parts-table td {
    display: block;
    width: 100%;
    box-sizing: border-box;
    padding: 0.3rem 0;
    text-align: left;
  }
  .parts-table td[data-label]::before {
    content: attr(data-label);
    display: block;
    font-size: var(--fs-xs);
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.03em;
    color: var(--c-muted);
  }
  .parts-table td.checkbox-col {
    display: flex;
    align-items: center;
    gap: var(--sp-2);
  }
  .parts-table td.checkbox-col::before {
    content: attr(data-label);
    font-size: var(--fs-sm);
    font-weight: 500;
    color: var(--c-ink-soft);
    text-transform: none;
    letter-spacing: normal;
  }
}
</style>
