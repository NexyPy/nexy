from nexy.core.models import NexyConfigModel
from nexy.frontend import preact


class NexyConfig(NexyConfigModel):
    useFF = preact()
    useCSR = True
    useTitle = "Nexy Web (FBR + Preact)"
    useAliases = {"@": "src"}
    useVite = True