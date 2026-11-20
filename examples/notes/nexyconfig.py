from nexy.core.models import NexyConfigModel
from nexy.frontend import svelte


class NexyConfig(NexyConfigModel):
    useFF = svelte()
    useCSR = True
    useTitle = "Margin"
    useAliases = {"@": "src"}
    useVite = True
    useDevTools = True  # the toolbar of `nexy dev` on every page; False removes it
    useORM = "Tortoise-ORM"  # the ORM `nx migrate` migrates
