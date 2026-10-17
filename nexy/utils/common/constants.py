from pathlib import Path

DEFAULT_PORT: int = 3000
DEFAULT_HOST: str = "0.0.0.0"
DEFAULT_VITE_PORT: int = 5173

# Scaffold templates shipped with the nexy package.
TEMPLATES_DIR: Path = Path(__file__).resolve().parent.parent.parent / "templates"
