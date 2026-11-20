<script lang="ts">
  import type { Snippet } from "svelte";

  import Icon from "@/components/icon.svelte";

  // `title` is visible, and also names the dialog for a screen reader.
  let {
    id,
    open,
    onclose,
    title,
    children,
  }: { id: string; open: boolean; onclose: () => void; title: string; children?: Snippet } =
    $props();

  const CLOSE = "M18 6L6 18M6 6l12 12";

  let panel = $state<HTMLElement | null>(null);
  let closer = $state<HTMLButtonElement | null>(null);
  let links = $state<HTMLElement | null>(null);
  let shown = $state(open);
  let state = $derived(open ? "open" : "closed");

  // Tab and Shift+Tab wrap inside the panel instead of walking out into the page: the close
  // button comes first, the last link of the menu last.
  function trap(event: KeyboardEvent) {
    const first = closer;
    const last = links?.lastElementChild;
    const here = document.activeElement;
    const away = event.shiftKey ? here === first || here === panel : here === last;
    if (!away || !(last instanceof HTMLElement) || !first) return;
    event.preventDefault();
    (event.shiftKey ? last : first).focus();
  }

  // The focus never leaves the open panel, so its own key handler sees every key.
  function onkey(event: KeyboardEvent) {
    if (event.key === "Escape") onclose();
    if (event.key === "Tab") trap(event);
  }

  // Opening shows the panel; closing plays the slide back before the panel leaves the page.
  $effect(() => {
    if (open) {
      shown = true;
      return;
    }
    const moves = panel?.getAnimations().map((move) => move.finished) ?? [];
    Promise.all(moves).then(() => {
      if (!open) shown = false;
    });
  });

  // While it is open the panel holds the keyboard, the page behind holds still, and a wide
  // screen closes it.
  $effect(() => {
    const element = panel;
    if (!open || !element) return;
    element.focus();
    document.body.style.overflow = "hidden";
    const wide = window.matchMedia("(min-width: 40rem)");
    wide.onchange = () => wide.matches && onclose();
    return () => {
      document.body.style.overflow = "";
      wide.onchange = null;
    };
  });
</script>

{#if shown}
  <div class="fixed inset-0 z-50 sm:hidden">
    <div class="sheet-scrim absolute inset-0 bg-ink/70" data-state={state} aria-hidden="true" onclick={onclose}></div>
    <div
      bind:this={panel}
      {id}
      tabindex="-1"
      class="sheet absolute inset-y-0 left-0 flex w-3/4 max-w-sm flex-col border-r border-paper/10 bg-ink text-paper shadow-[0_10px_30px_-12px_rgb(0_0_0/0.6)] outline-none"
      role="dialog"
      aria-modal="true"
      aria-labelledby="{id}-title"
      data-side="left"
      data-state={state}
      onkeydown={onkey}
    >
      <div class="flex items-center gap-3 border-b border-paper/10 py-4 pl-5 pr-16">
        <img src="/nexy.svg" alt="" class="h-5 invert" />
        <h2 id="{id}-title" class="font-mono text-xs uppercase tracking-[0.04em] text-paper/60">{title}</h2>
      </div>
      <button
        bind:this={closer}
        type="button"
        class="absolute right-2 top-1.5 grid size-11 place-items-center opacity-70 transition-opacity hover:opacity-100 focus-visible:opacity-100"
        aria-label="Close menu"
        onclick={onclose}
      >
        <Icon path={CLOSE} />
      </button>
      <nav bind:this={links} class="flex flex-1 flex-col overflow-y-auto p-3" aria-label="Pages">
        {@render children?.()}
      </nav>
    </div>
  </div>
{/if}
