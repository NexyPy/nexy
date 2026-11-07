# The snapshot, 2026-11-06

Everything a post is allowed to say about how big this project is, taken on one day from sources
anyone can re-read.

## The numbers

| what | value | read from |
|---|---|---|
| stars | 11 | `api.github.com/repos/NexyPy/nexy` |
| forks | 6 | same |
| watchers | 1 | same |
| open issues | 24 | `search/issues?q=repo:NexyPy/nexy+type:issue+is:open` |
| open pull requests | 3 | the same search with `type:pr` (the repository's `open_issues_count` says 27: issues and pull requests together) |
| issues closed | 204 | `search/issues?q=repo:NexyPy/nexy+type:issue+is:closed` |
| pull requests merged | 92 | `search/issues?q=repo:NexyPy/nexy+type:pr+is:merged` |
| pull requests closed unmerged | 5 | closed count 97 minus merged 92 |
| releases on PyPI | 164 | `pypi.org/pypi/nexy/json` |
| latest version | 2.2.2, 2026-11-05 | same |
| installs, last month | 330 | `pypistats.org/api/packages/nexy/recent` |
| installs, last week | 331 | same |
| installs, last day | 9 | same |
| first commit, first release | 2024-12-28 | GitHub `created_at`, first PyPI upload |

## The commands

```bash
curl -s https://api.github.com/repos/NexyPy/nexy | python -m json.tool | head -40
curl -s "https://api.github.com/search/issues?q=repo:NexyPy/nexy+type:issue+is:closed&per_page=1"
curl -s https://pypistats.org/api/packages/nexy/recent
curl -s https://pypi.org/pypi/nexy/json | python -c "import json,sys; d=json.load(sys.stdin); print(len(d['releases']), d['info']['version'])"
```

## What the numbers mean, and what they do not

330 installs a month against 11 stars is the interesting part: most people who try this never open
the repository, and a post that asks for a star is asking the smallest part of the audience to do
the least useful thing. The installs are the audience; the stars are a rounding error of it.

Two honest limits on the install figure. pypistats counts downloads, not people: a CI job that
installs the package on every push counts as a download, and so does a reinstall of the same
version. And the 12-month trend is not in this file, so no sentence about growth is allowed from it:
330 this month says nothing about 300 or 400 next month until both exist.

The issue counts are the ones we will point at when someone asks whether a project is alive: 204
closed, 24 open, 92 pull requests merged. They are also the only community numbers allowed in a post
until `community-2026-11.md` changes.
