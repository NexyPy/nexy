from nexy.core.models import NexyConfigModel
from nexy.frontend import react


class NexyConfig(NexyConfigModel):
    useFF = react()
    useRouter = None
    usePort: int = 3000
    useHost: str = "0.0.0.0"
    useTitle: str = "Nexy Minimal Example"
    useDocs: bool = False
    useVite: bool = False
    excludeDirs: list[str] = []