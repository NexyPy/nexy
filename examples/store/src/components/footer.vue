<script setup lang="ts">
import { Link } from "@nexy/client";

import Brand from "@/components/brand.vue";
import Container from "@/components/container.vue";
import LinePattern from "@/components/line-pattern.vue";

const LINK = "text-paper/65 transition-colors hover:text-paper";
</script>

<template>
  <footer class="relative overflow-hidden border-t border-paper/10 bg-ink py-14 text-paper">
    <LinePattern side="left" />
    <Container class="relative flex flex-wrap items-end justify-between gap-8">
      <div class="max-w-sm">
        <Brand />
        <p class="mt-3 text-sm leading-relaxed text-paper/65">
          Free delivery from $50. An example shop: orders are kept, nothing is paid and nothing ships.
        </p>
      </div>
      <nav aria-label="Footer">
        <ul class="flex flex-wrap gap-6 font-mono text-xs uppercase tracking-[0.04em]">
          <li><Link href="/" :class="LINK">Shop</Link></li>
          <li><Link href="/cart" :class="LINK">Cart</Link></li>
          <li><Link href="/orders" :class="LINK">Orders</Link></li>
          <li><a href="https://github.com/NexyPy/nexy" :class="LINK" target="_blank" rel="noopener noreferrer">Made with Nexy</a></li>
        </ul>
      </nav>
    </Container>
  </footer>
</template>
