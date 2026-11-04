"""Translate the pages of docs/ into every language of the site, once, into files git keeps.

    python scripts/translate_docs.py                 # every language, pages whose source changed
    python scripts/translate_docs.py --lang fr,de    # two languages
    python scripts/translate_docs.py --force         # translate again, keep nothing

The English tree stays the source of truth. Each language gets its own copy under `docs/<code>/`,
with the same file names, so a translated page has the same slug and its relative links keep
working. `docs/<code>/TRANSLATIONS.json` remembers the hash of the English page each file came from:
an unchanged page is never sent twice. A page a human improved by hand stays as it is until its
English source changes, or `--force` says otherwise.

Code, link targets, table pipes and heading markers never reach the service: see
`sites/shared/translator.py`.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import sys
import time
import urllib.parse
import urllib.request
from collections.abc import Callable
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from sites.shared import i18n, translator  # noqa: E402

DOCS = REPO / "docs"
MANIFEST = "TRANSLATIONS.json"
ENDPOINT = "https://translate.googleapis.com/translate_a/single?client=gtx"

# The language codes Google knows, for the twelve the site offers.
GOOGLE = {code: code for code in (language.code for language in i18n.LANGUAGES)}
GOOGLE["zh"] = "zh-CN"

Engine = Callable[[str, str], str]


def google(text: str, target: str) -> str:
    """One request to the public endpoint: the text in the target language."""
    query = urllib.parse.urlencode({"sl": "en", "tl": GOOGLE.get(target, target), "dt": "t"})
    request = urllib.request.Request(
        f"{ENDPOINT}&{query}&q={urllib.parse.quote(text)}",
        headers={"User-Agent": "Mozilla/5.0"},
    )
    with urllib.request.urlopen(request, timeout=60) as answer:
        data = json.loads(answer.read().decode("utf-8"))
    return "".join(segment[0] for segment in data[0] if segment[0])


def _pause(engine: Engine) -> None:
    """A local service is test-fast; the public one allows a few requests a second."""
    if engine is google:
        time.sleep(0.4)


def _indices(chunk: str) -> list[int]:
    return translator.placeholders(chunk)


def _keeps(answer: str, indices: list[int]) -> bool:
    """Whether the answer carries every placeholder of the piece, exactly once."""
    found = translator.placeholders(answer)
    return all(found.count(index) == 1 for index in indices)


def _ask(chunk: str, target: str, engine: Engine, retries: int) -> str:
    """The service's answer, asked again while it throttles or loses a placeholder."""
    for attempt in range(1, retries + 1):
        try:
            answer = engine(chunk, target)
        except Exception as error:
            if attempt == retries:
                raise
            wait = attempt * 4
            print(f"  retry {attempt} in {wait}s: {type(error).__name__}", flush=True)
            time.sleep(wait)
            continue
        if _keeps(answer, _indices(chunk)):
            return answer
        print(f"  retry {attempt}: placeholder lost", flush=True)
        _pause(engine)
    return answer


def _lost(answer: str, indices: list[int]) -> int:
    """The first placeholder the answer dropped or repeated."""
    found = translator.placeholders(answer)
    return next(index for index in indices if found.count(index) != 1)


def translate_chunk(chunk: str, target: str, engine: Engine, retries: int = 4) -> str:
    """One request, cut in two around a placeholder the service keeps losing."""
    indices = _indices(chunk)
    answer = _ask(chunk, target, engine, retries)
    if _keeps(answer, indices):
        return answer
    lost = _lost(answer, indices)
    at = chunk.find(f"[[{lost}]]")
    parts = translator.split(chunk, at) if at >= 0 else None
    if parts is None:
        raise RuntimeError(f"the service keeps losing placeholder {lost} in a chunk of {target}")
    head, between, tail = parts
    return translate_chunk(head, target, engine) + between + translate_chunk(tail, target, engine)


def translate_markdown(markdown: str, target: str, engine: Engine = google) -> str:
    """A whole page in another language, its skeleton intact."""
    template, kept = translator.protect(markdown)
    translated = []
    for chunk in translator.chunks(template):
        translated.append(translate_chunk(chunk, target, engine))
        _pause(engine)
    text = translator.restore(translated, kept)
    captions = translator.captions(markdown)
    if captions:
        mapping = {}
        for caption in captions:
            mapping[caption] = translate_chunk(caption, target, engine)
            _pause(engine)
        text = translator.with_captions(text, mapping)
    return translator.tidy(text)


def _digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _manifest(root: Path) -> dict[str, object]:
    path = root / MANIFEST
    if not path.is_file():
        return {"provider": "google", "pages": {}}
    return json.loads(path.read_text(encoding="utf-8"))


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8", newline="\n")


def source_pages(docs: Path) -> list[Path]:
    """The English pages: every Markdown of docs/ that is not inside a language tree."""
    codes = {language.code for language in i18n.LANGUAGES}
    return sorted(
        path for path in docs.rglob("*.md") if not codes.intersection(path.relative_to(docs).parts)
    )


def refresh(
    docs: Path,
    code: str,
    pages: list[Path],
    engine: Engine = google,
    force: bool = False,
    limit: int | None = None,
) -> list[Path]:
    """Translate the changed pages into `docs/<code>/`; return those written."""
    root = docs / code
    manifest = _manifest(root)
    written: list[Path] = []
    selected = pages[:limit] if limit else pages
    for number, page in enumerate(selected, start=1):
        relative = page.relative_to(docs).as_posix()
        target = root / relative
        digest = _digest(page)
        if not force and target.is_file() and manifest["pages"].get(relative, digest) == digest:
            manifest["pages"][relative] = digest
            continue
        print(f"[{code}] {number}/{len(selected)} {relative}", flush=True)
        text = translate_markdown(page.read_text(encoding="utf-8"), code, engine)
        _write(target, text)
        manifest["pages"][relative] = digest
        written.append(target)
    if written:
        _write(root / MANIFEST, json.dumps(manifest, ensure_ascii=False, indent=1) + "\n")
        _copy_assets(docs, root)
    return written


def _copy_assets(docs: Path, root: Path) -> None:
    """A page reaches `../assets/…`: each tree carries the drawings so the path stays true."""
    if (docs / "assets").is_dir():
        shutil.copytree(docs / "assets", root / "assets", dirs_exist_ok=True)


def arguments(argv: list[str]) -> argparse.Namespace:
    every = [language.code for language in i18n.LANGUAGES if language.code != i18n.DEFAULT]
    parser = argparse.ArgumentParser(description="Translate docs/ into the languages of the site.")
    parser.add_argument("--lang", default="", help=f"comma list among {','.join(every)}")
    parser.add_argument("--force", action="store_true", help="translate again, keep nothing")
    parser.add_argument("--limit", type=int, default=None, help="pages per language, for a check")
    parser.add_argument("--docs", type=Path, default=DOCS, help="the English tree")
    options = parser.parse_args(argv)
    chosen = [code.strip() for code in options.lang.split(",") if code.strip()] or every
    unknown = [code for code in chosen if code not in every]
    if unknown:
        parser.error(f"unknown language: {', '.join(unknown)}")
    options.lang = chosen
    return options


def main(argv: list[str] | None = None) -> int:
    options = arguments(sys.argv[1:] if argv is None else argv)
    docs: Path = options.docs
    pages = source_pages(docs)
    for code in options.lang:
        written = refresh(docs, code, pages, force=options.force, limit=options.limit)
        print(f"[{code}] {len(written)} page(s) written", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
