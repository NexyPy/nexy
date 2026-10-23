from nexy.core.models import NexyConfigModel
from nexy.frontend import solid


class NexyConfig(NexyConfigModel):
    useFF = solid()
    useCSR = True
    useTitle = "Nexy Web (FBR + Solid)"
    useAliases = {"@": "src"}
    useVite = True