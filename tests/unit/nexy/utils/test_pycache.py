import os
import tempfile
from pathlib import Path

from nexy.utils.dev.pycache import pycache


def test_pycache_sets_environment() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        orig = os.getcwd()
        try:
            os.chdir(tmp)
            pycache()
            env_val = os.environ.get("PYTHONPYCACHEPREFIX", "")
            assert env_val.endswith("__nexy__/__pycache__") or env_val.endswith("__nexy__\\__pycache__")
        finally:
            os.chdir(orig)
            os.environ.pop("PYTHONPYCACHEPREFIX", None)
