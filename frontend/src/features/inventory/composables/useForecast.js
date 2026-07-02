import { computed, unref } from "vue";

// Derives a weekly demand series (history + forecast) from a SKU's stored
// fields. There is no historical time-series in the data model, so we shape a
// plausible, *deterministic* series around avg_daily_demand — seeded by the SKU
// code so the same SKU always renders the same chart (no per-render jitter).
// This is illustrative of the planning view, not a real statistical forecast.

const HISTORY_WEEKS = 6;
const FORECAST_WEEKS = 4;

function seededVariation(seed, index) {
  // Cheap deterministic pseudo-random in [-0.18, 0.18].
  const x = Math.sin(seed * 99.13 + index * 12.7) * 43758.5453;
  return ((x - Math.floor(x)) - 0.5) * 0.36;
}

function seedFromSku(sku) {
  let h = 0;
  for (let i = 0; i < sku.length; i++) h = (h * 31 + sku.charCodeAt(i)) % 100000;
  return h;
}

export function useForecast(skuRef) {
  return computed(() => {
    const s = unref(skuRef);
    if (!s) return { history: [], forecast: [], weeklyBase: 0 };

    const weeklyBase = Number(s.avg_daily_demand) * 7;
    const seed = seedFromSku(s.sku);

    const history = Array.from({ length: HISTORY_WEEKS }, (_, i) => ({
      label: `W-${HISTORY_WEEKS - i}`,
      value: Math.max(0, Math.round(weeklyBase * (1 + seededVariation(seed, i)))),
    }));

    // Forecast continues from the base demand with a mild trend.
    const forecast = Array.from({ length: FORECAST_WEEKS }, (_, i) => ({
      label: `W+${i + 1}`,
      value: Math.max(
        0,
        Math.round(weeklyBase * (1 + seededVariation(seed, HISTORY_WEEKS + i) * 0.6))
      ),
    }));

    return { history, forecast, weeklyBase: Math.round(weeklyBase) };
  });
}
