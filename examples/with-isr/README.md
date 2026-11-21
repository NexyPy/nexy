# With ISR: a page rendered once, then served from memory

A departures board in two pages. `/` has `revalidate = 30`: the server renders it once, keeps the
HTML in memory, and sends that copy for 30 seconds. After that, a visit still gets the old copy at
once while a new one is rendered behind it (stale-while-revalidate). `/live` is the same board with
no `revalidate`, rendered on every visit. Each page prints its render number and time, so a reload
shows the difference.

```nexy filename="src/routes/index.nexy"
---
revalidate = 30
---
```

That line is the whole feature. [ISR in the docs](../../docs/rendering/isr.md) has the details.

## Run it

You need Python 3.12 or newer, [uv](https://docs.astral.sh/uv/), and Node.js with npm, pnpm or
bun.

```bash
git clone https://github.com/NexyPy/nexy
cd nexy/examples/with-isr
uv sync
npm install          # or pnpm install, bun install
uv run nexy dev
```

Open `/` and reload: the render number stays the same for 30 seconds. Open `/live` and reload: it
goes up each time.

## What to know before using it

- The copy is kept per path: `/?a=1` and `/?a=2` get the same one. Do not cache a page that reads
  the query string or the session.
- The cache lives in the memory of each server process. `nx start` runs one process per CPU on
  Linux and macOS, each with its own copy; this sample sets `useWorkers = 1` in `nexyconfig.py` so
  a reload always shows the same one.
- Nothing removes a copy before its 30 seconds are over.

The [portfolio example](../portfolio) uses `revalidate` on its case study pages.

## Test it

```bash
uv run pytest
```

The tests check the `cache-control` header, that a second visit is not rendered again, that `/live`
is, and, by moving the clock forward instead of waiting, that an old copy is sent at once and
replaced behind it.
