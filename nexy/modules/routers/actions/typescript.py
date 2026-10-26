"""Turn the JSON schema of a Python type into the TypeScript type of the generated client."""

from __future__ import annotations

import json
from enum import Enum
from typing import Any

from pydantic import BaseModel, TypeAdapter

_PRIMITIVES = {
    "string": "string",
    "integer": "number",
    "number": "number",
    "boolean": "boolean",
    "null": "null",
}

Declarations = dict[str, str]


def _is_named(annotation: Any) -> bool:
    return isinstance(annotation, type) and issubclass(annotation, (BaseModel, Enum))


def ts_type(
    annotation: Any, declarations: Declarations, mode: str = "serialization", inline: bool = False
) -> str:
    """The TypeScript type of *annotation*; named models are added to *declarations*.

    A model or enum is declared under its own name unless *inline* asks for its body.
    """
    if annotation in (None, type(None)):
        return "null"
    try:
        schema = TypeAdapter(annotation).json_schema(mode=mode)  # type: ignore[arg-type]
    except Exception:
        return "unknown"
    defs: dict[str, Any] = schema.pop("$defs", {})
    for name, definition in defs.items():
        declarations[name] = _convert(definition)
    body = _convert(schema)
    if inline or not _is_named(annotation):
        return body
    declarations[annotation.__name__] = body
    return str(annotation.__name__)


def _convert(schema: dict[str, Any]) -> str:
    if "$ref" in schema:
        return str(schema["$ref"]).rsplit("/", 1)[-1]
    if "enum" in schema:
        return " | ".join(json.dumps(value) for value in schema["enum"])
    if "const" in schema:
        return json.dumps(schema["const"])
    for key in ("anyOf", "oneOf"):
        if key in schema:
            return " | ".join(_convert(option) for option in schema[key])
    if "allOf" in schema and len(schema["allOf"]) == 1:
        return _convert(schema["allOf"][0])
    kind = schema.get("type")
    if isinstance(kind, list):
        return " | ".join(_convert({**schema, "type": one}) for one in kind)
    if kind == "array":
        return _array(schema)
    if kind == "object":
        return _object(schema)
    return _PRIMITIVES.get(str(kind), "unknown")


def _array(schema: dict[str, Any]) -> str:
    if "prefixItems" in schema:
        return "[" + ", ".join(_convert(item) for item in schema["prefixItems"]) + "]"
    inner = _convert(schema.get("items", {}))
    return f"({inner})[]" if " | " in inner else f"{inner}[]"


def _object(schema: dict[str, Any]) -> str:
    properties: dict[str, Any] = schema.get("properties", {})
    if not properties:
        extra = schema.get("additionalProperties")
        value = _convert(extra) if isinstance(extra, dict) else "unknown"
        return f"{{ [key: string]: {value} }}"
    required = set(schema.get("required", []))
    fields = [
        f"{_key(name)}{'' if name in required else '?'}: {_convert(value)}"
        for name, value in properties.items()
    ]
    return "{ " + "; ".join(fields) + " }"


def _key(name: str) -> str:
    return name if name.isidentifier() else json.dumps(name)
