import { setActivePinia, createPinia } from "pinia";
import { beforeEach, describe, expect, it, vi } from "vitest";
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

beforeEach(() => {
  setActivePinia(createPinia());
  vi.clearAllMocks();
});

describe("load", () => {
  it("populates skus on success", async () => {
    api.fetchSkus.mockResolvedValue([makeSku()]);
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

describe("visibleSkus / pagination", () => {
  it("filters by riskFilter", () => {
    const store = useInventoryStore();
    store.skus = [
      makeSku({ sku: "A", risk: "critical" }),
      makeSku({ sku: "B", risk: "ok" }),
    ];
    store.riskFilter = "critical";

    expect(store.visibleSkus.map((s) => s.sku)).toEqual(["A"]);
  });

  it("sorts by sortField/sortDir", () => {
    const store = useInventoryStore();
    store.skus = [
      makeSku({ sku: "A", risk_score: 5 }),
      makeSku({ sku: "B", risk_score: 1 }),
    ];
    store.sortField = "risk_score";
    store.sortDir = "asc";

    expect(store.visibleSkus.map((s) => s.sku)).toEqual(["B", "A"]);
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
    expect(store.isSelected("SP-1001")).toBe(true);
    expect(store.selectedCount).toBe(1);

    store.toggleSelected("SP-1001");
    expect(store.isSelected("SP-1001")).toBe(false);
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

describe("bulkAct", () => {
  it("does nothing when nothing is selected", async () => {
    const store = useInventoryStore();

    await store.bulkAct("accepted");

    expect(api.bulkUpdateSkuAction).not.toHaveBeenCalled();
  });

  it("updates selected rows and clears selection on success", async () => {
    api.bulkUpdateSkuAction.mockResolvedValue({ updated: 2 });
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
