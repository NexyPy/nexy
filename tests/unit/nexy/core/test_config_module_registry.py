"""Registry settings: where `nx add` reads releases from and whether signatures are required."""

from __future__ import annotations

from nexy.core.config import Config


def test_module_registry_defaults_to_the_public_service(nexy_project):
    nexy_project()
    assert Config().useModuleRegistry == "https://registry.nexypy.dev"


def test_module_registry_is_read_from_the_project_config(nexy_project):
    nexy_project('useModuleRegistry = "https://registry.example.com"')
    assert Config().useModuleRegistry == "https://registry.example.com"


def test_signed_modules_are_not_required_by_default(nexy_project):
    nexy_project()
    assert Config().useRequireSignedModules is False


def test_signed_modules_can_be_required(nexy_project):
    nexy_project("useRequireSignedModules = True")
    assert Config().useRequireSignedModules is True
