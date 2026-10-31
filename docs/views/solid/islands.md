# Solid islands

In server mode (the default) pages are `.nexy` files, and a Solid component imported in one is an
**island**: Nexy renders its HTML on the server, and Solid takes over only that component in the
browser. The rest of the page stays plain HTML with no JavaScript.

## Import a component

```tsx filename="src/components/Counter.tsx"
import { createSignal } from "solid-js";

export default function Counter(props: { start?: number }) {
  const [count, setCount] = createSignal(props.start ?? 0);
  return <button onClick={() => setCount(count() + 1)}>{count()}</button>;
}
```

```nexy filename="src/routes/index.nexy"
---
from "@/components/Counter.tsx" import Counter
---
<h1>Static heading</h1>
<Counter start=3 />
```

The import goes in the frontmatter, with the extension. The tag takes the name you imported and is
self-closing. With `useFF = solid()`, a `.tsx` or `.jsx` file is a Solid component.

| Import | Picks |
|---|---|
| `from "@/components/Counter.tsx" import Counter` | the default export, else the export named `Counter` |
| `import "@/components/Counter.tsx" as Counter` | the default export |
| `from "@/components/ui.tsx" import Button, Card` | `Button` and `Card`, when `ui.tsx` has no default export |
| `from "@/components/ui.tsx" import Button as UIButton` | a component under another name |

> [!WARNING]
> In Solid the **default export wins**: when a file has one, every name imported from it is the
> default component. Give each island its own file with a default export, or a file with named
> exports only.

`@` is the alias of `useAliases = {"@": "src"}`; a relative path from the page works too.

## Props

The attributes of the tag are the props, with the rules of the tag form: `start=3` is a number,
`open=True` a boolean, `label="Save"` a string, and `user="{{ user }}"` passes the Python value of
`user` from the frontmatter.

```nexy filename="src/routes/users/[id].nexy"
---
from "@/components/UserCard.tsx" import UserCard

id: prop[int]
user = {"id": id, "name": "Ada"}
---
<UserCard user="{{ user }}" editable=True />
```

```tsx filename="src/components/UserCard.tsx"
type User = { id: number; name: string };

export default function UserCard(props: { user: User; editable: boolean }) {
  return <h2 contentEditable={props.editable}>{props.user.name}</h2>;
}
```

The props travel as JSON inside the page, HTML-escaped so a string with quotes or tags cannot break
out. Pass plain data: strings, numbers, booleans, `None`, lists and dicts. Turn a Pydantic model into
a dict first with `user.model_dump()`.

> [!WARNING]
> if one value cannot be turned into JSON (a model, a date, a function), the component receives
> **no props at all**, not only that one.

## When it takes over

The server HTML shows first. Solid then renders the island again in the browser and puts it in place
of that HTML, so state set before (a focused input, a typed value) starts over. The `directive` prop
chooses when. Nexy keeps it and `media` for itself: they never reach the component.

| Directive | Takes over |
|---|---|
| none, or `client:load` | immediately |
| `client:idle` | when the browser is idle |
| `client:visible` | when the island scrolls into view |
| `client:media` | when the `media` query matches |
| `client:manual` | when your code asks |

```nexy
<Chart directive="client:visible" />
<Sidebar directive="client:media" media="(min-width: 768px)" />
```

The server renders the island in Node: code that reads `window` or `document` goes in `onMount`.

## What an island can use

- [Actions](actions-and-navigation.md#actions): `useAction` works the same in an island.
- `Link` and `Image` from `@nexy/client` render; without the client router a `Link` loads the page
  normally.
- The location hooks (`usePathname`, `useParams`...) follow the client router, which only runs in
  client mode. In an island, read the request in the page and pass it down:

```nexy filename="src/routes/index.nexy"
---
from nexy import usePathname
from "@/components/Nav.tsx" import Nav

pathname = usePathname()
---
<Nav path="{{ pathname }}" />
```

## Next steps

- [Islands and hydration](../../rendering/islands.md): directives for every framework
- [.nexy files](../nexy/README.md): frontmatter, props, Jinja2
- [Components](../nexy/components.md): `Import`, `Image`, `Link` on the server
- [Pages](pages.md): when the whole page should be Solid
