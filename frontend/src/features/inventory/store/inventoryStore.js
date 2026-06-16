import { defineStore } from "pinia";
import {
  fetchSkus,
  updateSkuAction,
  bulkUpdateSkuAction,
} from "../api/inventoryApi";

const PAGE_SIZE = 20;

export const useInventoryStore = defineStore("inventory", {
  state: () => ({
    skus: [],
    loading: false,
    error: null,
    actionError: null,
    riskFilter: null, // null | 'critical' | 'warning' | 'ok'
    sortField: "risk_score",
    sortDir: "asc", // 'asc' | 'desc'
    selected: new Set(),
    page: 1,
  }),

  getters: {
    visibleSkus(state) {
      let result = state.riskFilter
        ? state.skus.filter((s) => s.risk === state.riskFilter)
        : state.skus;

      const field = state.sortField;
      const dir = state.sortDir === "desc" ? -1 : 1;
      result = [...result].sort((a, b) => {
        if (a[field] < b[field]) return -1 * dir;
        if (a[field] > b[field]) return 1 * dir;
        return 0;
      });

      return result;
    },

    totalPages(state) {
      return Math.max(1, Math.ceil(this.visibleSkus.length / PAGE_SIZE));
    },

    paginatedSkus(state) {
      const start = (state.page - 1) * PAGE_SIZE;
      return this.visibleSkus.slice(start, start + PAGE_SIZE);
    },

    selectedCount(state) {
      return state.selected.size;
    },
  },

  actions: {
    async load() {
      this.loading = true;
      this.error = null;
      try {
        this.skus = await fetchSkus({ ordering: "risk_score" });
      } catch (err) {
        this.error = err.message;
      } finally {
        this.loading = false;
      }
    },

    setRiskFilter(risk) {
      this.riskFilter = risk;
      this.page = 1; // avoid landing on an empty page after filtering
      this.clearSelection(); // don't carry hidden selections into a
      // different filter — a bulk action should only ever touch rows
      // the user can currently see, not ones selected under a filter
      // they've since switched away from
    },

    setSort(field) {
      if (this.sortField === field) {
        this.sortDir = this.sortDir === "asc" ? "desc" : "asc";
      } else {
        this.sortField = field;
        this.sortDir = "asc";
      }
    },

    setPage(page) {
      this.page = Math.min(Math.max(1, page), this.totalPages);
    },

    toggleSelected(sku) {
      if (this.selected.has(sku)) {
        this.selected.delete(sku);
      } else {
        this.selected.add(sku);
      }
    },

    clearSelection() {
      this.selected.clear();
    },

    async act(sku, action) {
      this.actionError = null;
      try {
        const updated = await updateSkuAction(sku, action);
        const index = this.skus.findIndex((s) => s.sku === sku);
        if (index !== -1) this.skus[index] = updated;
      } catch (err) {
        this.actionError = `Failed to update ${sku}: ${err.message}`;
      }
    },

    async bulkAct(action) {
      const skuList = Array.from(this.selected);
      if (skuList.length === 0) return;

      this.actionError = null;
      try {
        await bulkUpdateSkuAction(skuList, action);
        this.skus = this.skus.map((s) =>
          skuList.includes(s.sku) ? { ...s, action_status: action } : s
        );
        this.clearSelection();
      } catch (err) {
        this.actionError = `Bulk update failed: ${err.message}`;
      }
    },
  },
});
