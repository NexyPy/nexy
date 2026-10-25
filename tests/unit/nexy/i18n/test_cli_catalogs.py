"""The command line speaks twelve languages, and each catalog is complete and consistent."""

from __future__ import annotations

import ast
import json
import re
import subprocess
import sys
from pathlib import Path

import pytest

from nexy.modules import i18n
from nexy.modules.i18n import _cli

PACKAGE = Path(i18n.__file__).parent
SOURCE = Path(_cli.__file__).resolve().parents[2]
PLACEHOLDER = re.compile(r"\{(\w+)\}")
EXPECTED = {"en", "zh", "hi", "es", "pt", "fr", "de", "ja", "ru", "ko", "id", "ar"}


def _flat(tree: dict, prefix: str = "") -> dict[str, str]:
    out: dict[str, str] = {}
    for key, value in tree.items():
        if isinstance(value, dict):
            out.update(_flat(value, f"{prefix}{key}."))
        else:
            out[f"{prefix}{key}"] = value
    return out


def _catalog(locale: str) -> dict[str, str]:
    return _flat(json.loads((PACKAGE / f"{locale}.json").read_text(encoding="utf-8")))


ENGLISH = _catalog("en")
LOCALES = sorted(EXPECTED - {"en"})


class TestSupportedLanguages:
    def test_twelve_languages_are_supported(self):
        assert set(_cli.SUPPORTED_LOCALES) == EXPECTED

    @pytest.mark.parametrize("locale", sorted(EXPECTED))
    def test_each_has_a_catalog(self, locale):
        assert (PACKAGE / f"{locale}.json").is_file()

    def test_there_is_no_catalog_for_an_unsupported_language(self):
        assert {p.stem for p in PACKAGE.glob("*.json")} == EXPECTED


class TestCatalogsAreComplete:
    @pytest.mark.parametrize("locale", LOCALES)
    def test_it_has_exactly_the_english_keys(self, locale):
        catalog = _catalog(locale)
        assert sorted(set(ENGLISH) - set(catalog)) == []
        assert sorted(set(catalog) - set(ENGLISH)) == []

    @pytest.mark.parametrize("locale", LOCALES)
    def test_no_message_is_empty(self, locale):
        assert [k for k, v in _catalog(locale).items() if not v.strip()] == []

    @pytest.mark.parametrize("locale", LOCALES)
    def test_it_keeps_the_placeholders_of_the_english_message(self, locale):
        catalog = _catalog(locale)
        wrong = [
            k
            for k, text in catalog.items()
            if set(PLACEHOLDER.findall(text)) != set(PLACEHOLDER.findall(ENGLISH[k]))
        ]
        assert wrong == []

    @pytest.mark.parametrize("locale", sorted(EXPECTED))
    def test_every_message_can_be_formatted(self, locale):
        # A stray brace would raise only when the message is shown, in front of a user.
        for key, text in _catalog(locale).items():
            text.format(**dict.fromkeys(PLACEHOLDER.findall(text), "x"))
            assert key


def _calls() -> dict[str, str | None]:
    found: dict[str, str | None] = {}
    for path in SOURCE.rglob("*.py"):
        relative = path.relative_to(SOURCE).as_posix()
        if relative.startswith(("modules/cli/templates", "modules/i18n/")):
            continue
        for node in ast.walk(ast.parse(path.read_text(encoding="utf-8"))):
            is_t = isinstance(node, ast.Call) and getattr(node.func, "id", "") == "t"
            if is_t and node.args and isinstance(node.args[0], ast.Constant):
                default = node.args[1] if len(node.args) > 1 else None
                found[node.args[0].value] = (
                    default.value if isinstance(default, ast.Constant) else None
                )
    return found


class TestCodeAndCatalogAgree:
    def test_every_message_the_code_asks_for_exists(self):
        assert sorted(set(_calls()) - set(ENGLISH)) == []

    def test_no_catalog_message_is_unused(self):
        assert sorted(set(ENGLISH) - set(_calls())) == []

    def test_the_default_in_the_code_is_the_english_message(self):
        differing = [k for k, d in _calls().items() if d is not None and ENGLISH[k] != d]
        assert differing == []


class TestLanguageDetection:
    @pytest.fixture(autouse=True)
    def _clean(self, monkeypatch):
        for name in ("NEXY_LANG", "LC_ALL", "LC_MESSAGES", "LANGUAGE", "LANG"):
            monkeypatch.delenv(name, raising=False)
        monkeypatch.setattr(_cli, "_operating_system_locale", lambda: None)
        _cli._detect_locale.cache_clear()
        yield
        _cli._detect_locale.cache_clear()

    @pytest.mark.parametrize(
        ("value", "expected"),
        [
            ("fr_FR.UTF-8", "fr"),
            ("pt_BR.UTF-8", "pt"),
            ("zh_CN.UTF-8", "zh"),
            ("zh-TW", "zh"),
            ("ja_JP", "ja"),
            ("ko-KR", "ko"),
            ("ru_RU", "ru"),
            ("de_DE@euro", "de"),
            ("hi_IN", "hi"),
            ("ar_EG", "ar"),
            ("id_ID", "id"),
            ("in_ID", "id"),
            ("EN_us", "en"),
        ],
    )
    def test_a_system_language_maps_to_a_supported_one(self, value, expected, monkeypatch):
        monkeypatch.setenv("LANG", value)
        assert _cli._detect_locale() == expected

    @pytest.mark.parametrize("value", ["C", "POSIX", "tr_TR", "", "xx"])
    def test_anything_else_falls_back_to_english(self, value, monkeypatch):
        monkeypatch.setenv("LANG", value)
        assert _cli._detect_locale() == "en"

    def test_nexy_lang_wins_over_the_system(self, monkeypatch):
        monkeypatch.setenv("LANG", "fr_FR")
        monkeypatch.setenv("NEXY_LANG", "ja")
        assert _cli._detect_locale() == "ja"

    def test_an_unsupported_nexy_lang_falls_back_to_the_system(self, monkeypatch):
        monkeypatch.setenv("LANG", "de_DE")
        monkeypatch.setenv("NEXY_LANG", "tlh")
        assert _cli._detect_locale() == "de"

    def test_language_lists_use_the_first_supported_entry(self, monkeypatch):
        monkeypatch.setenv("LANGUAGE", "tr:es:fr")
        assert _cli._detect_locale() == "es"

    def test_the_operating_system_is_the_last_resort(self, monkeypatch):
        monkeypatch.setattr(_cli, "_operating_system_locale", lambda: "pt_BR")
        assert _cli._detect_locale() == "pt"


class TestTranslate:
    def test_a_message_is_returned_in_the_requested_language(self):
        assert _cli.t("dev.restarting", locale="fr") == "Redémarrage..."

    def test_english_is_the_fallback_language(self, monkeypatch):
        monkeypatch.setattr(
            _cli, "_load_locale", lambda locale: {} if locale == "fr" else _cli_en()
        )
        assert _cli.t("dev.restarting", locale="fr") == "Restarting..."

    def test_an_unknown_key_returns_the_default_then_the_key(self):
        assert _cli.t("nope.nothing", "Fallback", locale="fr") == "Fallback"
        assert _cli.t("nope.nothing", locale="fr") == "nope.nothing"

    def test_a_group_is_not_a_message(self):
        assert _cli.t("dev", "Default", locale="fr") == "Default"

    def test_formatting_still_works_on_the_result(self):
        assert (
            _cli.t("watch.compiled", locale="de").format(path="a", time="1ms")
            == "a in 1ms kompiliert"
        )


def _cli_en() -> dict:
    return json.loads((PACKAGE / "en.json").read_text(encoding="utf-8"))


class TestTheCommandLineIsTranslated:
    def _run(self, language: str) -> str:
        code = "import sys; sys.argv = ['nexy', '--help']; from nexy.modules.cli import CLI; CLI()"
        done = subprocess.run(
            [sys.executable, "-c", code],
            capture_output=True,
            text=True,
            encoding="utf-8",
            env={**__import__("os").environ, "NEXY_LANG": language, "PYTHONIOENCODING": "utf-8"},
            timeout=120,
            check=False,
        )
        return done.stdout + done.stderr

    @pytest.mark.parametrize(
        ("language", "phrase"),
        [("fr", "Afficher la version"), ("ja", "バージョンを表示する"), ("ar", "عرض الإصدار")],
    )
    def test_help_follows_nexy_lang(self, language, phrase):
        assert phrase in self._run(language)

    def test_help_is_english_by_default(self):
        assert "Show version" in self._run("en")
