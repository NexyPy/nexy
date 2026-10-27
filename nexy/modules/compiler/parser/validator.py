import pathlib

from nexy.core.config import Config
from nexy.core.models import NexyImport


class ImportValidationError(Exception):
    """Raised when an imported path cannot be resolved.

    The message includes the original import, the resolved path and
    optional suggestions (files with same stem) to help the user fix it.
    """

    pass


class ImportValidator:
    """Validates that all imported files exist on the filesystem and
    raises helpful, precise errors when they don't.
    """

    @staticmethod
    def _find_suggestions(path: pathlib.Path) -> list[str]:
        """Return filenames in the same directory that share the same stem."""
        parent = path.parent
        if not parent.exists():
            return []
        stem = path.stem
        candidates = []
        for p in parent.iterdir():
            if p.is_file() and p.stem == stem:
                candidates.append(p.name)
        return candidates

    @staticmethod
    def _resolve(
        imp: NexyImport, current_dir: pathlib.Path, project_root: pathlib.Path
    ) -> pathlib.Path:
        """The file an import points at: absolute, relative to the importer, or to the project."""
        import_path = pathlib.Path(imp.path)
        if import_path.is_absolute():
            return import_path.resolve()
        if imp.path.replace("\\", "/").startswith(("./", "../")):
            return (current_dir / import_path).resolve()
        return (project_root / import_path).resolve()

    @staticmethod
    def _missing(imp: NexyImport, full_path: pathlib.Path) -> ImportValidationError:
        """The error for an import whose file does not exist, with names that may be meant."""
        parts = [f"Missing import file: '{imp.path}'"]
        if imp.symbol:
            parts.append(f"symbol='{imp.symbol}'")
        if imp.alias:
            parts.append(f"alias='{imp.alias}'")
        parts.append(f"resolved='{full_path}'")
        suggestions = ImportValidator._find_suggestions(full_path)
        hint = f" suggestions={suggestions}" if suggestions else ""
        return ImportValidationError(
            f'Import Error "{imp.path}" does not exist; {", ".join(parts)}{hint}'
        )

    @staticmethod
    def validate_imports(imports: list[NexyImport], current_file: str) -> None:
        """Check that all imported files exist.

        Raises ImportValidationError with a helpful message when an import path cannot be
        resolved: the original import path, the symbol and alias, the resolved absolute path
        and filename suggestions.
        """
        current_dir = pathlib.Path(current_file).resolve().parent
        project_root = pathlib.Path(Config.PROJECT_ROOT).resolve()
        for imp in imports:
            full_path = ImportValidator._resolve(imp, current_dir, project_root)
            if not full_path.exists():
                raise ImportValidator._missing(imp, full_path)


__all__ = ["ImportValidator", "ImportValidationError"]
