<script setup lang="ts">
// The top of every page: what kind of page it is, its title, and a line that says what to do here.
defineProps<{ eyebrow: string; title: string }>();
</script>

<template>
  <header class="min-w-0">
    <p class="flex items-center gap-2.5 font-mono text-[0.72rem] uppercase tracking-[0.08em] text-foreground-second before:h-1.5 before:w-1.5 before:bg-current before:content-['']">
      {{ eyebrow }}
    </p>
    <h1 class="mt-4 text-[clamp(2.4rem,6vw,3.6rem)] leading-[1.02] tracking-[-0.02em] [overflow-wrap:anywhere]">{{ title }}</h1>
    <div class="mt-4 max-w-[46ch] leading-relaxed text-foreground-second empty:hidden"><slot /></div>
  </header>
</template>
