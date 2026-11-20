import sys
from pathlib import Path

# The tests import `src.` and `nexyconfig` as the app does, from the root of the project.
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
