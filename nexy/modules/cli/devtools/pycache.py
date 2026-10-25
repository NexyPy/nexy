import os
import sys
from pathlib import Path


def pycache() -> None:
    """Keep Python bytecode in ``__nexy__/__pycache__`` instead of next to the sources.

    ``PYTHONPYCACHEPREFIX`` is only read when the interpreter starts, so it serves the processes
    spawned from here; ``sys.pycache_prefix`` is what applies to this one, immediately.
    """
    cache_dir = Path("__nexy__/__pycache__")
    cache_dir.mkdir(parents=True, exist_ok=True)
    os.environ["PYTHONPYCACHEPREFIX"] = str(cache_dir)
    sys.pycache_prefix = str(cache_dir.resolve())
