# Solid: actions and navigation

What `@nexy/client` gives a Solid component: call a Python function, link pages, read and change the
URL. The same module serves pages (client mode) and islands (server mode). Where React returns a
value, Solid returns an **accessor**: call it, `pending()`, inside the JSX.

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
import { createSignal, Show } from "solid-js";
import { ActionError, useAction } from "@nexy/client";
import { add_todo } from "@nexy/actions";

export default function AddTodo() {
  const [title, setTitle] = createSignal("");
  const save = useAction(add_todo, { onSuccess: () => setTitle("") });
  const message = () => {
    const error = save.error();
    if (!error) return undefined;
    return error instanceof ActionError ? error.fields.title ?? error.message : "Network error";
  };

  return (
    <form onSubmit={(event) => { event.preventDefault(); save.run({ title: title() }); }}>
      <input value={title()} onInput={(event) => setTitle(event.currentTarget.value)} />
      <button disabled={save.pending()}>Add</button>
      <Show when={message()}>
        <p role="alert">{message()}</p>
      </Show>
      <Show when={save.data()}>{(todo) => <p>Added {todo().title}</p>}</Show>
    </form>
  );
}
```

`message` is a function, so it is computed again each time `save.error()` changes.

| Field | Meaning |
|---|---|
| `run(input)` | Calls the action. It never throws: a failure lands in `error()`, and `run` resolves with `undefined`. |
| `pending()` | `true` while the call runs. |
| `data()` | The result of the last successful call. |
| `error()` | An `ActionError` when the server answered an error: `status`, `detail`, and `fields` (field name to message) for a `422`. A plain `Error` when the request never arrived. |
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
| `activeClassName` | Added to `class` while the link points at the current page or a page below it. |
| `exact` | Active only on the exact page. |

The current link also gets `aria-current="page"`. Every other prop reaches the `<a>`, and `ref`
receives it. In client mode a plain `<a href="/todos">` navigates on the client too; `Link` adds the
checked `href`, the prefetch and the active state.

## Image

```tsx
import { Image } from "@nexy/client";

<Image src="/hero.jpg" alt="The team" width={1200} height={600} priority />
```

Lazy by default, no layout shift when `width` and `height` are set, `priority` for the image visible
on arrival, `fill` to cover a positioned parent. `alt` is required (`alt=""` for decoration).

## Read the URL

Every hook returns an accessor that follows the client router:

| Hook | Calling it returns |
|---|---|
| `usePathname()` | `"/todos/42"` |
| `useParams<T>()` | the dynamic segments, `{ id: "42" }` |
| `useSearchParams()` | a `URLSearchParams` |
| `useLocation()` | `{ pathname, search, hash, params }` |
| `useMatch(path?)` | `{ match, found }`: which route would answer `path`, the current one without it |

```tsx
const pathname = usePathname();
<p>You are on {pathname()}</p>
```

On the server the hooks answer with the URL of the request, so the page hydrates without a mismatch.
They follow the client router, so in an island pass the values from the page as props instead.

## Change the URL

```tsx
import { useRouter } from "@nexy/client";

const router = useRouter();
router.push("/todos?filter=done", { scroll: false });
```

`push`, `replace`, `back`, `forward`, `refresh` and `prefetch(href)`.

### Keep the visitor on a page

```tsx
import { createSignal } from "solid-js";
import { useBlocker } from "@nexy/client";

const [dirty, setDirty] = createSignal(false);
useBlocker(() => (dirty() && !window.confirm("Leave without saving?") ? "unsaved" : undefined));
```

Call `useBlocker` in the component body: it stops blocking when the component is removed. The
blocker reads `dirty()` each time, so it always sees the current value. It runs before every client
navigation; returning a string, or a promise of one, cancels it, anything else lets it through. Nexy
asks nothing itself, so the blocker shows the question. It does not stop a reload or a link to
another site.

## Next steps

- [Actions](../../guides/actions.md): forms, types, errors, security
- [Linking and navigating](../../routing/fbr/navigation/linking-and-navigating.md): what the router does
- [Testing](../../guides/testing.md): test actions with pytest
