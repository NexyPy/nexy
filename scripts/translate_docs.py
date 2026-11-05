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
import re
import shutil
import sys
import time
import urllib.parse
import urllib.request
from collections.abc import Callable, Collection
from pathlib import Path
from typing import Any

REPO = Path(__file__).resolve().parent.parent
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from sites.shared import i18n, translator  # noqa: E402

DOCS = REPO / "docs"
MANIFEST = "TRANSLATIONS.json"
# The endpoint the Chrome extension reads. It answers a page of text as one list of strings, while
# `translate_a/single` throttles a client that asks for many pages in a row, then answers 429 before
# it reads the query at all.
ENDPOINT = "https://translate.googleapis.com/translate_a/t?client=dict-chrome-ex"

# The language codes Google knows, for the twelve the site offers.
GOOGLE = {code: code for code in (language.code for language in i18n.LANGUAGES)}
GOOGLE["zh"] = "zh-CN"

Engine = Callable[[str, str], str]


def google(text: str, target: str) -> str:
    """One request to the public endpoint: the text in the target language."""
    query = urllib.parse.urlencode({"sl": "en", "tl": GOOGLE.get(target, target)})
    request = urllib.request.Request(
        f"{ENDPOINT}&{query}&q={urllib.parse.quote(text)}",
        headers={"User-Agent": "Mozilla/5.0"},
    )
    with urllib.request.urlopen(request, timeout=60) as answer:
        data = json.loads(answer.read().decode("utf-8"))
    return "".join(data)


def _pause(engine: Engine) -> None:
    """A local service is test-fast; the public one allows a few requests a second."""
    if engine is google:
        time.sleep(1.2)


def _indices(chunk: str) -> list[int]:
    return translator.placeholders(chunk)


def _keeps(answer: str, indices: list[int]) -> bool:
    """Whether the answer carries every placeholder of the piece, exactly once."""
    found = translator.placeholders(answer)
    return all(found.count(index) == 1 for index in indices)


def _request(
    chunk: str, target: str, engine: Engine, opening: Collection[int] | None = None
) -> str:
    """One answer of the service; the placeholders that open a line never travel.

    Nor do the blank lines around the text, which the service drops: they are put back as they
    were, and a piece with no words left is not sent at all.
    """
    body, openings = translator.leads(chunk, opening)
    words = body.strip()
    if not translator.has_words(words):
        return chunk
    start = body.index(words)
    answer = translator.heal(engine(words, target))
    whole = body[:start] + answer + body[start + len(words) :]
    return translator.respace(translator.with_leads(whole, openings) or whole, chunk)


def _ask(
    chunk: str, target: str, engine: Engine, retries: int, opening: Collection[int] | None
) -> str:
    """The service's answer, asked again while it throttles or loses a placeholder."""
    for attempt in range(1, retries + 1):
        try:
            answer = _request(chunk, target, engine, opening)
        except Exception as error:
            if attempt == retries:
                raise
            wait = attempt * 10
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


# A kept part that sticks to its word with no space around it: `[[7]]Routing` comes back as
# `Routing`, and `React.[[8]]` as `React.`, where the same part inside a sentence survives. Such a
# piece travels as the word alone, the part put back on the side it was.
_GLUED = re.compile(r"\A(\[\[\d+\]\])(\S+)\Z")
_GLUED_END = re.compile(r"\A(\S+)(\[\[\d+\]\])\Z")


def translate_chunk(
    chunk: str,
    target: str,
    engine: Engine,
    retries: int = 4,
    opening: Collection[int] | None = None,
) -> str:
    """One request, cut in two around a placeholder the service keeps losing.

    `opening` names the layout placeholders, kept out of the request when they open a line.
    """
    glued = _GLUED.match(chunk)
    if glued is not None:
        return glued[1] + translate_chunk(glued[2], target, engine, retries, opening)
    closing = _GLUED_END.match(chunk)
    if closing is not None:
        return translate_chunk(closing[1], target, engine, retries, opening) + closing[2]
    indices = _indices(chunk)
    answer = _ask(chunk, target, engine, retries, opening)
    if _keeps(answer, indices):
        return answer
    lost = _lost(answer, indices)
    at = chunk.find(f"[[{lost}]]")
    parts = translator.split(chunk, at) if at >= 0 else None
    if parts is None:
        raise RuntimeError(f"the service keeps losing placeholder {lost} in a chunk of {target}")
    head, between, tail = parts
    first = translate_chunk(head, target, engine, retries, opening)
    return first + between + translate_chunk(tail, target, engine, retries, opening)


def translate_markdown(markdown: str, target: str, engine: Engine = google) -> str:
    """A whole page in another language, its skeleton intact."""
    template, kept = translator.protect(translator.unwrap(markdown))
    shape = translator.structural(kept)
    translated = []
    for chunk in translator.chunks(template):
        translated.append(translate_chunk(chunk, target, engine, opening=shape))
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


def _manifest(root: Path) -> dict[str, Any]:
    path = root / MANIFEST
    if not path.is_file():
        return {"provider": "google", "pages": {}}
    return json.loads(path.read_text(encoding="utf-8"))


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8", newline="\n")


def source_pages(docs: Path) -> list[Path]:
    """The English pages: every Markdown of docs/ that is not inside a language tree."""
    return [docs / relative for relative in i18n.english_pages(docs)]


def _save(root: Path, manifest: dict[str, Any]) -> None:
    _write(root / MANIFEST, json.dumps(manifest, ensure_ascii=False, indent=1) + "\n")


def _translate_page(page: Path, target: Path, code: str, engine: Engine) -> bool:
    """Write one translated page; on a page the service keeps breaking, keep the old one."""
    try:
        text = translate_markdown(page.read_text(encoding="utf-8"), code, engine)
    except RuntimeError as error:
        print(f"[{code}] kept the previous version: {error}", flush=True)
        return False
    _write(target, text)
    return True


def refresh(
    docs: Path,
    code: str,
    pages: list[Path],
    engine: Engine = google,
    force: bool = False,
    limit: int | None = None,
) -> tuple[list[Path], list[Path]]:
    """Translate the changed pages into `docs/<code>/`; return those written and those failed.

    The manifest is saved after each page, so a run cut short resumes where it stopped.
    """
    root = docs / code
    manifest = _manifest(root)
    written: list[Path] = []
    failed: list[Path] = []
    selected = pages[:limit] if limit else pages
    for number, page in enumerate(selected, start=1):
        relative = page.relative_to(docs).as_posix()
        target, digest = root / relative, _digest(page)
        if not force and target.is_file() and manifest["pages"].get(relative, digest) == digest:
            continue
        print(f"[{code}] {number}/{len(selected)} {relative}", flush=True)
        if not _translate_page(page, target, code, engine):
            failed.append(page)
            continue
        manifest["pages"][relative] = digest
        written.append(target)
        _save(root, manifest)
    if written:
        _copy_assets(docs, root)
    return written, failed


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
    failures = 0
    for code in options.lang:
        written, failed = refresh(docs, code, pages, force=options.force, limit=options.limit)
        print(f"[{code}] {len(written)} page(s) written, {len(failed)} failed", flush=True)
        failures += len(failed)
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
