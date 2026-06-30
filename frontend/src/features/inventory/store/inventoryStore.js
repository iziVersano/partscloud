import { defineStore } from "pinia";
import {
  fetchSkus,
  updateSkuAction,
  bulkUpdateSkuAction,
} from "../api/inventoryApi";

const PAGE_SIZE = 20;

export const useInventoryStore = defineStore("inventory", {
  state: () => ({
    skus: [],       // only the current page's rows — filtering, sorting,
                     // and pagination all happen server-side now so this
                     // store never holds the full dataset
    totalCount: 0,
    loading: false,
    error: null,
    actionError: null,
    riskFilter: null,
    sortField: "risk_score",
    sortDir: "asc",
    selected: [],   // plain array instead of Set — Vue 3 tracks array
                    // mutations reactively; Set.add()/delete() are invisible
                    // to the reactivity system and would freeze selectedCount
                    // at 0 and never show the bulk action bar
    page: 1,
  }),

  getters: {
    orderingParam(state) {
      return state.sortDir === "desc" ? `-${state.sortField}` : state.sortField;
    },

    totalPages(state) {
      return Math.max(1, Math.ceil(state.totalCount / PAGE_SIZE));
    },

    selectedCount(state) {
      return state.selected.length;
    },
  },

  actions: {
    async load() {
      this.loading = true;
      this.error = null;
      try {
        const data = await fetchSkus({
          risk: this.riskFilter,
          ordering: this.orderingParam,
          page: this.page,
        });
        this.skus = data.results;
        this.totalCount = data.count;
      } catch (err) {
        this.error = err.message;
      } finally {
        this.loading = false;
      }
    },

    setRiskFilter(risk) {
      this.riskFilter = risk;
      this.page = 1;
      this.clearSelection();
      this.load();
    },

    setSort(field) {
      if (this.sortField === field) {
        this.sortDir = this.sortDir === "asc" ? "desc" : "asc";
      } else {
        this.sortField = field;
        this.sortDir = "asc";
      }
      this.load();
    },

    setPage(page) {
      this.page = Math.min(Math.max(1, page), this.totalPages);
      this.load();
    },

    toggleSelected(sku) {
      const i = this.selected.indexOf(sku);
      if (i !== -1) {
        this.selected.splice(i, 1);
      } else {
        this.selected.push(sku);
      }
    },

    isSelected(sku) {
      return this.selected.includes(sku);
    },

    clearSelection() {
      this.selected = [];
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
      const skuList = [...this.selected];
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
