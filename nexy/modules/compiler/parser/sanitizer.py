import pathlib
import re
from re import Match

from nexy.core.config import Config
from nexy.modules.compiler.parser.import_paths import module_name, resolve_import

_PYTHON_MODULES = (".nexy", ".py", "")


def _require_identifier(module: str, alias: str) -> None:
    """A module path and an alias must be Python names: they end up in generated code."""
    if not re.match(r"^[a-zA-Z_][a-zA-Z0-9_\.]*$", module):
        raise ValueError(f"Invalid module name: {module}")
    if not re.match(r"^[a-zA-Z_][a-zA-Z0-9_]*$", alias):
        raise ValueError(f"Invalid alias: {alias}")


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

    def _framework_import(self, rel_path: str, framework: str, target: str) -> str:
        """``Name = __Import(...)`` for one target of a framework component import."""
        parts = re.split(r"\s+as\s+", target, flags=re.IGNORECASE)
        symbol = parts[0]
        alias = self._normalize_alias(parts[1] if len(parts) > 1 else symbol)
        return f'{alias} = __Import(path="{rel_path}", framework="{framework}", symbol="{symbol}")'

    def _replace_from(self, match: Match[str], current_file: str) -> str:
        """Callback for 'from "path" import targets' transformation."""
        rel_path = resolve_import(current_file, match.group("path"), self.aliases)
        extension = pathlib.Path(rel_path).suffix.lower()
        targets = self._clean_targets(match.group("targets"))
        if extension in _PYTHON_MODULES:
            module = module_name(rel_path, self.namespace, extension == ".nexy")
            return f"from {module} import {', '.join(targets)}"
        framework = self._get_framework(extension)
        lines = (self._framework_import(rel_path, framework, target) for target in targets)
        return "\n".join(lines)

    def _replace_import(self, match: Match[str], current_file: str) -> str:
        """Callback for 'import "path" [as alias]' transformation."""
        rel_path = resolve_import(current_file, match.group("path"), self.aliases)
        extension = pathlib.Path(rel_path).suffix.lower()
        alias = match.group("alias") or self._normalize_alias(pathlib.Path(rel_path).stem)
        if extension in _PYTHON_MODULES:
            module = module_name(rel_path, self.namespace, extension == ".nexy")
            _require_identifier(module, alias)
            return f"import {module} as {alias}"
        framework = self._get_framework(extension)
        return f'{alias} = __Import(path="{rel_path}", framework="{framework}", symbol="default")'
