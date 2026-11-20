<script setup lang="ts">
import { nextTick, onMounted, reactive, ref } from "vue";
import { useAction, useRouter } from "@nexy/client";
import { place_order } from "@nexy/actions";

import ButtonLink from "@/components/button-link.vue";
import Field from "@/components/field.vue";
import Page from "@/components/page.vue";
import PageHead from "@/components/page-head.vue";
import Totals from "@/components/totals.vue";
import { basket, load } from "@/lib/cart";
import { money } from "@/lib/money";

const router = useRouter();
const form = ref<HTMLFormElement | null>(null);
const delivery = reactive({ name: "", email: "", address: "", city: "", postcode: "" });
const errors = ref<Record<string, string>>({});
const { run, pending, error } = useAction(place_order);

// The first field the server refused gets the focus, so the keyboard lands where the fix goes.
async function focusFirst() {
  await nextTick();
  const first = Object.keys(errors.value).find((name) => name !== "cart");
  const field = first ? form.value?.elements.namedItem(first) : null;
  if (field instanceof HTMLElement) field.focus();
}

async function submit() {
  const placed = await run({ ...delivery });
  if (!placed) return;
  errors.value = placed.errors;
  if (placed.number) {
    await load();
    router.push(`/orders/${placed.number}?placed`);
    return;
  }
  focusFirst();
}

onMounted(load);
</script>

<template>
  <Page>
    <PageHead eyebrow="Checkout" title="Where does it go?">
      Nothing is paid here: this example shop keeps the order and stops there.
    </PageHead>

    <div v-if="!basket.loaded" class="mt-10 h-80 border border-border bg-background-second motion-safe:animate-pulse" aria-label="Loading your cart" />

    <div v-else-if="basket.cart.lines.length === 0" class="mt-10 border border-border px-6 py-16 text-center">
      <p class="font-display text-2xl">Your cart is empty.</p>
      <p class="mt-2 text-foreground-second">Add something before you check out.</p>
      <ButtonLink href="/" class="mt-6">Browse the shop</ButtonLink>
    </div>

    <div v-else class="mt-10 grid gap-10 lg:grid-cols-[minmax(0,1fr)_22rem] lg:items-start">
      <form ref="form" class="flex flex-col gap-8" novalidate @submit.prevent="submit">
        <p v-if="errors.cart || error" class="border border-danger px-5 py-4 text-danger" role="alert">
          {{ errors.cart || "The shop did not answer, so no order was placed. Try again in a moment." }}
          <ButtonLink v-if="errors.cart" href="/cart" :solid="false" class="mt-3 flex w-fit">Back to the cart</ButtonLink>
        </p>
        <fieldset class="grid gap-5">
          <legend class="mb-4 font-mono text-[0.72rem] uppercase tracking-[0.08em] text-foreground-second">You</legend>
          <Field v-model="delivery.name" name="name" label="Full name" autocomplete="name" :maxlength="80" :error="errors.name" />
          <Field v-model="delivery.email" name="email" label="Email" type="email" autocomplete="email" :maxlength="120" :error="errors.email" />
        </fieldset>
        <fieldset class="grid gap-5 sm:grid-cols-[minmax(0,1fr)_10rem]">
          <legend class="mb-4 font-mono text-[0.72rem] uppercase tracking-[0.08em] text-foreground-second">Delivery</legend>
          <Field v-model="delivery.address" class="sm:col-span-2" name="address" label="Street and number" autocomplete="street-address" :maxlength="200" :error="errors.address" />
          <Field v-model="delivery.city" name="city" label="City" autocomplete="address-level2" :maxlength="80" :error="errors.city" />
          <Field v-model="delivery.postcode" name="postcode" label="Postal code" autocomplete="postal-code" :maxlength="12" :error="errors.postcode" />
        </fieldset>
        <button
          type="submit"
          class="min-h-12 border border-foreground bg-foreground px-6 font-mono text-[0.8rem] font-semibold uppercase tracking-[0.05em] text-background transition-opacity hover:opacity-85 disabled:cursor-progress disabled:opacity-60 sm:w-fit"
          :disabled="pending"
        >
          {{ pending ? "Placing your order..." : `Place order, ${money(basket.cart.total_cents)}` }}
        </button>
      </form>

      <aside class="border border-border bg-background-second p-6 lg:sticky lg:top-28" aria-label="Your order">
        <h2 class="text-2xl">Your order</h2>
        <ul class="mt-4 divide-y divide-border border-b border-border">
          <li v-for="line in basket.cart.lines" :key="line.slug" class="flex items-center gap-3 py-3">
            <img :src="line.image" alt="" width="48" height="48" class="size-12 border border-border" />
            <span class="min-w-0 flex-1 text-sm">{{ line.name }} <span class="text-foreground-second">x {{ line.quantity }}</span></span>
            <span class="font-mono text-sm tabular-nums">{{ money(line.total_cents) }}</span>
          </li>
        </ul>
        <div class="mt-2">
          <Totals :subtotal="basket.cart.subtotal_cents" :shipping="basket.cart.shipping_cents" :total="basket.cart.total_cents" />
        </div>
      </aside>
    </div>
  </Page>
</template>
