<script setup lang="ts">
import { computed, onMounted, ref, watch } from "vue";
import { ActionError, Link, useSearchParams } from "@nexy/client";
import { order } from "@nexy/actions";
import type { Order } from "@nexy/actions";

import ButtonLink from "@/components/button-link.vue";
import Icon from "@/components/icon.vue";
import Page from "@/components/page.vue";
import PageHead from "@/components/page-head.vue";
import Totals from "@/components/totals.vue";
import { day, money } from "@/lib/money";

const props = defineProps<{ number: string }>();

const CHECK = "M5 12l5 5L20 7";

const params = useSearchParams();
const receipt = ref<Order | null>(null);
const missing = ref(false);
const problem = ref("");
// The checkout sends the visitor here with ?placed: the order has just been made.
const fresh = computed(() => params.value.has("placed"));

async function read() {
  receipt.value = null;
  missing.value = false;
  problem.value = "";
  try {
    receipt.value = await order({ number: Number(props.number) });
  } catch (error) {
    if (error instanceof ActionError && (error.status === 404 || error.status === 422)) missing.value = true;
    else problem.value = "The shop did not answer. Check your connection and try again.";
  }
}

onMounted(read);
watch(() => props.number, read);
</script>

<template>
  <Page>
    <div v-if="missing" class="border border-border px-6 py-16 text-center">
      <h1 class="text-4xl">This order is not one of yours</h1>
      <p class="mt-3 text-foreground-second">An order shows only in the browser that placed it.</p>
      <ButtonLink href="/orders" class="mt-6">Your orders</ButtonLink>
    </div>

    <p v-else-if="problem" class="border border-border bg-background-second px-5 py-4" role="alert">
      {{ problem }}
      <button type="button" class="ml-2 underline underline-offset-4" @click="read">Try again</button>
    </p>

    <div v-else-if="!receipt" class="h-96 border border-border bg-background-second motion-safe:animate-pulse" aria-label="Loading the order" />

    <template v-else>
      <p v-if="fresh" class="mb-10 flex items-start gap-3 border border-signal px-5 py-4" role="status">
        <span class="mt-0.5 text-signal"><Icon :path="CHECK" /></span>
        <span>Thank you, {{ receipt.name }}. Your order is placed, and a shop would send its receipt to {{ receipt.email }}.</span>
      </p>
      <PageHead :eyebrow="`Placed on ${day(receipt.placed_at)}`" :title="`Order ${receipt.number}`" />

      <div class="mt-10 grid gap-10 lg:grid-cols-[minmax(0,1fr)_22rem] lg:items-start">
        <ul class="divide-y divide-border border-y border-border" aria-label="Items">
          <li v-for="line in receipt.lines" :key="line.slug" class="flex items-center gap-4 py-4">
            <img :src="`/products/${line.slug}.svg`" alt="" width="64" height="64" class="size-16 border border-border" />
            <div class="min-w-0 flex-1">
              <Link :href="`/products/${line.slug}`" class="font-medium hover:underline hover:underline-offset-4">{{ line.name }}</Link>
              <p class="font-mono text-sm text-foreground-second tabular-nums">{{ line.quantity }} x {{ money(line.price_cents) }}</p>
            </div>
            <span class="font-mono tabular-nums">{{ money(line.total_cents) }}</span>
          </li>
        </ul>

        <aside class="flex flex-col gap-6 border border-border bg-background-second p-6">
          <Totals :subtotal="receipt.subtotal_cents" :shipping="receipt.shipping_cents" :total="receipt.total_cents" />
          <div>
            <h2 class="font-mono text-[0.72rem] font-normal uppercase tracking-[0.08em] text-foreground-second">Delivery to</h2>
            <address class="mt-2 not-italic leading-relaxed">
              {{ receipt.name }}<br />{{ receipt.address }}<br />{{ receipt.postcode }} {{ receipt.city }}
            </address>
          </div>
        </aside>
      </div>
      <Link href="/orders" class="mt-10 inline-block text-sm text-foreground-second underline underline-offset-4 hover:text-foreground">All your orders</Link>
    </template>
  </Page>
</template>
