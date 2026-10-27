"""What an `@Action` function accepts and returns, read once from its signature."""

from __future__ import annotations

import inspect
import typing
from collections.abc import Callable
from dataclasses import dataclass
from typing import Any

from pydantic import BaseModel, ConfigDict, create_model

_INJECTED = ("request", "response")


@dataclass(frozen=True)
class ActionSpec:
    """The input model, the injected arguments and the return type of one action."""

    func_id: str
    name: str
    handler: Callable[..., Any]
    model: type[BaseModel]
    injected: tuple[str, ...]
    returns: Any

    @property
    def takes_input(self) -> bool:
        return bool(self.model.model_fields)

    def arguments(self, payload: dict[str, Any]) -> dict[str, Any]:
        """The validated input as the keyword arguments of the handler (raises ValidationError)."""
        validated = self.model.model_validate(payload)
        return {name: getattr(validated, name) for name in self.model.model_fields}


def _hints(handler: Callable[..., Any]) -> dict[str, Any]:
    try:
        return typing.get_type_hints(handler)
    except Exception:
        return {}


def build_spec(func_id: str, handler: Callable[..., Any]) -> ActionSpec:
    hints = _hints(handler)
    fields: dict[str, Any] = {}
    injected: list[str] = []
    for name, parameter in inspect.signature(handler).parameters.items():
        if name in _INJECTED:
            injected.append(name)
            continue
        default = ... if parameter.default is inspect.Parameter.empty else parameter.default
        fields[name] = (hints.get(name, Any), default)
    name = func_id.rsplit(".", 1)[-1]
    model = create_model(f"{name}_input", __config__=ConfigDict(extra="ignore"), **fields)
    return ActionSpec(func_id, name, handler, model, tuple(injected), hints.get("return", Any))
