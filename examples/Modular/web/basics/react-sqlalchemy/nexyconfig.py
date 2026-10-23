from nexy.core.models import NexyConfigModel
from nexy.frontend import react
from src.apps.app_module import AppModule

class NexyConfig(NexyConfigModel):
    useFF = react()
    useTitle = "Nexy Web (Modular + React)"
    useRouter = AppModule
    useAliases = {"@": "src"}
    useVite = True