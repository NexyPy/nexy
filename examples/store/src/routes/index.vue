<script setup lang="ts">
import { computed, onMounted, ref, watch } from "vue";
import { useSearchParams } from "@nexy/client";
import { catalog } from "@nexy/actions";
import type { Category, Product } from "@nexy/actions";

import Icon from "@/components/icon.vue";
import Page from "@/components/page.vue";
import PageHead from "@/components/page-head.vue";
import ProductCard from "@/components/product-card.vue";

const SEARCH = "M11 4a7 7 0 100 14 7 7 0 000-14zM20 20l-4-4";
const CHIP =
  "inline-flex min-h-10 items-center gap-2 border px-3.5 text-[0.9rem] transition-colors aria-pressed:border-foreground aria-pressed:bg-foreground aria-pressed:text-background";
const WAIT_MS = 250;

const params = useSearchParams();
const category = ref("");
const search = ref("");
const products = ref<Product[]>([]);
const categories = ref<Category[]>([]);
const loaded = ref(false);
const problem = ref("");
const total = computed(() => categories.value.reduce((sum, item) => sum + item.count, 0));

async function browse() {
  try {
    const shelf = await catalog({ category: category.value, search: search.value });
    products.value = shelf.products;
    categories.value = shelf.categories;
    problem.value = "";
  } catch {
    problem.value = "The shop did not answer. Check your connection and try again.";
  }
  loaded.value = true;
}

// A search waits for a pause in the typing; a category answers at once.
let pause: ReturnType<typeof setTimeout> | undefined;
watch(search, () => {
  clearTimeout(pause);
  pause = setTimeout(browse, WAIT_MS);
});
watch(category, browse);

// A link such as /?category=Bags opens the shop on that category.
onMounted(() => {
  category.value = params.value.get("category") ?? "";
  if (!category.value) browse();
});
</script>

<template>
  <Page>
    <div class="flex flex-col gap-10 lg:flex-row lg:items-end lg:justify-between">
      <PageHead eyebrow="Free delivery from $50" title="Good things, made to last.">
        A mug, a notebook, a bag for the road: eight things we would buy again, each one in stock until it is not.
      </PageHead>
      <label class="relative block w-full lg:max-w-xs">
        <span class="sr-only">Search the shop</span>
        <span class="pointer-events-none absolute inset-y-0 left-4 grid place-items-center text-foreground-second">
          <Icon :path="SEARCH" :size="18" />
        </span>
        <input
          v-model.trim="search"
          type="search"
          placeholder="Search the shop"
          class="min-h-12 w-full border border-border-second bg-background pl-11 pr-4 text-base text-foreground placeholder:text-foreground-second focus:border-foreground focus:outline-none"
        />
      </label>
    </div>

    <div class="mt-10 flex flex-wrap gap-2 border-y border-border py-4" role="group" aria-label="Category">
      <button type="button" :class="[CHIP, 'border-border-second']" :aria-pressed="category === ''" @click="category = ''">
        All <span class="font-mono text-xs opacity-70">{{ total || "" }}</span>
      </button>
      <button
        v-for="item in categories"
        :key="item.name"
        type="button"
        :class="[CHIP, 'border-border-second']"
        :aria-pressed="category === item.name"
        @click="category = item.name"
      >
        {{ item.name }} <span class="font-mono text-xs opacity-70">{{ item.count }}</span>
      </button>
    </div>

    <p v-if="problem" class="mt-10 border border-border bg-background-second px-5 py-4" role="alert">
      {{ problem }}
      <button type="button" class="ml-2 underline underline-offset-4" @click="browse">Try again</button>
    </p>

    <ul v-if="!loaded" class="mt-10 grid grid-cols-2 gap-3 sm:gap-5 lg:grid-cols-4" aria-label="Loading the products">
      <li v-for="n in 8" :key="n" class="aspect-[3/4.4] border border-border bg-background-second motion-safe:animate-pulse" />
    </ul>

    <div v-else-if="products.length === 0 && !problem" class="mt-10 border border-border px-6 py-16 text-center">
      <p class="font-display text-2xl">Nothing matches "{{ search }}".</p>
      <p class="mt-2 text-foreground-second">Try another word, or look through every product.</p>
      <button type="button" class="mt-6 min-h-11 border border-foreground px-5 font-mono text-xs font-semibold uppercase tracking-[0.05em]" @click="search = ''; category = ''">
        Show every product
      </button>
    </div>

    <ul v-else class="mt-10 grid grid-cols-2 gap-3 sm:gap-5 lg:grid-cols-4" aria-label="Products">
      <li v-for="product in products" :key="product.slug" class="flex">
        <ProductCard :product="product" class="w-full" />
      </li>
    </ul>
  </Page>
</template>
