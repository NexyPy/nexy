import shutil
from pathlib import Path

from nexy.helpers.common.console import console
from nexy.helpers.fs.path import PathUtil

_PACKAGE_DIR = Path(__file__).resolve().parent


def copy_ssg_scripts(exclude_dirs: list[str]) -> None:
    """Copy the SSG scripts into __nexy__/scripts with project excludes."""
    try:
        dest = Path("__nexy__") / "scripts"
        shutil.copytree(_PACKAGE_DIR / "scripts", dest, dirs_exist_ok=True)
        _write_excludes(dest, exclude_dirs)
    except Exception as e:
        print(f"[nexy] Error copying scripts: {e}")


def _write_excludes(dest: Path, exclude_dirs: list[str]) -> None:
    entries = ",\n  ".join(f"'{d}/**'" for d in exclude_dirs)
    content = f"export const EXCLUDES: string[] = [\n  {entries}\n]\n"
    PathUtil.write_if_changed(dest / "excludes.ts", content)


def copy_vite_config() -> None:
    """Copy the frontend vite config from nexy/frontend/vite.ts to __nexy__/vite.ts."""
    try:
        source = _PACKAGE_DIR / "vite.ts"
        dest = Path("__nexy__") / "vite.ts"
        if source.is_file():
            PathUtil.write_if_changed(dest, source.read_text(encoding="utf-8"))
    except Exception as e:
        console.print(f"[red]nsc[/red] » error generating vite.ts: {e}")
