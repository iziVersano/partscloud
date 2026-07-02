<script setup>
import { computed } from "vue";

const props = defineProps({
  history: { type: Array, required: true },
  forecast: { type: Array, required: true },
});

const W = 320;
const H = 140;
const PAD_BOTTOM = 18;
const GAP = 4;

const bars = computed(() => {
  const all = [
    ...props.history.map((d) => ({ ...d, kind: "history" })),
    ...props.forecast.map((d) => ({ ...d, kind: "forecast" })),
  ];
  const max = Math.max(1, ...all.map((d) => d.value));
  const n = all.length;
  const barW = (W - GAP * (n - 1)) / n;
  const chartH = H - PAD_BOTTOM;

  return all.map((d, i) => {
    const h = (d.value / max) * (chartH - 6);
    return {
      ...d,
      x: i * (barW + GAP),
      y: chartH - h,
      w: barW,
      h,
    };
  });
});

// X where the dashed divider sits (between last history and first forecast bar).
const dividerX = computed(() => {
  if (!props.history.length) return 0;
  const b = bars.value[props.history.length - 1];
  return b.x + b.w + GAP / 2;
});
</script>

<template>
  <div class="forecast">
    <div class="forecast__legend">
      <span class="forecast__key"><i class="dot dot--history" /> History</span>
      <span class="forecast__key"><i class="dot dot--forecast" /> Forecast</span>
    </div>
    <svg :viewBox="`0 0 ${W} ${H}`" class="forecast__svg" role="img" aria-label="Weekly demand: history and forecast">
      <line
        :x1="dividerX"
        :x2="dividerX"
        y1="0"
        :y2="H - PAD_BOTTOM"
        class="forecast__divider"
      />
      <g v-for="b in bars" :key="b.label">
        <rect
          :x="b.x"
          :y="b.y"
          :width="b.w"
          :height="b.h"
          rx="2"
          :class="b.kind === 'history' ? 'bar bar--history' : 'bar bar--forecast'"
        />
        <text :x="b.x + b.w / 2" :y="H - 5" class="forecast__label">{{ b.label }}</text>
      </g>
    </svg>
  </div>
</template>

<style scoped>
.forecast__legend {
  display: flex;
  gap: var(--sp-4);
  margin-bottom: var(--sp-2);
}
.forecast__key {
  display: inline-flex;
  align-items: center;
  gap: var(--sp-2);
  font-size: var(--fs-xs);
  color: var(--c-muted);
}
.dot {
  width: 9px;
  height: 9px;
  border-radius: 2px;
}
.dot--history {
  background: var(--c-blue);
}
.dot--forecast {
  background: var(--c-purple);
}
.forecast__svg {
  width: 100%;
  height: auto;
  display: block;
}
.bar--history {
  fill: var(--c-blue);
}
.bar--forecast {
  fill: var(--c-purple);
}
.forecast__divider {
  stroke: var(--c-muted);
  stroke-width: 1;
  stroke-dasharray: 3 3;
  opacity: 0.6;
}
.forecast__label {
  font-size: 8px;
  fill: var(--c-muted);
  text-anchor: middle;
}
</style>
