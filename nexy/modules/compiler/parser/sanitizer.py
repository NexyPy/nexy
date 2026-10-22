import os
import pathlib
import re
from re import Match

from nexy.core.config import Config


class LogicSanitizer:
    """
    Sanitizer for Nexy logic blocks.
    Handles custom import syntaxes like 'from "./file.nexy" import Comp'
    or 'import "./data.json" as data' and converts them to valid Python code.
    """

    def __init__(self) -> None:
        self.RE_NEXY_FROM = re.compile(
            r'^\s*from\s+["\'](?P<path>[^"\']+)["\']\s+import\s+(?P<targets>.+?)(?=\n\S|$)',
            re.M | re.S,
        )

        self.RE_NEXY_IMPORT = re.compile(
            r'^\s*import\s+["\'](?P<path>[^"\']+)["\'](?:\s+as\s+(?P<alias>\w+))?(?=\n\S|$)',
            re.M | re.S,
        )

    @property
    def aliases(self) -> dict[str, str]:
        return Config.ALIASES

    @property
    def namespace(self) -> str:
        return Config.NAMESPACE

    def _resolve_full_path(self, current_file: str, import_str: str) -> str:
        """
        Resolves the full relative path from the current file,
        taking aliases and relative paths into account.
        """
        first_ch = import_str[0]
        if first_ch in ("@", "$", "~") and not any(
            import_str.startswith(alias) for alias in self.aliases
        ):
            raise ImportError(f"Alias '{import_str.split('/')[0]}' not configured.")

        is_relative = import_str.startswith("./") or import_str.startswith("../")
        is_alias = any(import_str.startswith(alias) for alias in self.aliases)

        if not (is_relative or is_alias):
            return import_str

        root_path = pathlib.Path.cwd().absolute()
        current_path = pathlib.Path(current_file).absolute()

        for alias, replacement in self.aliases.items():
            if import_str.startswith(alias):
                resolved_path = root_path / import_str.replace(alias, replacement, 1)
                return resolved_path.absolute().relative_to(root_path).as_posix()

        resolved_path = current_path.parent.joinpath(import_str).resolve()

        try:
            return resolved_path.relative_to(root_path).as_posix()
        except ValueError:
            return os.path.normpath(resolved_path).replace("\\", "/")

    def _clean_targets(self, targets_str: str) -> list[str]:
        """Cleans parentheses, newlines, and spaces from import targets."""
        cleaned = targets_str.replace("(", "").replace(")", "").replace("\n", " ")
        return [t.strip() for t in cleaned.split(",") if t.strip()]

    def _get_framework(self, extension: str) -> str:
        """Returns the framework name associated with the extension."""
        return Config.FRONTEND_EXTENSIONS.get(extension.lower(), "unknown")

    def sanitize(self, source: str, current_file: str) -> str:
        """
        Main entry point for sanitizing logic blocks.
        Transforms custom Nexy import syntax into valid Python AST-parsable code.
        """
        source = self.RE_NEXY_FROM.sub(lambda m: self._replace_from(m, current_file), source)
        source = self.RE_NEXY_IMPORT.sub(lambda m: self._replace_import(m, current_file), source)

        return source

    def _normalize_alias(self, name: str) -> str:
        """Converts a string into a valid Python identifier."""
        return re.sub(r"[^a-zA-Z0-9_]", "_", name)

    def _replace_from(self, match: Match[str], current_file: str) -> str:
        """Callback for 'from "path" import targets' transformation."""
        path_str = match.group("path")
        targets_raw = match.group("targets")

        full_rel_path = self._resolve_full_path(current_file, path_str)
        ext = pathlib.Path(full_rel_path).suffix.lower()
        targets = self._clean_targets(targets_raw)

        if ext in (".nexy", ".py", ""):
            is_nexy = ext == ".nexy"
            prefix = f"{self.namespace.replace('/', '.')}" if is_nexy else ""
            module_name = re.sub(r"\.nexy$|\.py$", "", full_rel_path)
            module_name = re.sub(r"\.+", ".", module_name.replace("/", ".")).strip(".")
            module_name = prefix + module_name
            return f"from {module_name} import {', '.join(targets)}"

        framework = self._get_framework(ext)

        import_lines = []
        for t in targets:
            parts = re.split(r"\s+as\s+", t, flags=re.I)
            symbol = parts[0]
            alias = parts[1] if len(parts) > 1 else symbol
            alias = self._normalize_alias(alias)

            line = (
                f"{alias} = __Import("
                f'path="{full_rel_path}", framework="{framework}", symbol="{symbol}")'
            )
            import_lines.append(line)

        return "\n".join(import_lines)

    def _replace_import(self, match: Match[str], current_file: str) -> str:
        """Callback for 'import "path" [as alias]' transformation."""
        path_str = match.group("path")
        alias = match.group("alias")

        full_rel_path = self._resolve_full_path(current_file, path_str)
        ext = pathlib.Path(full_rel_path).suffix.lower()

        if not alias:
            alias = self._normalize_alias(pathlib.Path(full_rel_path).stem)

        if ext in (".nexy", ".py", ""):
            is_nexy_module = ext == ".nexy"

            prefix = ""

            if is_nexy_module and self.namespace:
                prefix = self.namespace.replace("\\", "/").replace("/", ".").strip(".")

                if prefix:
                    prefix += "."

            module_name = re.sub(r"\.(nexy|py)$", "", full_rel_path)

            module_name = module_name.replace("\\", "/").replace("/", ".").strip(".")

            module_name = re.sub(r"\.+", ".", module_name)

            if not re.match(r"^[a-zA-Z_][a-zA-Z0-9_\.]*$", module_name):
                raise ValueError(f"Invalid module name: {module_name}")

            if not re.match(r"^[a-zA-Z_][a-zA-Z0-9_]*$", alias):
                raise ValueError(f"Invalid alias: {alias}")

            module_name = f"{prefix}{module_name}"

            return f"import {module_name} as {alias}"

        framework = self._get_framework(ext)
        return (
            f'{alias} = __Import(path="{full_rel_path}", framework="{framework}", symbol="default")'
        )
