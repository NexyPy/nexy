from nexy.core.models import NexyConfigModel
from nexy.frontend import react


class NexyConfig(NexyConfigModel):
    useFF = [react()]
    useTitle = "Nexy Web (FBR + React)"
    useAliases = {"@": "src"}
    useVite = True