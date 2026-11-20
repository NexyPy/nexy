<script lang="ts">
  import Link from "@nexy/Link.svelte";
  import type { Summary } from "@nexy/actions";

  import Icon from "@/components/icon.svelte";
  import { ago } from "@/lib/time";

  let { note }: { note: Summary } = $props();

  const PIN = "M12 17v5M8 3h8l-1 6 3 4H6l3-4z";
</script>

<Link
  href={`/notes/${note.id}`}
  class="group block border-l-2 border-transparent px-4 py-3 transition-colors hover:bg-background-second aria-[current=page]:border-signal aria-[current=page]:bg-background-second"
>
  <span class="flex items-center justify-between gap-3">
    <span class="truncate font-medium {note.title ? '' : 'text-foreground-second'}">
      {note.title || "Untitled"}
    </span>
    {#if note.pinned}
      <span class="shrink-0 text-signal" title="Pinned"><Icon path={PIN} size={14} /><span class="sr-only">Pinned</span></span>
    {/if}
  </span>
  <span class="mt-0.5 block truncate text-sm text-foreground-second">{note.excerpt || "No text yet"}</span>
  <span class="mt-1.5 block font-mono text-[0.7rem] uppercase tracking-[0.04em] text-foreground-second">
    {ago(note.updated_at)}
  </span>
</Link>
