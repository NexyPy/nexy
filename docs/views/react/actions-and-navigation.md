# React: actions and navigation

What `@nexy/client` gives a React component: call a Python function, link pages, read and change
the URL. The same module serves pages (client mode) and islands (server mode).

## Actions

An action is a Python function marked `@Action`. Nexy writes a typed client for it in
`@nexy/actions`, and `useAction` tracks one call:

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

```tsx filename="src/components/AddTodo.tsx"
import { useState } from "react";
import { ActionError, useAction } from "@nexy/client";
import { add_todo } from "@nexy/actions";

export default function AddTodo() {
  const [title, setTitle] = useState("");
  const { run, pending, error, data } = useAction(add_todo, {
    onSuccess: () => setTitle(""),
  });

  return (
    <form onSubmit={(event) => { event.preventDefault(); run({ title }); }}>
      <input value={title} onChange={(event) => setTitle(event.target.value)} />
      <button disabled={pending}>Add</button>
      {error && (
        <p role="alert">
          {error instanceof ActionError ? error.fields.title ?? error.message : "Network error"}
        </p>
      )}
      {data && <p>Added {data.title}</p>}
    </form>
  );
}
```

| Field | Meaning |
|---|---|
| `run(input)` | Calls the action. It never throws: a failure lands in `error`, and `run` resolves with `undefined`. |
| `pending` | `true` while the call runs. |
| `data` | The result of the last successful call. |
| `error` | An `ActionError` when the server answered an error: `status`, `detail`, and `fields` (field name to message) for a `422`. A plain `Error` when the request never arrived. |
| `reset()` | Back to the initial state; a call still running no longer updates it. |

Only the latest call updates the state. Without the hook an action is an `async` function:
`await add_todo({ title: "Milk" })`, which throws an `ActionError` on failure.

`revalidate()` in the action asks the browser to refresh the open page: the client router re-renders
it in client mode, the browser reloads it in server mode. See [Actions](../../guides/actions.md) for
forms without JavaScript, types and security.

## Link

```tsx
import { Link } from "@nexy/client";

<Link href="/todos" activeClassName="active">Todos</Link>
```

| Prop | Meaning |
|---|---|
| `href` | A route of the project; a typo is a type error. A `?query`, a `#fragment` or an external URL also work. |
| `replace` | Replace the history entry instead of adding one. |
| `scroll` | `false` keeps the scroll position. |
| `prefetch` | `'intent'` (default) on hover, focus or touch; `'viewport'` when visible; `false` never. |
| `activeClassName` | Added while the link points at the current page or a page below it. |
| `exact` | Active only on the exact page. |

The current link also gets `aria-current="page"`. Every other prop reaches the `<a>`, and a `ref`
is forwarded to it. In client mode a plain `<a href="/todos">` navigates on the client too; `Link`
adds the checked `href`, the prefetch and the active state.

## Image

```tsx
import { Image } from "@nexy/client";

<Image src="/hero.jpg" alt="The team" width={1200} height={600} priority />
```

Lazy by default, no layout shift when `width` and `height` are set, `priority` for the image visible
on arrival, `fill` to cover a positioned parent. `alt` is required (`alt=""` for decoration).

## Read the URL

| Hook | Returns |
|---|---|
| `usePathname()` | `"/todos/42"` |
| `useParams<T>()` | the dynamic segments, `{ id: "42" }` |
| `useSearchParams()` | a `URLSearchParams` |
| `useLocation()` | `{ pathname, search, hash, params }` |
| `useMatch(path)` | `{ match, found }`: which route would answer `path` |

On the server the hooks answer with the URL of the request, so the page hydrates without a mismatch.
They follow the client router, so in an island pass the values from the page as props instead.

## Change the URL

```tsx
import { useRouter } from "@nexy/client";

const router = useRouter();
router.push("/todos?filter=done", { scroll: false });
```

`push`, `replace`, `back`, `forward`, `refresh` and `prefetch(href)`. The object never changes, so
it is safe in a dependency list.

### Show progress

```tsx
import { useTransition } from "@nexy/client";

const { pending, next } = useTransition();
return pending ? <div className="progress">Loading {next?.pathname}</div> : null;
```

`pending` is `true` while the next page renders; `next` is the location it goes to.

### Keep the visitor on a page

```tsx
import { useCallback } from "react";
import { useBlocker } from "@nexy/client";

const block = useCallback(
  () => (dirty && !window.confirm("Leave without saving?") ? "unsaved" : undefined),
  [dirty]
);
useBlocker(block);
```

A blocker runs before every client navigation. Returning a string, or a promise of one, cancels it;
anything else lets it through. Nexy asks nothing itself, so the blocker shows the question. It does
not stop a reload or a link to another site.

## Next steps

- [Actions](../../guides/actions.md): forms, types, errors, security
- [Linking and navigating](../../routing/fbr/navigation/linking-and-navigating.md): what the router does
- [Testing](../../guides/testing.md): test actions with pytest
