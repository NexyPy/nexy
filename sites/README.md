# Documentation sites

Two sites show the pages of [`docs/`](../docs/README.md). Neither owns any text: both read the
Markdown through [`shared/docs_source.py`](shared/docs_source.py), so a page edited in `docs/` changes
both. The menu is the sections and tables of `docs/README.md`.

| Site | Built with | Runs on |
|---|---|---|
| [`vanilla/`](vanilla/) | one Python script, plain HTML, CSS and JS, no framework | GitHub Pages: static files |
| [`nexy/`](nexy/) | Nexy itself: `.nexy` components, a layout and two Python handlers | any host that runs Nexy |

## Vanilla

```bash
uv run python sites/vanilla/build.py          # writes sites/vanilla/dist
python -m http.server -d sites/vanilla/dist   # then open http://localhost:8000/docs/
```

Every link is relative, so the folder also works under a project URL such as
`https://nexypy.github.io/nexy/`. [`.github/workflows/pages.yml`](../.github/workflows/pages.yml)
builds and publishes it on each push to `main` that touches `docs/` or `sites/`. Turn it on once in
**Settings > Pages > Source: GitHub Actions**.

## Nexy

```bash
cd sites/nexy
nx dev
```

The stylesheet and the script come from `sites/vanilla/assets`, served at `/assets/`, so both sites
look the same and there is one copy to maintain. `useDocs` is off in `nexyconfig.py`: FastAPI's own
`/docs` would shadow the `/docs` pages.

## Tests

`tests/unit/sites/` builds the vanilla site and checks that every page exists, every relative link
resolves to a file and search lists every page. It also runs the Nexy site and requests each page of
the menu. Another test checks that every `page.md#heading` link in `docs/` finds its heading.

## Rules

- The text lives in `docs/`. Do not write prose in a site.
- Keep the vanilla site free of frameworks and of a build step other than `build.py`.
- A new site reads `docs/` through `shared/docs_source.py` and passes its own `link` function.
