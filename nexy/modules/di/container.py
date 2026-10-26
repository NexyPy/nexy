"""`@Injectable` classes and the container that builds them, with their scope."""

from __future__ import annotations

import functools
import inspect
from collections.abc import Callable
from contextvars import ContextVar
from enum import Enum
from threading import RLock
from typing import Any


class Scope(Enum):
    SINGLETON = "singleton"
    REQUEST = "request"
    TRANSIENT = "transient"


def _guarded(cls: type[Any], original_init: Callable[..., None]) -> Callable[..., None]:
    """An `__init__` that refuses to run outside the container."""

    @functools.wraps(original_init)
    def guarded_init(self: Any, *args: Any, **kwargs: Any) -> None:
        if not Container._di_context.get():
            raise TypeError(
                f"{cls.__name__} is managed by Nexy. "
                f"Use Container.resolve() or inject it via another service/controller."
            )
        original_init(self, *args, **kwargs)

    return guarded_init


def Injectable(scope: Scope = Scope.SINGLETON) -> Callable[[type[Any]], type[Any]]:
    def wrapper(cls: type[Any]) -> type[Any]:
        cls.__injectable__ = True
        cls.__injectable_scope__ = scope
        if cls.__init__ is not object.__init__:
            cls.__init__ = _guarded(cls, cls.__init__)
        return cls

    return wrapper


class Container:
    _instances: dict[type[Any], Any] = {}
    _lock = RLock()
    _resolving: set[type[Any]] = set()
    _request_store: ContextVar[Any] = ContextVar("_request_store", default=None)
    _di_context: ContextVar[bool] = ContextVar("_di_context", default=False)

    @classmethod
    def resolve(cls, target_cls: type[Any]) -> Any:
        scope = getattr(target_cls, "__injectable_scope__", Scope.SINGLETON)
        if scope == Scope.REQUEST:
            return cls._resolve_request(target_cls)
        if scope == Scope.TRANSIENT:
            return cls._create(target_cls)
        return cls._resolve_singleton(target_cls)

    @classmethod
    def _resolve_singleton(cls, target_cls: type[Any]) -> Any:
        if target_cls in cls._instances:
            return cls._instances[target_cls]
        with cls._lock:
            if target_cls not in cls._instances:
                cls._instances[target_cls] = cls._create(target_cls)
            return cls._instances[target_cls]

    @classmethod
    def _resolve_request(cls, target_cls: type[Any]) -> Any:
        store = cls._request_store.get()
        if store is None:
            store = {}
        if target_cls not in store:
            store[target_cls] = cls._create(target_cls)
            cls._request_store.set(store)
        return store[target_cls]

    @classmethod
    def clear_request_scope(cls) -> None:
        cls._request_store.set(None)

    @classmethod
    def _create(cls, target_cls: type[Any]) -> Any:
        if target_cls in cls._resolving:
            raise RecursionError(f"Cycle detected for {target_cls.__name__}")
        cls._resolving.add(target_cls)
        try:
            return cls._instantiate(target_cls)
        finally:
            cls._resolving.discard(target_cls)

    @classmethod
    def _instantiate(cls, target_cls: type[Any]) -> Any:
        if "__init__" not in target_cls.__dict__:
            return target_cls()
        dependencies = cls._dependencies(target_cls)
        token = cls._di_context.set(True)
        try:
            return target_cls(*dependencies)
        finally:
            cls._di_context.reset(token)

    @classmethod
    def _dependencies(cls, target_cls: type[Any]) -> list[Any]:
        """The instances of the injectable parameters of `__init__`; others need a default."""
        found: list[Any] = []
        for name, param in inspect.signature(target_cls.__init__).parameters.items():
            if name == "self":
                continue
            if hasattr(param.annotation, "__injectable__"):
                found.append(cls.resolve(param.annotation))
            elif param.default is inspect.Parameter.empty:
                raise ValueError(
                    f"Dependency {name}: {param.annotation} is not injectable in "
                    f"{target_cls.__name__}"
                )
        return found
