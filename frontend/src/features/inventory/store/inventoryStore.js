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
    selected: new Set(),
  }),

  getters: {
    visibleSkus(state) {
      if (!state.riskFilter) return state.skus;
      return state.skus.filter((s) => s.risk === state.riskFilter);
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
