from nexy.core.models import NexyConfigModel
from nexy.frontend import preact


class NexyConfig(NexyConfigModel):
    useFF = preact()
    useTitle = "Nexy Web (FBR + Preact)"
    useAliases = {"@": "src"}
    useVite = True
    useDevTools = True  # the toolbar of `nexy dev` on every page; False removes it
    useORM = "SQLModel"  # the ORM `nx migrate` migrates
