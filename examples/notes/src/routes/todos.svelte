<script lang="ts">
  import { onMount } from "svelte";
  import { EMPTY, FILTERS, LOADING, count, server, shown, took } from "../lib/todos";
  import type { Answer, Filter, Todo } from "../lib/todos";

  let items = $state<Todo[]>([]);
  let filter = $state<Filter>("all");
  let editing = $state<number | null>(null);
  let draft = $state("");
  let note = $state("");
  let last = $state<Answer | null>(null);
  let pending = $state(false);
  const visible = $derived(shown(items, filter));

  function focus(element: HTMLElement) {
    element.focus();
  }

  async function run(call: Promise<Answer>): Promise<Answer> {
    const answer = await call;
    if (answer.items) items = answer.items;
    note = answer.note;
    last = answer;
    return answer;
  }

  async function add(event: SubmitEvent & { currentTarget: HTMLFormElement }) {
    event.preventDefault();
    const form = event.currentTarget;
    pending = true;
    const answer = await run(server.add(String(new FormData(form).get("title") ?? "")));
    pending = false;
    if (answer.items && !answer.note) form.reset();
  }

  function edit(todo: Todo) {
    editing = todo.id;
    draft = todo.title;
  }

  async function save(todo: Todo) {
    if (editing !== todo.id) return;
    editing = null;
    if (draft.trim() !== todo.title) await run(server.rename(todo.id, draft));
  }

  function key(event: KeyboardEvent, todo: Todo) {
    if (event.key === "Enter") save(todo);
    if (event.key === "Escape") editing = null;
  }

  onMount(() => run(server.load()));
</script>

<section class="mx-auto grid w-full max-w-[72rem] grid-cols-[minmax(0,1fr)] gap-12 px-6 pb-20 pt-[8.5rem] lg:grid-cols-[minmax(0,22rem)_minmax(0,1fr)] lg:items-start lg:gap-[4.5rem]">
  <header class="min-w-0">
    <p class="flex items-center gap-2.5 font-mono text-[0.72rem] uppercase tracking-[0.08em] text-foreground-second before:h-1.5 before:w-1.5 before:bg-current before:content-['']">Client and server</p>
    <h1 class="mt-4 text-[clamp(2.6rem,6vw,3.6rem)] leading-[1.02] tracking-[-0.02em]">Todos</h1>
    <p class="mt-5 max-w-[40ch] leading-relaxed text-foreground-second">
      Each change calls an action of <code class="font-mono text-[0.85em] text-foreground">src/actions/todos.py</code>, and the page shows the list
      the server answers with. The tasks live in the <code class="font-mono text-[0.85em] text-foreground">todos</code> table of
      your database.
    </p>
    <dl class="mt-8 divide-y divide-border border border-border bg-background-second">
      <div class="flex justify-between gap-4 px-4 py-3 text-sm">
        <dt class="font-mono text-foreground-second">Last call</dt>
        <dd class="text-right font-mono tabular-nums">{last?.call ?? "none"}</dd>
      </div>
      <div class="flex justify-between gap-4 px-4 py-3 text-sm">
        <dt class="font-mono text-foreground-second">Answered in</dt>
        <dd class="text-right font-mono tabular-nums">{took(last)}</dd>
      </div>
      <div class="flex justify-between gap-4 px-4 py-3 text-sm">
        <dt class="font-mono text-foreground-second">Stored in</dt>
        <dd class="text-right font-mono tabular-nums">todos table</dd>
      </div>
    </dl>
  </header>
  <div class="border border-border bg-background shadow-[0_24px_60px_-32px_rgb(0_0_0/0.25)]">
    <form class="flex gap-2 border-b border-border p-4" onsubmit={add}>
      <input class="min-h-12 min-w-0 flex-1 border border-border-second bg-background px-4 text-base text-foreground placeholder:text-foreground-second focus:border-foreground focus:outline-none" name="title" placeholder="What needs to be done?" aria-label="New task" maxlength="200" autocomplete="off" />
      <button class="min-h-12 whitespace-nowrap border border-foreground bg-foreground px-6 font-mono text-[0.8rem] font-semibold uppercase tracking-[0.05em] text-background transition-opacity hover:opacity-85 disabled:cursor-progress disabled:opacity-50" type="submit" disabled={pending}>Add</button>
    </form>
    <p class="px-4 pt-3 text-sm text-foreground empty:hidden" aria-live="polite">{note}</p>
    <div class="flex flex-wrap items-center justify-between gap-x-4 gap-y-2 border-b border-border px-4 py-2.5">
      <div class="flex gap-1" role="group" aria-label="Show">
        {#each FILTERS as option (option.key)}
          <button type="button" class="inline-flex min-h-10 items-center gap-2 border border-transparent px-3 text-[0.9rem] text-foreground-second hover:text-foreground aria-pressed:border-border-second aria-pressed:text-foreground" aria-pressed={filter === option.key} onclick={() => (filter = option.key)}>
            {option.label} <span class="font-mono text-xs text-foreground-second">{count(items, option.key)}</span>
          </button>
        {/each}
      </div>
      <button type="button" class="min-h-10 px-2 text-[0.9rem] text-foreground-second underline underline-offset-4 hover:text-foreground disabled:hidden" disabled={count(items, "done") === 0} onclick={() => run(server.clear())}>Clear done</button>
    </div>
    <ul class="divide-y divide-border" aria-label="Tasks">
      {#each visible as todo (todo.id)}
        <li class="flex min-h-14 items-center gap-3.5 py-1.5 pl-4 pr-2.5">
          <input type="checkbox" class="grid h-[1.4rem] w-[1.4rem] flex-none cursor-pointer appearance-none place-content-center border-[1.5px] border-border-second bg-background transition-colors hover:border-foreground checked:border-signal checked:bg-signal after:-mt-0.5 after:h-[0.8rem] after:w-[0.45rem] after:rotate-45 after:scale-0 after:border-b-2 after:border-r-2 after:border-background after:content-[''] after:transition-transform checked:after:scale-100" checked={todo.done} aria-label={`Done: ${todo.title}`} onchange={() => run(server.toggle(todo.id))} />
          {#if editing === todo.id}
            <input bind:value={draft} use:focus class="min-h-10 min-w-0 flex-1 border border-foreground bg-background px-3 text-foreground focus:outline-none" aria-label="Rename the task" onkeydown={(event) => key(event, todo)} onblur={() => save(todo)} />
          {:else}
            <span class={todo.done ? "min-w-0 flex-1 cursor-text leading-snug [overflow-wrap:anywhere] text-foreground-second line-through decoration-border-second" : "min-w-0 flex-1 cursor-text leading-snug [overflow-wrap:anywhere]"} role="presentation" ondblclick={() => edit(todo)}>{todo.title}</span>
          {/if}
          <div class="flex flex-none gap-0.5">
            <button type="button" class="grid h-10 w-10 place-items-center text-foreground-second transition-colors hover:bg-background-second hover:text-foreground" aria-label="Rename" onclick={() => edit(todo)}><svg viewBox="0 0 16 16" width="16" height="16" fill="none" stroke="currentColor" aria-hidden="true"><path d="M10.5 2.5l3 3L6 13H3v-3z" /></svg></button>
            <button type="button" class="grid h-10 w-10 place-items-center text-foreground-second transition-colors hover:bg-background-second hover:text-foreground" data-danger aria-label="Delete" onclick={() => run(server.remove(todo.id))}><svg viewBox="0 0 16 16" width="16" height="16" fill="none" stroke="currentColor" aria-hidden="true"><path d="M4 4l8 8M12 4l-8 8" /></svg></button>
          </div>
        </li>
      {/each}
    </ul>
    {#if visible.length === 0}
      <p class="px-6 py-12 text-center text-foreground-second">{last ? EMPTY[filter] : LOADING}</p>
    {/if}
    <footer class="flex justify-between gap-4 border-t border-border px-4 py-3 font-mono text-xs uppercase tracking-[0.04em] text-foreground-second">
      <span>{count(items, "todo")} left</span>
      <span>{items.length} on the server</span>
    </footer>
  </div>
</section>
