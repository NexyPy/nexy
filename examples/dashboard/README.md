# Dashboard: a React dashboard routed in the browser, with shadcn/ui

Kiln Coffee is the sales dashboard of a small coffee roaster: revenue, orders, channels and best
sellers. It is a React application with the components of [shadcn/ui](https://ui.shadcn.com): the
sidebar, the cards, the chart, the tables and the filters. After the first page, moving between pages
never asks the server for HTML: the client router of Nexy renders the next page in the browser, and
the numbers come from Nexy actions, Python functions the pages call like TypeScript ones.

![The overview of the dashboard, a day of the chart under the pointer](../../docs/assets/examples/dashboard.png)

## What it shows

| Nexy feature | Where |
|---|---|
| Client mode: React pages, a client router, one document rendered on the server | `nexyconfig.py`, `src/routes/layout.tsx` |
| `Link`, `usePathname`, `useSearchParams` and `useRouter` from `@nexy/client` | `src/components/app-sidebar.tsx`, `src/components/filters.tsx` |
| Filters kept in the URL: a reload, a shared link and the back button keep them | `src/lib/query.ts` |
| Actions called from React, with their TypeScript types | `src/actions/dashboard.py`, `src/routes/*.tsx` |
| shadcn/ui as the CLI installs it: `components.json`, Radix, Tailwind v4 | `components.json`, `src/components/ui/` |
| A shadcn chart (Recharts) fed by an action | `src/components/revenue-chart.tsx` |
| SQLModel tables and Alembic migrations, with `nexy migrate` | `src/models/`, `alembic/versions/` |
| Tests of every action over HTTP, hostile values included | `tests/` |

The same orders, read by server pages written with the modular router, are in
[`examples/sales-report`](../sales-report).

## Run it

You need Python 3.12 or newer, [uv](https://docs.astral.sh/uv/), and Node.js with npm, pnpm or
bun.

```bash
git clone https://github.com/NexyPy/nexy
cd nexy/examples/dashboard
cp .env.example .env
uv sync
npm install                     # or pnpm install, bun install
uv run nexy migrate --upgrade   # creates the table and records four months of orders
uv run nexy dev
```

Open the address `nexy dev` prints.

## How a page gets its numbers

The overview reads `?days=7&channel=Cafe` from the URL with `useSearchParams`, and calls the
`overview` action with them. A click on a filter does not change any state of its own: it pushes a
new URL, the page reads it again and calls the action again. While the answer comes, the last
numbers stay on the page, dimmed. That is why the back button gives the filters before a change,
and why a link to `/orders?channel=Wholesale` opens on the wholesale orders.

The actions take the period and the page as text, the way the URL holds them, and keep only the
values the page offers: `?days=²` or a page number 5000 digits long gives the default, not an error.

The data set is written by the second migration from a seeded generator: 2750 orders over the 120
days that end on November 15, 2026, so every copy of the example shows the same numbers. The
dashboard ends its periods on the last day with an order, so it still has data to show in a year.

## Add a shadcn/ui component

`components.json` is the one shadcn writes for a Vite project, so the CLI works as it does
anywhere else:

```bash
npx shadcn@latest add dialog    # writes src/components/ui/dialog.tsx
```

## Test it

```bash
uv run pytest
```

The tests run the migrations once, give each test a fresh copy of that database, and call the
actions over HTTP the way the pages do.

## Files

```text
alembic/versions/           the table, then four months of orders
src/
  models/order_model.py     the orders table
  services/                 the period of a page, the sums, a page of orders
  actions/dashboard.py      what the pages call: overview, products, orders
  lib/                      number formats, the query of the URL, loading an action
  components/ui/            the components of shadcn/ui, as the CLI wrote them
  components/               the sidebar, the header, the filters, the cards, the chart
  routes/layout.tsx         the document around every page: sidebar and header
  routes/index.tsx          the overview
  routes/orders.tsx         the orders, 20 to a page
  routes/products.tsx       every product of the period
  globale.css               the theme of shadcn/ui, with the clay of Kiln Coffee
tests/                      the services and the actions, on a migrated database
```
