# Changelog

## [Unreleased]

### Security
- Sandboxed `exec()` via `nexy/core/sandbox.py`: restricted builtins whitelist,
  dangerous names (`__import__`, `open`, `exec`, `eval`, `compile`) denied.
  Applied to `template.py:91` and `runtime/mdx.py:250`.

### Performance
- `routers/fbrouter/discovery.py`: `rglob("*")` → targeted `glob("**/*.{ext}")`.
- `frontend/__init__.py`: same pattern for key generation.
- `builder/__init__.py`: sequential compile → `ThreadPoolExecutor(os.cpu_count())`.

### Fixed
- `WATCH_EXTENSIONS_GLOB` no longer silently overrides user-supplied config.
- Circular import in `hooks.py` (`from nexy import Vite` → `from nexy.vite import Vite`).
- Dead code in `sanitizer.py` (duplicate `RE_NEXY_IMPORT` after return statement).
- `B904` bare raises in `clone.py` (3 sites).

### Changed
- `__pycache__` centralized to `__nexy__/__pycache__` via `pycache()`.
- `VFS.set_dev_mode(True)` prevents `flush_to_disk()` during `nexy dev`.
- `FFModel` → `FrontendFramework`, `FF_REGISTRY` → `FRAMEWORK_REGISTRY`.
- `NCC` → `NexyClientComponent`, `_emit_ncc` → `_emit_client_component`.
- `_ndp`/`_ndc`/`_ngp` suffixes → `_dynamic_param`/`_catch_all`/`_group`.
- `CODE_PARSED` → `code_parsed`, `C` → `COLORS`.
- `NexyVFSLoader` → `NexyTemplateLoader`.
- `__version__.py`: class `__Version__().get()` → plain string `__version__`.
- Removed 9 empty non-init `.py` files; populated `core/types.py` with `JsonResponse`.
- Translated 38 French comments to English across 8 files.
- Extracted inline CSS from `errors.py` into `_page_404()`/`_page_500()` helpers.
- Removed dead `Task()`/`Job()` stubs from `decorators.py`.

### Added
- Tests: sandbox (9), VFS dev mode (3), builder parallel (1), pycache (1),
  version (3), string transform (13) — 30 new tests, 84 total pass.
- CI workflow (`.github/workflows/ci.yml`): ruff → mypy → pytest on 3.12/3.13.
