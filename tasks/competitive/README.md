# Competitive Source Analysis

How to read these analyses. Each framework file documents the **source code** of a core
mechanism — not the docs, not the marketing — and contrasts it with the equivalent Nexy
code path (`file:line` anchors verified against this repo).

## Goal

Every epic under `TASKS/` must be grounded in one of these analyses. A gap is only real
when it can be pointed at in both the competitor source and the Nexy source.

## Reading Order

1. `ANALYSIS.md` — the 6×6 matrix synthesis. Start here for the big picture.
2. Per-framework files — deep dives with file:line references from each upstream repo.
3. Per-epic READMEs — the actionable optimization plan derived from a specific gap.

## Conventions

- Upstream references use `owner/repo@path:line` notation (repo state captured mid-2026).
- Nexy references use `nexy/...` paths relative to this repo; line numbers are current.
- Each analysis ends with a "Nexy gap" section that links to the relevant `TASKS/` epic.

## Scope

Mechanisms only — routing, compilation, SSR rendering, data protocols, hydration, dev/HMR,
static generation, caching. Component APIs are explicitly out of scope.