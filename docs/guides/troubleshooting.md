# Troubleshooting

The problems people hit first, with what you see and what to do. Each one comes from a real run.

## A page answers 404 but its file exists

Look at the terminal that runs `nx dev` or `nx start`. When a page cannot be imported, Nexy reports
the error with its file and line, and the route is not registered:

```text
nexy » error __nexy__/src/routes/index.py:18  ImportError: cannot import name 'FrameworkLogo' ...
```

Fix the import named there. The usual causes are a component whose function name does not match
what you import (see the next item) and a typo in the path.

## A `.nexy` page does not compile: "Logic Parse Error"

```text
src/components/live-panel.nexy - Logic Parse Error: invalid syntax
```

A `.nexy` component is imported as a Python module, so its file name must be a valid name. A hyphen
is not. Name it in PascalCase, `LivePanel.nexy`, and import it with the same name:

```nexy
from "@/components/LivePanel.nexy" import LivePanel
```

## A component renders its children as the text `<slot />`

A `.nexy` component places its children with `<Slot />`, with a capital S. A lowercase `<slot />` is
left in the page as it is. Vue, which has its own `<slot />`, is not affected.

## A prop shows the name of the variable

```nexy
<Icon path=icon />          renders: icon
<Icon path="{{ icon }}" />  renders: the value of icon
```

An attribute with no braces is text. Put the Jinja expression in the attribute to pass a computed
value.

## A value in `{{ ... }}` renders empty

Jinja2 hides an undefined variable. Declare every property you use in the frontmatter
(`title: prop[str] = ""`), and check the spelling.

## Utility classes have no effect in a `.nexy` page (UnoCSS)

UnoCSS reads a file only when its extension is in its content pipeline. A server project created
by `nx new` with UnoCSS already lists `.nexy`; an older one needs it in `uno.config.ts`:

```ts
content: {
  filesystem: ['src/**/*.nexy'],
  pipeline: { include: [/\.(vue|svelte|[jt]sx|mdx?|astro|html|nexy)($|\?)/] },
},
```

Tailwind finds `.nexy` files on its own.

## An `.mdx` page asks for packages

```text
[nexy] MDX support requires optional packages that are not installed.
```

Install them in the project: `@mdx-js/rollup`, `remark-gfm` and `@mdx-js/react` (plus
`@mdx-js/esbuild` for `nx build`). MDX needs React or Preact in `useFF`. Without a client framework,
write the page as `.md`. See [Markdown and MDX](../views/markdown.md).

## `No module named 'sqlmodel'` (or any package) when a command starts

```text
nexy » nexyconfig.py cannot be loaded: No module named 'sqlmodel'. If it is a package, install it
in this Python (...) or activate the project's virtual environment.
```

The command ran in the wrong Python. The packages of your project (your ORM, your libraries) are in
its `.venv`, and `uvx nexy` or a global `nexy` runs in an environment of its own that has none of
them.

Activate the project's virtual environment, from the project folder, then run the command again:

```bash
.venv\Scripts\activate    # Windows; on macOS and Linux: source .venv/bin/activate
nexy dev
```

The prompt starts with `(.venv)` when it is active. Or skip the activation with
`uv run nexy dev`. If the package is really missing from the project, add it with `uv add sqlmodel`.

## `nx dev` shows an error and waits

When your application cannot start, `nx dev` reports why and waits for the next file change; it does
not exit. Fix the file and save. Only Ctrl+C stops it.

## The port is busy

`nx dev` takes the next free port and prints it. To choose one, use `--port` or set `usePort` in
`nexyconfig.py`.

## The theme flashes white on a dark page

The saved theme must be applied before the first paint. Keep the small script of the starter in the
`<head>` of the root layout, and put `suppressHydrationWarning` on `<html>` in React.

## Still stuck

- Read the page of the feature in [the documentation index](../README.md).
- If the docs and the code disagree, the code is right: please open an
  [issue](https://github.com/NexyPy/nexy/issues) naming the page.
