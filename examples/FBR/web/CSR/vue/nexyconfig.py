from nexy.core.models import NexyConfigModel
from nexy.frontend import vue


class NexyConfig(NexyConfigModel):
    useFF = vue()
    useCSR = True
    useTitle = "Nexy Web (FBR + Vue)"
    useAliases = {"@": "src"}
    useVite = True