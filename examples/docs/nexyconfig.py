from nexy.core.models import NexyConfigModel
from nexy.frontend import react


class NexyConfig(NexyConfigModel):
    useFF = react()
    useTitle = "Cairn docs"
    useAliases = {"@": "src"}
    useVite = True
    # FastAPI answers /docs with its API docs by default: off, so /docs is the Markdown.
    useDocs = False
    useDevTools = True  # the toolbar of `nexy dev` on every page; False removes it
    # The public address of the site: Nexy then serves /sitemap.xml and /robots.txt.
    useSiteUrl = "https://docs.cairn.example"
