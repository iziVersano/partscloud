import { setActivePinia, createPinia } from "pinia";
import { beforeEach, describe, expect, it, vi } from "vitest";
import { flushPromises } from "@vue/test-utils";
import { useInventoryStore } from "../inventoryStore";
import * as api from "../../api/inventoryApi";

vi.mock("../../api/inventoryApi");

function makeSku(overrides = {}) {
  return {
    sku: "SP-1001",
    name: "Test part",
    category: "Test",
    risk: "ok",
    risk_score: 1,
    action_status: "pending",
    ...overrides,
  };
}

function makePageResponse(skus, { total = null, total_pages = 1 } = {}) {
  return { results: skus, total: total ?? skus.length, total_pages };
}

beforeEach(() => {
  setActivePinia(createPinia());
  vi.clearAllMocks();
});

describe("load", () => {
  it("populates skus on success", async () => {
    api.fetchSkus.mockResolvedValue(makePageResponse([makeSku()]));
    const store = useInventoryStore();

    await store.load();

    expect(store.skus).toHaveLength(1);
    expect(store.loading).toBe(false);
    expect(store.error).toBeNull();
  });

  it("sets error and stops loading on failure", async () => {
    api.fetchSkus.mockRejectedValue(new Error("network down"));
    const store = useInventoryStore();

    await store.load();

    expect(store.error).toBe("network down");
    expect(store.loading).toBe(false);
  });
});

describe("server-side filtering and sorting", () => {
  it("passes riskFilter to fetchSkus when setRiskFilter is called", async () => {
    api.fetchSkus.mockResolvedValue(makePageResponse([]));
    const store = useInventoryStore();

    store.setRiskFilter("critical");
    await flushPromises();

    expect(api.fetchSkus).toHaveBeenCalledWith(
      expect.objectContaining({ risk: "critical" })
    );
  });

  it("passes ordering to fetchSkus when setSort is called", async () => {
    api.fetchSkus.mockResolvedValue(makePageResponse([]));
    const store = useInventoryStore();

    store.setSort("name");
    await flushPromises();

    expect(api.fetchSkus).toHaveBeenCalledWith(
      expect.objectContaining({ ordering: "name" })
    );
  });
});

describe("setRiskFilter", () => {
  it("resets to page 1 and clears selection", () => {
    const store = useInventoryStore();
    store.page = 3;
    store.selected = ["SP-1001"];

    store.setRiskFilter("critical");

    expect(store.riskFilter).toBe("critical");
    expect(store.page).toBe(1);
    expect(store.selected).toEqual([]);
  });
});

describe("setSort", () => {
  it("flips direction when sorting the same field again", () => {
    const store = useInventoryStore();
    store.sortField = "risk_score";
    store.sortDir = "asc";

    store.setSort("risk_score");

    expect(store.sortDir).toBe("desc");
  });

  it("switches field and resets to ascending", () => {
    const store = useInventoryStore();
    store.sortField = "risk_score";
    store.sortDir = "desc";

    store.setSort("name");

    expect(store.sortField).toBe("name");
    expect(store.sortDir).toBe("asc");
  });
});

describe("selection", () => {
  it("toggles a sku in and out of selected", () => {
    const store = useInventoryStore();

    store.toggleSelected("SP-1001");
    expect(store.selected.includes("SP-1001")).toBe(true);
    expect(store.selectedCount).toBe(1);

    store.toggleSelected("SP-1001");
    expect(store.selected.includes("SP-1001")).toBe(false);
    expect(store.selectedCount).toBe(0);
  });

  it("clearSelection empties the array", () => {
    const store = useInventoryStore();
    store.selected = ["A", "B"];

    store.clearSelection();

    expect(store.selected).toEqual([]);
  });
});

describe("act", () => {
  it("replaces the row with the server response on success", async () => {
    const updated = makeSku({ action_status: "accepted" });
    api.updateSkuAction.mockResolvedValue(updated);
    const store = useInventoryStore();
    store.skus = [makeSku({ action_status: "pending" })];

    await store.act("SP-1001", "accepted");

    expect(store.skus[0].action_status).toBe("accepted");
    expect(store.actionError).toBeNull();
  });

  it("sets actionError on failure without touching skus", async () => {
    api.updateSkuAction.mockRejectedValue(new Error("404"));
    const store = useInventoryStore();
    store.skus = [makeSku({ action_status: "pending" })];

    await store.act("SP-1001", "accepted");

    expect(store.skus[0].action_status).toBe("pending");
    expect(store.actionError).toContain("SP-1001");
  });
});

describe("search", () => {
  it("passes search to fetchSkus, resets to page 1, and clears selection", async () => {
    api.fetchSkus.mockResolvedValue(makePageResponse([]));
    const store = useInventoryStore();
    store.page = 3;
    store.selected = ["SP-1001"];

    store.setSearch("bearing");
    await flushPromises();

    expect(store.search).toBe("bearing");
    expect(store.page).toBe(1);
    expect(store.selected).toEqual([]);
    expect(api.fetchSkus).toHaveBeenCalledWith(
      expect.objectContaining({ search: "bearing" })
    );
  });
});

describe("query cache", () => {
  it("serves a repeated query from cache without calling the API again", async () => {
    api.fetchSkus.mockResolvedValue(makePageResponse([makeSku()]));
    const store = useInventoryStore();

    await store.load();
    expect(api.fetchSkus).toHaveBeenCalledTimes(1);

    await store.load();
    expect(api.fetchSkus).toHaveBeenCalledTimes(1);
    expect(store.skus).toHaveLength(1);
  });

  it("fetches again when the query key changes", async () => {
    api.fetchSkus.mockResolvedValue(makePageResponse([]));
    const store = useInventoryStore();

    await store.load();
    store.setRiskFilter("critical");
    await flushPromises();

    expect(api.fetchSkus).toHaveBeenCalledTimes(2);
  });

  it("bypasses the cache after an accept invalidates it", async () => {
    api.fetchSkus.mockResolvedValue(makePageResponse([makeSku()]));
    api.updateSkuAction.mockResolvedValue(makeSku({ action_status: "accepted" }));
    const store = useInventoryStore();

    await store.load();
    await store.act("SP-1001", "accepted");
    await store.load();

    expect(api.fetchSkus).toHaveBeenCalledTimes(2);
  });
});

describe("loadStats", () => {
  it("populates stats on success", async () => {
    api.fetchStats.mockResolvedValue({
      total: 50,
      critical: 19,
      warning: 2,
      ok: 29,
      at_risk_value_eur: 29156.26,
      service_level_pct: 58.0,
    });
    const store = useInventoryStore();

    await store.loadStats();

    expect(store.stats.critical).toBe(19);
    expect(store.stats.service_level_pct).toBe(58.0);
  });

  it("sets stats to null on failure instead of throwing", async () => {
    api.fetchStats.mockRejectedValue(new Error("network down"));
    const store = useInventoryStore();

    await expect(store.loadStats()).resolves.not.toThrow();
    expect(store.stats).toBeNull();
  });
});

describe("SKU drawer", () => {
  it("openSku/closeSku toggle activeSku", () => {
    const store = useInventoryStore();

    store.openSku("SP-1001");
    expect(store.activeSku).toBe("SP-1001");

    store.closeSku();
    expect(store.activeSku).toBeNull();
  });

  it("activeSkuRow resolves the full row from the current page", () => {
    const store = useInventoryStore();
    store.skus = [makeSku({ sku: "A" }), makeSku({ sku: "B" })];

    store.openSku("B");

    expect(store.activeSkuRow.sku).toBe("B");
  });

  it("activeSkuRow is null when the active sku isn't on the current page", () => {
    const store = useInventoryStore();
    store.skus = [makeSku({ sku: "A" })];

    store.openSku("NOT-ON-PAGE");

    expect(store.activeSkuRow).toBeNull();
  });
});

describe("act (optimistic update)", () => {
  it("reflects the new status immediately, before the request resolves", async () => {
    let resolveRequest;
    api.updateSkuAction.mockReturnValue(
      new Promise((resolve) => {
        resolveRequest = resolve;
      })
    );
    const store = useInventoryStore();
    store.skus = [makeSku({ sku: "SP-1001", action_status: "pending" })];

    const promise = store.act("SP-1001", "accepted");
    expect(store.skus[0].action_status).toBe("accepted");

    resolveRequest(makeSku({ sku: "SP-1001", action_status: "accepted" }));
    await promise;
  });

  it("rolls back to the previous status if the request fails", async () => {
    api.updateSkuAction.mockRejectedValue(new Error("server error"));
    const store = useInventoryStore();
    store.skus = [makeSku({ sku: "SP-1001", action_status: "pending" })];

    await store.act("SP-1001", "accepted");

    expect(store.skus[0].action_status).toBe("pending");
  });
});

describe("bulkAct", () => {
  it("does nothing when nothing is selected", async () => {
    const store = useInventoryStore();

    await store.bulkAct("accepted");

    expect(api.bulkUpdateSkuAction).not.toHaveBeenCalled();
  });

  it("re-fetches from server and clears selection on success", async () => {
    api.bulkUpdateSkuAction.mockResolvedValue({ updated: 2 });
    api.fetchSkus.mockResolvedValue(
      makePageResponse([
        makeSku({ sku: "A", action_status: "declined" }),
        makeSku({ sku: "B", action_status: "declined" }),
        makeSku({ sku: "C", action_status: "pending" }),
      ])
    );
    const store = useInventoryStore();
    store.skus = [
      makeSku({ sku: "A", action_status: "pending" }),
      makeSku({ sku: "B", action_status: "pending" }),
      makeSku({ sku: "C", action_status: "pending" }),
    ];
    store.selected = ["A", "B"];

    await store.bulkAct("declined");

    expect(store.skus.find((s) => s.sku === "A").action_status).toBe("declined");
    expect(store.skus.find((s) => s.sku === "B").action_status).toBe("declined");
    expect(store.skus.find((s) => s.sku === "C").action_status).toBe("pending");
    expect(store.selected).toEqual([]);
  });

  it("sets actionError and keeps selection on failure", async () => {
    api.bulkUpdateSkuAction.mockRejectedValue(new Error("server error"));
    const store = useInventoryStore();
    store.selected = ["A"];

    await store.bulkAct("accepted");

    expect(store.actionError).toContain("Bulk update failed");
    expect(store.selected).toEqual(["A"]);
  });
});
