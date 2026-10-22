import sys
import textwrap
from pathlib import Path

import pytest

from nexy.core.config import Config


@pytest.fixture
def nexy_project(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    """Scaffold an isolated user project with its own nexyconfig.py.

    Returns a ``configure`` helper: call it with the attribute lines of the
    ``NexyConfig`` class body (e.g. ``"useVite = True"``) BEFORE the first
    ``Config()`` call of the test. The test cwd becomes ``tmp_path``.

    Isolation guarantees:
    - the Config singleton is reset on configure and after the test, so every
      user config stays local to its test;
    - class attributes mutated by Config._load are restored from a snapshot;
    - the synthetic ``nexyconfig`` module is dropped from sys.modules.
    """
    class_snapshot = {k: v for k, v in vars(Config).items() if not k.startswith("__")}
    monkeypatch.chdir(tmp_path)

    def configure(attrs: str = "", imports: str = "") -> None:
        Config._instance = None
        Config._loaded = False
        Config._load_error = None
        sys.modules.pop("nexyconfig", None)
        body = textwrap.indent(textwrap.dedent(attrs).strip(), "    ") or "    pass"
        extra_imports = ""
        if imports.strip():
            extra_imports = textwrap.dedent(imports).strip() + "\n"
        (tmp_path / "nexyconfig.py").write_text(
            "from nexy.core.models import NexyConfigModel\n"
            f"{extra_imports}"
            "\n"
            "\n"
            f"class NexyConfig(NexyConfigModel):\n{body}\n",
            encoding="utf-8",
        )
        monkeypatch.syspath_prepend(str(tmp_path))

    yield configure

    sys.modules.pop("nexyconfig", None)
    current_keys = {k for k in vars(Config) if not k.startswith("__")}
    for key, value in class_snapshot.items():
        setattr(Config, key, value)
    for key in current_keys - set(class_snapshot):
        delattr(Config, key)
