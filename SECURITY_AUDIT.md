# Nexy — Security & Supply Chain Audit

**Date**: 2026-10-21 · **Auditor**: automated audit, evidence-backed
**Target**: `D:\dev\python\nexy` · branch `V2` · HEAD `fb5a82974d3b8773f67d01a3c84d65ee0ee6be04` · `nexy` 2.1.1 (`pyproject.toml:3`)
**Supersedes**: the security section of `SECURITY.md` (2026-10-19), whose numbers are no longer accurate (see F1).

---

## 1. Scope & freeze

| | |
|---|---|
| **Dimensions** | Supply-chain integrity · CI/CD gate integrity · application-security posture (SAST + control verification) · accuracy of the project's own security documentation |
| **Threat model** | Adversary: (a) a compromised upstream package or registry, (b) a malicious PR contributor, (c) an accidental regression in the framework's own security controls. Assets: CI runner credentials, the integrity of the published `nexy` wheel, and the 10 template projects shipped to users. Entry points: `uv pip install` resolution in CI, GitHub Actions references, `.nexy` frontmatter executed at build time, PyPI publish. |
| **Frozen state** | The **working tree**, not the committed SHA. It is dirty: 58 paths (49 modified, 9 untracked). This distinction is load-bearing — F1 and F11 exist only because of it. |
| **Out of scope** | `docs/` (separate git repo, own `.git`, HEAD `59de0e39`) · performance · accessibility · product UX · the resolved dependency *trees* of `templates/` and `extensions/vscode/` (manifests inspected, trees not resolved) · any dynamic testing or exploitation |

---

## 2. Standards applied

| Standard | Version | Retrieved | Source |
|---|---|---|---|
| OWASP Application Security Verification Standard | **5.0.0** (stable, 30 May 2025) | 2026-10-21 | https://asvs.owasp.org/ |
| OWASP Top 10 | **2025** | 2026-10-21 | https://owasp.org/Top10/2025/ |
| GitHub Docs — *Secure use reference* (Actions) | current | 2026-10-21 | https://docs.github.com/en/actions/reference/security/secure-use |
| OWASP Cheat Sheet — *GitHub Actions Security* | current | 2026-10-21 | https://cheatsheetseries.owasp.org/cheatsheets/GitHub_Actions_Security_Cheat_Sheet.html |
| Bandit | **1.9.4** (installed locally; *not* a declared dependency — see F6) | 2026-10-21 | `.venv/Lib/site-packages/bandit-1.9.4.dist-info` |
| `uv` | **0.6.17** | 2026-10-21 | `uv --version` |

Top 10:2025 categories engaged by these findings: **A03 Software Supply Chain Failures**, **A08 Software or Data Integrity Failures**, **A02 Security Misconfiguration**, **A10 Mishandling of Exceptional Conditions**.

> ASVS requirement IDs are deliberately **not** quoted. ASVS 5.x renumbered every chapter relative to 4.0.3, so a 4.0 ID quoted in 2026 would silently point at the wrong requirement.

---

## 3. Coverage & blind spots

**Scanned**
- `nexy/` Python source — 9 244 LOC (bandit's own metric) — full Bandit scan, run twice: with and without `.bandit`
- `.github/workflows/ci.yml` — the repository's only workflow
- `pyproject.toml` — all dependency declarations
- All 43 tracked `package.json` / `tsconfig.json` — install hooks
- Tracked binaries, lockfiles, `.gitignore` policy
- Secret sweep: regex over `*.py` for literal `password|secret|api_key|token|passwd` assignments

**NOT checked — stated up front, because absence ≠ cleanliness**
- **No SCA was run.** `pip-audit` / OSV was **not executed**: it is not installed and not a declared dev dependency. **No claim is made about whether any current dependency has a known CVE.** Installing it mutates the venv, so it was deliberately not done silently.
- `docs/` — a separate repository, not audited.
- `extensions/vscode/` TypeScript source and the `templates/` JS projects — dependency trees not resolved.
- No dynamic testing, no runtime exploitation, no fuzzing. This is static + configuration analysis.
- Bandit is pattern-matching and is structurally blind to multi-step logic flaws — the F2 class is exactly such a flaw and Bandit cannot see it.
- The secret sweep covered `*.py` only. `*.md`, `*.yml`, `*.json`, `*.nexy` were **not** swept. No `gitleaks`/`trufflehog` binary was available.
- `bandit` reports `nosec: 0` — no inline suppression markers exist to be missed.

---

## 4. Findings

Ordered by exploitability × impact.

> **Fix pass (2026-10-22) — resolution status:**

| Finding | Status | Where |
|---|---|---|
| F1 `.bandit` untracked | **RESOLVED** | `.bandit` tracked; rewritten to `skips: []` with the inline-`# nosec` governance rule |
| F2 sandbox is dead code | **RESOLVED** | `nexy/core/sandbox.py` deleted; `SECURITY.md` states plainly that `.nexy` frontmatter runs unsandboxed (author's own code) |
| F3 no lockfile / no SCA | **RESOLVED** | `uv.lock` committed (`bandit` + `pip-audit` declared in `[dependency-groups].dev`); CI installs with `uv sync --frozen --group dev` and runs `pip-audit` on the exported lock; result register in `SECURITY.md` (1 documented ignore: PYSEC-2022-252) |
| F4 CI misses PRs to `V2` | **RESOLVED** | `.github/workflows/ci.yml` `pull_request.branches: [main, develop, V2]` |
| F5 actions pinned to tags | **RESOLVED** | All four actions SHA-pinned, tags cross-checked via the GitHub API (checkout v4.2.2, setup-uv v5.4.2, pnpm/action-setup v4.0.0, setup-node v4.1.0) |
| F6 no bandit gate | **RESOLVED** | `bandit` declared + `uv run --no-sync python -m bandit -r nexy/ -c .bandit` in CI; no `--exit-zero`, rc must be 0 |
| F7 whole-class skips | **RESOLVED** | `.bandit` `skips: []`; every residual risk is an inline `# nosec <ID>` with justification, mirrored in the `SECURITY.md` residual risk register |
| F8 prebuilt `.vsix` tracked | **RESOLVED** | 5 binaries unstaged from git (`git rm --cached`, files remain on disk) + `*.vsix` ignored |
| F9 lockfile ignore policy | **RESOLVED** | `bun.lock` / `pnpm-lock.yaml` ignore lines removed from `.gitignore`; lockfiles are versioned by policy (root `uv.lock` included) |
| F10 `tests/` unlinted | **RESOLVED** for lint: `ruff check tests/` → 0 (23 auto-fixes + 29 manual), `ruff format tests/ --check` → clean, both gated in CI. [PARTIAL] `mypy tests/` intentionally not added — `nexy/`-strict is the framework contract; tests use plain annotations. JS/TS side: new CI `extension` job typechecks, lints and production-builds `extensions/vscode/` |
| F11 work uncommitted | **RESOLVED** | This fix pass committed in atomic commits (see `git log`) |

Bandit after the pass: **0 HIGH / 0 MEDIUM / 0 LOW, 0 skipped** (`python -m bandit -r nexy/ -c .bandit` rc=0). All five quality gates re-verified after every change: ruff check/format (185 files), mypy --strict (125 files), pytest 381 passed + 1 skipped, coverage 54.54% (floor 54).

### [HIGH] [VERIFIED] F1 — The `.bandit` accepted-risk registry is not in the repository. The documented audit command fails, and the security baseline collapses to 4 HIGH / 9 MEDIUM on any fresh clone.

**Location** `.bandit` (untracked) · `SECURITY.md:57-89` · `.github/workflows/ci.yml`

**Evidence**
```
> git ls-files | Select-String -Pattern 'bandit'
(empty — the file is NOT tracked)

> git check-ignore -v .bandit
exit=1   (not gitignored — simply never committed)

> .\.venv\Scripts\bandit.exe -r nexy/ -c "D:\nonexistent\.bandit"
[main] ERROR D:\nonexistent\.bandit : Could not read config file.
bandit_missing_config_exit=2
```

Baseline **without** the config — i.e. what every clone of this repository sees:
```
TOTALS: SEVERITY.HIGH=4  SEVERITY.MEDIUM=9  SEVERITY.LOW=52

HIGH   nexy/cli/commands/migrate.py:64          [B701] jinja2 autoescape=False
       nexy/template.py:68                       [B701]
       nexy/helpers/init/renderer.py:41            [B701]
       nexy/helpers/init/template_setup.py:251     [B701]
MEDIUM nexy/cli/commands/dev.py:108              [B104] bind all interfaces
       nexy/cli/commands/start.py:24             [B104]
       nexy/core/config.py:44                    [B104]
       nexy/core/models.py:197                   [B104]
       nexy/helpers/common/constants.py:4          [B104]
       nexy/helpers/server/ports.py:12             [B104]
       nexy/helpers/server/ports.py:25             [B104]
       nexy/core/sandbox.py:103                  [B102] exec
       nexy/helpers/server/server.py:225           [B310] urlopen
```
With the local (untracked) `.bandit`: `HIGH=0 MEDIUM=1 LOW=22`.

**Impact** `.bandit` is the audit trail for every accepted risk **and** the suppression registry for the three 2026-10-19 fixes (B602 `shell=True`, B310 scheme allowlist, B324 MD5). It exists only in one developer's working tree. Anyone who clones — a contributor, a reviewer, a CI job, a downstream packager — receives an unaudited tree carrying 4 HIGH-severity Jinja2-autoescape findings, with no record of which were reviewed and on what grounds. `SECURITY.md:62` states "Accepted risks are listed in `.bandit` with their justification; nothing is skipped without an entry here." For the repository, that statement is false.

**Fix** `git add .bandit` — it is not gitignored, so this is a plain add, nothing more.

**Verify** `git ls-files .bandit` prints `.bandit`; clone the repo and re-run `bandit -r nexy/ -c .bandit`.

---

### [HIGH] [VERIFIED] F2 — The `exec` sandbox cited by both `.bandit` and `SECURITY.md` as the mitigating control for dynamic code execution is dead code. The real execution path has no sandbox.

**Location** `nexy/core/sandbox.py:99` · `nexy/compiler/parser/logic.py:65-107` · `nexy/compiler/parser/sanitizer.py:76-83` · `nexy/runtime/importer.py:45-75` · `.bandit:21-25` · `SECURITY.md:83-85`

**Evidence**
```
> git grep -n 'sandboxed_exec'
nexy/core/sandbox.py:99:def sandboxed_exec(code: str, namespace: dict[str, Any]) -> None:
tests/unit/nexy/core/test_sandbox.py:3,8,14,19,24,29,34,39,45,51
```
The only non-definition references are in the sandbox's **own unit test**. There is no production caller.

The actual path for `.nexy` frontmatter logic is:

| Step | Code | What it actually does |
|---|---|---|
| 1 | `LogicParser.process` — `compiler/parser/logic.py:65` | entry point |
| 2 | `LogicSanitizer.sanitize` — `compiler/parser/sanitizer.py:76-83` | rewrites only the custom `from "./x.nexy" import Y` / `import "./x.json" as d` syntax. Applies **no** restriction on code content. |
| 3 | `ast.parse(clean_code)` — `logic.py:77` | validates **syntax only** |
| 4 | `ast.unparse` — `logic.py:104-107` | re-serialises. `ast` is a parser/serialiser, not a filter — it removes nothing. |
| 5 | `NexyVFSFinder.find_spec` — `runtime/importer.py:45-69`, installed at `sys.meta_path[0]` (`importer.py:74-75`) | the emitted module is imported as ordinary Python, with full privileges |

Meanwhile the two security documents state:
- `.bandit:21-25` — "B102 - exec in `nexy/core/sandbox.py` (component logic blocks). Core feature: .nexy frontmatter logic is the project owner's own code, **executed with a restricted builtins set and a denied-names guard**."
- `SECURITY.md:83-84` — "**`exec` of component logic** (`core/sandbox.py`): executes the project author's own code **with a restricted builtins set**"

**Impact** Two independent security documents assert a control that is not on the execution path. The code that does run has unrestricted Python semantics — full builtins, unrestricted imports, no denied-name guard. `sandboxed_exec` is nonetheless shipped in the published wheel (`pyproject.toml:50` → `packages = ["nexy"]`), so a maintainer or downstream reader can reasonably conclude the logic path is sandboxed and either omit a needed control, or wire `sandboxed_exec` in believing it is already wired in.

*Calibration:* the code executed is the **project author's own**, so this is not privilege escalation against an external attacker. The defect is **false assurance plus a misleading module name** — a control documented in two places that does not exist.

**Fix** — choose one; do not do both.
- **(a) Make the documents true.** Delete `nexy/core/sandbox.py` and its test, remove the `B102` skip from `.bandit`, and rewrite the `SECURITY.md` entry to state plainly that frontmatter logic is the project author's own code, executed with full privileges, by design.
- **(b) Make the code true.** Route frontmatter execution through `sandboxed_exec`. This means abandoning the current "emit a module and import it" design for an eval-style one, and reworking prop/import extraction. It is a design change, not a patch.

**Verify** `git grep -n sandboxed_exec -- nexy/` returns only the definition — **or** the frontmatter path demonstrably calls it. Whichever is chosen, `.bandit` and `SECURITY.md` must describe the same system.

---

### [MEDIUM] [VERIFIED] F3 — No lockfile, floating version ranges, a CI install command that structurally cannot consume a lockfile, and no vulnerability scanning.

**Location** `pyproject.toml:13-34` · `.github/workflows/ci.yml:24`

**Evidence**
- `pyproject.toml` — all 9 runtime deps and all 7 dev deps use lower-bound-only ranges (`fastapi>=0.128.0`, `jinja2>=3.1.6`, `uvicorn[standard]>=0.40.0`, …). No upper bounds, no hashes.
- `Test-Path uv.lock` → **NO root uv.lock**.
- CI: `run: uv pip install -e . --group dev`
- ```
  > uv pip install --help   → contains '--frozen': False   contains '--locked': False
  > uv sync --help          → contains '--frozen': True    contains '--locked': True
  ```
  The CI command **cannot** be made lockfile-reproducible as written — and even if a `uv.lock` were committed, `uv pip install` would still resolve fresh versions, because only `uv sync` reads the lockfile.
- No SCA anywhere: `pip-audit` is not installed (no `pip_audit` in `.venv/Scripts`), not in the dev group, and there is no CI step. No OSV, no `npm audit`, no SBOM step.

**Impact** Every CI run and every user install resolves the newest matching upstream version. A compromised or malicious release of `fastapi`, `jinja2`, `uvicorn`, `typer` or `watchdog` — or any transitive dependency — lands unreviewed. Nothing in the pipeline detects a known CVE, so an upstream advisory surfaces only when a user hits it. Maps to Top 10:2025 **A03** and **A08**.

**Fix**
1. `uv lock` and commit `uv.lock`.
2. CI: `uv pip install -e . --group dev` → `uv sync --frozen`.
3. Add `pip-audit` to the dev group + a CI step (`pip-audit`, or `uv export` → `pip-audit -r`).

**Verify** `uv lock --check` exits 0; two consecutive CI runs report identical resolved versions.

---

### [MEDIUM] [VERIFIED] F4 — CI does not run on pull requests targeting `V2`, the active development branch.

**Location** `.github/workflows/ci.yml:3-7`

**Evidence**
```yaml
on:
  push:
    branches: [main, develop, V2]
  pull_request:
    branches: [main]
```
`git branch --show-current` → `V2`.

**Impact** A PR opened against `V2` triggers no `pull_request` workflow. The four quality gates and the coverage floor run only **after** the merge lands. All 49 modified files in the current working tree are work destined for `V2`; reviewers get no automated signal on the PR, and a red suite is discovered post-merge.

**Fix** `pull_request: branches: [main, V2, develop]`.

**Verify** Open a PR against `V2` → the `quality` job appears in the checks list.

---

### [MEDIUM] [VERIFIED] F5 — CI actions are pinned to mutable tags, not commit SHAs.

**Location** `.github/workflows/ci.yml:17,19`

**Evidence**
```yaml
- uses: actions/checkout@v4
- uses: astral-sh/setup-uv@v5
```
GitHub Docs, *Secure use reference* (retrieved 2026-10-21): "The best measure is to lock your workflow dependencies with a lockfile… For repositories that cannot adopt a lockfile: **Pin actions to a full-length commit SHA**." GitHub's actions policy can enforce SHA pinning repository-wide (GitHub Changelog, 2025-08-15).

**Impact** A tag can be moved. Both actions execute with the workflow's credentials and `GITHUB_TOKEN`. Combined with F3 (no lockfile), the *entire* CI dependency surface — actions **and** Python packages — floats on every run, with no integrity check at either layer.

**Fix**
```yaml
- uses: actions/checkout@<40-hex-sha> # v4
- uses: astral-sh/setup-uv@<40-hex-sha> # v5
```

**Verify** `grep -E 'uses: .*@(v[0-9]+|main|master)$' .github/workflows/*.yml` returns nothing.

---

### [MEDIUM] [VERIFIED] F6 — The security posture has no automated gate: Bandit never runs in CI, and `bandit` is not a declared dependency, so the documented audit command cannot be run from a clean checkout.

**Location** `pyproject.toml:26-34` · `.github/workflows/ci.yml:9-39` · `SECURITY.md:89`

**Evidence**
- `[dependency-groups].dev` = `deep-translator, httpx, mypy, pytest, pytest-cov, ruff, types-jinja2`. **No `bandit`.**
- `.venv/Lib/site-packages` contains `bandit-1.9.4.dist-info` — installed out-of-band on this machine only.
- `ci.yml` steps: checkout · setup-uv · install · lint · format · typecheck · test · test coverage. **No bandit step.**
- `SECURITY.md:89` — "To re-run the audit: `python -m bandit -r nexy/ -c .bandit`" → on a clean checkout: `ModuleNotFoundError: No module named 'bandit'`.

**Impact** The three 2026-10-19 fixes have **no CI gate**. A future change reintroducing `shell=True` or a weak hash passes all four quality gates and ships. The stated re-audit procedure is not reproducible from the repository.

**Fix** Add `bandit>=1.9` to the dev group; add a CI step `python -m bandit -r nexy/ -c .bandit`. Bandit exits 1 on the known LOW/MEDIUM findings, so either resolve the remaining B310 or pin the gate to a recorded baseline and fail only on regression.

**Verify** `uv sync --group dev && python -m bandit -r nexy/ -c .bandit` runs in a clean environment.

---

### [LOW] [VERIFIED] F7 — `.bandit` suppresses whole rule classes repo-wide instead of triaging individual findings; the subprocess attack surface is unaudited by rule.

**Location** `.bandit:29-37`

**Evidence**
```yaml
skips:
  - B102   # exec
  - B104   # bind 0.0.0.0
  - B701   # jinja2 autoescape
  - B101   # assert_used
  - B110   # try_except_pass
  - B112   # try_except_continue
  - B404   # import_subprocess
  - B607   # start_process_with_partial_path
```
In `nexy/`: **12** `import subprocess` sites · **22** `subprocess.run`/`Popen` call sites (B603) · **72** `except:` handlers · **2** `assert` statements.

Disabling B404 and B607 turns off Bandit's *entire* subprocess rule family for the tree; the 22 surviving B603 findings are the only subprocess signal left, and all are LOW confidence.

**Impact** This is broader than `SECURITY.md:62-63` — "Every finding was triaged against the FastAPI security guidance and the OWASP API Security Top 10. Accepted risks are listed in `.bandit` with their justification; nothing is skipped without an entry here." The triage is *rule-level*, not finding-level. `subprocess.run(["tsc", "-b"])` (`cli/commands/check.py:48`) and `subprocess.run(["npx", "vitest", "run", ...])` (`cli/commands/test.py:55`) resolve their executable through `PATH` (B607 territory) and are never surfaced. With B110/B112 off, the 72 `except:` blocks that silently swallow failures are invisible.

**Fix** Replace the blanket `B404` / `B607` / `B110` / `B112` skips with per-site `# nosec` markers carrying a one-line justification, or adopt a `bandit-baseline.json` so new violations of those rules still fail the gate.

**Verify** `bandit -r nexy/ -c .bandit` reports only triaged findings, and a deliberate `subprocess.run(cmd, shell=True)` is flagged.

---

### [LOW] [VERIFIED] F8 — Five prebuilt `.vsix` binaries are tracked in git.

**Location** `extensions/vscode/nexy-0.0.1{5,6,7,8,9}.vsix`

**Evidence** `git ls-files | Select-String -Pattern '\.(vsix|whl|tar\.gz|zip|exe|node)$'` → the 5 `.vsix` files. `.gitignore` blocks `*.exe`, `*.dll`, `*.so` — but not `*.vsix`.

**Impact** A VSIX is an installable extension package. Five are committed, freezing their contents in history with no reproducible build and no in-repo provenance record. A release job that globs `extensions/vscode/*.vsix` can publish a stale or tampered artifact — and CI never builds the extension at all (F10), so nothing verifies any of them.

**Fix** Untrack them, add `*.vsix` to `.gitignore`, build in CI and publish the artifact from the CI run.

**Verify** `git ls-files | grep -c '\.vsix$'` → 0.

---

### [LOW] [VERIFIED] F9 — `.gitignore` blocks lockfiles that the project otherwise tracks.

**Location** `.gitignore:81-85`

**Evidence**
```
# Lock files (files, not directories)
bun.lock
**/bun.lock
pnpm-lock.yaml
**/pnpm-lock.yaml
```
Yet `git ls-files | Select-String -Pattern 'pnpm-lock\.yaml$|bun\.lock$|uv\.lock$'` → **26 tracked lockfiles**, including 10 `templates/web-*/` projects that each ship both a `pnpm-lock.yaml` and a `bun.lock` to every user of the framework.

**Impact** The ignore rule only affects untracked files, so the 26 tracked lockfiles keep working — but the policy is self-contradictory, and any *new* lockfile (a new template, a new example) requires `git add -f` and will be silently missed by a routine `git add`. This is a supply-chain inconsistency for the artifacts the framework ships: the dependency set a new user receives is not reproducible by default.

**Fix** Remove the lockfile lines from `.gitignore`, add `uv.lock` to the ignore-exempt set, then commit any lockfile that is currently ignored-but-needed.

**Verify** `git status --ignored --short | Select-String 'lock'` lists no lockfile that should be tracked.

---

### [LOW] [VERIFIED] F10 — `tests/` is neither linted nor type-checked in CI, and the TypeScript/JavaScript surfaces are never built.

**Location** `.github/workflows/ci.yml:26-39`

**Evidence**
- CI runs `ruff check nexy/`, `ruff format nexy/ --check`, `python -m mypy nexy --strict`, `python -m pytest tests/`. **`tests/` is never linted or type-checked.**
- `ruff check tests/` → `Found 53 errors.` (exit 1), measured on the current tree.
- No CI job for `extensions/vscode/` (TypeScript: own `package.json`, `pnpm-lock.yaml`, `vitest.config.ts`, `tsconfig.json`) and none for the 10 `templates/*/package.json` projects.
- The five gates that *do* exist are green today (see §5).

**Impact** Test code executes in CI and is a real supply-chain surface — a malicious fixture in a PR runs with the CI runner's credentials. 53 lint errors currently sit there unmonitored. The extension and the templates, the two things a user actually installs, are never built by the pipeline, so a broken template is discovered by the user rather than by CI.

**Fix** Add `ruff check tests/` and `ruff format tests/ --check` (after fixing the 53); add a `pnpm install --frozen-lockfile && pnpm run build` job for `extensions/vscode/`; add a template smoke-build matrix.

**Verify** CI shows the 2 extra Python steps and ≥1 new job; `pnpm -C extensions/vscode run build` succeeds on the runner.

---

### [LOW] [VERIFIED] F11 — The security-relevant work of this cycle is uncommitted; `HEAD` does not contain the controls the documentation describes.

**Location** working tree vs `fb5a829`

**Evidence** `git status --porcelain` → 58 paths: 49 modified, 9 untracked (`.bandit`, `tests/conftest.py`, `tests/integration/conftest.py`, `tests/unit/nexy/routers/test_tier_a.py`, `tests/unit/nexy/test_docstrings_google.py`, `tests/unit/nexy/test_error_paths.py`, `tests/unit/nexy/test_media_components.py`, `tests/unit/nexy/test_tier_a_surface.py`, `tests/unit/nexy/helpers/test_server.py`). `git ls-files --error-unmatch audit_session.log` → *"did not match any file(s) known to git"*.

**Impact** `HEAD` contains neither the `.bandit` registry, nor the current `fail_under = 54` coverage floor, nor the mypy fixes, nor the integration tests — `pyproject.toml` itself is modified but uncommitted. An audit of the committed SHA (which is what CI clones) sees the *old* state. The quality claims in `QUALITY_PLAN.md` §6.7 describe a tree that does not exist in the repository.

**Fix** Commit the working tree in atomic commits per the repo's Conventional Commits convention, with `.bandit` in its own commit so the security registry lands together with the documentation that references it.

**Verify** `git status --porcelain` is empty and `git ls-files .bandit` prints `.bandit`.

---

## 5. Non-findings

What was checked and found clean. This section is load-bearing — it marks the difference between *"checked and clean"* and *"not checked"*.

| # | Check | Result |
|---|---|---|
| 1 | **All 5 quality gates** | **Green.** `ruff check nexy/` → "All checks passed!" exit 0 · `ruff format nexy/ --check` → "126 files already formatted" exit 0 · `mypy nexy --strict` → "Success: no issues found in 126 source files" exit 0 · `pytest tests/` → "378 passed, 1 skipped in 6.62s" exit 0 · `pytest --cov=nexy` → "Required test coverage of 54.0% reached. Total coverage: 54.15%" exit 0 |
| 2 | **`shell=True` anywhere in `nexy/`** | **None.** The only two matches are explanatory comments (`utils/init/dependencies.py:54,82`). The B602 fix holds: `shutil.which(cmd[0]) or cmd[0]` + list args (`:55-56`, `:83-89`) |
| 3 | **Install-time code execution in any tracked `package.json`** | **None.** 0 `preinstall` / `install` / `postinstall` / `prepare` / `prepublish` hooks across all 43 tracked manifests |
| 4 | **Hardcoded secrets in `*.py`** | **None.** Regex for literal `password|secret|api_key|token|passwd` assignments ≥ 6 chars → 0 matches. *(Limited to `*.py` — see blind spots.)* |
| 5 | **Weak hashes (B324)** | **None.** The `usedforsecurity=False` fix holds — bandit reports no hashlib finding |
| 6 | **Import interception is scoped** | `NexyVFSFinder.find_spec` returns `None` for any module not prefixed `__nexy__` (`runtime/importer.py:48-49`), so the `sys.meta_path[0]` insertion does not shadow stdlib or site-packages |
| 7 | **`ast.parse` + `ast.unparse` do not weaken the frontmatter code** | Semantics are preserved exactly. F2 is a *missing* control, not a broken one |
| 8 | **Templates ship lockfiles** | 10 `templates/web-*/` each carry both `pnpm-lock.yaml` and `bun.lock`, so users of the *existing* templates receive pinned dependencies despite F9 |
| 9 | **Coverage gate is effective** | `fail_under = 54` in `pyproject.toml:127` is honoured by `pytest --cov=nexy` — the run reports "Required test coverage of 54.0% reached" and exits 0 |

---

## 6. Residual risk

1. ~~**No dependency CVE data was obtained.**~~ **Closed in the fix pass:** `pip-audit` now runs in CI against the frozen lock (result register in `SECURITY.md`), and the lock is hash-pinned. One advisory (PYSEC-2022-252) is ignored with written justification — see the register.
2. ~~**The `B701` Jinja2-autoescape decision is documented, not verified.**~~ **Traced in the fix pass:** the framework's own environments render author-authored sources only; the one place visitor-controlled data can flow unescaped is route path params (`[slug]` components) into author templates. Accepted with that boundary made explicit: it is the same default Jinja itself ships with; authors escape with `|e`. Documented in the `SECURITY.md` B701 register entry.
3. **Multi-step logic flaws are outside SAST's reach.** Bandit is pattern-matching; it structurally cannot detect the F2 class — a documented control that does not exist. A manual review of the `nexy/compiler/` → `nexy/runtime/` trust boundary is warranted and was **not** completed.
4. **`docs/` (separate repo) and the JS dependency trees of `templates/` were not audited.** The new CI `extension` job now builds + tscs `extensions/vscode/`, but **no npm SCA (`pnpm audit` / OSV) exists for the template lockfiles** — still unchecked at the time of this report's fix pass.
5. **The `0.0.0.0` bind default (B104) is accepted but unenforced.** `core/config.py:44`, `core/models.py:197`, `utils/common/constants.py:4` (`DEFAULT_HOST = "0.0.0.0"`), `utils/server/ports.py:12,25` — the dev server binds all interfaces by default. Documented as a deliberate default in the `SECURITY.md` B104 register entry.

---

## 7. Fix order

| Order | Finding | Effort |
|---|---|---|
| 1 | **F1** — `git add .bandit` | 1 minute |
| 2 | **F2** — decide (a) or (b); align `.bandit` + `SECURITY.md` with reality | 1 h for (a), days for (b) |
| 3 | **F4** — add `V2` to the `pull_request` trigger | 1 minute |
| 4 | **F6** — declare `bandit`, add the CI step | 15 minutes |
| 5 | **F5** — SHA-pin both actions | 10 minutes |
| 6 | **F3** — `uv lock` + `uv sync --frozen` + `pip-audit` | 1 hour |
| 7 | **F11** — commit the working tree | 1 hour |
| 8 | **F7, F8, F9, F10** — hygiene follow-ups | 1 day |
