<script setup lang="ts">
import { computed } from "vue";
import { Link } from "@nexy/client";

import Icon from "@/components/icon.vue";
import { basket } from "@/lib/cart";

const BAG = "M5 8h14l-1.2 12H6.2L5 8zM9 8V7a3 3 0 016 0v1";

const label = computed(() => {
  const count = basket.cart.count;
  return count === 1 ? "Cart, 1 item" : `Cart, ${count} items`;
});
</script>

<template>
  <Link
    href="/cart"
    :aria-label="label"
    class="relative grid size-11 place-items-center text-paper transition-opacity hover:opacity-70"
  >
    <Icon :path="BAG" />
    <span
      v-if="basket.cart.count > 0"
      class="absolute right-0.5 top-0.5 grid min-w-5 place-items-center bg-signal px-1 font-mono text-[0.7rem] font-semibold leading-5 text-ink tabular-nums"
      aria-hidden="true"
    >{{ basket.cart.count }}</span>
  </Link>
</template>
