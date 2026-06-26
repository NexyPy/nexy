"""Translate MDX documentation pages while preserving code blocks, inline code, and URLs.

Batch translates all text segments per file in a single API call.

Usage:
    cd docs && uv run python ../scripts/translate_mdx.py
"""

from __future__ import annotations

import asyncio
import re
import sys
import threading
import time
from pathlib import Path

_GOOGLE_RPS = 3.0
_GOOGLE_LOCALE_MAP: dict[str, str] = {"zh": "zh-CN"}
_MAX_WORKERS = 8


class _SyncRateLimiter:
    def __init__(self, max_rps: float = _GOOGLE_RPS) -> None:
        self._max_rps = max_rps
        self._lock = threading.Lock()
        self._last_call = 0.0
        self._failures = 0
        self._last_fail = 0.0

    def wait(self) -> None:
        with self._lock:
            now = time.monotonic()
            backoff = min(2**self._failures, 30)
            wait = 0.0
            if self._failures > 0 and now - self._last_fail < backoff:
                wait = backoff - (now - self._last_fail)
            else:
                wait = max(0.0, (1.0 / self._max_rps) - (now - self._last_call))
            self._last_call = time.monotonic()
        if wait > 0:
            time.sleep(wait)

    def report_success(self) -> None:
        with self._lock:
            self._failures = max(0, self._failures - 1)

    def report_failure(self) -> None:
        with self._lock:
            self._failures = min(self._failures + 1, 10)
            self._last_fail = time.monotonic()


_limiter = _SyncRateLimiter()


def _map_locale(locale: str) -> str:
    return _GOOGLE_LOCALE_MAP.get(locale, locale)


_INLINE_CODE_RE = re.compile(r"(`[^`]+`)")
_MD_LINK_RE = re.compile(r"(\[[^\]]*\]\([^)]*\))")
_RAW_URL_RE = re.compile(r"(https?://[^\s<>\"']+)")
_JSX_TAG_RE = re.compile(r"(<[A-Z][^>]*>[^<]*</[A-Z][^>]*>|<[A-Z][^>]*/>)")


def _protect(text: str) -> tuple[str, list[tuple[str, str]]]:
    placeholders: list[tuple[str, str]] = []

    def _replace(pat: re.Pattern[str], prefix: str, txt: str) -> str:
        def _replacer(m: re.Match) -> str:
            idx = len(placeholders)
            ph = f"%%{prefix}{idx}%%"
            placeholders.append((ph, m.group(1)))
            return ph
        return pat.sub(_replacer, txt)

    text = _replace(_JSX_TAG_RE, "J", text)
    text = _replace(_MD_LINK_RE, "L", text)
    text = _replace(_RAW_URL_RE, "U", text)
    text = _replace(_INLINE_CODE_RE, "C", text)
    return text, placeholders


def _restore(text: str, placeholders: list[tuple[str, str]]) -> str:
    for ph, orig in placeholders:
        text = text.replace(ph, orig)
    return text


_CODE_FENCE_RE = re.compile(r"^(```+)\w*\s*\n.*?^\1\s*$", re.MULTILINE | re.DOTALL)
_FRONTMATTER_RE = re.compile(r"^---\s*\n(.*?\n)---\s*\n?", re.DOTALL)


def parse_mdx(content: str) -> list[dict]:
    segments: list[dict] = []

    fm_match = _FRONTMATTER_RE.match(content)
    if fm_match:
        segments.append({"type": "fm", "content": fm_match.group(0)})
        content = content[fm_match.end():]

    pos = 0
    for cb in _CODE_FENCE_RE.finditer(content):
        if cb.start() > pos:
            raw = content[pos:cb.start()]
            protected, phs = _protect(raw)
            segments.append({"type": "txt", "content": protected, "phs": phs})
        segments.append({"type": "code", "content": cb.group(0)})
        pos = cb.end()

    if pos < len(content):
        raw = content[pos:]
        protected, phs = _protect(raw)
        segments.append({"type": "txt", "content": protected, "phs": phs})

    return segments


def _translate_page_sync(
    source_path: Path, target: str, source_locale: str
) -> str | None:
    """Translate one file. All text segments batched in a single API call."""
    from deep_translator import GoogleTranslator

    content = source_path.read_text(encoding="utf-8")
    segments = parse_mdx(content)

    try:
        translator = GoogleTranslator(
            source=_map_locale(source_locale), target=_map_locale(target)
        )
    except Exception as exc:
        print(f"  [ERROR] translator({source_locale}->{target}) failed: {exc}", file=sys.stderr)
        return None

    # Collect all text segments to batch-translate
    txt_segs = [s for s in segments if s["type"] == "txt" and s["content"].strip()]
    txt_texts = [s["content"].strip() for s in txt_segs]

    translated_map: dict[int, str] = {}
    if txt_texts:
        # Batch translate all texts at once
        _limiter.wait()
        try:
            results = translator.translate_batch(txt_texts)
            _limiter.report_success()
        except Exception as exc:
            _limiter.report_failure()
            print(f"  [WARN] batch translate failed ({exc}), falling back individually", file=sys.stderr)
            results = []
            for t in txt_texts:
                _limiter.wait()
                try:
                    results.append(translator.translate(t))
                    _limiter.report_success()
                except Exception as exc2:
                    _limiter.report_failure()
                    print(f"  [WARN] translate '{t[:40]}...' failed ({exc2}), keeping original", file=sys.stderr)
                    results.append(t)
        for idx, translated in enumerate(results):
            translated_map[id(txt_segs[idx])] = translated

    out: list[str] = []
    for seg in segments:
        if seg["type"] == "txt":
            text = seg["content"].strip()
            if not text:
                out.append(seg["content"])
            else:
                translated = translated_map.get(id(seg), text)
                translated = _restore(translated, seg["phs"])
                if text in seg["content"]:
                    out.append(seg["content"].replace(text, translated))
                else:
                    out.append(translated)
        else:
            out.append(seg["content"])

    return "".join(out)


async def _translate_one(
    mdx_path: Path, target: str, source_locale: str, sem: asyncio.Semaphore
) -> tuple[str, bool]:
    async with sem:
        docs_dir = Path("src/routes/docs")
        rel = mdx_path.relative_to(docs_dir)
        variant = mdx_path.with_name(f"{mdx_path.stem}.{target}.mdx")
        if not variant.exists():
            return (f"{rel} -> {target}", False)

        translated = await asyncio.to_thread(
            _translate_page_sync, mdx_path, target, source_locale
        )
        if translated is None:
            return (f"{rel} -> {target}", False)

        variant.write_text(translated, encoding="utf-8")
        return (f"{rel} -> {target}", True)


async def main() -> None:
    from nexy.core.config import Config

    cfg = Config()
    locales = cfg.useLocales or []
    if not locales:
        print("No locales configured in nexyconfig.py (useLocales)", file=sys.stderr)
        sys.exit(1)

    source_locale = cfg.useDefaultLocale or "en"
    target_locales = [loc for loc in locales if loc != source_locale]
    if not target_locales:
        print("No target locales")
        return

    docs_dir = Path("src/routes/docs")
    if not docs_dir.is_dir():
        print(f"Directory not found: {docs_dir}", file=sys.stderr)
        sys.exit(1)

    mdx_files = sorted(docs_dir.rglob("*.mdx"))
    base_files = [f for f in mdx_files if f.stem.count(".") == 0]

    tasks: list[tuple[Path, str]] = []
    for mdx_path in base_files:
        for target in target_locales:
            tasks.append((mdx_path, target))

    total = len(tasks)
    if total == 0:
        print("No files to translate")
        return

    print(f"Translating {len(base_files)} pages x {len(target_locales)} locales = {total} files", flush=True)

    sem = asyncio.Semaphore(_MAX_WORKERS)
    done = errors = 0
    start = time.perf_counter()

    coros = [_translate_one(p, t, source_locale, sem) for p, t in tasks]
    for coro in asyncio.as_completed(coros):
        msg, ok = await coro
        if ok:
            done += 1
        else:
            errors += 1
        elapsed = time.perf_counter() - start
        rate = done / elapsed if elapsed > 0 else 0
        eta = (total - done) / rate if rate > 0 else 0
        print(f"  [{done}/{total}] {msg}  ({rate:.1f}/s, ETA {eta:.0f}s)", flush=True)

    elapsed = time.perf_counter() - start
    print(f"\nDone: {done} translated, {errors} errors in {elapsed:.0f}s", flush=True)


if __name__ == "__main__":
    asyncio.run(main())
