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
