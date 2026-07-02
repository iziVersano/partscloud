import { mount } from "@vue/test-utils";
import { setActivePinia, createPinia } from "pinia";
import { beforeEach, describe, expect, it } from "vitest";
import StatCards from "../StatCards.vue";
import { useInventoryStore } from "../../store/inventoryStore";

function setStats(store, overrides = {}) {
  store.stats = {
    total: 50,
    critical: 19,
    warning: 2,
    ok: 29,
    at_risk_value_eur: 29156.26,
    service_level_pct: 58.0,
    ...overrides,
  };
}

beforeEach(() => {
  setActivePinia(createPinia());
});

describe("StatCards", () => {
  it("renders skeleton placeholders while stats are unloaded", () => {
    const wrapper = mount(StatCards);

    expect(wrapper.findAll(".stat-card")).toHaveLength(3);
    expect(wrapper.text()).not.toContain("Critical SKUs");
  });

  it("renders the three cards once stats are loaded", async () => {
    const wrapper = mount(StatCards);
    const store = useInventoryStore();
    setStats(store);
    await wrapper.vm.$nextTick();

    const text = wrapper.text();
    expect(text).toContain("Critical SKUs");
    expect(text).toContain("Inventory at risk");
    expect(text).toContain("Service level");
  });

  it("clicking the Critical card sets the risk filter", async () => {
    const wrapper = mount(StatCards);
    const store = useInventoryStore();
    setStats(store);
    await wrapper.vm.$nextTick();

    await wrapper.findAll(".stat-card")[0].trigger("click");

    expect(store.riskFilter).toBe("critical");
  });

  it("clicking an already-active card clears the filter", async () => {
    const wrapper = mount(StatCards);
    const store = useInventoryStore();
    setStats(store);
    store.riskFilter = "critical";
    await wrapper.vm.$nextTick();

    await wrapper.findAll(".stat-card")[0].trigger("click");

    expect(store.riskFilter).toBeNull();
  });

  it("clicking the Inventory at risk card filters to critical and warning", async () => {
    const wrapper = mount(StatCards);
    const store = useInventoryStore();
    setStats(store);
    await wrapper.vm.$nextTick();

    await wrapper.findAll(".stat-card")[1].trigger("click");

    expect(store.riskFilter).toBe("critical,warning");
  });
});
