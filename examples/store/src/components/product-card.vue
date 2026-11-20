<script setup lang="ts">
import { Link } from "@nexy/client";
import type { Product } from "@nexy/actions";

import AddButton from "@/components/add-button.vue";
import { availability, money } from "@/lib/money";

defineProps<{ product: Product }>();
</script>

<template>
  <article class="group flex flex-col border border-border bg-background">
    <Link :href="`/products/${product.slug}`" class="flex flex-1 flex-col">
      <div class="relative aspect-square overflow-hidden border-b border-border">
        <img
          :src="product.image"
          :alt="product.name"
          width="400"
          height="400"
          class="size-full object-cover transition-transform duration-500 motion-safe:group-hover:scale-[1.03]"
          loading="lazy"
        />
        <span
          v-if="product.stock <= 5"
          class="absolute left-3 top-3 border border-border-second bg-background px-2 py-1 font-mono text-[0.68rem] uppercase tracking-[0.06em]"
        >{{ availability(product.stock) }}</span>
      </div>
      <div class="flex flex-1 flex-col gap-1 p-4">
        <p class="font-mono text-[0.68rem] uppercase tracking-[0.08em] text-foreground-second">{{ product.category }}</p>
        <h3 class="text-xl leading-tight group-hover:underline group-hover:underline-offset-4">{{ product.name }}</h3>
        <p class="mt-auto pt-2 font-mono text-sm tabular-nums">{{ money(product.price_cents) }}</p>
      </div>
    </Link>
    <div class="px-4 pb-4">
      <AddButton :slug="product.slug" :stock="product.stock" wide />
    </div>
  </article>
</template>
