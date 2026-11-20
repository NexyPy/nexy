from nexy.core.models import NexyConfigModel
from nexy.frontend import react
from src.apps.app_module import AppModule

class NexyConfig(NexyConfigModel):
    useFF = react()
    useTitle = "Nexy Web (Modular + React)"
    useRouter = AppModule
    useAliases = {"@": "src"}
    useVite = True
    useDevTools = True  # the toolbar of `nexy dev` on every page; False removes it
    useORM = "SQLModel"  # the ORM `nx migrate` migrates
