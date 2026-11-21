from nexy.core.models import NexyConfigModel

from src.apps.app_module import AppModule


class NexyConfig(NexyConfigModel):
    useTitle = "Newsroom"
    useRouter = AppModule
    useAliases = {"@": "src"}
    useVite = True
    # The stories live in the memory of the server process. `nx start` runs one process per CPU on
    # Linux and macOS, each with its own stories: one process here. A real API uses a database.
    useWorkers = 1
    useDevTools = True  # the toolbar of `nexy dev` on every page; False removes it
