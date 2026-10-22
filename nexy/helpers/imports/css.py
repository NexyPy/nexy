from collections.abc import Callable
from pathlib import Path


class CSS:
    @staticmethod
    def create(path: str) -> Callable[[], str]:
        p = Path(path)
        if p.exists():
            content = p.read_text(encoding="utf-8")
            return lambda: f"<style>\n{content}\n</style>"
        return lambda: ""
