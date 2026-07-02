<script setup>
import { computed } from "vue";
import {
  Cog,
  CircleDot,
  Waves,
  Cable,
  Link2,
  Package,
  Snowflake,
  Link,
  Zap,
  Bolt,
  Filter,
  Flame,
  Droplet,
  Gauge,
  Settings,
  CircuitBoard,
  Wind,
  ArrowRightLeft,
  ShieldCheck,
  Radio,
  ToggleLeft,
  Box,
} from "@lucide/vue";

const props = defineProps({
  category: {
    type: String,
    required: true,
  },
});

// One icon per seed category, falling back to a generic box for anything
// outside that set (e.g. a category introduced via CSV import).
const ICONS = {
  Automation: Cog,
  Bearings: CircleDot,
  Belts: Waves,
  Cables: Cable,
  Chains: Link2,
  Consumables: Package,
  Cooling: Snowflake,
  Couplings: Link,
  Drives: Zap,
  Electrical: Bolt,
  Fasteners: Bolt,
  Filters: Filter,
  Heating: Flame,
  Hoses: Droplet,
  Instrumentation: Gauge,
  Mechanical: Settings,
  "Motor parts": CircuitBoard,
  Pneumatics: Wind,
  Pumps: ArrowRightLeft,
  Seals: ShieldCheck,
  Sensors: Radio,
  Valves: ToggleLeft,
};

const icon = computed(() => ICONS[props.category] || Box);
</script>

<template>
  <component :is="icon" :size="14" class="category-icon" aria-hidden="true" />
</template>

<style scoped>
.category-icon {
  color: var(--c-muted);
  flex-shrink: 0;
  vertical-align: -2px;
  margin-right: 4px;
}
</style>
