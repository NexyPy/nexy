from nexy.core.models import NexyConfigModel


class NexyConfig(NexyConfigModel):
    useTitle = "Nexy docs"
    useAliases = {"@": "src"}
    useVite = False
    # FastAPI's own /docs would shadow the /docs pages of this site.
    useDocs = False
