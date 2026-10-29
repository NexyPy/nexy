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

Every link between pages is relative, so the folder also works under a project URL such as
`https://nexypy.github.io/nexy/`. Only `404.html` needs to know where the site lives, because GitHub
shows it at the address that failed, whatever its depth: pass `--base /nexy` (the workflow does).
[`.github/workflows/pages.yml`](../.github/workflows/pages.yml) builds and publishes it on each push
to `main` that touches `docs/` or `sites/`. Turn it on once in **Settings > Pages > Source: GitHub
Actions**.

What it gives a reader: a menu by section, with collapsible groups that remember what you closed and a
filter that narrows the list as you type; an outline of the page that follows the scroll; search
(`Ctrl K` or `/`) that shows the words found; light and dark themes that follow the system; code
coloured when the site is built (so it reads without JavaScript); GitHub alerts (`> [!NOTE]`) drawn
as callouts; `diagram` fences drawn as framed illustrations; a copy button on code; links to every
heading; previous and next pages; a "skip to content" link; and a layout that holds from a phone to a
wide screen.

**Two routers, one menu.** Like the docs of Next.js, which has two routers, the menu starts with a
choice: *File-based* or *Modular*. It shows the pages of the router you chose, plus every page both
share, and remembers the choice in the browser. A page under `docs/routing/fbr/` or
`docs/routing/modular/` belongs to that router, so opening one sets the menu by itself, and
choosing the other router from it leads to that router's overview. The router of a page comes from
its folder (`router_of` in `shared/docs_source.py`): put a page of a router in its folder, and
nothing else needs to change.

The build is in English, like `docs/`. A new language is a new folder of Markdown read the same way,
not a change to the script.

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
