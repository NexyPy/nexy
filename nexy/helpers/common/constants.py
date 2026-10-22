from pathlib import Path

DEFAULT_PORT: int = 3000
DEFAULT_HOST: str = "0.0.0.0"  # nosec B104 - deliberate dev default, see SECURITY.md
DEFAULT_VITE_PORT: int = 5173

TEMPLATES_DIR: Path = Path(__file__).resolve().parent.parent.parent / "templates"
