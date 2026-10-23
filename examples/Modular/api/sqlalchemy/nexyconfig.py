from nexy.core.models import NexyConfigModel
from src.apps.app_module import AppModule

class NexyConfig(NexyConfigModel):
    useTitle = "Nexy API (Modular)"
    useRouter = AppModule