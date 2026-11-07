# REACH

A curated list is the cheapest durable distribution Nexy has: one accepted line sends developers who
already search for the problem, and it keeps sending them for years. GitHub marks outbound links
`nofollow`, so an entry buys discovery and a branded search more than PageRank; the SEO work itself
stays on the docs site (canonical, sitemap, one page per question).

This page records where Nexy is listed, where it is not yet, and why. It is updated when a PR is
opened or merged, not when a list is merely considered.

## The registry

One row per repository, so the next PR starts where the last one stopped. A row changes the day a PR
is merged or declined; a declined row keeps the reason in the Status cell, and the next attempt waits
until the reason is gone.

| Repository | Section | Status | PR |
|---|---|---|---|
| [awesome-python-web-frameworks](https://github.com/sfermigier/awesome-python-web-frameworks) | Full-stack frameworks, but data-layer agnostic | open, 2026-11-07 | [#19](https://github.com/sfermigier/awesome-python-web-frameworks/pull/19) |
| [awesome-asgi](https://github.com/florimondmanca/awesome-asgi) | Application frameworks | open, 2026-11-07 | [#121](https://github.com/florimondmanca/awesome-asgi/pull/121) |
| [awesome-vite](https://github.com/vitejs/awesome-vite) | SSR > Frameworks | open, 2026-11-07 | [#1173](https://github.com/vitejs/awesome-vite/pull/1173) |
| [awesome-starlette](https://github.com/sfermigier/awesome-starlette) | Frameworks | open, 2026-11-07 | [#3](https://github.com/sfermigier/awesome-starlette/pull/3) |
| [awesome-fastapi](https://github.com/mjhea0/awesome-fastapi) | Projects > Open Source Projects | open, 2026-11-07 | [#373](https://github.com/mjhea0/awesome-fastapi/pull/373) |
| [best-of-web-python](https://github.com/ml-tooling/best-of-web-python) | web-frameworks | blocked, 50 stars | — |
| [awesome-python](https://github.com/vinta/awesome-python) | Web Frameworks | blocked, 3+2 cap and downloads | — |
| [awesome-fastapi-projects](https://github.com/Kludex/awesome-fastapi-projects) | — | auto-indexed, no PR | — |
| [uhub/awesome-python](https://github.com/uhub/awesome-python) | — | mirror, no PR | — |
| [Correia-jpv/fucking-awesome-python](https://github.com/Correia-jpv/fucking-awesome-python) | — | mirror, no PR | — |
| [sindresorhus/awesome](https://github.com/sindresorhus/awesome) | — | lists lists, no entry | — |

The canonical line, used where the list has no length rule:

> A full-stack Python meta-framework with Next.js-style file routing, layouts and islands, built on
> FastAPI and Vite.

`awesome-vite` asks for fewer than 24 words and no mention of Vite, so it gets the short variant:

> Next.js-style file routing, layouts and islands with Python on the server.

## Why two rows are blocked

Most lists are a PR away. Two are not, and opening a PR before the threshold only burns the one
submission a maintainer remembers:

- `ml-tooling/best-of-web-python` refuses projects below **50 GitHub stars** (`min_stars: 50` in
  `projects.yaml`). At 50, add Nexy to the `web-frameworks` category with `github_id:
  NexyPy/nexy`, `pypi_id: nexy` and `category: web-frameworks`.
- `vinta/awesome-python` caps each use case at **3 obvious choices + 2 challengers**, and admission
  is decided on PyPI downloads, not stars. Its Web Frameworks use case is full (Django, Flask,
  FastAPI). Do not open a PR before Nexy is a challenger by downloads.

## Auto-indexed, no PR to open

- `Kludex/awesome-fastapi-projects` is generated from a SourceGraph scan of public repositories that
  import FastAPI. A PR there would be overwritten; the next scan is the only entry point, and Nexy
  already has the import and the `fastapi` topic.
- `uhub/awesome-python` and `Correia-jpv/fucking-awesome-python` mirror `vinta/awesome-python`. They
  follow the original; do not submit to them separately.
- `sindresorhus/awesome` lists lists, not projects. There is no entry to add.

## Directories and newsletters

These do not take a PR. One form or one email each, once Nexy has something to show: a release, a
reproducible number, or a demo.

| Target | What to submit | Note |
|---|---|---|
| [LibHunt](https://www.libhunt.com/) | a project page | Python section; links GitHub, PyPI and mentions |
| [SaaSHub](https://www.saashub.com/) | a tool page | free listing; name the alternatives |
| [AlternativeTo](https://alternativeto.net/) | an app page | list it as an alternative to Next.js, Django and Flask |
| [StackShare](https://stackshare.io/) | a tool profile | tags, description, GitHub link |
| [Slant](https://www.slant.co/) | an option | add to "Best Python web frameworks" |
| [Product Hunt](https://www.producthunt.com/) | one launch | one shot; use the cards from `COM/BRAND.md` |
| [DevHunt](https://devhunt.org/) | one launch | weekly dev-tool launch |
| [Hacker News](https://news.ycombinator.com/) | a Show HN | a demo and a number a reader can reproduce |
| [PyCoder's Weekly](https://pycoders.com/) | a link and one line | newsletter; send on a release, not twice for the same one |
| [Python Weekly](https://www.pythonweekly.com/) | a link and one line | same rule |
| [Import Python](https://importpython.com/) | a link and one line | same rule |
| [Console.dev](https://console.dev/) | a dev tool | newsletter for developer tools |

`r/Python`, `r/FastAPI` and `r/webdev` are not listed above on purpose: each subreddit has its own
self-promotion rule and its own moderation history. Read the rule of the day before posting, and
answer the comments after.

## What a list does not fix

A list entry points at the repository. The pages a search engine actually ranks are the ones Nexy
owns:

- The PyPI page has no `project_urls` and no classifiers yet (`pyproject.toml`). A release should add
  Homepage, Documentation, Repository and Changelog, plus the Framework and Environment classifiers,
  so the page links back to the docs and the source.
- The docs site already writes `robots.txt` and `sitemap.xml` (`sites/vanilla/build.py`). Verify the
  property in Search Console once and submit the sitemap; a list cannot do that part.
- GitHub topics are already set (`fastapi`, `vite`, `ssr`, `full-stack`, and others). Keep them
  accurate instead of adding forty.
- The page that should own "Python Next.js alternative" is a docs page, not a list entry. One page
  per question, as `AGENTS.md` says.

## The order

1. The five list PRs above, and the second wave once `best-of-web-python` reaches its threshold.
2. The directory forms, which cost one submission each and keep working without an editor.
3. A newsletter only when there is a release or a measurement worth a line.
4. Product Hunt and Show HN once, when the demo and the number are both ready.

## Rules

- One list, one PR, one entry. Never paste the same sentence into two lists.
- Read the current README and contributing guide before editing: order, star counts, badges and
  entry formats change.
- Search for `nexy` before opening a PR; a duplicate closes itself.
- Follow the list's order: alphabetical when it is alphabetical, append when it is first-come,
  descending stars when it is ranked.
- Describe what Nexy does, not how it feels. No "blazing fast", no "revolutionary".
- Disclose that you are the author in the PR body. A list is a shared resource, not a billboard.
- Never ask for a star or a follow in a list PR. `COM/VOICE.md` bans it everywhere else too.
- Record the PR link here the day it opens. If a list declines, keep the reason next to the link and
  do not reopen before the reason is gone.
