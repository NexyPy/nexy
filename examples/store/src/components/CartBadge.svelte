<script lang="ts">
  import { onMount } from "svelte";

  let { count }: { count: number } = $props();
  let shown = $state(count);

  onMount(() => {
    const update = (event: Event) => (shown = (event as CustomEvent<number>).detail);
    window.addEventListener("cart:count", update);
    return () => window.removeEventListener("cart:count", update);
  });
</script>

<a
  href="/cart"
  class="flex min-h-11 items-center gap-2 px-3 font-mono text-xs uppercase tracking-[0.04em] text-paper/80 hover:text-paper"
  aria-label={`Cart, ${shown} ${shown === 1 ? "item" : "items"}`}
>
  Cart
  <span class="grid min-w-6 place-items-center bg-paper px-1.5 py-0.5 text-ink tabular-nums">{shown}</span>
</a>
