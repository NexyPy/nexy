# With sitemap: sitemap.xml and robots.txt from useSiteUrl

Crumb is a made-up bakery with three pages, a page per bake and a JSON route. One line in
`nexyconfig.py` gives it a `/sitemap.xml` and a `/robots.txt`:

```python filename="nexyconfig.py"
useSiteUrl = "https://crumb.example"
```

Without `useSiteUrl` neither address exists, so the address of a dev server is never published by
mistake.

## What the sitemap lists

| File | Address | In the sitemap |
|---|---|---|
| `src/routes/index.nexy` | `/` | yes |
| `src/routes/menu/index.nexy` | `/menu` | yes |
| `src/routes/visit.nexy` | `/visit` | yes |
| `src/routes/menu/[slug].nexy` | `/menu/rye` | no: Nexy cannot know the values of `[slug]` |
| `src/routes/api/hours.py` | `/api/hours` | no: it answers JSON, not a page |
| `src/routes/notfound.nexy` | any other address | no |

To list the page of each bake too, write your own: a `public/sitemap.xml`, or a route at
`/sitemap.xml`, always wins over the one Nexy writes. [The sitemap guide](../../docs/guides/sitemap.md)
has the details.

## Run it

You need Python 3.12 or newer, [uv](https://docs.astral.sh/uv/), and Node.js with npm, pnpm or
bun.

```bash
git clone https://github.com/NexyPy/nexy
cd nexy/examples/with-sitemap
uv sync
npm install          # or pnpm install, bun install
uv run nexy dev
```

## Test it

```bash
uv run pytest
```

The tests read `/sitemap.xml` and check it lists exactly the three static pages, that `/robots.txt`
points to it, and that a dynamic page answers without being listed.
