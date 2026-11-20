from nexy.core.models import NexyConfigModel
from nexy.frontend import react


class NexyConfig(NexyConfigModel):
    useFF = react()
    useCSR = True
    useTitle = "Todos"
    useAliases = {"@": "src"}
    useVite = True
    useDevTools = True  # the toolbar of `nexy dev` on every page; False removes it
