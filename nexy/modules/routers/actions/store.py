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

    def template_context(self) -> dict[str, object]:
        """What every template can call: each action by name, and the two maps behind them."""
        actions = {func_id.split(".")[-1]: handler for func_id, handler in self.registry.items()}
        paths = {
            func_id.split(".")[-1]: self.path_map.get(func_id, "") for func_id in self.registry
        }
        return {**actions, "__actions": actions, "__actions_path": paths}


ACTIONS_STORE = ActionsStore()
