# Layouts

A layout wraps every page below its directory. Layouts nest: the page renders inside the layout of
its directory, which renders inside the layout of the parent directory, up to the root layout.

There is one page per layout file type:

| File | Mode | Owns the HTML document | Page |
|---|---|---|---|
| `layout.nexy` | server (`useCSR = False`) | yes, at the root | [layout.nexy](../../../views/nexy/layouts.md) |
| `layout.tsx` | client (`useCSR = True`) | yes, at the root (React, Solid, Preact) | [layout.tsx](layout.tsx.md) |
| `layout.vue` | client | yes, at the root | [layout.vue](layout.vue.md) |
| `layout.svelte` | client | yes, at the root | [layout.svelte](layout.svelte.md) |

A project uses one family. `layout.nexy` and `layout.tsx` cannot live in the same project: server
mode has `.nexy` layouts and client mode has framework layouts. See
[Server mode and client mode](../modes.md).

## How the browser takes over the document

In client mode Nexy renders the root layout in Node, so the first response is a complete document. The
browser then takes it over in one of two ways:

| Framework | Takeover | What it means |
|---|---|---|
| React, Solid | **hydration** of the whole document | the server HTML is reused as it is |
| Preact, Vue, Svelte | **body takeover** | the framework builds the page body and swaps it in for the one the server sent |

Preact, Vue and Svelte cannot hydrate a whole document: Preact's `hydrate` builds a second `<html>`
element, Vue's compiler drops a `<script>` from a client template, and Svelte cannot create `<html>`,
`<head>` or `<body>` in the browser. So for them `<html>`, `<head>` and the `<body>` attributes are
the ones the server sent, and only the body is built by the browser. In practice:

- Put the title, meta tags, fonts and theme script in the root layout: they are rendered by the server
  and stay as they are.
- A binding on `<html>`, `<head>` or `<body>` (for example a reactive class) is applied by the server
  but does not update in the browser. Change them from a script, as the theme script does.
- The browser renders the body from scratch instead of reusing the server markup, so the body is
  replaced once, in the same task as the first render.

## The root layout

The root layout is `src/routes/layout.<ext>`. It is created by `nx new` and it is the only place that
writes `<!DOCTYPE html>`, `<html>`, `<head>` and `<body>` (every framework and `.nexy`). Pages and nested
layouts never repeat them.

```text
src/routes/
├─ layout.*              root: the document
├─ index.*
└─ dashboard/
   ├─ layout.*           nested: UI only
   ├─ index.*
   └─ settings.*
```

`dashboard/index` renders as `root layout > dashboard layout > page`.

## Route groups

A directory in parentheses can have its own layout without changing URLs:

```text
src/routes/
├─ layout.nexy
├─ (marketing)/
│  ├─ layout.nexy        wraps /pricing and /about only
│  ├─ pricing.nexy
│  └─ about.nexy
└─ (app)/
   └─ dashboard.nexy     only the root layout
```

## Persistence

In client mode a layout stays mounted while the user navigates between the pages that share it: its
DOM, state and scroll position are kept. In server mode every navigation is a new document.

## Next steps

- [layout.nexy](../../../views/nexy/layouts.md)
- [layout.tsx](layout.tsx.md)
- [Inheritance](../inheritance.md)
