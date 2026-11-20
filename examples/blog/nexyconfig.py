from nexy.core.models import NexyConfigModel


class NexyConfig(NexyConfigModel):
    useTitle = "Plain Text"
    useAliases = {"@": "src"}
    useVite = True
    useDevTools = True  # the toolbar of `nx dev` on every page; False removes it
    # Where the blog is published: the links of the feed, then /sitemap.xml and /robots.txt.
    useSiteUrl = "https://plaintext.example"
