import hashlib
from collections.abc import Callable

from nexy.modules.routers.actions.secret import action_secret


class ActionsStore:
    def __init__(self) -> None:
        self.registry: dict[str, Callable[..., object]] = {}
        self.path_map: dict[str, str] = {}

    def _generate_hash(self, func_id: str) -> str:
        return hashlib.sha256(f"{func_id}{action_secret()}".encode()).hexdigest()[:12]

    def register(self, func: Callable[..., object]) -> str:
        func_id = f"{func.__module__}.{func.__name__}"
        self.registry[func_id] = func
        return func_id


ACTIONS_STORE = ActionsStore()
