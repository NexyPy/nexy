from nexy.core.models import NexyConfigModel

from src.library import service


class NexyConfig(NexyConfigModel):
    useTitle = "Library"
    # The routes of the FastAPI app, served as they are, next to the files of src/routes.
    useRouter = service.router
    useAliases = {"@": "src"}
    useVite = True
    # The loans are kept in memory: one process, so every request sees the same books.
    useWorkers = 1
    useDevTools = True  # the toolbar of `nexy dev` on every page; False removes it
