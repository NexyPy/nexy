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

**Every section, one router.** The menu shows every section of `docs/README.md` at once (each `##`
is a heading, each `###` a folder that opens and closes), so a reader never has to switch to find
React, the route handlers or the reference. The only choice above it is the router: *FBR*
(file-based routing), *Modular* (controllers, modules and injection) or *Custom Router* (create your
own). It hides the routing folders of the other routers and is remembered in the browser. A folder
whose pages all live under `docs/routing/<router>/` belongs to that router (`router_of` in
`shared/docs_source.py`): opening one of its pages sets the choice by itself, and choosing another
router from it leads to that router's overview. On a shared page the choice only swaps the folders.
Previous and next never lead into another router.

The build is in English, like `docs/`. A new language is a new folder of Markdown read the same way,
not a change to the script.

## What a crawler reads

Every page is HTML a crawler can index without running a script: one `<h1>`, a `<title>`, a summary
taken from the opening paragraph, and the whole menu of links. Three more things say what to index.

| What | Where it comes from | What it holds |
|---|---|---|
| `sitemap.xml` | `build.py`, from the pages it writes | the absolute address of every page |
| `robots.txt` | `build.py` | where the sitemap is, and `Disallow: /*.md$` for the raw Markdown copies |
| the `<head>` | `sites/shared/seo.py` | canonical, `og:*` and `twitter:*` cards, a `TechArticle` graph with the breadcrumb |

`--site-url` is the address the site is published at, `https://nexypy.github.io/nexy` by default;
`.github/workflows/pages.yml` passes the one GitHub reports, so the canonical tags follow the host
the site really runs on. The picture the cards show is `vanilla/assets/og.png`, 1200 by 630.

> [!NOTE]
> A crawler reads `robots.txt`, and the rules inside it, only at the root of the host
> (`https://nexypy.github.io/robots.txt`), which a project page does not own. The sitemap is still
> worth submitting in Search Console; the rules apply once the docs have a domain of their own.

## Nexy

```bash
cd sites/nexy
nx dev
```

The stylesheet and the script come from `sites/vanilla/assets`, served at `/assets/`, so both sites
look the same and there is one copy to maintain. `useDocs` is off in `nexyconfig.py`: FastAPI's own
`/docs` would shadow the `/docs` pages. It writes the same head tags, from the same module, with
`SITE_URL` in `src/content.py` as the address it is published at.

## Tests

`tests/unit/sites/` builds the vanilla site and checks that every page exists, every relative link
resolves to a file and search lists every page. It also runs the Nexy site and requests each page of
the menu. Another test checks that every `page.md#heading` link in `docs/` finds its heading.

## Rules

- The text lives in `docs/`. Do not write prose in a site.
- Keep the vanilla site free of frameworks and of a build step other than `build.py`.
- A new site reads `docs/` through `shared/docs_source.py` and passes its own `link` function.
