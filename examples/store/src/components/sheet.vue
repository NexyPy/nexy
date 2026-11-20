<script setup lang="ts">
import { computed, nextTick, onBeforeUnmount, ref, watch } from "vue";

import Brand from "@/components/brand.vue";
import Icon from "@/components/icon.vue";

// `title` is visible, and also names the dialog for a screen reader.
const props = defineProps<{ id: string; open: boolean; title: string }>();
const emit = defineEmits<{ close: [] }>();

const CLOSE = "M18 6L6 18M6 6l12 12";

const panel = ref<HTMLElement | null>(null);
const shown = ref(props.open);
const state = computed(() => (props.open ? "open" : "closed"));
// Read when the sheet opens: the server renders this component too, and has no window.
let wide: MediaQueryList | null = null;

const closer = ref<HTMLButtonElement | null>(null);
const links = ref<HTMLElement | null>(null);

// Tab and Shift+Tab wrap inside the panel instead of walking out into the page: the close button
// comes first, the last link of the menu last.
function trap(event: KeyboardEvent) {
  const first = closer.value;
  const last = links.value?.lastElementChild;
  const here = document.activeElement;
  const away = event.shiftKey ? here === first || here === panel.value : here === last;
  if (!away || !(last instanceof HTMLElement) || !first) return;
  event.preventDefault();
  (event.shiftKey ? last : first).focus();
}

// The focus never leaves the open panel, so its own key handler sees every key.
function onKey(event: KeyboardEvent) {
  if (event.key === "Escape") emit("close");
  if (event.key === "Tab") trap(event);
}

function release() {
  document.body.style.overflow = "";
  if (wide) wide.onchange = null;
}

// While it is open the panel holds the keyboard, the page behind holds still, and a wide screen
// closes it. Closing plays the slide back before the panel leaves the page.
watch(
  () => props.open,
  async (open) => {
    if (!open) {
      release();
      const moves = panel.value?.getAnimations().map((move) => move.finished) ?? [];
      await Promise.all(moves);
      if (!props.open) shown.value = false;
      return;
    }
    shown.value = true;
    await nextTick();
    panel.value?.focus();
    document.body.style.overflow = "hidden";
    wide = window.matchMedia("(min-width: 40rem)");
    wide.onchange = () => wide?.matches && emit("close");
  },
  // After the DOM update: the closing panel must carry its new state before its exit is read.
  { flush: "post" },
);

onBeforeUnmount(release);
</script>

<template>
  <div v-if="shown" class="fixed inset-0 z-50 sm:hidden">
    <div class="sheet-scrim absolute inset-0 bg-ink/70" :data-state="state" aria-hidden="true" @click="emit('close')" />
    <div
      :id="id"
      ref="panel"
      tabindex="-1"
      class="sheet absolute inset-y-0 left-0 flex w-3/4 max-w-sm flex-col border-r border-paper/10 bg-ink text-paper shadow-[0_10px_30px_-12px_rgb(0_0_0/0.6)] outline-none"
      role="dialog"
      aria-modal="true"
      :aria-labelledby="`${id}-title`"
      data-side="left"
      :data-state="state"
      @keydown="onKey"
    >
      <div class="flex items-center gap-3 border-b border-paper/10 py-4 pl-5 pr-16">
        <Brand />
        <h2 :id="`${id}-title`" class="font-mono text-xs uppercase tracking-[0.04em] text-paper/60">{{ title }}</h2>
      </div>
      <button
        ref="closer"
        type="button"
        class="absolute right-2 top-1.5 grid size-11 place-items-center opacity-70 transition-opacity hover:opacity-100 focus-visible:opacity-100"
        aria-label="Close menu"
        @click="emit('close')"
      >
        <Icon :path="CLOSE" />
      </button>
      <nav ref="links" class="flex flex-1 flex-col overflow-y-auto p-3" aria-label="Pages">
        <slot />
      </nav>
    </div>
  </div>
</template>
