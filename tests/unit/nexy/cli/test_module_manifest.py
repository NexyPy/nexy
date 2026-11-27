"""The `nx.toml` inside a release archive tells `nx add` what it may change."""

from __future__ import annotations

import textwrap

import pytest

from nexy.modules.cli.add.manifest import ManifestError, parse_manifest


def manifest(body: str = "") -> str:
    return (
        textwrap.dedent(
            """
        name = "@acme/auth"
        version = "1.2.0"
        kind = "source"

        [[migrations]]
        argv = ["alembic", "upgrade", "head"]

        [compatibility]
        nexy = ">=2.0.0"
        python = ">=3.12"

        [dependencies]
        python = ["argon2-cffi"]
        node = ["zod"]

        [source]
        files = ["src/auth.py"]

        [config.nexyconfig]
        useSiteUrl = "https://example.com"

        [config.package_json]
        "devDependencies.vitest" = "^3"
        """
        )
        + body
    )


def test_parse_manifest_reads_a_source_module():
    parsed = parse_manifest(manifest())
    assert parsed.files == ("src/auth.py",)


def test_parse_manifest_reads_dependencies():
    parsed = parse_manifest(manifest())
    assert (parsed.python_dependencies, parsed.node_dependencies) == (
        ("argon2-cffi",),
        ("zod",),
    )


def test_parse_manifest_reads_config_hooks():
    parsed = parse_manifest(manifest())
    assert parsed.config["nexyconfig"]["useSiteUrl"] == "https://example.com"


def test_parse_manifest_reads_migration_argv():
    parsed = parse_manifest(manifest())
    assert parsed.migrations == (("alembic", "upgrade", "head"),)


def test_parse_manifest_reads_a_package_module():
    text = textwrap.dedent(
        """
        name = "@acme/auth"
        version = "1.2.0"
        kind = "package"

        [compatibility]
        nexy = ">=2.0.0"
        python = ">=3.12"

        [dependencies]
        python = []
        node = []

        [source]
        package = "nexy-auth"
        """
    )
    assert parse_manifest(text).package == "nexy-auth"


@pytest.mark.parametrize("bad", ["../secret.py", "/etc/passwd", "src\\secret.py", "a/../../b"])
def test_parse_manifest_refuses_a_file_outside_the_module(bad):
    with pytest.raises(ManifestError, match="relative path"):
        parse_manifest(manifest().replace('files = ["src/auth.py"]', f"files = ['{bad}']"))


@pytest.mark.parametrize("bad", ["pkg; rm -rf /", "pkg && whoami", "pkg\\nrm", "pkg | tee x"])
def test_parse_manifest_refuses_a_dependency_with_a_shell_separator(bad):
    with pytest.raises(ManifestError, match="unsafe"):
        parse_manifest(manifest().replace('python = ["argon2-cffi"]', f'python = ["{bad}"]'))


@pytest.mark.parametrize("bad", ["__import__", "useAuth; import os", "a-b"])
def test_parse_manifest_refuses_an_unsafe_config_key(bad):
    with pytest.raises(ManifestError, match="config key"):
        parse_manifest(manifest().replace("useSiteUrl", f'"{bad}"'))


def test_parse_manifest_refuses_a_shell_migration():
    with pytest.raises(ManifestError, match="migration"):
        parse_manifest(
            manifest().replace('argv = ["alembic", "upgrade", "head"]', 'argv = "alembic"')
        )


def test_parse_manifest_refuses_an_unknown_module_kind():
    with pytest.raises(ManifestError, match="kind"):
        parse_manifest(manifest().replace('kind = "source"', 'kind = "script"'))


def test_parse_manifest_refuses_a_module_without_a_namespace():
    with pytest.raises(ManifestError, match="name"):
        parse_manifest(manifest().replace('name = "@acme/auth"', 'name = "auth"'))


def test_parse_manifest_refuses_bad_toml():
    with pytest.raises(ManifestError, match="valid TOML"):
        parse_manifest("name = ")


@pytest.mark.parametrize(
    ("old", "new", "message"),
    [
        ('version = "1.2.0"', 'version = "latest"', "version"),
        ('python = ["argon2-cffi"]', 'python = ""', "dependency must be a list"),
        ('python = ["argon2-cffi"]', 'python = [""]', "dependency is empty"),
        ('files = ["src/auth.py"]', 'files = ""', "files must be a list"),
        ('files = ["src/auth.py"]', 'files = [""]', "relative path"),
        ('files = ["src/auth.py"]', "files = []", "at least one file"),
        ("[config.nexyconfig]", "[config.unknown]", "unknown config section"),
        (
            '[config.nexyconfig]\nuseSiteUrl = "https://example.com"',
            '[config]\nnexyconfig = "x"',
            "must be a table",
        ),
        (
            'useSiteUrl = "https://example.com"',
            'useSiteUrl = { value = "x" }',
            "scalar or a list",
        ),
        ('"devDependencies.vitest"', '"../bad"', "config key"),
        (
            '[[migrations]]\nargv = ["alembic", "upgrade", "head"]',
            'migrations = "alembic"',
            "migrations must be a list",
        ),
        (
            '[[migrations]]\nargv = ["alembic", "upgrade", "head"]',
            'migrations = ["alembic"]',
            "migration must be a table",
        ),
        ('argv = ["alembic", "upgrade", "head"]', 'argv = ""', "migration must be a list"),
    ],
)
def test_parse_manifest_refuses_an_invalid_shape(old, new, message):
    with pytest.raises(ManifestError, match=message):
        parse_manifest(manifest().replace(old, new))


def test_parse_manifest_ignores_a_section_that_is_not_a_table():
    text = manifest().replace(
        '[compatibility]\nnexy = ">=2.0.0"\npython = ">=3.12"', 'compatibility = "x"'
    )
    assert parse_manifest(text).nexy_version == ""


def test_parse_manifest_refuses_a_package_module_without_a_package():
    text = textwrap.dedent(
        """
        name = "@acme/auth"
        version = "1.2.0"
        kind = "package"

        [compatibility]
        nexy = ">=2.0.0"
        python = ">=3.12"

        [dependencies]
        python = []
        node = []

        [source]
        package = ""
        """
    )
    with pytest.raises(ManifestError, match="package module needs"):
        parse_manifest(text)
