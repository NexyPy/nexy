from __future__ import annotations

import asyncio
import importlib.util
import json
import threading
import time
from collections import defaultdict
from pathlib import Path
from typing import Any

import typer

from nexy.core.config import Config
from nexy.i18n.i18n_decorator import _I18N_REGISTRY
from nexy.utils.common.console import console

_GOOGLE_LOCALE_MAP = {"zh": "zh-CN"}
_GOOGLE_RPS = 3.0


class _SyncRateLimiter:
    """Sync rate limiter with exponential backoff. Thread-safe."""

    def __init__(self, max_rps: float = _GOOGLE_RPS) -> None:
        self._max_rps = max_rps
        self._lock = threading.Lock()
        self._last_call = 0.0
        self._failures = 0
        self._last_fail = 0.0

    def wait(self) -> None:
        with self._lock:
            now = time.monotonic()
            backoff = min(2 ** self._failures, 30)
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


_sync_limiter = _SyncRateLimiter()


def _map_locale(locale: str) -> str:
    return _GOOGLE_LOCALE_MAP.get(locale, locale)


def _translate_batch(translator: Any, batch: list[str]) -> list[str]:
    """Translate a batch via deep_translator with rate limiting."""
    _sync_limiter.wait()
    try:
        result = translator.translate_batch(batch)
        _sync_limiter.report_success()
        return result
    except Exception as exc:
        _sync_limiter.report_failure()
        console.print(
            f"  [yellow]WARN[/yellow] translate_batch failed ({exc}), "
            f"retrying individually..."
        )
        results: list[str] = []
        for text in batch:
            _sync_limiter.wait()
            try:
                results.append(translator.translate(text))
            except Exception as exc2:
                console.print(
                    f"  [yellow]WARN[/yellow] translate('{text[:30]}…') "
                    f"failed ({exc2}), keeping original"
                )
                results.append(text)
        return results


def _translate_module_sync(
    target: str,
    module_name: str,
    cls_list: list[type],
    source_locale: str,
) -> tuple[str, str, dict[str, dict[str, str]]]:
    """Translate a single module for a target locale. Sync — runs in to_thread."""
    from deep_translator import GoogleTranslator

    try:
        translator = GoogleTranslator(
            source=_map_locale(source_locale), target=_map_locale(target)
        )
    except Exception as exc:
        console.print(
            f"  [red]ERROR[/red] GoogleTranslator({source_locale}→{target}) "
            f"failed: {exc}"
        )
        return (target, module_name, {})

    data: dict[str, dict[str, str]] = {}
    for cls in cls_list:
        class_name = cls.__qualname__
        defaults = cls.__i18n_defaults__
        if target == source_locale:
            data[class_name] = dict(defaults)
        else:
            keys = list(defaults.keys())
            values = list(defaults.values())
            if values:
                translated = _translate_batch(translator, values)
                data[class_name] = dict(zip(keys, translated))
            else:
                data[class_name] = {}
    return (target, module_name, data)


def _scan_i18n_classes(src_dir: Path) -> dict[str, type]:
    _I18N_REGISTRY.clear()
    for py_file in sorted(src_dir.rglob("*.py")):
        if py_file.stem == "__init__":
            continue
        rel_module = ".".join(py_file.relative_to(src_dir).with_suffix("").parts)
        try:
            spec = importlib.util.spec_from_file_location(rel_module, py_file)
            if spec and spec.loader:
                mod = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(mod)
        except Exception:
            continue
    return dict(_I18N_REGISTRY)


async def _translate_module_async(
    client: httpx.AsyncClient,
    target: str,
    module_name: str,
    cls_list: list[type],
    source_locale: str,
) -> tuple[str, str, dict[str, dict[str, str]]]:
    data: dict[str, dict[str, str]] = {}
    for cls in cls_list:
        class_name = cls.__qualname__
        defaults = cls.__i18n_defaults__
        if target == source_locale:
            data[class_name] = dict(defaults)
        else:
            keys = list(defaults.keys())
            values = list(defaults.values())
            if values:
                translated = await _translate_batch_async(
                    client, values, source_locale, target
                )
                data[class_name] = dict(zip(keys, translated))
            else:
                data[class_name] = {}
    return (target, module_name, data)


def _restructure(
    locales_data: dict[str, dict[str, dict[str, str]]],
) -> dict[str, dict[str, dict[str, str]]]:
    """Restructure {locale: {class: {attr: val}}} to {class: {locale: {attr: val}}}."""
    output: dict[str, dict[str, dict[str, str]]] = {}
    for locale, classes in locales_data.items():
        for class_name, attrs in classes.items():
            if class_name not in output:
                output[class_name] = {}
            output[class_name][locale] = attrs
    return output


async def _translate_async(
    tasks: list[tuple[str, str, list[type]]],
    source_locale: str,
) -> tuple[dict[str, dict[str, dict[str, dict[str, str]]]], bool]:
    """Schedule all translation tasks via asyncio.to_thread. 0 threads overhead."""
    module_results: dict[str, dict[str, dict[str, dict[str, str]]]] = {}
    total = len(tasks)
    completed = 0
    cancelled = False

    coros = [
        asyncio.to_thread(_translate_module_sync, t, m, cl, source_locale)
        for t, m, cl in tasks
    ]
    with console.status("") as status:
        for coro in asyncio.as_completed(coros):
            try:
                target, module_name, data = await coro
            except asyncio.CancelledError:
                console.print()
                console.print(
                    "  [yellow]\u26a0 Translation cancelled by user (Ctrl+C)[/yellow]"
                )
                cancelled = True
                break
            except Exception as exc:
                console.print(
                    f"  [red]ERROR[/red] ... failed: {exc}"
                )
                continue

            if module_name not in module_results:
                module_results[module_name] = {}
            module_results[module_name][target] = data
            completed += 1
            status.update(
                f"[dim]translated [yellow]{completed}[/yellow] / {total} tasks[/dim]\n"
                f"[green]nexy[/green] \u00bb [cyan]{target}[/cyan] \u2192 [dim]{module_name}[/dim]"
            )

    return module_results, cancelled


def translate(
    source: str = typer.Option("fr", "--source", "-s", help="Source locale code (default: fr)"),
    targets: list[str] = typer.Option(
        None,
        "--target",
        "-t",
        help="Target locale(s). Default: all configured locales except source.",
    ),
    locales_source_dir: str | None = typer.Option(
        None,
        "--dir",
        "-d",
        help="Source directory with @i18n() .py files "
        "(default: useLocalesSourceDir or src/locales/).",
    ),
    force: bool = typer.Option(False, "--force", "-f", help="Regenerate all files."),
) -> None:
    config = Config()
    source_locale = source
    default_locale = config.useDefaultLocale or "en"
    available = config.useLocales or [default_locale]

    if targets:
        target_locales = targets
    else:
        target_locales = [loc for loc in available if loc != source_locale]

    all_locales = list(dict.fromkeys([source_locale] + target_locales))

    src_dir = (
        Path(locales_source_dir)
        if locales_source_dir
        else Path.cwd() / (config.useLocalesSourceDir or "src/locales")
    )
    if not src_dir.exists():
        console.print(f"[red]Error:[/red] Source directory not found: {src_dir}")
        raise typer.Exit(1)

    with console.status("[dim]Scanning @i18n() classes…[/dim]") as status:
        classes = _scan_i18n_classes(src_dir)

    if not classes:
        console.print(f"[yellow]No @i18n() classes found in {src_dir}[/yellow]")
        raise typer.Exit(0)

    module_classes: dict[str, list[type]] = defaultdict(list)
    for cls in classes.values():
        module_classes[cls.__module__].append(cls)

    module_mtimes: dict[str, float] = {}
    for mod_path in module_classes:
        mod_file = src_dir / f"{mod_path.replace('.', '/')}.py"
        module_mtimes[mod_path] = mod_file.stat().st_mtime if mod_file.exists() else 0.0

    gen_dir = Path.cwd() / "__nexy__" / "i18n"
    gen_dir.mkdir(parents=True, exist_ok=True)

    total_keys = sum(len(cls.__i18n_defaults__) for cls in classes.values())
    console.print(
        f"[dim]Scanning[/dim] [green]\u2713[/green] "
        f"{len(classes)} classes, {total_keys} keys"
    )
    console.print(
        f"[dim]Translating[/dim] {source_locale} \u2192 "
        f"{', '.join(target_locales)}"
    )
    console.print(f"[dim]Source: {src_dir}[/dim]")
    console.print()

    tasks: list[tuple[str, str, list[type]]] = []
    skipped_modules: list[str] = []
    for module_name, cls_list in module_classes.items():
        gen_file = gen_dir / f"{module_name}.json"
        if gen_file.exists() and not force:
            if gen_file.stat().st_mtime >= module_mtimes[module_name]:
                skipped_modules.append(module_name)
                continue
        for target in all_locales:
            tasks.append((target, module_name, cls_list))

    total = len(tasks)
    if total == 0:
        console.print("  [dim]All modules are up to date.[/dim]\n")
        console.print("  [green]\u2713[/green] Translation complete")
        return

    module_results, cancelled = asyncio.run(
        _translate_async(tasks, source_locale)
    )

    if cancelled and not module_results:
        console.print()
        return

    # Write one consolidated file per module with all locales
    console.print()
    with console.status("[dim]Writing consolidated translation files…[/dim]") as status:
        for module_name, locales_data in module_results.items():
            output = _restructure(locales_data)
            gen_file = gen_dir / f"{module_name}.json"
            gen_file.write_text(
                json.dumps(output, indent=2, ensure_ascii=False) + "\n",
                encoding="utf-8",
            )
            locale_count = len(locales_data)
            class_count = len(output)
            console.print(
                f"  [green]\u2713[/green] {gen_file.name} "
                f"[dim]({class_count} classes, {locale_count} locales)[/dim]"
            )

    # Clean up legacy per-locale files (previous format)
    for old_file in sorted(gen_dir.glob("*.json")):
        stem = old_file.stem
        if any(stem.endswith(f".{loc}") for loc in all_locales):
            old_file.unlink()
            console.print(f"  [dim]cleanup: removed {old_file.name}[/dim]")

    if skipped_modules:
        console.print(
            f"  [dim]\u2014 {len(skipped_modules)} modules up to date, skipped[/dim]"
        )
 
    console.print("\n[green]\u2713[/green] Translation complete")
    console.print("  [dim]Restart the dev server to pick up new translations.[/dim]")
