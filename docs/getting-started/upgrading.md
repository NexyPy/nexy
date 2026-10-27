# Upgrading to 2.2

What changes for an existing project when you move from 2.1 to 2.2, and what to do about it. The
full list is in the [changelog](../../CHANGELOG.md).

```bash
uv add "nexy>=2.2"            # or: uv tool upgrade nexy
nx build
nx test
```

## What you may have to change

| Change | Do this |
|---|---|
| **`.mdx` is compiled by Vite only.** The Python compiler no longer renders it | Keep React or Preact in `useFF` and install `@mdx-js/rollup`, `remark-gfm` and `@mdx-js/react`. A page with no components can be a `.md` file instead |
| **`useBadge` is gone.** The "Built with Nexy" tag no longer exists | Delete the line from `nexyconfig.py`. A leftover line is ignored |
| **`nx check` no longer compiles `.mdx`** | Nothing: Vite reports MDX errors at build |

## What stays the same

- Your routes, layouts, actions and configuration.
- Existing projects keep their own starter pages. The new starter design only applies to projects
  created after the upgrade.
- The development toolbar and `useDevTools`.

## New in 2.2

- **Agent files.** `nx new` writes `AGENTS.md`, `CLAUDE.md` and the skills for coding agents. For a
  project you already have, run `nx skills`. It never overwrites a file you wrote. See
  [Coding agents](../guides/ai-agents.md).
- **A dev server that keeps running.** When your application cannot start, `nx dev` reports why and
  waits for the next change instead of exiting.
- **A new starter** for every framework in Tailwind or UnoCSS, with the same pages and components.
- **UnoCSS reads `.nexy` files** in a server project. If you use UnoCSS with `.nexy` pages, add the
  `content` block shown in [Troubleshooting](../guides/troubleshooting.md).

## Corrected documentation

Three pages said something the code does not do. If you followed them, check your files:

- A `.nexy` component places its children with `<Slot />` (capital S), not `<slot />`.
- A `.nexy` component file is named in PascalCase: it is imported as a Python module, so a hyphen
  does not compile.
- For `.mdx`, the framework is Preact when the file imports `preact`, React otherwise.
