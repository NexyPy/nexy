<script setup lang="ts">
import { Link } from "@nexy/client";

// A link that looks like the main button of a page: it goes somewhere, so it stays a link.
withDefaults(defineProps<{ href: string; solid?: boolean }>(), { solid: true });
</script>

<template>
  <Link
    :href="href as '/'"
    :class="[
      'inline-flex min-h-12 items-center justify-center border px-6 font-mono text-[0.78rem] font-semibold uppercase tracking-[0.05em] transition-opacity hover:opacity-85',
      solid ? 'border-foreground bg-foreground text-background' : 'border-border-second text-foreground hover:border-foreground',
    ]"
  >
    <slot />
  </Link>
</template>
