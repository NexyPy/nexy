from nexy.helpers.init.resolver import TemplateResolver


def test_resolve_web_fbr() -> None:
    assert TemplateResolver.resolve({"FBRouter": True, "project_type": "web"}) == "web-fbr"


def test_resolve_web_modular() -> None:
    assert TemplateResolver.resolve({"FBRouter": False, "project_type": "web"}) == "web-modular"


def test_resolve_api_fbr() -> None:
    assert TemplateResolver.resolve({"FBRouter": True, "project_type": "api"}) == "api-fbr"


def test_resolve_api_modular() -> None:
    assert TemplateResolver.resolve({"FBRouter": False, "project_type": "api"}) == "api-modular"


def test_resolve_default_project_type_is_web() -> None:
    assert TemplateResolver.resolve({"FBRouter": True}) == "web-fbr"
