# Nexy examples

Four apps you can run, read and copy. Each one is a project of its own, with its README, its
tests and a screenshot; each shows a different part of Nexy.

| Example | What it is | Client components | Data |
|---|---|---|---|
| [todos](todos/) | A todo list: add, tick, rename, filter, clear | React, calling server actions | SQLite (SQLModel) |
| [blog](blog/) | Markdown posts, tags, a table of contents, RSS | None: every page is server HTML | Markdown files |
| [dashboard](dashboard/) | Invoices behind a sign-in: totals, search, pages, a chart | A Vue chart in a server page | SQLite (SQLModel) |
| [store](store/) | A shop: catalog, a cart in a cookie, checkout, orders | Svelte islands | SQLite (SQLModel) |

## Run one

```bash
git clone https://github.com/NexyPy/nexy && cd nexy/examples/blog
uv sync
bun install          # or npm install, pnpm install
uv run nx dev
```

The README of each example says what else it needs (a `.env` for the session secret of the
dashboard and the store) and how to run its tests.

## Start your own

`nexy new my-app` writes a starter project with the router, client framework, style and database
you choose. These examples began as such starters: compare one with a fresh starter to see what
was added.

## The tests of the examples

`tests/unit/examples/test_example_suites.py` in the repository runs the tests of every example with
the Nexy of the branch, so a change to Nexy that breaks one of them fails in CI.
