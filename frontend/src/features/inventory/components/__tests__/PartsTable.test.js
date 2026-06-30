import { mount } from "@vue/test-utils";
import { setActivePinia, createPinia } from "pinia";
import { beforeEach, describe, expect, it, vi } from "vitest";
import PartsTable from "../PartsTable.vue";
import { useInventoryStore } from "../../store/inventoryStore";
import * as api from "../../api/inventoryApi";

vi.mock("../../api/inventoryApi");

function makeSku(overrides = {}) {
  return {
    sku: "SP-1001",
    name: "Test part",
    category: "Test",
    on_hand: 10,
    risk: "ok",
    risk_score: 1,
    action_status: "pending",
    ...overrides,
  };
}

beforeEach(() => {
  setActivePinia(createPinia());
});

describe("PartsTable", () => {
  it("clicking a sortable header sorts by that field", async () => {
    const wrapper = mount(PartsTable);
    const store = useInventoryStore();
    store.skus = [makeSku()];

    const nameHeader = wrapper.findAll("th.sortable").find((h) => h.text().includes("Name"));
    await nameHeader.trigger("click");

    expect(store.sortField).toBe("name");
  });

  it("clicking Accept calls act with the row's sku", async () => {
    api.updateSkuAction.mockResolvedValue(makeSku({ action_status: "accepted" }));
    const wrapper = mount(PartsTable);
    const store = useInventoryStore();
    store.skus = [makeSku({ sku: "SP-2002" })];
    await wrapper.vm.$nextTick();

    await wrapper.find(".btn.accept").trigger("click");

    expect(api.updateSkuAction).toHaveBeenCalledWith("SP-2002", "accepted");
  });

  it("disables Accept once a row is already accepted", async () => {
    const wrapper = mount(PartsTable);
    const store = useInventoryStore();
    store.skus = [makeSku({ action_status: "accepted" })];
    await wrapper.vm.$nextTick();

    expect(wrapper.find(".btn.accept").attributes("disabled")).toBeDefined();
  });
});
