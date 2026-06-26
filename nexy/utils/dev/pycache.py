import os
from pathlib import Path


def pycache() -> None:
    cache_dir = Path("__nexy__/__pycache__")
    cache_dir.mkdir(parents=True, exist_ok=True)
    os.environ["PYTHONPYCACHEPREFIX"] = str(cache_dir)
