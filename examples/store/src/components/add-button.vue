<script setup lang="ts">
import { computed } from "vue";

import { add, basket } from "@/lib/cart";

// One button for a product card and for the product page: it says what it does, and what is
// happening once pressed.
const props = withDefaults(defineProps<{ slug: string; stock: number; quantity?: number; wide?: boolean }>(), {
  quantity: 1,
  wide: false,
});

const adding = computed(() => basket.busy === props.slug);
const label = computed(() => {
  if (props.stock === 0) return "Sold out";
  return adding.value ? "Adding..." : "Add to cart";
});
</script>

<template>
  <button
    type="button"
    :class="[
      'min-h-11 whitespace-nowrap border px-5 font-mono text-[0.78rem] font-semibold uppercase tracking-[0.05em] transition-opacity',
      'border-foreground bg-foreground text-background hover:opacity-85',
      'disabled:cursor-not-allowed disabled:border-border-second disabled:bg-transparent disabled:text-foreground-second disabled:hover:opacity-100',
      'aria-busy:cursor-progress aria-busy:opacity-60',
      wide ? 'w-full' : '',
    ]"
    :disabled="stock === 0"
    :aria-busy="adding"
    @click="!adding && add(slug, quantity)"
  >
    {{ label }}
  </button>
</template>
