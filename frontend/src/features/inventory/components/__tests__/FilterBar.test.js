import { mount } from "@vue/test-utils";
import { setActivePinia, createPinia } from "pinia";
import { beforeEach, describe, expect, it } from "vitest";
import FilterBar from "../FilterBar.vue";
import { useInventoryStore } from "../../store/inventoryStore";

beforeEach(() => {
  setActivePinia(createPinia());
});

describe("FilterBar", () => {
  it("clicking a filter button sets riskFilter on the store", async () => {
    const wrapper = mount(FilterBar);
    const store = useInventoryStore();

    await wrapper.findAll(".filter-btn")[1].trigger("click"); // Critical

    expect(store.riskFilter).toBe("critical");
  });

  it("marks the active filter button", async () => {
    const wrapper = mount(FilterBar);
    const store = useInventoryStore();
    store.riskFilter = "warning";
    await wrapper.vm.$nextTick();

    const active = wrapper.findAll(".filter-btn.active");
    expect(active).toHaveLength(1);
    expect(active[0].text()).toContain("Warning");
  });
});
