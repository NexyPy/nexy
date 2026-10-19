import ast
from typing import Any, cast

from nexy.core.models import (
    ComponentType,
    LogicResult,
    NexyImport,
    NexyProp,
)

from .sanitizer import LogicSanitizer


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
    def extract_loader_args(node: ast.Assign) -> dict[str, Any] | None:
        """Attempts to extract path/framework/symbol from a __nexy_loader__ or __Import call."""
        if not (isinstance(node.value, ast.Call)):
            return None

        call = node.value
        func = call.func

        valid_call = False
        if isinstance(func, ast.Attribute):
            if (
                isinstance(func.value, ast.Name)
                and func.value.id == "__nexy_loader__"
                and func.attr == "import_component"
            ):
                valid_call = True
        elif isinstance(func, ast.Name) and func.id == "__Import":
            valid_call = True

        if not valid_call:
            return None

        args = {}
        for kw in call.keywords:
            if isinstance(kw.value, ast.Constant):
                args[kw.arg] = kw.value.value
        return args


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
        final_nodes = []
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
        if not args:
            return False

        target = node.targets[0]
        alias = target.id if isinstance(target, ast.Name) else None

        path = args.get("path")
        symbol = args.get("symbol")
        fw_str = args.get("framework")

        if not path or not symbol:
            return False

        if fw_str == "css" or (path and path.endswith(".css")):
            result.css_imports.append(path)

        comp_type = self._determine_component_type(path, fw_str)
        ext = path[path.rfind(".") :] if "." in path else ""

        result.nexy_imports.append(
            NexyImport(
                path=path,
                symbol=symbol,
                alias=alias,
                raw_source="",
                extension=ext,
                comp_type=comp_type,
            )
        )
        return True

    def _determine_component_type(self, path: str, framework: str | None) -> ComponentType:
        """Maps file extensions and framework strings to ComponentType."""
        path_lower = path.lower()
        mapping = {
            ".nexy": ComponentType.NEXY,
            ".vue": ComponentType.VUE,
            ".svelte": ComponentType.SVELTE,
            ".tsx": ComponentType.REACT,
            ".jsx": ComponentType.REACT,
            ".solid": ComponentType.SOLID,
            ".preact": ComponentType.PREACT,
            ".json": ComponentType.JSON,
        }

        for ext, ctype in mapping.items():
            if path_lower.endswith(ext):
                return ctype

        fw_map = {
            "vue": ComponentType.VUE,
            "react": ComponentType.REACT,
            "svelte": ComponentType.SVELTE,
            "solid": ComponentType.SOLID,
            "preact": ComponentType.PREACT,
            "json": ComponentType.JSON,
        }
        if framework in fw_map:
            return fw_map[framework]

        return ComponentType.UNKNOWN
