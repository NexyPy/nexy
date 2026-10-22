import pytest

from nexy.modules.cli.init.project import AlreadyInitializedError, InitProject
from nexy.modules.cli.init.template_setup import generate_init_files


def test_ensure_ready_skips_for_new_project(tmp_path) -> None:
    project = InitProject()
    project._ensure_ready(tmp_path, project_dir="myapp")


def test_ensure_ready_raises_when_nexyconfig_present(tmp_path) -> None:
    (tmp_path / "nexyconfig.py").write_text("")
    project = InitProject()
    with pytest.raises(AlreadyInitializedError):
        project._ensure_ready(tmp_path, None)


def test_ensure_ready_raises_when_nexy_dir_present(tmp_path) -> None:
    (tmp_path / "__nexy__").mkdir()
    project = InitProject()
    with pytest.raises(AlreadyInitializedError):
        project._ensure_ready(tmp_path, None)


def test_generate_init_files_creates_for_python_dirs(tmp_path) -> None:
    (tmp_path / "src" / "models").mkdir(parents=True)
    (tmp_path / "src" / "models" / "user_model.py").write_text("")
    generate_init_files(tmp_path / "src")
    assert (tmp_path / "src" / "__init__.py").exists()
    assert (tmp_path / "src" / "models" / "__init__.py").exists()


def test_generate_init_files_creates_for_nexy_dirs(tmp_path) -> None:
    (tmp_path / "src" / "routes").mkdir(parents=True)
    (tmp_path / "src" / "routes" / "index.nexy").write_text("")
    generate_init_files(tmp_path / "src")
    assert (tmp_path / "src" / "routes" / "__init__.py").exists()


def test_generate_init_files_skips_asset_only_dirs(tmp_path) -> None:
    (tmp_path / "src" / "public").mkdir(parents=True)
    (tmp_path / "src" / "public" / "logo.svg").write_text("")
    generate_init_files(tmp_path / "src")
    assert (tmp_path / "src" / "__init__.py").exists()
    assert not (tmp_path / "src" / "public" / "__init__.py").exists()
