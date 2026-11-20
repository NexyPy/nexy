<script setup lang="ts">
import { onMounted } from "vue";
import { Link } from "@nexy/client";

import ButtonLink from "@/components/button-link.vue";
import Page from "@/components/page.vue";
import PageHead from "@/components/page-head.vue";
import QuantityStepper from "@/components/quantity-stepper.vue";
import Totals from "@/components/totals.vue";
import { basket, change, load, remove } from "@/lib/cart";
import { money } from "@/lib/money";

// The cart may have changed in another tab: this page asks again when it opens.
onMounted(load);
</script>

<template>
  <Page>
    <PageHead eyebrow="Cart" title="Your cart">
      <template v-if="basket.cart.count">
        {{ basket.cart.count === 1 ? "One item" : `${basket.cart.count} items` }}, kept for this browser for a month.
      </template>
    </PageHead>

    <p v-if="basket.problem" class="mt-8 border border-border bg-background-second px-5 py-4" role="alert">
      {{ basket.problem }}
      <button type="button" class="ml-2 underline underline-offset-4" @click="load">Try again</button>
    </p>

    <div v-if="!basket.loaded" class="mt-10 h-64 border border-border bg-background-second motion-safe:animate-pulse" aria-label="Loading your cart" />

    <div v-else-if="basket.cart.lines.length === 0" class="mt-10 border border-border px-6 py-16 text-center">
      <p class="font-display text-2xl">Your cart is empty.</p>
      <p class="mt-2 text-foreground-second">Everything you add stays here until you order it.</p>
      <ButtonLink href="/" class="mt-6">Browse the shop</ButtonLink>
    </div>

    <div v-else class="mt-10 grid gap-10 lg:grid-cols-[minmax(0,1fr)_22rem] lg:items-start">
      <div>
        <p v-if="basket.cart.note" class="mb-4 border border-border bg-background-second px-5 py-3 text-sm" aria-live="polite">{{ basket.cart.note }}</p>
        <ul class="divide-y divide-border border-y border-border" aria-label="Items">
          <li v-for="line in basket.cart.lines" :key="line.slug" class="grid grid-cols-[5rem_minmax(0,1fr)] gap-4 py-5 sm:grid-cols-[6rem_minmax(0,1fr)_auto]">
            <Link :href="`/products/${line.slug}`" tabindex="-1" aria-hidden="true">
              <img :src="line.image" alt="" width="96" height="96" class="aspect-square w-full border border-border object-cover" />
            </Link>
            <div class="flex min-w-0 flex-col gap-3">
              <div>
                <Link :href="`/products/${line.slug}`" class="text-lg font-medium hover:underline hover:underline-offset-4">{{ line.name }}</Link>
                <p class="font-mono text-sm text-foreground-second tabular-nums">{{ money(line.price_cents) }} each</p>
              </div>
              <div class="flex flex-wrap items-center gap-3">
                <QuantityStepper
                  :model-value="line.quantity"
                  :max="line.stock"
                  :name="line.name"
                  :disabled="basket.busy === line.slug"
                  @update:model-value="(quantity: number) => change(line.slug, quantity)"
                />
                <button type="button" class="min-h-11 px-2 text-sm text-foreground-second underline underline-offset-4 hover:text-foreground" @click="remove(line.slug)">
                  Remove<span class="sr-only"> {{ line.name }}</span>
                </button>
              </div>
            </div>
            <p class="col-start-2 font-mono tabular-nums sm:col-start-3 sm:text-right">{{ money(line.total_cents) }}</p>
          </li>
        </ul>
      </div>

      <aside class="border border-border bg-background-second p-6 lg:sticky lg:top-28" aria-label="Summary">
        <h2 class="text-2xl">Summary</h2>
        <div class="mt-4">
          <Totals :subtotal="basket.cart.subtotal_cents" :shipping="basket.cart.shipping_cents" :total="basket.cart.total_cents" />
        </div>
        <ButtonLink href="/checkout" class="mt-6 w-full">Check out</ButtonLink>
        <Link href="/" class="mt-4 block text-center text-sm text-foreground-second underline underline-offset-4 hover:text-foreground">Keep shopping</Link>
      </aside>
    </div>
  </Page>
</template>
