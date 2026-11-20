<script setup lang="ts">
import { onMounted, ref } from "vue";
import { Link } from "@nexy/client";
import { orders } from "@nexy/actions";
import type { OrderSummary } from "@nexy/actions";

import ButtonLink from "@/components/button-link.vue";
import Page from "@/components/page.vue";
import PageHead from "@/components/page-head.vue";
import { day, money } from "@/lib/money";

const placed = ref<OrderSummary[] | null>(null);
const problem = ref("");

async function read() {
  problem.value = "";
  try {
    placed.value = await orders();
  } catch {
    problem.value = "The shop did not answer. Check your connection and try again.";
  }
}

onMounted(read);
</script>

<template>
  <Page>
    <PageHead eyebrow="Orders" title="Your orders">
      The shop has no accounts: it shows the orders placed from this browser.
    </PageHead>

    <p v-if="problem" class="mt-8 border border-border bg-background-second px-5 py-4" role="alert">
      {{ problem }}
      <button type="button" class="ml-2 underline underline-offset-4" @click="read">Try again</button>
    </p>

    <div v-else-if="placed === null" class="mt-10 h-48 border border-border bg-background-second motion-safe:animate-pulse" aria-label="Loading your orders" />

    <div v-else-if="placed.length === 0" class="mt-10 border border-border px-6 py-16 text-center">
      <p class="font-display text-2xl">No orders yet.</p>
      <p class="mt-2 text-foreground-second">An order you place appears here, with its receipt.</p>
      <ButtonLink href="/" class="mt-6">Browse the shop</ButtonLink>
    </div>

    <ul v-else class="mt-10 divide-y divide-border border-y border-border">
      <li v-for="order in placed" :key="order.number">
        <Link :href="`/orders/${order.number}`" class="grid grid-cols-[minmax(0,1fr)_auto] items-center gap-x-6 gap-y-1 py-5 hover:bg-background-second sm:grid-cols-[10rem_minmax(0,1fr)_auto] sm:px-3">
          <span class="font-display text-xl">Order {{ order.number }}</span>
          <span class="row-start-2 text-sm text-foreground-second sm:row-start-1 sm:col-start-2">
            {{ day(order.placed_at) }}, {{ order.count === 1 ? "1 item" : `${order.count} items` }}
          </span>
          <span class="row-span-2 font-mono tabular-nums sm:row-span-1">{{ money(order.total_cents) }}</span>
        </Link>
      </li>
    </ul>
  </Page>
</template>
