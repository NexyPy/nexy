from nexy.core.models import NexyConfigModel


class NexyConfig(NexyConfigModel):
    useTitle = "Notes"
    useAliases = {"@": "src"}
    useVite = True
    useDevTools = True  # the toolbar of `nexy dev` on every page; False removes it
    # The public address of the blog: the feed links to it, and /sitemap.xml lists its pages on it.
    useSiteUrl = "https://example.com"
