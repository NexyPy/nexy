<script setup lang="ts">
import { computed } from "vue";

import { money } from "@/lib/money";

// What an order costs, as the cart, the checkout and the receipt show it. The server counted it.
const props = defineProps<{ subtotal: number; shipping: number; total: number }>();

const FREE_FROM = 5000;
const missing = computed(() => (props.shipping > 0 ? FREE_FROM - props.subtotal : 0));
const ROW = "flex justify-between gap-4 py-2.5";
</script>

<template>
  <dl class="text-[0.95rem]">
    <div :class="ROW">
      <dt class="text-foreground-second">Subtotal</dt>
      <dd class="font-mono tabular-nums">{{ money(subtotal) }}</dd>
    </div>
    <div :class="ROW">
      <dt class="text-foreground-second">Delivery</dt>
      <dd class="font-mono tabular-nums">{{ shipping === 0 ? "Free" : money(shipping) }}</dd>
    </div>
    <p v-if="missing > 0" class="pb-2.5 text-sm text-foreground-second">
      Add {{ money(missing) }} more for free delivery.
    </p>
    <div :class="[ROW, 'border-t border-border pt-4 text-lg font-medium']">
      <dt>Total</dt>
      <dd class="font-mono tabular-nums">{{ money(total) }}</dd>
    </div>
  </dl>
</template>
