<script setup>
import { computed } from "vue";
import { TriangleAlert, Wallet, ShieldCheck } from "@lucide/vue";
import { useInventoryStore } from "../store/inventoryStore";
import { formatEur } from "../../../shared/lib/format";
import BaseCard from "../../../shared/ui/BaseCard.vue";
import BaseSkeleton from "../../../shared/ui/BaseSkeleton.vue";

const store = useInventoryStore();

const cards = computed(() => {
  const s = store.stats;
  if (!s) return [];
  return [
    {
      key: "critical",
      label: "Critical SKUs",
      value: s.critical,
      accent: "critical",
      filter: "critical",
      clickable: true,
      hint: "Below zero projected cover",
      icon: TriangleAlert,
    },
    {
      key: "at-risk",
      label: "Inventory at risk",
      value: formatEur(s.at_risk_value_eur),
      accent: "warning",
      filter: "critical,warning",
      clickable: true,
      hint: "Capital exposed to stockout — click to view",
      icon: Wallet,
    },
    {
      key: "service-level",
      label: "Service level",
      value: `${s.service_level_pct}%`,
      accent: "ok",
      filter: "ok",
      clickable: true,
      hint: "SKUs not at risk",
      icon: ShieldCheck,
    },
  ];
});

function activate(card) {
  if (!card.clickable) return;
  // Clicking an already-active card clears the filter instead of re-applying it.
  store.setRiskFilter(store.riskFilter === card.filter ? null : card.filter);
}
</script>

<template>
  <section class="stat-cards" aria-label="Inventory summary">
    <template v-if="store.stats">
      <BaseCard
        v-for="card in cards"
        :key="card.key"
        :interactive="card.clickable"
        class="stat-card"
        :class="{ 'stat-card--active': card.clickable && store.riskFilter === card.filter }"
        :role="card.clickable ? 'button' : undefined"
        :tabindex="card.clickable ? 0 : undefined"
        @click="activate(card)"
        @keydown.enter="activate(card)"
        @keydown.space.prevent="activate(card)"
      >
        <div class="stat-card__top">
          <p class="stat-card__label">{{ card.label }}</p>
          <component :is="card.icon" class="stat-card__icon" :class="`stat-card__icon--${card.accent}`" :size="18" aria-hidden="true" />
        </div>
        <p class="stat-card__value" :class="`stat-card__value--${card.accent}`">
          {{ card.value }}
        </p>
        <p class="stat-card__hint">{{ card.hint }}</p>
      </BaseCard>
    </template>

    <template v-else>
      <BaseCard v-for="n in 3" :key="n" class="stat-card">
        <BaseSkeleton width="60%" height="0.8rem" />
        <BaseSkeleton width="40%" height="1.8rem" style="margin: 0.6rem 0" />
        <BaseSkeleton width="70%" height="0.7rem" />
      </BaseCard>
    </template>
  </section>
</template>

<style scoped>
.stat-cards {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: var(--sp-4);
  margin-bottom: var(--sp-5);
}
.stat-card {
  outline: none;
}
.stat-card--active {
  border-color: var(--c-purple);
  box-shadow: 0 0 0 2px var(--c-purple);
  background: var(--c-purple-bg);
}
.stat-card:focus-visible {
  outline: 2px solid var(--c-purple);
  outline-offset: 2px;
}
.stat-card__top {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: var(--sp-2);
}
.stat-card__label {
  margin: 0;
  font-size: var(--fs-sm);
  color: var(--c-muted);
  font-weight: 500;
}
.stat-card__icon {
  flex-shrink: 0;
}
.stat-card__icon--critical {
  color: var(--c-critical);
}
.stat-card__icon--warning {
  color: var(--c-warning);
}
.stat-card__icon--ok {
  color: var(--c-ok);
}
.stat-card__value {
  margin: 0.4rem 0 0.3rem;
  font-size: var(--fs-2xl);
  font-weight: 700;
  letter-spacing: -0.02em;
  color: var(--c-ink);
}
.stat-card__value--critical {
  color: var(--c-critical);
}
.stat-card__value--warning {
  color: var(--c-warning);
}
.stat-card__value--ok {
  color: var(--c-ok);
}
.stat-card__hint {
  margin: 0;
  font-size: var(--fs-xs);
  color: var(--c-muted);
}

@media (max-width: 720px) {
  .stat-cards {
    grid-template-columns: 1fr;
  }
}
</style>
