<!--
  Thanks for the pull request. The three sections below are required: a reviewer reads them before
  the code. Before you open it:

  1. Branch from `develop`: `feature/*`, `fix/*`, `docs/*` or `perf/*`.
  2. Write the test first, and watch it fail before the code makes it pass.
  3. Run the gates the CI runs: `python scripts/verify.py`.

  Learn more in CONTRIBUTING.md.
-->

## Summary

<!--
  The motivation: what problem does this solve, for whom? Link one issue on its own line below:
  "Closes #123", "Fixes #123" or "Resolves #123". CI requires it and a bot closes the issue
  when the pull request is merged.
-->

Closes #123

## How did you test this change?

<!--
  The commands you ran and what they printed; for a change a person sees, a screenshot or a short
  video. A pull request with this section empty will very likely be closed.
-->

## Checklist

- [ ] The description has a `Closes #123`, `Fixes #123` or `Resolves #123` line
- [ ] `python scripts/verify.py` passes (lint, format, typecheck, structure, tests)
- [ ] Each new behaviour has a test that failed before the change
- [ ] Each commit changes one file written by hand, with its test (a docs page also carries its
      translations, written by `scripts/translate_docs.py`)
- [ ] Commit messages follow [Conventional Commits](https://www.conventionalcommits.org/)
- [ ] No AI tool appears as author or co-author: no `Co-authored-by` trailer for one, no
      "Generated with" footer
- [ ] A new docs page is listed in `docs/README.md` and `llms.txt`
