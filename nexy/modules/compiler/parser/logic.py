import ast
from typing import Any, cast

from nexy.core.models import (
    ComponentType,
    LogicResult,
    NexyImport,
    NexyProp,
)

from .sanitizer import LogicSanitizer

_BY_EXTENSION = {
    ".nexy": ComponentType.NEXY,
    ".vue": ComponentType.VUE,
    ".svelte": ComponentType.SVELTE,
    ".tsx": ComponentType.REACT,
    ".jsx": ComponentType.REACT,
    ".solid": ComponentType.SOLID,
    ".preact": ComponentType.PREACT,
    ".json": ComponentType.JSON,
}
_BY_FRAMEWORK = {
    "vue": ComponentType.VUE,
    "react": ComponentType.REACT,
    "svelte": ComponentType.SVELTE,
    "solid": ComponentType.SOLID,
    "preact": ComponentType.PREACT,
    "json": ComponentType.JSON,
}


class ASTUtils:
    """Helper class to reduce the complexity of AST inspection."""

    @staticmethod
    def is_prop_annotation(node: ast.AnnAssign) -> bool:
        """Checks if the node is a prop annotation: var: prop[T]"""
        return (
            isinstance(node.annotation, ast.Subscript)
            and isinstance(node.annotation.value, ast.Name)
            and node.annotation.value.id == "prop"
        )

    @staticmethod
    def _is_loader_call(func: ast.expr) -> bool:
        """True for ``__nexy_loader__.import_component(...)`` and ``__Import(...)``."""
        if isinstance(func, ast.Attribute):
            return (
                isinstance(func.value, ast.Name)
                and func.value.id == "__nexy_loader__"
                and func.attr == "import_component"
            )
        return isinstance(func, ast.Name) and func.id == "__Import"

    @staticmethod
    def extract_loader_args(node: ast.Assign) -> dict[str | None, Any] | None:
        """Attempts to extract path/framework/symbol from a __nexy_loader__ or __Import call."""
        call = node.value
        if not isinstance(call, ast.Call) or not ASTUtils._is_loader_call(call.func):
            return None
        return {
            kw.arg: kw.value.value for kw in call.keywords if isinstance(kw.value, ast.Constant)
        }


class LogicParser:
    """
    Parser for the logic block of a Nexy component.
    Uses an AST-based approach after sanitization to extract props and component imports.
    """

    def __init__(self) -> None:
        self.sanitizer = LogicSanitizer()

    def process(self, code: str, current_file: str) -> LogicResult:
        """
        Processes the logic block code and returns a LogicResult containing
        extracted props, imports, and the cleaned Python code.
        """
        result = LogicResult()
        if not code.strip():
            return result

        clean_code = self.sanitizer.sanitize(code, current_file=current_file)

        try:
            tree = ast.parse(clean_code)
        except SyntaxError as e:
            raise SyntaxError(f"Logic Parse Error: {e}") from e

        final_body = self._process_nodes(tree.body, result)

        if final_body:
            result.python_code = self._wrap_in_module(final_body)

        return result

    def _process_nodes(self, nodes: list[ast.stmt], result: LogicResult) -> list[ast.stmt]:
        """Iterates through AST nodes to extract metadata and filter nodes."""
        final_nodes: list[ast.stmt] = []
        for node in nodes:
            if isinstance(node, ast.AnnAssign) and ASTUtils.is_prop_annotation(node):
                result.props.append(self._build_prop(node))
                continue

            if isinstance(node, ast.Assign) and self._try_extract_import(node, result):
                final_nodes.append(node)
                continue

            final_nodes.append(node)

        return final_nodes

    def _wrap_in_module(self, nodes: list[ast.stmt]) -> str:
        """Unparses the filtered nodes back into a Python source string."""
        full_module = ast.Module(body=nodes, type_ignores=[])
        return ast.unparse(full_module)

    def _build_prop(self, node: ast.AnnAssign) -> NexyProp:
        """Builds a NexyProp object from an AnnAssign node."""
        ann = cast(ast.Subscript, node.annotation)
        target = cast(ast.Name, node.target)

        return NexyProp(
            name=target.id,
            type=ast.unparse(ann.slice),
            default=ast.unparse(node.value) if node.value else None,
        )

    def _try_extract_import(self, node: ast.Assign, result: LogicResult) -> bool:
        """Attempts to extract import metadata for the component manifest."""
        args = ASTUtils.extract_loader_args(node)
        path = args.get("path") if args else None
        symbol = args.get("symbol") if args else None
        if not (args and path and symbol):
            return False
        framework = args.get("framework")
        if framework == "css" or path.endswith(".css"):
            result.css_imports.append(path)
        target = node.targets[0]
        result.nexy_imports.append(
            NexyImport(
                path=path,
                symbol=symbol,
                alias=target.id if isinstance(target, ast.Name) else None,
                raw_source="",
                extension=path[path.rfind(".") :] if "." in path else "",
                comp_type=self._determine_component_type(path, framework),
            )
        )
        return True

    def _determine_component_type(self, path: str, framework: str | None) -> ComponentType:
        """Maps file extensions and framework strings to ComponentType."""
        lowered = path.lower()
        by_extension = next(
            (kind for ext, kind in _BY_EXTENSION.items() if lowered.endswith(ext)), None
        )
        return by_extension or _BY_FRAMEWORK.get(framework or "", ComponentType.UNKNOWN)
