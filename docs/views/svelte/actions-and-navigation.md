# Svelte: actions and navigation

What Nexy gives a Svelte component: call a Python function, link pages, read and change the URL. The
same modules serve pages (client mode) and islands (server mode). Where React has hooks, Svelte has
stores: read them with `$`.

| Import | From |
|---|---|
| `useAction`, `ActionError`, the stores, `router`, `useMatch`, `useBlocker` | `@nexy/client` |
| `Link` | `@nexy/Link.svelte` |
| `Image` | `@nexy/Image.svelte` |

## Actions

An action is a Python function marked `@Action`. Nexy writes a typed client for it in
`@nexy/actions`, and `useAction` tracks one call as a store:

```python filename="src/actions/todos.py"
from pydantic import BaseModel

from nexy.decorators import Action, revalidate


class Todo(BaseModel):
    title: str


@Action
async def add_todo(title: str) -> Todo:
    revalidate()
    return Todo(title=title)
```

```svelte filename="src/components/AddTodo.svelte"
<script lang="ts">
  import { ActionError, useAction } from "@nexy/client";
  import { add_todo } from "@nexy/actions";

  let title = $state("");
  const save = useAction(add_todo, { onSuccess: () => (title = "") });

  function submit(event: SubmitEvent) {
    event.preventDefault();
    save.run({ title });
  }
</script>

<form onsubmit={submit}>
  <input bind:value={title} />
  <button disabled={$save.pending}>Add</button>
  {#if $save.error}
    <p role="alert">
      {$save.error instanceof ActionError ? $save.error.fields.title ?? $save.error.message : "Network error"}
    </p>
  {/if}
  {#if $save.data}<p>Added {$save.data.title}</p>{/if}
</form>
```

| Field | Meaning |
|---|---|
| `save.run(input)` | Calls the action. It never throws: a failure lands in `error`, and `run` resolves with `undefined`. |
| `$save.pending` | `true` while the call runs. |
| `$save.data` | The result of the last successful call. |
| `$save.error` | An `ActionError` when the server answered an error: `status`, `detail`, and `fields` (field name to message) for a `422`. A plain `Error` when the request never arrived. |
| `save.reset()` | Back to the initial state; a call still running no longer updates it. |

Only the latest call updates the state. Without the store an action is an `async` function:
`await add_todo({ title: "Milk" })`, which throws on failure.

`revalidate()` in the action asks the browser to refresh the open page: the client router re-renders
it in client mode, the browser reloads it in server mode. See [Actions](../../guides/actions.md) for
forms without JavaScript, types and security.

## Link

```svelte
<script lang="ts">
  import Link from "@nexy/Link.svelte";
</script>

<Link href="/todos" activeClass="active">Todos</Link>
```

| Prop | Meaning |
|---|---|
| `href` | A route of the project; a typo is a type error. A `?query`, a `#fragment` or an external URL also work. |
| `replace` | Replace the history entry instead of adding one. |
| `scroll` | `false` keeps the scroll position. |
| `prefetch` | `'intent'` (default) on hover, focus or touch; `'viewport'` when visible; `false` never. |
| `activeClass` | Added while the link points at the current page or a page below it. `activeClassName` is the same. |
| `exact` | Active only on the exact page. |

The content is the `children` snippet. The current link also gets `aria-current="page"`, and every
other attribute and handler reaches the `<a>`. In client mode a plain `<a href="/todos">` navigates
on the client too; `Link` adds the checked `href`, the prefetch and the active class.

## Image

```svelte
<script lang="ts">
  import Image from "@nexy/Image.svelte";
</script>

<Image src="/hero.jpg" alt="The team" width={1200} height={600} priority />
```

Lazy by default, no layout shift when `width` and `height` are set, `priority` for the image visible
on arrival, `fill` to cover a positioned parent. `alt` is required (`alt=""` for decoration).

## Read the URL

| Store | Holds |
|---|---|
| `pathname` | `"/todos/42"` |
| `params` | the dynamic segments, `{ id: "42" }` |
| `searchParams` | a `URLSearchParams` |
| `location` | `{ pathname, search, hash, params }` |
| `useMatch(path?)` | a store `{ match, found }`: which route answers `path`, the current one by default |

```svelte
<script lang="ts">
  import { searchParams } from "@nexy/client";
</script>

<p>Filter: {$searchParams.get("filter") ?? "all"}</p>
```

On the server the stores hold the URL of the request. They follow the client router, so in an island
pass the values from the page as props instead.

## Change the URL

```ts
import { router } from "@nexy/client";

router.push("/todos?filter=done", { scroll: false });
```

`push`, `replace`, `back`, `forward`, `refresh` and `prefetch(href)`. `router` is a plain object,
not a store: no `$`.

### Keep the visitor on a page

```svelte
<script lang="ts">
  import { onDestroy } from "svelte";
  import { useBlocker } from "@nexy/client";

  let dirty = $state(false);
  onDestroy(useBlocker(() => (dirty && !window.confirm("Leave without saving?") ? "unsaved" : undefined)));
</script>
```

`useBlocker` returns the function that removes the blocker: hand it to `onDestroy`. A blocker runs
before every client navigation. Returning a string, or a promise of one, cancels it; anything else
lets it through. Nexy asks nothing itself, so the blocker shows the question. It does not stop a
reload or a link to another site.

## Next steps

- [Actions](../../guides/actions.md): forms, types, errors, security
- [Linking and navigating](../../routing/fbr/navigation/linking-and-navigating.md): what the router does
- [Testing](../../guides/testing.md): test actions with pytest
