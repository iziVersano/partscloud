import { defineStore } from "pinia";
import {
  fetchSkus,
  updateSkuAction,
  bulkUpdateSkuAction,
} from "../api/inventoryApi";

export const useInventoryStore = defineStore("inventory", {
  state: () => ({
    skus: [],
    loading: false,
    error: null,
    riskFilter: null, // null | 'critical' | 'warning' | 'ok'
    sortField: "risk_score",
    sortDir: "asc", // 'asc' | 'desc'
    selected: new Set(),
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
    },

    setSort(field) {
      if (this.sortField === field) {
        this.sortDir = this.sortDir === "asc" ? "desc" : "asc";
      } else {
        this.sortField = field;
        this.sortDir = "asc";
      }
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
      const updated = await updateSkuAction(sku, action);
      const index = this.skus.findIndex((s) => s.sku === sku);
      if (index !== -1) this.skus[index] = updated;
    },

    async bulkAct(action) {
      const skuList = Array.from(this.selected);
      if (skuList.length === 0) return;

      await bulkUpdateSkuAction(skuList, action);

      this.skus = this.skus.map((s) =>
        skuList.includes(s.sku) ? { ...s, action_status: action } : s
      );
      this.clearSelection();
    },
  },
});
