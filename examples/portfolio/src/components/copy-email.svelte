<script lang="ts">
  // The address is in the component, not a prop: the HTML rendered at build carries it, so the
  // link works before the island wakes up and with JavaScript off.
  const EMAIL = "hello@noor.example";

  let live = $state(false);
  let outcome = $state<"" | "copied" | "refused">("");

  $effect(() => {
    live = true;
  });

  async function copy() {
    try {
      await navigator.clipboard.writeText(EMAIL);
      outcome = "copied";
    } catch {
      outcome = "refused";
    }
    setTimeout(() => (outcome = ""), 3000);
  }
</script>

<div class="flex flex-wrap items-center gap-2">
  <a
    href="mailto:{EMAIL}"
    class="inline-flex h-12 items-center rounded-full bg-foreground px-6 text-sm font-medium text-background transition-opacity hover:opacity-85"
  >
    {EMAIL}
  </a>
  {#if live}
    <button
      type="button"
      onclick={copy}
      class="inline-flex h-12 items-center rounded-full border border-border px-5 text-sm font-medium transition-colors hover:border-foreground"
    >
      {outcome === "copied" ? "Copied" : "Copy the address"}
    </button>
  {/if}
  <p aria-live="polite" class="w-full text-sm text-foreground-second empty:hidden">
    {#if outcome === "refused"}The browser did not allow copying: select the address instead.{/if}
  </p>
</div>
