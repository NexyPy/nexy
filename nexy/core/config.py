import importlib.util
import sys
from pathlib import Path
from typing import TYPE_CHECKING, Any

from nexy.core.models import FrontendFramework, NexyConfigModel

if TYPE_CHECKING:
    pass

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
    useHost: str = "0.0.0.0"
    useTitle: str = "Nexy App"
    useDocs: bool = True
    useVite: bool = True
    useMarkdownExtensions: list[str] = []
    excludeDirs: list[str] = ["templates", "extension", "docs"]
    useLocales: list[str] | None = None
    useAliases: dict[str, str] | None = None
    useDocsUrl: str = "/docs"
    useRedocsUrl: str | None = "/redocs"
    useDefaultLocale: str = "en"
    useLocaleCookieName: str = "nexy-locale"
    useLocalesDir: str | None = None
    useLocalesSourceDir: str | None = None
    useMiddlewares: list[Any] = []
    useCORS: dict[str, Any] | None = None
    useGZip: dict[str, Any] | None = None
    useTrustedHost: dict[str, Any] | None = None
    useHTTPSRedirect: bool = False
    useSession: dict[str, Any] | None = None
    useAuth: dict[str, Any] | None = None
    useSslKeyfile: str | None = None
    useSslCertfile: str | None = None
    useTocDepth: str = "2-6"
    useTocTitle: str = "Table of Contents"
    useTocAuto: bool = True

    MARKDOWN_EXTENSIONS: list[str] = list(_DEFAULT_MARKDOWN_EXTENSIONS)
    TARGET_EXTENSIONS: list[str] = [".nexy", ".md", ".mdx", ".tsx", ".jsx", ".vue", ".svelte"]
    FRAMEWORK_REGISTRY: dict[str, FrontendFramework] = {}
    ROUTE_FILE_EXCEPTIONS: list[str] = ["__init__.py", "layout.nexy", "dependencies.py"]
    ROUTE_FILE_DEFAULT: list[str] = ["index.py", "index.nexy", "index.mdx", "index.md"]
    LAYOUT_FILE_NAMES: list[str] = ["layout.nexy"]
    NOTFOUND_FILE_NAMES: list[str] = ["notfound.nexy"]
    ERROR_FILE_NAMES: list[str] = ["errors.nexy"]
    LOADING_FILE_NAMES: list[str] = ["loading.nexy"]
    TOC_DEPTH: str = "2-6"
    TOC_TITLE: str = "Table of Contents"
    TOC_AUTO: bool = True

    WATCH_EXTENSIONS: list[str] = [".nexy", ".py", ".md", ".mdx", ".tsx", ".jsx", ".vue", ".svelte"]
    # One glob per extension: watchdog 6 matches these with pathlib.PurePath.match,
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

    @staticmethod
    def _normalize_ff(
        use_ff: FrontendFramework | list[FrontendFramework] | None,
    ) -> list[FrontendFramework]:
        if use_ff is None:
            return []
        if isinstance(use_ff, list):
            return use_ff
        return [use_ff]

    @staticmethod
    def validate_single_framework(
        use_ff: FrontendFramework | list[FrontendFramework] | None,
    ) -> None:
        if isinstance(use_ff, list) and len(use_ff) != 1:
            raise ValueError("useFF must configure exactly one frontend framework")

    @classmethod
    def derive_route_extensions(cls, ff: FrontendFramework | None) -> list[str]:
        exts = list(cls.ALWAYS_ACTIVE_EXTENSIONS)
        if ff is None:
            return exts
        for ext in ff.extension or []:
            dotted = ext if ext.startswith(".") else f".{ext}"
            if dotted not in exts:
                exts.append(dotted)
        return exts

    @staticmethod
    def derive_special_names(
        prefix: str,
        registry: dict[str, Any],
        user_exts: list[str] | None = None,
    ) -> list[str]:
        names: list[str] = []
        if prefix in ("layout", "errors", "loading"):
            names.append(f"{prefix}.nexy")

        extensions: set[str] = set()
        if user_exts:
            for ext in user_exts:
                extensions.add(ext if ext.startswith(".") else f".{ext}")
        for ff in registry.values():
            for ext in getattr(ff, "extension", []) or []:
                extensions.add(ext if ext.startswith(".") else f".{ext}")

        for ext in sorted(extensions):
            names.append(f"{prefix}{ext.lower()}")
        return names

    @classmethod
    def _import_nexyconfig(cls) -> Any | None:
        try:
            import nexyconfig

            return nexyconfig
        except ModuleNotFoundError:
            for candidate in ("nexyconfig.example.py", "nexyconfig.example"):
                path = Path(candidate)
                if path.is_file():
                    spec = importlib.util.spec_from_file_location("nexyconfig", path)
                    if spec and spec.loader:
                        module = importlib.util.module_from_spec(spec)
                        spec.loader.exec_module(module)
                        return module
            return None

    def _load(self) -> None:
        """Load user configuration from nexyconfig.py if present."""
        if self._loaded:
            return

        self._loaded = True

        nexyconfig = self._import_nexyconfig()
        if nexyconfig is None:
            Config._load_error = "nexyconfig.py not found"
            return

        try:
            nc = nexyconfig.NexyConfig
        except AttributeError as e:
            Config._load_error = f"nexyconfig.py missing NexyConfig class: {e}"
            return

        for attr in NexyConfigModel.__annotations__:
            val = getattr(nc, attr, None)
            if val is not None:
                setattr(Config, attr, val)

        try:
            Config.validate_single_framework(Config.useFF)
        except ValueError as e:
            Config._load_error = str(e)
            return

        if Config.useAliases:
            Config.ALIASES = Config.useAliases

        if Config.useMarkdownExtensions:
            Config.MARKDOWN_EXTENSIONS = Config.useMarkdownExtensions

        if Config.useTocDepth:
            Config.TOC_DEPTH = Config.useTocDepth
        if Config.useTocTitle:
            Config.TOC_TITLE = Config.useTocTitle
        if hasattr(nc, "useTocAuto") and Config.useTocAuto is not None:
            Config.TOC_AUTO = Config.useTocAuto

        ff_list = self._normalize_ff(Config.useFF)
        Config.ROUTE_FILE_EXTENSIONS = self.derive_route_extensions(ff_list[0] if ff_list else None)

        mapping: dict[str, str] = dict(Config.FRONTEND_EXTENSIONS)
        registry: dict[str, FrontendFramework] = {}
        for ff in ff_list:
            name = ff.name.lower()
            registry[name] = ff
            for ext in ff.extension or []:
                dotted = ext if ext.startswith(".") else f".{ext}"
                mapping[dotted.lower()] = name
        Config.FRONTEND_EXTENSIONS = mapping
        Config.FRAMEWORK_REGISTRY = registry

        for ff in ff_list:
            for ext in ff.extension or []:
                dotted = ext if ext.startswith(".") else f".{ext}"
                if dotted not in Config.FRAMEWORK_ROUTE_EXTENSIONS:
                    Config.FRAMEWORK_ROUTE_EXTENSIONS.append(dotted)
                if dotted not in Config.WATCH_EXTENSIONS:
                    Config.WATCH_EXTENSIONS.append(dotted)

        Config.TARGET_EXTENSIONS = [ext for ext in Config.ROUTE_FILE_EXTENSIONS if ext != ".py"]

        Config.LAYOUT_FILE_NAMES = self.derive_special_names(
            "layout",
            registry,
            user_exts=getattr(nc, "useLayoutExtensions", None),
        )
        Config.NOTFOUND_FILE_NAMES = self.derive_special_names(
            "notfound",
            registry,
            user_exts=getattr(nc, "useNotFoundExtensions", None),
        )
        Config.ERROR_FILE_NAMES = self.derive_special_names(
            "errors",
            registry,
            user_exts=getattr(nc, "useErrorsExtensions", None),
        )
        Config.LOADING_FILE_NAMES = self.derive_special_names(
            "loading",
            registry,
            user_exts=getattr(nc, "useLoadingExtensions", None),
        )

        Config.ROUTE_FILE_EXCEPTIONS = list(
            dict.fromkeys(
                [
                    "__init__.py",
                    "dependencies.py",
                    *Config.LAYOUT_FILE_NAMES,
                ]
            )
        )

        watch_ext = getattr(nc, "useWatchExtensions", None)
        if watch_ext:
            Config.WATCH_EXTENSIONS_GLOB = (
                [watch_ext] if isinstance(watch_ext, str) else list(watch_ext)
            )
        else:
            Config.WATCH_EXTENSIONS_GLOB = [f"*{ext}" for ext in Config.WATCH_EXTENSIONS]

        watch_exclude = getattr(nc, "useWatchExcludePatterns", None)
        if watch_exclude:
            Config.WATCH_EXCLUDE_PATTERNS = watch_exclude

        if Config.excludeDirs:
            for dir_name in Config.excludeDirs:
                pattern = f"**/{dir_name}/**"
                if pattern not in Config.WATCH_EXCLUDE_PATTERNS:
                    Config.WATCH_EXCLUDE_PATTERNS.append(pattern)

        Config._load_error = None

    @classmethod
    def get_load_error(cls) -> str | None:
        """Get the configuration load error, if any."""
        return cls._load_error


for _name in NexyConfigModel.__annotations__:
    if _name not in Config.__dict__:
        setattr(Config, _name, getattr(NexyConfigModel, _name, None))
