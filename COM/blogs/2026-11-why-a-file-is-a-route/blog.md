+++
date = 2026-11-20
title = "Why a route is a file"
description = "One file per route, and the URL is its path. What that buys on a FastAPI and React project, and where the idea stops paying."
tags = ["python", "fastapi", "react", "routing"]
canonical = "https://nexypy.github.io/nexy/docs/routing/fbr/"
cover = "cover.png"
proof = ["compile-2026-11.md"]
+++

## Two projects, one URL

A React app with a router has the path in a component tree. A FastAPI app has the same path in a
decorator. Between the two, a CORS block, a base URL in an environment file, and the question of who
owns `/products` the day someone asks for `/produits` too.

None of that is hard. It is a second place to remember, and the two places drift: the front end keeps a
route the endpoint no longer serves, and the 404 shows up in production.

## The URL is the path

A file under `src/routes/` is a page, and its path under that folder is its URL.

| file | URL |
|---|---|
| `index.nexy` | `/` |
| `about.nexy` | `/about` |
| `blog/[slug].nexy` | `/blog/hello` |
| `docs/[...path].nexy` | `/docs/a/b` |
| `(marketing)/pricing.nexy` | `/pricing` |
| `api/products.py` | `/api/products` |

Two details are worth the paragraph. `index` maps to its directory, so there is no `/index` page to
explain. A folder in parentheses is a group: it orders files on disk and disappears from the URL.

## One file, one page, its own data

A `.nexy` file has two halves. The top, between `---`, is Python: it imports, queries, and returns
the values the page needs. The rest is the page, written in Jinja and Tailwind.

```nexy title="src/routes/products/[slug].nexy"
---
from app.db import load_product

slug: prop[str]
product = load_product(slug)
---
<h1>{{ product["name"] }}</h1>
```

The query runs on the server, so the HTML that leaves it already has the name in it. That matters for
the two readers who never run JavaScript: the crawler, and the person on a train with one bar of
signal.

The other half: a `.py` file next to it is the API. The function name is the HTTP method, so
`/api/products` has one owner in the repository.

```python title="src/routes/api/products.py"
async def GET():
    return {"products": []}
```

## What the convention costs

A naming convention is a constraint, and pretending otherwise is how a framework page turns into an
advertisement.

- Renaming a file moves a URL. That is the point, and it still means a redirect to write the day a
  page moves.
- The folder is the URL, so a URL you do not like is a folder you have to reorganise. Groups help;
  they do not remove the constraint.

## Where it stops paying

File-based routing is a good fit for pages, and a page is a document with a URL. Three places where
that stops being true:

1. **A large API surface.** Twenty endpoints over four resources want a controller layer, not twenty
   loose files. Nexy keeps a modular router for exactly this, and a project can serve its pages from
   files and its API from modules.
2. **Client mode.** With `useCSR = True`, `.tsx`, `.vue` or `.svelte` files are the pages instead of
   `.nexy`. A project picks one mode; server pages and client routes do not mix in one tree.
3. **Authorisation.** The file decides where a page lives, not who may read it. A check belongs in a
   layout, a middleware or the handler, and the file router has no opinion about which.

## The part that makes it usable

A convention that costs 200 ms per save is a convention nobody keeps. So the number that decides
whether this is pleasant is the recompile a save triggers: on an 87-line route with three component
imports and a loop over 380 items, it is 1.6 ms, median of 25 runs on a Ryzen 5 4500U. The raw runs,
the command and the one outlier at 4.21 ms are in the repository next to the post that quotes them.

That is the compile step alone. A browser reload adds a websocket message and Vite's module graph on
top, which is a different measurement and will be published as one when it exists.

## Start

```bash
nx new shop
```

Then `src/routes/products/[slug].nexy`, and the URL works. The routing page of the docs covers
layouts, middleware and the catch-all syntax; the repository has a five-framework example if you
would rather read the whole tree first.

- Espoir Loem
