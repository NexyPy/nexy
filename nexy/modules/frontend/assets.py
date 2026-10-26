import shutil
from pathlib import Path

from rich.markup import escape

from nexy.helpers.common.console import console
from nexy.helpers.common.log_line import tagged
from nexy.helpers.fs.path import PathUtil

_PACKAGE_DIR = Path(__file__).resolve().parent


def copy_ssg_scripts(exclude_dirs: list[str]) -> None:
    """Copy the SSG scripts into __nexy__/scripts with project excludes."""
    try:
        dest = Path("__nexy__") / "scripts"
        shutil.copytree(_PACKAGE_DIR / "scripts", dest, dirs_exist_ok=True)
        _write_excludes(dest, exclude_dirs)
    except OSError as error:
        message = (
            f"could not copy the SSG scripts, static pages will not build: {escape(str(error))}"
        )
        console.print(tagged("nsc", message, "red"))


def _write_excludes(dest: Path, exclude_dirs: list[str]) -> None:
    entries = ",\n  ".join(f"'{d}/**'" for d in exclude_dirs)
    content = f"export const EXCLUDES: string[] = [\n  {entries}\n]\n"
    PathUtil.write_if_changed(dest / "excludes.ts", content)


def copy_vite_config() -> None:
    """Copy the frontend vite config from nexy/modules/frontend/vite.ts to __nexy__/vite.ts."""
    try:
        for name in ("vite.ts", "document.ts"):
            source = _PACKAGE_DIR / name
            if source.is_file():
                PathUtil.write_if_changed(
                    Path("__nexy__") / name, source.read_text(encoding="utf-8")
                )
    except Exception as e:
        console.print(tagged("nsc", f"error generating vite.ts: {e}", "red"))
