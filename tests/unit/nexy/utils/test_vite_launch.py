"""How Vite is started: local binary, custom dev script, PnP, bun without node."""

import json
from pathlib import Path

import pytest

from nexy.helpers.common import package_manager, vite_launch
from nexy.helpers.common.vite_launch import _plain_vite_args, vite_argv, vite_installed


def _project(tmp_path: Path, monkeypatch, *, vite=True, scripts=None, files=()):
    monkeypatch.chdir(tmp_path)
    if vite:
        entry = tmp_path / "node_modules" / "vite" / "bin" / "vite.js"
        entry.parent.mkdir(parents=True)
        entry.write_text("", encoding="utf-8")
    if scripts is not None:
        (tmp_path / "package.json").write_text(json.dumps({"scripts": scripts}), encoding="utf-8")
    for name in files:
        (tmp_path / name).write_text("", encoding="utf-8")


def _which(monkeypatch, **found: str):
    monkeypatch.setattr(vite_launch.shutil, "which", lambda name: found.get(name))
    monkeypatch.setattr(package_manager, "resolve", lambda name: found.get(name))


class TestPlainScripts:
    @pytest.mark.parametrize(
        ("script", "expected"),
        [
            ("vite", []),
            ("vite --mode staging", ["--mode", "staging"]),
            ("vite --config vite.custom.ts --port 4000 --host", ["--config", "vite.custom.ts"]),
            ("vite --port=4000", []),
        ],
    )
    def test_plain_vite_keeps_user_flags_but_not_port_or_host(self, script, expected):
        assert _plain_vite_args(script) == expected

    @pytest.mark.parametrize(
        "script", ["cross-env A=1 vite", "vite && echo done", "tsc && vite", "FOO=1 vite"]
    )
    def test_wrapped_or_chained_scripts_are_not_plain(self, script):
        assert _plain_vite_args(script) is None


class TestLocalBinary:
    def test_node_runs_the_local_vite(self, tmp_path, monkeypatch):
        _project(tmp_path, monkeypatch)
        _which(monkeypatch, node="/bin/node")
        argv = vite_argv(build=False, port=3456)
        assert argv[0] == "/bin/node" and argv[-3:] == ["--port", "3456", "--host"]

    def test_user_flags_from_a_plain_dev_script_are_forwarded(self, tmp_path, monkeypatch):
        _project(tmp_path, monkeypatch, scripts={"dev": "vite --mode staging"})
        _which(monkeypatch, node="/bin/node")
        argv = vite_argv(build=False, port=3456)
        assert argv[2:4] == ["--mode", "staging"]

    def test_build_ignores_the_dev_script(self, tmp_path, monkeypatch):
        _project(tmp_path, monkeypatch, scripts={"dev": "vite --mode staging"})
        _which(monkeypatch, node="/bin/node")
        assert vite_argv(build=True, port=1)[-1] == "build"
        assert "--mode" not in vite_argv(build=True, port=1)


class TestCustomDevScript:
    def test_custom_script_runs_through_the_package_manager(self, tmp_path, monkeypatch):
        _project(tmp_path, monkeypatch, scripts={"dev": "cross-env A=1 vite"}, files=["bun.lock"])
        _which(monkeypatch, node="/bin/node", bun="/bin/bun")
        assert vite_argv(build=False, port=3456) == [
            "/bin/bun",
            "run",
            "dev",
            "--port",
            "3456",
            "--host",
        ]

    def test_npm_needs_a_separator(self, tmp_path, monkeypatch):
        _project(tmp_path, monkeypatch, scripts={"dev": "tsc && vite"}, files=["package-lock.json"])
        _which(monkeypatch, node="/bin/node", npm="/bin/npm")
        assert vite_argv(build=False, port=1)[:4] == ["/bin/npm", "run", "dev", "--"]


class TestRuntimes:
    def test_bun_without_node_runs_vite_itself(self, tmp_path, monkeypatch):
        _project(tmp_path, monkeypatch, files=["bun.lock"])
        _which(monkeypatch, bun="/bin/bun")
        assert vite_argv(build=True, port=1)[0] == "/bin/bun"

    def test_no_runtime_at_all_is_a_clear_error(self, tmp_path, monkeypatch):
        _project(tmp_path, monkeypatch)
        _which(monkeypatch)
        with pytest.raises(RuntimeError, match="Node.js"):
            vite_argv(build=True, port=1)

    def test_missing_vite_names_the_install_command(self, tmp_path, monkeypatch):
        _project(tmp_path, monkeypatch, vite=False, files=["pnpm-lock.yaml"])
        _which(monkeypatch, node="/bin/node", pnpm="/bin/pnpm")
        with pytest.raises(RuntimeError, match="pnpm install"):
            vite_argv(build=True, port=1)


class TestPlugAndPlay:
    def test_pnp_is_installed_without_node_modules(self, tmp_path, monkeypatch):
        _project(tmp_path, monkeypatch, vite=False, files=[".pnp.cjs", "yarn.lock"])
        assert vite_installed()

    def test_pnp_uses_the_package_manager_runner(self, tmp_path, monkeypatch):
        _project(tmp_path, monkeypatch, vite=False, files=[".pnp.cjs", "yarn.lock"])
        _which(monkeypatch, node="/bin/node", yarn="/bin/yarn")
        assert vite_argv(build=True, port=1) == ["/bin/yarn", "vite", "build"]

    def test_nothing_installed_is_not_installed(self, tmp_path, monkeypatch):
        _project(tmp_path, monkeypatch, vite=False)
        assert not vite_installed()
