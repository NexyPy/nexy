<script setup lang="ts">
import { computed, onMounted, ref, watch } from "vue";
import { ActionError, Link } from "@nexy/client";
import { product } from "@nexy/actions";
import type { ProductPage } from "@nexy/actions";

import AddButton from "@/components/add-button.vue";
import Icon from "@/components/icon.vue";
import Page from "@/components/page.vue";
import ProductCard from "@/components/product-card.vue";
import QuantityStepper from "@/components/quantity-stepper.vue";
import { basket } from "@/lib/cart";
import { availability, money } from "@/lib/money";

const props = defineProps<{ slug: string }>();

const BACK = "M19 12H5M12 19l-7-7 7-7";
const CHECK = "M5 12l5 5L20 7";

const page = ref<ProductPage | null>(null);
const missing = ref(false);
const problem = ref("");
const quantity = ref(1);
const added = ref(false);
const item = computed(() => page.value?.product);
const held = computed(() => basket.cart.lines.find((line) => line.slug === props.slug)?.quantity ?? 0);

async function open() {
  page.value = null;
  missing.value = false;
  problem.value = "";
  quantity.value = 1;
  added.value = false;
  try {
    page.value = await product({ slug: props.slug });
  } catch (error) {
    if (error instanceof ActionError && error.status === 404) missing.value = true;
    else problem.value = "The shop did not answer. Check your connection and try again.";
  }
}

// The cart answered for this product: say so next to the button.
watch(
  () => basket.busy,
  (busy, before) => {
    if (before === props.slug && !busy && !basket.problem) added.value = true;
  },
);

onMounted(open);
watch(() => props.slug, open);
</script>

<template>
  <Page>
    <Link href="/" class="inline-flex min-h-11 items-center gap-2 font-mono text-xs uppercase tracking-[0.05em] text-foreground-second hover:text-foreground">
      <Icon :path="BACK" :size="16" /> All products
    </Link>

    <div v-if="missing" class="mt-8 border border-border px-6 py-16 text-center">
      <h1 class="text-4xl">This product is not in the shop</h1>
      <p class="mt-3 text-foreground-second">It may have left the shelves for good.</p>
      <Link href="/" class="mt-6 inline-flex min-h-11 items-center border border-foreground px-5 font-mono text-xs font-semibold uppercase tracking-[0.05em]">See every product</Link>
    </div>

    <p v-else-if="problem" class="mt-8 border border-border bg-background-second px-5 py-4" role="alert">
      {{ problem }}
      <button type="button" class="ml-2 underline underline-offset-4" @click="open">Try again</button>
    </p>

    <div v-else-if="!item" class="mt-8 grid gap-10 lg:grid-cols-2" aria-label="Loading the product">
      <div class="aspect-square border border-border bg-background-second motion-safe:animate-pulse" />
      <div class="h-72 border border-border bg-background-second motion-safe:animate-pulse" />
    </div>

    <template v-else>
      <article class="mt-8 grid gap-10 lg:grid-cols-2 lg:gap-16">
        <img :src="item.image" :alt="item.name" width="400" height="400" class="aspect-square w-full border border-border object-cover" />
        <div class="flex flex-col">
          <p class="font-mono text-[0.72rem] uppercase tracking-[0.08em] text-foreground-second">{{ item.category }}</p>
          <h1 class="mt-3 text-[clamp(2.4rem,5vw,3.4rem)] leading-[1.02] tracking-[-0.02em]">{{ item.name }}</h1>
          <p class="mt-4 font-mono text-2xl tabular-nums">{{ money(item.price_cents) }}</p>
          <p class="mt-5 max-w-[42ch] text-lg leading-relaxed text-foreground-second">{{ item.summary }}</p>

          <p class="mt-6 flex items-center gap-2 text-sm">
            <span :class="['size-2', item.stock === 0 ? 'bg-danger' : 'bg-signal']" aria-hidden="true" />
            <span>{{ availability(item.stock) }}<span v-if="held > 0" class="text-foreground-second">, {{ held }} in your cart</span></span>
          </p>

          <div v-if="item.stock > 0" class="mt-6 flex flex-wrap items-center gap-3">
            <QuantityStepper v-model="quantity" :max="Math.max(1, item.stock - held)" :name="item.name" />
            <AddButton :slug="item.slug" :stock="item.stock - held" :quantity="quantity" />
          </div>
          <AddButton v-else class="mt-6 self-start" :slug="item.slug" :stock="0" />

          <p v-if="added" class="mt-4 flex flex-wrap items-center gap-2 text-sm" aria-live="polite">
            <Icon :path="CHECK" :size="16" />
            {{ basket.cart.note || "Added to your cart." }}
            <Link href="/cart" class="underline underline-offset-4">View your cart</Link>
          </p>

          <h2 class="mt-10 font-mono text-[0.72rem] font-normal uppercase tracking-[0.08em] text-foreground-second">Details</h2>
          <ul class="mt-3 divide-y divide-border border-y border-border">
            <li v-for="detail in item.details" :key="detail" class="py-3">{{ detail }}</li>
          </ul>
        </div>
      </article>

      <section v-if="page && page.related.length" class="mt-20" aria-labelledby="related">
        <div class="flex items-end justify-between gap-4 border-b border-border pb-4">
          <h2 id="related" class="text-3xl">More in {{ item.category }}</h2>
          <Link :href="`/?category=${item.category}`" class="font-mono text-xs uppercase tracking-[0.05em] text-foreground-second hover:text-foreground">See all</Link>
        </div>
        <ul class="mt-6 grid grid-cols-2 gap-3 sm:gap-5 lg:grid-cols-4">
          <li v-for="other in page.related" :key="other.slug" class="flex">
            <ProductCard :product="other" class="w-full" />
          </li>
        </ul>
      </section>
    </template>
  </Page>
</template>
