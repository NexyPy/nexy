<script setup lang="ts">
import { computed, ref } from "vue";

type Month = { label: string; cents: number };
const props = defineProps<{ months: Month[] }>();

const active = ref<number | null>(null);
const top = computed(() => Math.max(1, ...props.months.map((month) => month.cents)));
const money = (cents: number) =>
  new Intl.NumberFormat("en-US", { style: "currency", currency: "USD", maximumFractionDigits: 0 }).format(cents / 100);
const shown = computed(() => props.months[active.value ?? props.months.length - 1]);
</script>

<template>
  <figure class="flex flex-col gap-4">
    <figcaption class="flex flex-wrap items-baseline justify-between gap-2">
      <span class="font-mono text-xs uppercase tracking-[0.04em] text-foreground-second">Collected by month</span>
      <span aria-live="polite" class="text-sm">
        <span class="text-foreground-second">{{ shown?.label }}</span>
        <strong class="ml-2 font-medium tabular-nums">{{ money(shown?.cents ?? 0) }}</strong>
      </span>
    </figcaption>
    <ol class="flex h-48 items-end gap-1.5 sm:gap-2" @mouseleave="active = null">
      <li v-for="(month, index) in months" :key="month.label" class="flex h-full flex-1 flex-col justify-end">
        <button
          type="button"
          class="w-full rounded-t-sm bg-foreground/80 transition-colors hover:bg-signal focus-visible:bg-signal focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-signal"
          :class="{ 'bg-signal': active === index }"
          :style="{ height: `${Math.max(2, (month.cents / top) * 100)}%` }"
          :aria-label="`${month.label}: ${money(month.cents)}`"
          @mouseenter="active = index"
          @focus="active = index"
          @blur="active = null"
        ></button>
      </li>
    </ol>
    <div class="flex justify-between font-mono text-[0.7rem] text-foreground-second" aria-hidden="true">
      <span>{{ months[0]?.label }}</span>
      <span>{{ months[months.length - 1]?.label }}</span>
    </div>
  </figure>
</template>
