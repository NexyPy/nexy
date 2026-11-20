<script lang="ts">
  // Pin and delete. Deleting asks once, in place: no dialog that hides the note it is about.
  import Icon from "@/components/icon.svelte";

  let { pinned, onpin, ondelete }: { pinned: boolean; onpin: () => void; ondelete: () => void } =
    $props();

  const PIN = "M12 17v5M8 3h8l-1 6 3 4H6l3-4z";
  const BIN = "M4 7h16M10 11v6M14 11v6M6 7l1 13h10l1-13M9 7V4h6v3";
  const BUTTON =
    "inline-flex min-h-10 items-center gap-1.5 px-2.5 font-mono text-xs uppercase tracking-[0.04em] transition-colors";

  let asking = $state(false);
</script>

<div class="ml-auto flex items-center gap-1">
  {#if asking}
    <span class="mr-1 text-sm">Delete this note?</span>
    <button type="button" onclick={ondelete} class="{BUTTON} bg-danger text-background hover:opacity-85">Delete</button>
    <button type="button" onclick={() => (asking = false)} class="{BUTTON} hover:bg-background-second">Keep</button>
  {:else}
    <button type="button" onclick={onpin} aria-pressed={pinned} class="{BUTTON} hover:bg-background-second {pinned ? 'text-signal' : ''}">
      <Icon path={PIN} size={16} />{pinned ? "Pinned" : "Pin"}
    </button>
    <button type="button" onclick={() => (asking = true)} class="{BUTTON} hover:bg-background-second hover:text-danger">
      <Icon path={BIN} size={16} />Delete
    </button>
  {/if}
</div>
