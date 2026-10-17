from nexy.core.models import NexyConfigModel
from nexy.frontend import react


class NexyConfig(NexyConfigModel):
    # Frontend framework selection
    useFF = react()

    # Path aliases for imports
    useAliases: dict[str, str] = {"@": "src/components"}

    # Router selection (None for file-based router, or your AppModule)
    useRouter = None

    # Server configuration
    usePort: int = 3000
    useHost: str = "0.0.0.0"
    useTitle: str = "My Nexy App"

    # Feature flags
    useDocs: bool = True
    useVite: bool = True
    useMarkdownExtensions: list[str] = []

    # Directories to exclude from compilation
    excludeDirs: list[str] = ["templates", "extension", "docs"]
