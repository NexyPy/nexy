<script setup lang="ts">
import { onMounted, ref } from "vue";
import { Link } from "@nexy/client";

import Brand from "@/components/brand.vue";
import CartLink from "@/components/cart-link.vue";
import Icon from "@/components/icon.vue";
import LinePattern from "@/components/line-pattern.vue";
import Sheet from "@/components/sheet.vue";
import ThemeToggle from "@/components/theme-toggle.vue";
import { basket, load } from "@/lib/cart";

const LINK =
  "px-3.5 py-2 font-mono text-xs uppercase tracking-[0.04em] transition-opacity hover:opacity-60 aria-[current=page]:underline aria-[current=page]:underline-offset-4";
const SHEET_LINK =
  "flex min-h-11 items-center gap-2 px-3 text-base transition-colors hover:bg-paper/5 aria-[current=page]:bg-paper/10 aria-[current=page]:font-medium";
const MENU = "M4 7h16M4 12h16M4 17h16";

const open = ref(false);
const opener = ref<HTMLButtonElement | null>(null);

// Closing gives the focus back to the button that opened the menu.
function close() {
  open.value = false;
  opener.value?.focus();
}

// The header stays on screen from page to page: it asks for the cart once.
onMounted(() => {
  if (!basket.loaded) load();
});
</script>

<template>
  <header class="fixed inset-x-0 top-0 z-20 py-4 [view-transition-name:nx-header]">
    <nav
      class="relative mx-auto flex w-[72rem] max-w-[calc(100%-2rem)] items-center justify-between border border-paper/10 bg-ink/85 py-2 pl-5 pr-2 text-paper shadow-[0_10px_30px_-12px_rgb(0_0_0/0.4)] backdrop-blur-[4px]"
      aria-label="Main"
    >
      <LinePattern side="right" />
      <Link href="/" class="relative" aria-label="Good Stock, the shop" @click="open = false"><Brand /></Link>

      <div class="relative flex items-center gap-1">
        <div class="mr-2 hidden items-center sm:flex">
          <Link href="/" :class="LINK" exact>Shop</Link>
          <Link href="/orders" :class="LINK">Orders</Link>
        </div>
        <ThemeToggle />
        <CartLink />
        <button
          ref="opener"
          type="button"
          aria-label="Open menu"
          :aria-expanded="open"
          aria-controls="mobile-menu"
          class="grid size-11 place-items-center sm:hidden"
          @click="open = true"
        >
          <Icon :path="MENU" />
        </button>
      </div>
    </nav>
  </header>

  <Sheet id="mobile-menu" :open="open" title="Menu" @close="close">
    <Link href="/" :class="SHEET_LINK" exact @click="close">Shop</Link>
    <Link href="/orders" :class="SHEET_LINK" @click="close">Orders</Link>
    <Link href="/cart" :class="SHEET_LINK" @click="close">Cart</Link>
  </Sheet>
</template>
