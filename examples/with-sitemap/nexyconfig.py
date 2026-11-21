from nexy.core.models import NexyConfigModel


class NexyConfig(NexyConfigModel):
    useTitle = "Crumb"
    useAliases = {"@": "src"}
    useVite = True
    useDevTools = True  # the toolbar of `nexy dev` on every page; False removes it
    # The public address of the site. With it, Nexy serves /sitemap.xml and /robots.txt; without
    # it neither exists, so the address of a dev server is never published by mistake.
    useSiteUrl = "https://crumb.example"
