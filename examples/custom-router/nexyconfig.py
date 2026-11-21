from nexy.core.models import NexyConfigModel



class NexyConfig(NexyConfigModel):
    useTitle = "Nexy Web (FBR)"
    useAliases = {"@": "src"}
    useVite = True
    useDevTools = True  # the toolbar of `nexy dev` on every page; False removes it
