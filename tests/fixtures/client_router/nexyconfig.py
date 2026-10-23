from nexy.core.models import NexyConfigModel
from nexy.modules.frontend import react


class NexyConfig(NexyConfigModel):
    useFF = [react()]
    useDocs = False
    usePort = 4610
    useTitle = "Nexy E2E Fixture"
    useVite = True
