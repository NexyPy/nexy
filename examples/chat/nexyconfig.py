from nexy.core.models import NexyConfigModel
from nexy.frontend import preact


class NexyConfig(NexyConfigModel):
    useFF = preact()
    useTitle = "Fernhill chat"
    useAliases = {"@": "src"}
    useVite = True
    useDevTools = True  # the toolbar of `nexy dev` on every page; False removes it
