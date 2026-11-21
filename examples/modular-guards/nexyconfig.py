from nexy.core.models import NexyConfigModel

from src.apps.app_module import AppModule

class NexyConfig(NexyConfigModel):
    useTitle = "Nexy Web (Modular)"
    useRouter = AppModule
    useAliases = {"@": "src"}
    useVite = True
    useDevTools = True  # the toolbar of `nexy dev` on every page; False removes it
