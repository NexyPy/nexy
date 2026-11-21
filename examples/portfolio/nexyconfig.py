from nexy.core.models import NexyConfigModel
from nexy.frontend import svelte


class NexyConfig(NexyConfigModel):
    useFF = svelte()
    useTitle = "Noor Halvorsen"
    useAliases = {"@": "src"}
    useVite = True
    useDevTools = True  # the toolbar of `nexy dev` on every page; False removes it
    # The public address of the site: Nexy then serves /sitemap.xml and /robots.txt.
    useSiteUrl = "https://noor.example"
