from nexy.core.models import NexyConfigModel
from nexy.frontend import svelte


class NexyConfig(NexyConfigModel):
    useFF = svelte()
    useCSR = True
    useTitle = "Nexy Web (FBR + Svelte)"
    useAliases = {"@": "src"}
    useVite = True