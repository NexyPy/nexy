<script lang="ts">
  import { onMount } from "svelte";

  import NoteRow from "@/components/note-row.svelte";
  import SearchBox from "@/components/search-box.svelte";
  import { refresh, shelf } from "@/lib/notes";

  onMount(() => {
    if (!$shelf.loaded) void refresh();
  });

  const pinned = $derived($shelf.items.filter((note) => note.pinned));
  const others = $derived($shelf.items.filter((note) => !note.pinned));
</script>

<div class="flex min-h-0 flex-1 flex-col">
  <div class="border-b border-border p-3">
    <SearchBox />
  </div>
  <div class="min-h-0 flex-1 overflow-y-auto" aria-live="polite" aria-busy={!$shelf.loaded}>
    {#if $shelf.problem}
      <div class="p-4 text-sm">
        <p class="text-danger">{$shelf.problem}</p>
        <button type="button" onclick={refresh} class="mt-2 min-h-10 underline underline-offset-4">Try again</button>
      </div>
    {:else if !$shelf.loaded}
      {#each [1, 2, 3, 4] as row (row)}
        <div class="space-y-2 px-4 py-3" aria-hidden="true">
          <div class="h-4 w-2/3 animate-pulse bg-background-second"></div>
          <div class="h-3 w-full animate-pulse bg-background-second"></div>
        </div>
      {/each}
    {:else if $shelf.items.length === 0}
      <p class="p-4 text-sm text-foreground-second">
        {$shelf.search ? `No note holds "${$shelf.search}".` : "No notes yet. Start one with New note."}
      </p>
    {:else}
      {#if pinned.length}
        <h2 class="px-4 pb-1 pt-3 font-mono text-[0.7rem] font-normal uppercase tracking-[0.06em] text-foreground-second">Pinned</h2>
        <ul>{#each pinned as note (note.id)}<li><NoteRow {note} /></li>{/each}</ul>
      {/if}
      {#if others.length}
        {#if pinned.length}
          <h2 class="px-4 pb-1 pt-3 font-mono text-[0.7rem] font-normal uppercase tracking-[0.06em] text-foreground-second">Notes</h2>
        {/if}
        <ul>{#each others as note (note.id)}<li><NoteRow {note} /></li>{/each}</ul>
      {/if}
    {/if}
  </div>
</div>
