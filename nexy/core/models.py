from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Literal

from fastapi import APIRouter


@dataclass
class ScanResult:
    """Raw split of a .nexy file into its two frontmatter-separated blocks.

    Attributes:
        logic_block: Python code of the `---` frontmatter block.
        template_block: HTML/Jinja template body following the frontmatter.
    """

    logic_block: str
    template_block: str

    @property
    def frontmatter(self) -> str:
        return self.logic_block

    @property
    def template(self) -> str:
        return self.template_block


@dataclass
class NexyProp:
    """A component prop parsed from a `name: prop[type] = default` declaration.

    Attributes:
        name: Prop name passed to the component.
        type: Declared Python type (e.g. "str").
        default: Source expression of the default value, None when required.
    """

    name: str
    type: str
    default: str | None = None


class ComponentType(Enum):
    """Implementation family of a component import (Nexy, Vue, Svelte, unknown)."""

    NEXY = "nexy"
    VUE = "vue"
    SVELTE = "svelte"
    REACT = "react"
    SOLID = "solid"
    PREACT = "preact"
    JSON = "json"
    UNKNOWN = "unknown"


@dataclass
class NexyImport:
    """A component import resolved from the logic block.

    Attributes:
        path: Import path as written in the source.
        symbol: Imported symbol, None for wildcard imports.
        alias: Local alias when the import renames the symbol.
        raw_source: Raw source of the imported component (filled when inlined).
        extension: File extension of the imported component (e.g. ".tsx").
        comp_type: Family of the imported component.
    """

    path: str
    symbol: str | None = None
    alias: str | None = None
    raw_source: str = ""
    extension: str = ""
    comp_type: ComponentType = ComponentType.UNKNOWN


@dataclass
class LogicResult:
    """Everything extracted from the logic block of one component.

    Attributes:
        nexy_imports: Component imports discovered in the block.
        props: Declared props of the component.
        python_code: Sanitized Python code kept for execution.
        css_imports: Stylesheet paths imported by the component.
    """

    nexy_imports: list[NexyImport] = field(default_factory=list)
    props: list[NexyProp] = field(default_factory=list)
    python_code: str = ""
    css_imports: list[str] = field(default_factory=list)


@dataclass
class ContextModel:
    """A context entry passed to the template.

    Attributes:
        key: Context variable name.
        value: Its source expression.
    """

    key: str
    value: str


@dataclass
class ParserModel:
    """Complete parse of one .nexy file, consumed by the generator.

    Attributes:
        frontmatter: Sanitized Python logic block.
        template: HTML/Jinja template body.
        props: Declared props of the component.
        context: Non-prop context entries of the logic block.
        styles: Inline `<style>` blocks of the template.
    """

    frontmatter: str
    template: str
    props: list[NexyProp]
    context: list[ContextModel] = field(default_factory=list)
    styles: list[str] = field(default_factory=list)


@dataclass
class FrontendFramework:
    """Description of a supported frontend framework.

    Attributes:
        name: Lowercase identifier (e.g. "react").
        render: Rendering mode used by the SSG pipeline.
        extension: File extensions owned by the framework (e.g. [".tsx"]).
    """

    name: str
    render: str
    extension: list[str] = field(default_factory=list)


class NexyConfigModel:
    """Base of the user-facing NexyConfig class (nexyconfig.py camelCase API).

    Every attribute is overridable by the user project's NexyConfig subclass;
    Config mirrors these fields with framework defaults.
    """

    useAliases: dict[str, str] | None = None
    useRouter: APIRouter | None = None
    usePort: int = 3000
    useHost: str = "0.0.0.0"  # nosec B104 - deliberate dev default, see SECURITY.md
    useTitle: str = "Nexy"
    useDocsUrl: str = "/docs"
    useRedocsUrl: str | None = "/redocs"
    # Where the API reference and /openapi.json are served: "dev" (the dev server only), True
    # (production too: it lists every route and server action), False (nowhere).
    useDocs: bool | Literal["dev"] = "dev"
    useVite: bool = False
    useViteDevUrl: str | None = None
    useFF: FrontendFramework | list[FrontendFramework] | None = None
    useCSR: bool = False
    useMarkdownExtensions: list[str] = []
    excludeDirs: list[str] = []
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
    useDevTools: bool = True
    useHealth: bool = False
    # The largest request body a worker reads, in bytes (1 MiB); larger is a 413. 0: no limit.
    useMaxBodySize: int = 1024 * 1024
    # Requests one client address may send per window: {"requests": 60, "per": 60}. None: no limit.
    useRateLimit: dict[str, Any] | None = None
    # The ORM `nx new` scaffolded the project with; `nx migrate` picks its migration tool from it.
    useORM: Literal["SQLModel", "SQLAlchemy", "Tortoise-ORM"] | None = None
    useRTL: bool = False
    useTocDepth: str = "2-6"
    useTocTitle: str = "Table of Contents"
    useTocAuto: bool = True
    useWatchExtensions: list[str] | None = None
    useWatchExcludePatterns: list[str] | None = None
    useLayoutExtensions: list[str] | None = None
    useNotFoundExtensions: list[str] | None = None
    useErrorsExtensions: list[str] | None = None
    useLoadingExtensions: list[str] | None = None
    useForbiddenExtensions: list[str] | None = None
    useUnauthorizedExtensions: list[str] | None = None
    useRedirects: list[dict[str, Any]] | None = None
    useRewrites: list[dict[str, Any]] | None = None
    useHeaders: list[dict[str, Any]] | None = None
    useBasePath: str | None = None
    # Widths, in pixels, of the responsive variants `nx build` writes for local images.
    useImageWidths: list[int] | None = None
    # ISR store: None or "memory" for this process, "file" for one host, "redis" for several
    # workers, a mapping with "type" and its options, or an object with get/set/invalidate.
    useISRCache: Any = None
    # The public origin of the site, such as "https://example.com": the sitemap writes its URLs
    # with it, and /sitemap.xml and /robots.txt are served only once it is set.
    useSiteUrl: str | None = None
