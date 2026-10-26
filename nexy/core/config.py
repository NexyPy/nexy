import sys
from pathlib import Path
from typing import Any

from nexy.core.config_loader import MISSING_CONFIG_ERROR, ConfigLoader
from nexy.core.models import FrontendFramework, NexyConfigModel

_current_dir = str(Path.cwd())
if _current_dir not in sys.path:
    sys.path.insert(0, _current_dir)

_DEFAULT_MARKDOWN_EXTENSIONS: list[str] = [
    "extra",
    "tables",
    "fenced_code",
    "codehilite",
    "toc",
    "admonition",
    "attr_list",
    "pymdownx.highlight",
    "pymdownx.superfences",
    "pymdownx.inlinehilite",
    "pymdownx.details",
    "pymdownx.tabbed",
]


class Config:
    """Singleton configuration manager for Nexy applications."""

    _instance: "Config | None" = None
    _loaded: bool = False
    _load_error: str | None = None

    ROUTER_PATH: str = "src/routes"
    ALIASES: dict[str, str] = {}
    NAMESPACE: str = "__nexy__/"
    useFF: FrontendFramework | list[FrontendFramework] | None = None
    useRouter: Any = None
    usePort: int = 3000
    useHost: str = "0.0.0.0"  # nosec B104 - deliberate dev default, see SECURITY.md
    useTitle: str = "Nexy App"
    useCSR: bool = False
    useDocs: bool = True
    useVite: bool = True
    useMarkdownExtensions: list[str] = []
    excludeDirs: list[str] = ["templates", "extension", "docs"]
    useAliases: dict[str, str] | None = None
    useDocsUrl: str = "/docs"
    useRedocsUrl: str | None = "/redocs"
    useMiddlewares: list[Any] = []
    useCORS: dict[str, Any] | None = None
    useGZip: dict[str, Any] | None = None
    useTrustedHost: dict[str, Any] | None = None
    useHTTPSRedirect: bool = False
    useSession: dict[str, Any] | None = None
    useAuth: dict[str, Any] | None = None
    useSslKeyfile: str | None = None
    useSslCertfile: str | None = None
    useWorkers: int = 0
    useTocDepth: str = "2-6"
    useTocTitle: str = "Table of Contents"
    useTocAuto: bool = True

    MARKDOWN_EXTENSIONS: list[str] = list(_DEFAULT_MARKDOWN_EXTENSIONS)
    TARGET_EXTENSIONS: list[str] = [".nexy", ".md", ".mdx", ".tsx", ".jsx", ".vue", ".svelte"]
    FRAMEWORK_REGISTRY: dict[str, FrontendFramework] = {}
    ROUTE_FILE_EXCEPTIONS: list[str] = [
        "__init__.py",
        "layout.nexy",
        "dependencies.py",
        "middleware.py",
    ]
    ROUTE_FILE_DEFAULT: list[str] = ["index.py", "index.nexy", "index.mdx", "index.md"]
    LAYOUT_FILE_NAMES: list[str] = ["layout.nexy"]
    NOTFOUND_FILE_NAMES: list[str] = ["notfound.nexy"]
    ERROR_FILE_NAMES: list[str] = ["errors.nexy"]
    LOADING_FILE_NAMES: list[str] = ["loading.nexy"]
    TOC_DEPTH: str = "2-6"
    TOC_TITLE: str = "Table of Contents"
    TOC_AUTO: bool = True

    WATCH_EXTENSIONS: list[str] = [".nexy", ".py", ".md", ".mdx", ".tsx", ".jsx", ".vue", ".svelte"]
    # One glob per extension: the watcher matches these with pathlib.PurePath.match,
    # which has no {a,b} alternation, so a single "*{.nexy,.py}" glob matches nothing.
    WATCH_EXTENSIONS_GLOB: list[str] = [
        "*.nexy",
        "*.py",
        "*.md",
        "*.mdx",
        "*.tsx",
        "*.jsx",
        "*.vue",
        "*.svelte",
    ]
    WATCH_EXCLUDE_PATTERNS: list[str] = [
        "**/.venv/**",
        "**/node_modules/**",
        "**/__pycache__/**",
        "**/.pytest_cache/**",
        "**/.mypy_cache/**",
        "**/.git/**",
        "**/__nexy__/**",
        "**/dist/**",
        "**/build/**",
    ]

    FRAMEWORK_ROUTE_EXTENSIONS: list[str] = [".tsx", ".jsx", ".vue", ".svelte", ".solid"]
    FRONTEND_EXTENSIONS: dict[str, str] = {
        ".tsx": "react",
        ".jsx": "react",
        ".vue": "vue",
        ".svelte": "svelte",
        ".solid": "solid",
        ".preact": "preact",
        ".json": "json",
        ".css": "css",
    }
    ROUTE_FILE_EXTENSIONS: list[str] = [
        ".nexy",
        ".py",
        ".md",
        ".mdx",
        *FRAMEWORK_ROUTE_EXTENSIONS,
    ]
    ALWAYS_ACTIVE_EXTENSIONS: list[str] = [".nexy", ".md", ".mdx", ".py"]

    PROJECT_ROOT: Path = Path.cwd()

    def __new__(cls) -> "Config":
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._load()
        return cls._instance

    def __init__(self) -> None:
        """Prevent re-initialization (singleton pattern)."""
        pass

    @classmethod
    def reset(cls) -> None:
        """Reset the singleton (mainly for testing)."""
        cls._instance = None
        cls._loaded = False
        cls._load_error = None

    def _load(self) -> None:
        """Load user configuration from nexyconfig.py if present."""
        if self._loaded:
            return
        self._loaded = True
        ConfigLoader(Config).load()

    @classmethod
    def get_load_error(cls) -> str | None:
        """Get the configuration load error, if any."""
        return cls._load_error

    @classmethod
    def require_valid(cls) -> None:
        """Raise ValueError when nexyconfig.py describes an impossible project.

        A missing nexyconfig.py is not an error: framework defaults apply.
        """
        error = cls._load_error
        if error and error != MISSING_CONFIG_ERROR:
            raise ValueError(error)


for _name in NexyConfigModel.__annotations__:
    if _name not in Config.__dict__:
        setattr(Config, _name, getattr(NexyConfigModel, _name, None))
