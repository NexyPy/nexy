import pytest

from nexy.modules.cli.init.registry import (
    GITHUB_TEMPLATES,
    TemplateNotFoundError,
    template_source,
)


def test_source_github_framework_template() -> None:
    assert template_source("web-fbr-react") == "github"


def test_source_github_api_template() -> None:
    assert template_source("api-modular") == "github"


def test_source_bundled_generic_template() -> None:
    assert template_source("web-modular") == "bundled"


def test_unknown_template_raises() -> None:
    with pytest.raises(TemplateNotFoundError):
        template_source("totoro")


def test_github_templates_contain_framework_variants() -> None:
    assert "web-fbr-solid" in GITHUB_TEMPLATES
    assert "web-modular-preact" in GITHUB_TEMPLATES


class TestTemplateConfig:
    """`nx new --template NAME` has no prompts: the name alone says what to generate."""

    def test_a_fbr_web_template(self) -> None:
        from nexy.modules.cli.init.resolver import TemplateResolver

        config = TemplateResolver.config_for("web-fbr")
        assert config["project_type"] == "web" and config["FBRouter"] is True
        assert config["client_framework"] == "none" and config["useCSR"] is False

    def test_a_modular_api_template(self) -> None:
        from nexy.modules.cli.init.resolver import TemplateResolver

        config = TemplateResolver.config_for("api-modular")
        assert config["project_type"] == "api" and config["FBRouter"] is False

    def test_a_framework_variant_names_its_framework(self) -> None:
        from nexy.modules.cli.init.resolver import TemplateResolver

        assert TemplateResolver.config_for("web-fbr-react")["client_framework"] == "react"

    def test_the_resolver_and_the_config_agree(self) -> None:
        from nexy.modules.cli.init.resolver import TemplateResolver

        for name in ("web-fbr", "web-modular", "api-fbr", "api-modular"):
            assert TemplateResolver.resolve(TemplateResolver.config_for(name)) == name

    def test_a_bundled_fbr_project_is_not_generated_as_modular(self, tmp_path) -> None:
        from nexy.modules.cli.init.resolver import TemplateResolver
        from nexy.modules.cli.init.template_setup import _render_local_template

        _render_local_template("web-fbr", tmp_path, TemplateResolver.config_for("web-fbr"), "demo")
        config = (tmp_path / "nexyconfig.py").read_text(encoding="utf-8")
        assert "AppModule" not in config
        assert (tmp_path / "src" / "routes" / "index.nexy").is_file()
