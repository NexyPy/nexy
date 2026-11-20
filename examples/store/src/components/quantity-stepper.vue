<script setup lang="ts">
import Icon from "@/components/icon.vue";

// How many of a product: one less, one more, never under one nor over what the shelves hold.
const quantity = defineModel<number>({ required: true });
defineProps<{ max: number; name: string; disabled?: boolean }>();

const MINUS = "M5 12h14";
const PLUS = "M12 5v14M5 12h14";
const BUTTON =
  "grid size-11 place-items-center text-foreground-second transition-colors hover:bg-background-second hover:text-foreground disabled:cursor-not-allowed disabled:opacity-40 disabled:hover:bg-transparent";
</script>

<template>
  <div class="inline-flex items-center border border-border-second" role="group" :aria-label="`Quantity of ${name}`">
    <button type="button" :class="BUTTON" :disabled="disabled || quantity <= 1" :aria-label="`One less ${name}`" @click="quantity--">
      <Icon :path="MINUS" :size="16" />
    </button>
    <output class="min-w-10 text-center font-mono tabular-nums" aria-live="polite">{{ quantity }}</output>
    <button type="button" :class="BUTTON" :disabled="disabled || quantity >= max" :aria-label="`One more ${name}`" @click="quantity++">
      <Icon :path="PLUS" :size="16" />
    </button>
  </div>
</template>
