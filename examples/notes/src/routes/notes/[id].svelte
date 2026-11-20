<script lang="ts">
  // One note. It saves itself 600 ms after the last key, and before any navigation: there is no
  // save button. A note left empty is deleted on the way out. What the server answers is never written back into the fields, so a key typed
  // while a save is on its way is kept.
  import { onMount, untrack } from "svelte";
  import Link from "@nexy/Link.svelte";
  import { ActionError, router, useBlocker } from "@nexy/client";
  import { delete_note, note as readNote, pin_note, preview, save_note } from "@nexy/actions";
  import type { Note } from "@nexy/actions";

  import Icon from "@/components/icon.svelte";
  import NoteActions from "@/components/note-actions.svelte";
  import { refresh } from "@/lib/notes";
  import { ago, words } from "@/lib/time";

  let { id }: { id: string } = $props();

  const WAIT = 600;
  const BACK = "M15 18l-6-6 6-6";
  const SILENT = "Not saved: the server did not answer. Your text is still here.";

  let note = $state<Note | null>(null);
  let missing = $state(false);
  let title = $state("");
  let body = $state("");
  let stored = $state({ title: "", body: "" }); // what the server holds, as this page knows it
  let status = $state<"saved" | "saving" | "refused">("saved");
  let problem = $state("");
  let tab = $state<"write" | "preview">("write");
  let html = $state("");
  let timer: ReturnType<typeof setTimeout> | undefined;
  let saving: Promise<void> = Promise.resolve();

  const noteId = $derived(Number(id));
  const dirty = $derived(title.trim() !== stored.title || body !== stored.body);

  async function open(target: number) {
    note = null;
    tab = "write";
    missing = !Number.isInteger(target) || target < 1;
    if (missing) return;
    try {
      note = await readNote({ note_id: target });
      ({ title, body } = note);
      stored = { title: note.title, body: note.body };
    } catch (error) {
      missing = error instanceof ActionError && [404, 422].includes(error.status);
      if (!missing) (problem = SILENT.replace("Not saved: ", "")), (status = "refused");
    }
  }

  // The id, the title and the body are read when the save is asked for, never later: a save for
  // one note can never carry the text of the next one.
  async function store(target: number, nextTitle: string, nextBody: string) {
    if (nextTitle.trim() === stored.title && nextBody === stored.body) return;
    status = "saving";
    try {
      const saved = await save_note({ note_id: target, title: nextTitle, body: nextBody });
      if (saved.note) {
        stored = { title: saved.note.title, body: saved.note.body };
        if (note && note.id === target) note.updated_at = saved.note.updated_at;
        void refresh();
      }
      problem = saved.problem;
    } catch {
      problem = SILENT;
    }
    status = problem ? "refused" : dirty ? "saving" : "saved";
  }

  function changed() {
    status = "saving";
    clearTimeout(timer);
    timer = setTimeout(flush, WAIT);
  }

  /** Save now what waits to be saved, and wait for it. */
  function flush(): Promise<void> {
    clearTimeout(timer);
    timer = undefined;
    if (!note || !dirty) return saving;
    const [target, nextTitle, nextBody] = [note.id, title, body];
    saving = saving.then(() => store(target, nextTitle, nextBody));
    return saving;
  }

  /** Leave the note: an empty one is deleted, any other is saved first. */
  async function leave(): Promise<void> {
    if (!note || title.trim() || body.trim()) return flush();
    clearTimeout(timer);
    const target = note.id;
    note = null;
    await delete_note({ note_id: target }).catch(() => false);
    await refresh();
  }

  async function show(next: "write" | "preview") {
    tab = next;
    if (next === "preview") html = await preview({ body }).catch(() => "<p>The preview did not load.</p>");
  }

  async function pin() {
    if (!note) return;
    note = await pin_note({ note_id: note.id, pinned: !note.pinned });
    void refresh();
  }

  async function remove() {
    if (!note) return;
    clearTimeout(timer);
    const target = note.id;
    note = null; // nothing left to save on the way out
    await delete_note({ note_id: target });
    await refresh();
    router.push("/");
  }

  // Any navigation away waits for the last save; a reload or a closed tab asks the browser first.
  $effect(() => useBlocker(() => leave()));
  onMount(() => {
    const leave = (event: BeforeUnloadEvent) => dirty && event.preventDefault();
    addEventListener("beforeunload", leave);
    return () => removeEventListener("beforeunload", leave);
  });

  $effect(() => {
    const target = noteId; // the only thing this effect follows: open() reads state of its own
    untrack(() => void open(target));
    return () => void leave(); // the next note waits for nothing, but this one is still saved
  });

  const STATUS = { saved: "Saved", saving: "Saving", refused: "Not saved" };
</script>

<svelte:head><title>{note ? `${note.title || "Untitled"}, Margin` : "Margin"}</title></svelte:head>

<div class="flex items-center justify-between gap-3 border-b border-border px-4 py-2 md:px-8">
  <Link href="/" class="-ml-2 inline-flex min-h-10 items-center gap-1 px-2 text-sm md:hidden">
    <Icon path={BACK} size={16} /> All notes
  </Link>
  {#if note}
    <p class="hidden font-mono text-[0.7rem] uppercase tracking-[0.04em] text-foreground-second md:block">
      Changed {ago(note.updated_at)}
    </p>
    <NoteActions pinned={note.pinned} onpin={pin} ondelete={remove} />
  {/if}
</div>

{#if missing}
  <section class="m-auto max-w-sm px-6 py-16 text-center">
    <h1 class="text-2xl">This note is not here.</h1>
    <p class="mt-2 text-foreground-second">It may have been deleted, or the address is wrong.</p>
    <Link href="/" class="mt-6 inline-block underline underline-offset-4">Back to all notes</Link>
  </section>
{:else if !note}
  <div class="space-y-4 px-4 py-8 md:px-8" aria-busy="true" aria-label="Loading the note">
    <div class="h-9 w-1/2 animate-pulse bg-background-second"></div>
    <div class="h-4 w-full animate-pulse bg-background-second"></div>
    <div class="h-4 w-5/6 animate-pulse bg-background-second"></div>
    {#if problem}<p role="alert" class="text-danger">{problem}</p>{/if}
  </div>
{:else}
  <article class="flex min-h-0 flex-1 flex-col px-4 pt-6 md:px-8">
    <label for="note-title" class="sr-only">Title</label>
    <input
      id="note-title"
      bind:value={title}
      oninput={changed}
      placeholder="Untitled"
      maxlength="120"
      class="w-full bg-transparent font-display text-3xl font-semibold tracking-[-0.01em] placeholder:text-foreground-second/60 focus:outline-none"
    />

    <div class="mt-4 flex items-center justify-between gap-3 border-b border-border">
      <div role="tablist" aria-label="View" class="flex">
        {#each [["write", "Write"], ["preview", "Preview"]] as [name, label] (name)}
          <button
            type="button"
            role="tab"
            aria-selected={tab === name}
            onclick={() => show(name as "write" | "preview")}
            class="-mb-px min-h-10 border-b-2 px-3 font-mono text-xs uppercase tracking-[0.04em] {tab === name ? 'border-foreground' : 'border-transparent text-foreground-second hover:text-foreground'}"
          >{label}</button>
        {/each}
      </div>
      <p class="font-mono text-[0.7rem] uppercase tracking-[0.04em] {status === 'refused' ? 'text-danger' : 'text-foreground-second'}" aria-live="polite">
        <span class="mr-1.5 inline-block size-1.5 rounded-full align-middle {status === 'saved' ? 'bg-signal' : status === 'saving' ? 'bg-foreground-second' : 'bg-danger'}"></span>{STATUS[status]}
        <span class="ml-2 hidden sm:inline">{words(body)} words</span>
      </p>
    </div>
    {#if problem}<p role="alert" class="mt-2 text-sm text-danger">{problem}</p>{/if}

    {#if tab === "write"}
      <label for="note-body" class="sr-only">Note, in Markdown</label>
      <textarea
        id="note-body"
        bind:value={body}
        oninput={changed}
        placeholder="Write in Markdown: # a heading, - a list, **bold**"
        class="min-h-0 w-full flex-1 resize-none bg-transparent py-4 font-mono text-[0.9rem] leading-7 placeholder:text-foreground-second/60 focus:outline-none"
      ></textarea>
    {:else}
      <div class="prose min-h-0 flex-1 overflow-y-auto py-4">
        {#if body.trim()}{@html html}{:else}<p class="text-foreground-second">Nothing to show yet.</p>{/if}
      </div>
    {/if}
  </article>
{/if}
