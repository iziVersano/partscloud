import { defineStore } from "pinia";
import {
  fetchSkus,
  fetchStats,
  updateSkuAction,
  bulkUpdateSkuAction,
} from "../api/inventoryApi";
import { useToast } from "../../../shared/composables/useToast";

const PAGE_SIZE = 10;
const ACTION_LABEL = { accepted: "Accepted", declined: "Declined" };

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
    search: "",
    sortField: "risk_score",
    sortDir: "asc",
    selected: [],
    pendingSkus: [],
    bulkPending: false,
    stats: null,
    activeSku: null,
    // Client-side cache of list responses keyed by query. Revisiting a
    // page/filter you've already loaded is instant and skips the network.
    // Invalidated wholesale on any write (accept/decline) so it never
    // serves a stale action_status.
    _cache: {},
  }),

  getters: {
    selectedCount(state) {
      return state.selected.length;
    },

    isPending(state) {
      return (sku) => state.pendingSkus.includes(sku);
    },

    activeSkuRow(state) {
      if (!state.activeSku) return null;
      return state.skus.find((s) => s.sku === state.activeSku) || null;
    },
  },

  actions: {
    _queryKey() {
      const ordering =
        this.sortDir === "desc" ? `-${this.sortField}` : this.sortField;
      return JSON.stringify({
        risk: this.riskFilter,
        search: this.search,
        ordering,
        page: this.page,
      });
    },

    async load({ silent = false, useCache = true } = {}) {
      const key = this._queryKey();
      if (useCache && this._cache[key]) {
        const cached = this._cache[key];
        this.skus = cached.results;
        this.total = cached.total;
        this.totalPages = cached.total_pages;
        this.error = null;
        return;
      }

      if (!silent) this.loading = true;
      this.error = null;
      try {
        const data = await fetchSkus({
          risk: this.riskFilter,
          search: this.search,
          ordering: this.sortDir === "desc" ? `-${this.sortField}` : this.sortField,
          page: this.page,
          pageSize: PAGE_SIZE,
        });
        this.skus = data.results;
        this.total = data.total;
        this.totalPages = data.total_pages;
        this._cache[key] = data;
      } catch (err) {
        this.error = err.message;
      } finally {
        if (!silent) this.loading = false;
      }
    },

    async loadStats() {
      try {
        this.stats = await fetchStats();
      } catch {
        // Stats are supplementary; a failure here shouldn't block the table.
        this.stats = null;
      }
    },

    _invalidateCache() {
      this._cache = {};
    },

    setSearch(term) {
      this.search = term;
      this.page = 1;
      this.clearSelection();
      this.load();
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

    openSku(sku) {
      this.activeSku = sku;
    },

    closeSku() {
      this.activeSku = null;
    },

    async act(sku, action) {
      if (this.pendingSkus.includes(sku) || this.bulkPending) return;

      const toast = useToast();
      const index = this.skus.findIndex((s) => s.sku === sku);
      const previous = index !== -1 ? this.skus[index].action_status : null;

      // Optimistic: reflect the new status immediately, roll back on failure.
      if (index !== -1) this.skus[index] = { ...this.skus[index], action_status: action };
      this.pendingSkus.push(sku);

      try {
        const updated = await updateSkuAction(sku, action);
        if (index !== -1) this.skus[index] = updated;
        this._invalidateCache();
        this.actionError = null;
        toast.success(`${sku} ${ACTION_LABEL[action].toLowerCase()}`);
      } catch (err) {
        if (index !== -1 && previous !== null) {
          this.skus[index] = { ...this.skus[index], action_status: previous };
        }
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

      const toast = useToast();
      this.bulkPending = true;
      try {
        const result = await bulkUpdateSkuAction(skuList, action);
        this._invalidateCache();
        await this.load({ silent: true, useCache: false });
        this.clearSelection();
        this.actionError = result.detail || null;
        if (result.detail) {
          toast.error(result.detail);
        } else {
          toast.success(`${result.updated} SKUs ${ACTION_LABEL[action].toLowerCase()}`);
        }
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
