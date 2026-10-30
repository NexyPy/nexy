# Svelte islands

In server mode (the default) pages are `.nexy` files, and a Svelte component imported in one is an
**island**: Nexy renders its HTML on the server, and Svelte takes over only that component in the
browser. The rest of the page stays plain HTML with no JavaScript.

## Import a component

```svelte filename="src/components/Counter.svelte"
<script lang="ts">
  let { start = 0 }: { start?: number } = $props();
  let count = $state(start);
</script>

<button onclick={() => count++}>{count}</button>
```

```nexy filename="src/routes/index.nexy"
---
from "@/components/Counter.svelte" import Counter
---
<h1>Static heading</h1>
<Counter start=3 />
```

The import goes in the frontmatter, with the extension. The tag takes the name you imported and is
self-closing. `import "@/components/Counter.svelte" as Counter` does the same. `@` is the alias of
`useAliases = {"@": "src"}`; a relative path from the page works too.

> [!NOTE]
> the Svelte markup lives in the `.svelte` file. In the `.nexy` page `{{ }}` is Jinja2, run on the
> server; a `.nexy` page that needs a literal `{{` wraps it in `{% raw %}...{% endraw %}`.

## Props

The attributes of the tag are the props, with the rules of the tag form: `start=3` is a number,
`open=True` a boolean, `label="Save"` a string, and `user="{{ user }}"` passes the Python value of
`user` from the frontmatter.

```nexy filename="src/routes/users/[id].nexy"
---
from "@/components/UserCard.svelte" import UserCard

id: prop[int]
user = {"id": id, "name": "Ada"}
---
<UserCard user="{{ user }}" editable=True />
```

```svelte filename="src/components/UserCard.svelte"
<script lang="ts">
  let { user, editable }: { user: { id: number; name: string }; editable: boolean } = $props();
</script>

<h2 contenteditable={editable}>{user.name}</h2>
```

The props travel as JSON inside the page, HTML-escaped so a string with quotes or tags cannot break
out. Pass plain data: strings, numbers, booleans, `None`, lists and dicts. Turn a Pydantic model into
a dict first with `user.model_dump()`.

> [!WARNING]
> if one value cannot be turned into JSON (a model, a date, a function), the component receives
> **no props at all**, not only that one.

## When it hydrates

The `directive` prop chooses when Svelte takes over. Nexy keeps it and `media` for itself: they
never reach the component.

| Directive | Hydrates |
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
- `Link` (`@nexy/Link.svelte`) and `Image` (`@nexy/Image.svelte`) render; without the client router a
  `Link` loads the page normally.
- The location stores (`$pathname`, `$params`...) follow the client router, which only runs in
  client mode. In an island, read the request in the page and pass it down:

```nexy filename="src/routes/index.nexy"
---
from nexy import usePathname
from "@/components/Nav.svelte" import Nav

pathname = usePathname()
---
<Nav path="{{ pathname }}" />
```

## Next steps

- [Islands and hydration](../../rendering/islands.md): directives for every framework
- [.nexy files](../nexy/README.md): frontmatter, props, Jinja2
- [Components](../nexy/components.md): `Import`, `Image`, `Link` on the server
- [Pages](pages.md): when the whole page should be Svelte
