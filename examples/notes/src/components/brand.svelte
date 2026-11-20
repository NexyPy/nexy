<script lang="ts">
  // The name of the app, drawn once: the header and the empty page show it.
  let { size = "text-xl" }: { size?: string } = $props();
</script>

<span class="inline-flex items-baseline gap-1.5 font-display font-semibold tracking-[-0.01em] {size}">
  <span aria-hidden="true" class="inline-block h-[0.95em] w-[3px] translate-y-[0.12em] bg-signal"></span>
  Margin
</span>
