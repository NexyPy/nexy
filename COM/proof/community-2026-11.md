# What can be shown about the community, 2026-11-06

The rule this file exists to enforce: a post shows the community through artefacts it can point at,
and never calls it `our community`. That sentence becomes available the day this file can show three
people outside the maintainer with a merged pull request.

Today it cannot.

## Who is here

- One maintainer: Espoir Loem (`Espoir-Loem`), 2 244 commits at the time of writing.
- One GitHub Actions account, which opens the release pull requests: 3 merged.
- Everyone else: no merged pull request.

The contributors endpoint returns two logins, and one of them is a bot. `2 contributors` is therefore
a number that must never appear in a post.

## What exists, and what it enforces

| artefact | what it does | where |
|---|---|---|
| `CONTRIBUTING.md` | one commit one unit, Conventional Commits, a maintainer review before merge, no force-push on `main` | root |
| `.githooks/commit-msg` | refuses an AI co-author trailer, so the contributor graph stays human | root |
| `scripts/check_attribution.py` | the check the hook runs, usable in CI | `scripts/` |
| 3 issue templates + 1 pull request template | a report that arrives with the version, the steps and the trace | `.github/` |
| the `good first issue` label | the shelf a stranger can pick from without asking | GitHub labels |
| `CHANGELOG.md` | dated entries, 2.2.2 on 2026-11-05 | root |
| `CODE_OF_CONDUCT.md`, `SECURITY.md` | how to behave, and how to report something privately | root |
| 204 closed issues, 24 open | someone answers, and the queue is not a graveyard | GitHub search |

## What is missing

- A second person with a merged pull request. Until then, no post may say `our contributors`,
  `built with the community`, or quote a user as a testimonial.
- A discussion thread answered by someone other than the maintainer.
- An integration written outside the repository. Every example in `examples/` was written here,
  which is exactly why a post about them shows the code and never the word `adoption`.
- Native review of the French and Portuguese entry pages, which is why no post claims the docs are
  published in 12 languages, even though they are.

## How this file changes

A new file, `community-2027-02.md`, when a month has something to show. Not an edit of this one: the
point of a dated snapshot is that the older, smaller one stays readable.

The first line that unlocks `our community` is the day this table gains a row with a name that is
not `Espoir-Loem` and not a bot, with the pull request number next to it.
