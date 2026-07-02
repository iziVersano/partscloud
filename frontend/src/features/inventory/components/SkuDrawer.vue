<script setup>
import { computed } from "vue";
import { useInventoryStore } from "../store/inventoryStore";
import { useForecast } from "../composables/useForecast";
import { formatEur, formatDate } from "../../../shared/lib/format";
import BaseDrawer from "../../../shared/ui/BaseDrawer.vue";
import BasePill from "../../../shared/ui/BasePill.vue";
import BaseButton from "../../../shared/ui/BaseButton.vue";
import ForecastChart from "../../../shared/ui/ForecastChart.vue";
import RiskBadge from "./RiskBadge.vue";

const store = useInventoryStore();
const row = computed(() => store.activeSkuRow);
const forecast = useForecast(row);

// The stored risk formula, recomputed here purely to *show* the planner the
// math behind the risk label (projected cover vs. safety stock).
const projected = computed(() => {
  const s = row.value;
  if (!s) return 0;
  return Math.round(s.on_hand - s.avg_daily_demand * s.lead_time_days);
});

const daysOfCover = computed(() => {
  const s = row.value;
  if (!s || !s.avg_daily_demand) return "∞";
  return Math.round(s.on_hand / s.avg_daily_demand);
});

const inventoryValue = computed(() =>
  row.value ? formatEur(row.value.on_hand * row.value.unit_cost_eur) : "—"
);

const details = computed(() => {
  const s = row.value;
  if (!s) return [];
  return [
    { label: "Category", value: s.category },
    { label: "On hand", value: s.on_hand },
    { label: "Avg daily demand", value: s.avg_daily_demand },
    { label: "Lead time", value: `${s.lead_time_days} days` },
    { label: "Safety stock", value: s.safety_stock },
    { label: "Unit cost", value: formatEur(s.unit_cost_eur) },
    { label: "Inventory value", value: inventoryValue.value },
    { label: "Last delivery", value: formatDate(s.last_delivery_date) },
  ];
});

const toneFor = (risk) => risk;

function accept() {
  if (row.value) store.act(row.value.sku, "accepted");
}
function decline() {
  if (row.value) store.act(row.value.sku, "declined");
}
</script>

<template>
  <BaseDrawer :open="!!row" :title="row ? row.sku : ''" @close="store.closeSku()">
    <template v-if="row">
      <div class="sku-head">
        <div>
          <h3 class="sku-name">{{ row.name }}</h3>
          <RiskBadge :risk="row.risk" />
        </div>
      </div>

      <!-- Risk math: makes the stored risk label explainable at a glance. -->
      <section class="risk-calc" :class="`risk-calc--${toneFor(row.risk)}`">
        <div class="risk-calc__row">
          <span>Projected cover</span>
          <strong>{{ projected }}</strong>
        </div>
        <div class="risk-calc__formula">
          on_hand {{ row.on_hand }} − (demand {{ row.avg_daily_demand }} × lead {{ row.lead_time_days }}d)
        </div>
        <div class="risk-calc__row risk-calc__row--muted">
          <span>Safety stock</span>
          <span>{{ row.safety_stock }}</span>
        </div>
        <div class="risk-calc__row risk-calc__row--muted">
          <span>Days of cover</span>
          <span>{{ daysOfCover }}</span>
        </div>
      </section>

      <section class="drawer-section">
        <h4 class="drawer-section__title">Demand forecast</h4>
        <ForecastChart :history="forecast.history" :forecast="forecast.forecast" />
        <p class="forecast-note">Illustrative weekly demand derived from average daily demand.</p>
      </section>

      <section class="drawer-section">
        <h4 class="drawer-section__title">Details</h4>
        <dl class="detail-grid">
          <div v-for="d in details" :key="d.label" class="detail-grid__item">
            <dt>{{ d.label }}</dt>
            <dd>{{ d.value }}</dd>
          </div>
        </dl>
      </section>

      <div class="drawer-actions">
        <BaseButton
          variant="primary"
          block
          :loading="store.isPending(row.sku)"
          :disabled="row.action_status === 'accepted' || store.bulkPending"
          @click="accept"
        >
          {{ row.action_status === "accepted" ? "Accepted" : "Accept" }}
        </BaseButton>
        <BaseButton
          variant="danger"
          block
          :loading="store.isPending(row.sku)"
          :disabled="row.action_status === 'declined' || store.bulkPending"
          @click="decline"
        >
          {{ row.action_status === "declined" ? "Declined" : "Decline" }}
        </BaseButton>
      </div>
    </template>
  </BaseDrawer>
</template>

<style scoped>
.sku-head {
  margin-bottom: var(--sp-4);
}
.sku-name {
  margin: 0 0 var(--sp-2);
  font-size: var(--fs-lg);
  font-weight: 600;
  color: var(--c-ink);
}
.risk-calc {
  background: var(--c-surface-2);
  border-radius: var(--r-md);
  padding: var(--sp-4);
  margin-bottom: var(--sp-5);
  border-left: 3px solid var(--c-muted);
}
.risk-calc--critical {
  border-left-color: var(--c-critical);
}
.risk-calc--warning {
  border-left-color: var(--c-warning);
}
.risk-calc--ok {
  border-left-color: var(--c-ok);
}
.risk-calc__row {
  display: flex;
  justify-content: space-between;
  align-items: baseline;
  font-size: var(--fs-md);
  color: var(--c-ink);
}
.risk-calc__row strong {
  font-size: var(--fs-lg);
}
.risk-calc__row--muted {
  color: var(--c-muted);
  font-size: var(--fs-sm);
  margin-top: var(--sp-2);
}
.risk-calc__formula {
  font-family: "SF Mono", "Roboto Mono", Consolas, monospace;
  font-size: var(--fs-xs);
  color: var(--c-muted);
  margin-top: var(--sp-1);
}
.drawer-section {
  margin-bottom: var(--sp-5);
}
.drawer-section__title {
  margin: 0 0 var(--sp-3);
  font-size: var(--fs-sm);
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.03em;
  color: var(--c-muted);
}
.forecast-note {
  margin: var(--sp-2) 0 0;
  font-size: var(--fs-xs);
  color: var(--c-muted);
}
.detail-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: var(--sp-3);
  margin: 0;
}
.detail-grid__item dt {
  font-size: var(--fs-xs);
  color: var(--c-muted);
  margin-bottom: 2px;
}
.detail-grid__item dd {
  margin: 0;
  font-size: var(--fs-md);
  color: var(--c-ink);
  font-weight: 500;
}
.drawer-actions {
  display: flex;
  gap: var(--sp-3);
  padding-top: var(--sp-2);
}
</style>
