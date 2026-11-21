# FBR basics: how files become addresses

A three-bird field guide that shows the file-based router (FBR) of Nexy: each file under
`src/routes` is an address, and each page says which file draws it.

| File | Address | What it shows |
|---|---|---|
| `src/routes/index.nexy` | `/` | a folder's `index` answers the folder itself |
| `src/routes/about.nexy` | `/about` | a file name is a path |
| `src/routes/layout.nexy` | every page | the document around all pages |
| `src/routes/birds/layout.nexy` | `/birds/...` | a layout wraps only its folder, inside the root one |
| `src/routes/birds/index.nexy` | `/birds` | a page inside a folder |
| `src/routes/birds/[slug].nexy` | `/birds/robin` | `[slug]` in the name is a value of the address; an unknown bird is `notFound()`, a 404 |
| `src/routes/api/birds.py` | `/api/birds` | a Python file answers with what `GET` returns, here JSON |
| `src/routes/notfound.nexy` | any other address | the 404 page |

The birds themselves are plain Python in `src/birds.py`, read by the pages.

## Run it

You need Python 3.12 or newer, [uv](https://docs.astral.sh/uv/), and Node.js with npm, pnpm or
bun.

```bash
git clone https://github.com/NexyPy/nexy
cd nexy/examples/fbr-basics
uv sync
npm install          # or pnpm install, bun install
uv run nexy dev
```

## Test it

```bash
uv run pytest
```

The tests ask each address the way a browser does, with no server to start: every file answers its
address, the birds layout wraps `/birds` and nothing else, an unknown bird and an unknown address
answer 404, and `/api/birds` answers JSON.

## Next

The [docs example](../docs) and the [blog example](../blog) use the same router for a whole site.
