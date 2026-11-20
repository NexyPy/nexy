<script lang="ts">
  import { router } from "@nexy/client";

  import Icon from "@/components/icon.svelte";
  import { start } from "@/lib/notes";

  // `tone` says what the button sits on: the dark header or the page.
  let { tone = "on-paper" }: { tone?: "on-ink" | "on-paper" } = $props();

  const PLUS = "M12 5v14M5 12h14";
  const TONES = {
    "on-ink": "border-paper bg-paper text-ink hover:bg-paper/85",
    "on-paper": "border-foreground bg-foreground text-background hover:opacity-85",
  };

  let busy = $state(false);
  let failed = $state(false);

  async function begin() {
    busy = true;
    failed = false;
    try {
      router.push(`/notes/${await start()}`);
    } catch {
      failed = true;
    } finally {
      busy = false;
    }
  }
</script>

<button
  type="button"
  onclick={begin}
  disabled={busy}
  aria-describedby={failed ? "new-note-failed" : undefined}
  class="inline-flex min-h-10 items-center gap-2 border px-4 font-mono text-xs font-semibold uppercase tracking-[0.04em] transition-colors disabled:opacity-60 {TONES[tone]}"
>
  <Icon path={PLUS} size={16} />
  {busy ? "Opening" : "New note"}
</button>
{#if failed}
  <span id="new-note-failed" role="alert" class="sr-only">The note was not created. Try again.</span>
{/if}
