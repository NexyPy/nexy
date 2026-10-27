---
name: nexy-file
description: How to write a .nexy file - frontmatter, props, Jinja2 template, components, slots, islands, styles, hooks and ISR. Load it for any .nexy page, layout or component in a server-mode project.
---

# `.nexy` files

A `.nexy` file is a component: Python on top, HTML in the middle, CSS at the bottom.

```nexy
---
from "@/components/card.nexy" import Card
from nexy import usePathname

title: prop[str] = "Untitled"
pathname = usePathname()
---
<Card title="{{ title }}">
  <p>You are on {{ pathname }}</p>
</Card>

<style>
  p { max-width: 60ch; }
</style>
```

## Frontmatter

Everything between the two `---` lines is Python. Imports resolve at compile time. The rest runs on
every request.

- `name: prop[type] = default` declares a property. No default means the parent must pass it.
- Declare every property you use: an undeclared variable renders as an empty string.
- `revalidate = 60` caches the page with stale-while-revalidate (ISR).
- Keep side effects inside functions. No file handle, connection or network call at the top level.

## Template

HTML with Jinja2: `{{ value }}`, `{% for %}`, `{% if %}`.

- Autoescaping is **off**. Escape untrusted values with `{{ value | e }}`. `| safe` changes nothing.
- Wrap JavaScript that contains `{{` or `{%` in `{% raw %}...{% endraw %}`.

## Components

An imported name that starts with an uppercase letter is a tag. Attributes become keyword
arguments. Children go through `<slot />` in the child and `{{ children }}` in a layout.

A built-in helper tag (`Link`, `Image`, `Audio`, `Video`, `Import`) is always self-closing; content
goes through its `children` argument.

One component per file, and the file name is the component name.

## Hooks

Hooks read the current request and only work while one is handled.

| Hook | Returns |
|---|---|
| `usePathname()` | request path |
| `useSearchParams()` | query string, first value per key |
| `useQuery()` | dynamic path parameters |
| `useCookies()` | cookies |
| `useSession()` | the session dict; needs `useSession` in config |
| `useToc()` | table of contents HTML of the page |

## Islands

A client component imported in a `.nexy` page is an island: the server renders it, the browser
makes it interactive. `directive` says when.

```nexy
<Counter directive="client:visible" />
```

Use the default for content above the fold, `client:visible` below it, `client:idle` for
non-essential widgets, `client:media` for desktop-only, `client:only` for code that reads `window`
while rendering. `directive` and `media` are consumed by Nexy and not passed as props.

## Styles

`<style>` is emitted with the page and is **not scoped**. Prefix class names. In a project that uses
Tailwind or UnoCSS, write utility classes in the template and keep `<style>` for what utilities
cannot express (see [nexy-styling](../nexy-styling/SKILL.md)).

## Layout

`layout.nexy` is the root of the document in server mode:

```nexy
---
children: prop[NexyElement]
---
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>My app</title>
</head>
<body>
  {{ children | safe }}
</body>
</html>
```

For the experience of the page, run [nexy-ux-audit](../nexy-ux-audit/SKILL.md) first.
