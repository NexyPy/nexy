from pathlib import Path

from nexy.modules.cli.init.renderer import TemplateRenderer


def _renderer(client_framework: str) -> TemplateRenderer:
    return TemplateRenderer(Path("src"), Path("dest"), {"client_framework": client_framework})


def test_resolve_target_matching_framework_keeps_jinja2() -> None:
    r = _renderer("react")
    assert r._resolve_target(Path("card.react.jinja2")) == Path("card.tsx.jinja2")


def test_resolve_target_wrong_framework_skips() -> None:
    r = _renderer("react")
    assert r._resolve_target(Path("card.vue.jinja2")) is None


def test_resolve_target_preact_maps_to_tsx() -> None:
    r = _renderer("preact")
    assert r._resolve_target(Path("card.preact.jinja2")) == Path("card.tsx.jinja2")


def test_resolve_target_bare_jinja2_gets_framework_ext() -> None:
    r = _renderer("react")
    assert r._resolve_target(Path("card.jinja2")) == Path("card.tsx.jinja2")


def test_resolve_target_none_framework_maps_to_nexy() -> None:
    r = _renderer("none")
    assert r._resolve_target(Path("card.jinja2")) == Path("card.nexy.jinja2")


def test_resolve_target_plain_file_unchanged() -> None:
    r = _renderer("react")
    assert r._resolve_target(Path("header.nexy")) == Path("header.nexy")
