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
    riskFilter: null,
    sortField: "risk_score",
    sortDir: "asc",
    selected: [],   // plain array instead of Set — Vue 3 tracks array
                    // mutations reactively; Set.add()/delete() are invisible
                    // to the reactivity system and would freeze selectedCount
                    // at 0 and never show the bulk action bar
    page: 1,
    pendingSkus: [],  // SKUs with an in-flight single accept/decline request
    bulkPending: false,
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
      return state.selected.length;
    },

    isPending(state) {
      return (sku) => state.pendingSkus.includes(sku);
    },
  },

  actions: {
    async load({ silent = false } = {}) {
      // silent=true skips toggling the global loading flag — used after
      // accept/decline actions to refresh from the server without
      // flashing the whole page to a "Loading…" state.
      if (!silent) this.loading = true;
      this.error = null;
      try {
        this.skus = await fetchSkus({ ordering: "risk_score" });
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
      // Ignore clicks while a request for this row is already in flight,
      // instead of firing a second overlapping request.
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
        // Don't trust the request list — re-fetch so the table reflects
        // what the server actually updated, not what we asked it to.
        // The bulk endpoint silently skips SKUs it can't find, so
        // optimistically marking every selected row as updated would lie
        // about rows that were skipped.
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
