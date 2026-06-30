import { defineStore } from "pinia";
import {
  fetchSkus,
  updateSkuAction,
  bulkUpdateSkuAction,
} from "../api/inventoryApi";

const PAGE_SIZE = 10;

export const useInventoryStore = defineStore("inventory", {
  state: () => ({
    skus: [],
    total: 0,
    page: 1,
    totalPages: 1,
    loading: false,
    error: null,
    actionError: null,
    riskFilter: null,
    sortField: "risk_score",
    sortDir: "asc",
    selected: [],
    pendingSkus: [],
    bulkPending: false,
  }),

  getters: {
    selectedCount(state) {
      return state.selected.length;
    },

    isPending(state) {
      return (sku) => state.pendingSkus.includes(sku);
    },
  },

  actions: {
    async load({ silent = false } = {}) {
      if (!silent) this.loading = true;
      this.error = null;
      try {
        const data = await fetchSkus({
          risk: this.riskFilter,
          ordering: this.sortDir === "desc" ? `-${this.sortField}` : this.sortField,
          page: this.page,
          pageSize: PAGE_SIZE,
        });
        this.skus = data.results;
        this.total = data.total;
        this.totalPages = data.total_pages;
      } catch (err) {
        this.error = err.message;
      } finally {
        if (!silent) this.loading = false;
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
      this.page = 1;
      this.load();
    },

    setPage(page) {
      this.page = Math.min(Math.max(1, page), this.totalPages);
      this.clearSelection();
      this.load();
    },

    toggleSelected(sku) {
      const idx = this.selected.indexOf(sku);
      if (idx === -1) this.selected.push(sku);
      else this.selected.splice(idx, 1);
    },

    toggleSelectAll() {
      const allSelected = this.skus.every((s) => this.selected.includes(s.sku));
      if (allSelected) {
        this.skus.forEach((s) => {
          const idx = this.selected.indexOf(s.sku);
          if (idx !== -1) this.selected.splice(idx, 1);
        });
      } else {
        this.skus.forEach((s) => {
          if (!this.selected.includes(s.sku)) this.selected.push(s.sku);
        });
      }
    },

    clearSelection() {
      this.selected = [];
    },

    async act(sku, action) {
      if (this.pendingSkus.includes(sku) || this.bulkPending) return;

      this.pendingSkus.push(sku);
      try {
        const updated = await updateSkuAction(sku, action);
        const index = this.skus.findIndex((s) => s.sku === sku);
        if (index !== -1) this.skus[index] = updated;
        this.actionError = null;
      } catch (err) {
        this.actionError = `Failed to update ${sku}: ${err.message}`;
      } finally {
        const i = this.pendingSkus.indexOf(sku);
        if (i !== -1) this.pendingSkus.splice(i, 1);
      }
    },

    async bulkAct(action) {
      if (this.bulkPending || this.pendingSkus.length > 0) return;

      const skuList = [...this.selected];
      if (skuList.length === 0) return;

      this.bulkPending = true;
      try {
        const result = await bulkUpdateSkuAction(skuList, action);
        await this.load({ silent: true });
        this.clearSelection();
        this.actionError = result.detail || null;
      } catch (err) {
        this.actionError = `Bulk update failed: ${err.message}`;
      } finally {
        this.bulkPending = false;
      }
    },

    dismissActionError() {
      this.actionError = null;
    },
  },
});
