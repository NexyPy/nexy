"""Which file of a template goes where, for which framework, and what a render writes."""

from pathlib import Path

import pytest

from nexy.modules.cli.init.renderer import PARTIALS_DIR, TemplateRenderer, resolve_target


class TestResolveTarget:
    def test_matching_framework_keeps_jinja2(self) -> None:
        assert resolve_target(Path("card.react.jinja2"), "react") == Path("card.tsx.jinja2")

    def test_wrong_framework_skips(self) -> None:
        assert resolve_target(Path("card.vue.jinja2"), "react") is None

    def test_preact_maps_to_tsx(self) -> None:
        assert resolve_target(Path("card.preact.jinja2"), "preact") == Path("card.tsx.jinja2")

    def test_bare_jinja2_gets_framework_ext(self) -> None:
        assert resolve_target(Path("card.jinja2"), "react") == Path("card.tsx.jinja2")

    def test_none_framework_maps_to_nexy(self) -> None:
        assert resolve_target(Path("card.jinja2"), "none") == Path("card.nexy.jinja2")

    def test_plain_file_unchanged(self) -> None:
        assert resolve_target(Path("header.nexy"), "react") == Path("header.nexy")

    def test_the_folder_is_kept(self) -> None:
        assert resolve_target(Path("a/b/card.react.jinja2"), "react") == Path("a/b/card.tsx.jinja2")

    def test_the_framework_name_is_case_insensitive(self) -> None:
        assert resolve_target(Path("card.react.jinja2"), "React") == Path("card.tsx.jinja2")

    def test_a_file_with_an_extension_keeps_it(self) -> None:
        assert resolve_target(Path("theme.tsx.jinja2"), "react") == Path("theme.tsx.jinja2")

    def test_a_plain_file_for_another_framework_is_skipped(self) -> None:
        assert resolve_target(Path("card.svelte"), "react") is None

    def test_an_unknown_framework_adds_no_extension(self) -> None:
        assert resolve_target(Path("card.jinja2"), "") == Path("card.jinja2")


@pytest.fixture
def template(tmp_path: Path) -> Path:
    src = tmp_path / "tpl"
    (src / "src").mkdir(parents=True)
    (src / "src" / "page.jinja2").write_text("name={{ name }}", encoding="utf-8")
    (src / "src" / "empty.txt.jinja2").write_text("{% if false %}x{% endif %}", encoding="utf-8")
    (src / "src" / "raw.txt").write_text("copied", encoding="utf-8")
    (src / "src" / "only-vue.vue.jinja2").write_text("vue", encoding="utf-8")
    (src / "hollow").mkdir()
    return src


def _render(src: Path, dest: Path, framework: str = "react", exclude=None) -> Path:
    TemplateRenderer(src, dest, {"client_framework": framework, "name": "x"}, exclude).render()
    return dest


class TestRender:
    def test_a_template_is_rendered_with_the_context(self, template, tmp_path):
        dest = _render(template, tmp_path / "out")
        assert (dest / "src" / "page.tsx").read_text(encoding="utf-8") == "name=x"

    def test_a_plain_file_is_copied(self, template, tmp_path):
        assert (_render(template, tmp_path / "out") / "src" / "raw.txt").read_text() == "copied"

    def test_a_template_that_renders_to_nothing_writes_nothing(self, template, tmp_path):
        assert not (_render(template, tmp_path / "out") / "src" / "empty.txt").exists()

    def test_a_file_of_another_framework_is_left_out(self, template, tmp_path):
        assert not (_render(template, tmp_path / "out") / "src" / "only-vue.vue").exists()

    def test_the_file_of_the_chosen_framework_is_kept(self, template, tmp_path):
        assert (_render(template, tmp_path / "out", "vue") / "src" / "only-vue.vue").is_file()

    def test_an_excluded_kind_is_not_written(self, template, tmp_path):
        dest = _render(template, tmp_path / "out", exclude={".tsx"})
        assert not (dest / "src" / "page.tsx").exists()

    def test_folders_left_empty_are_removed(self, template, tmp_path):
        assert not (_render(template, tmp_path / "out") / "hollow").exists()

    def test_a_missing_template_folder_is_an_error(self, tmp_path):
        with pytest.raises(FileNotFoundError):
            TemplateRenderer(tmp_path / "nope", tmp_path / "out").render()

    def test_the_shared_partials_can_be_included(self, tmp_path):
        src = tmp_path / "tpl"
        src.mkdir()
        partial = next(PARTIALS_DIR.glob("footer.html.jinja2")).name
        (src / "page.html.jinja2").write_text(f"{{% include '{partial}' %}}", encoding="utf-8")
        context = {"client_framework": "react", "cls": "class", "nexy_version": "1"}
        TemplateRenderer(src, tmp_path / "out", context).render()
        assert "<footer" in (tmp_path / "out" / "page.html").read_text(encoding="utf-8")
