# With i18n: a site in two languages

Harbour Cafe is a made-up cafe whose site speaks English and French. Nexy has no locale layer of its
own ([the i18n guide](../../docs/guides/i18n.md) says why), so this sample shows the plain way:

- the language is the first part of the address: `/en/about`, `/fr/about`;
- `src/routes/index.nexy` sends `/` to the language the browser asks for, read from
  `Accept-Language` with its weights: `de, fr;q=0.8, en;q=0.5` gives `/fr`;
- every sentence is in `src/i18n/catalog.py`, once per language, and `t(lang, key)` reads it;
  a plural is a pair, picked by `count`;
- the root layout sets `<html lang>`, links the same page in each language with `hreflang`, and
  lists them for search engines with `<link rel="alternate">`, `x-default` included;
- an address in a language the site does not have answers 404, and the 404 page speaks the language
  of the address.

| File | What it does |
|---|---|
| `src/i18n/__init__.py` | the languages, `best()` for `Accept-Language`, `t()` for a sentence |
| `src/i18n/catalog.py` | every sentence, in each language |
| `src/routes/index.nexy` | `/`: a redirect to the best language |
| `src/routes/layout.nexy` | `<html lang>`, the menus, the `hreflang` links |
| `src/routes/[lang]/index.nexy`, `[lang]/about.nexy` | the pages, with the language as a value of the address |
| `src/routes/notfound.nexy` | the 404 page, in the language of the address |

When the catalog grows, swap the dictionaries for gettext from the standard library or Babel: `t()`
is the only function that changes.

## Run it

You need Python 3.12 or newer, [uv](https://docs.astral.sh/uv/), and Node.js with npm, pnpm or
bun.

```bash
git clone https://github.com/NexyPy/nexy
cd nexy/examples/with-i18n
uv sync
npm install          # or pnpm install, bun install
uv run nexy dev
```

## Test it

```bash
uv run pytest
```

The tests send `Accept-Language` headers with weights to `/`, read the `lang` attribute and the
`hreflang` links, check that both languages have every sentence and that a plural picks the right
form, and send an address with HTML in it: the layout prints the address with `| e`.
