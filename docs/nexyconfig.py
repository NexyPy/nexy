from nexy.core.models import NexyConfigModel
from nexy.frontend import react

class NexyConfig(NexyConfigModel):
    useFF = [react()]
    # usePort = 4000
    useAliases = {"@": "src/"}
    useTitle = "Nexy Docs"
    useVite = True
    useDocs = False
    useLocales = ["en", "fr", "ar", "hi", "zh", "es", "pt", "ja", "ko", "de", "ru"]
    useLocalesDir = "src/locales"
    useDefaultLocale = "en"

