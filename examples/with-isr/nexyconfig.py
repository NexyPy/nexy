from nexy.core.models import NexyConfigModel


class NexyConfig(NexyConfigModel):
    useTitle = "Departures"
    useAliases = {"@": "src"}
    useVite = True
    # The ISR cache lives in the memory of each server process. `nx start` runs one process per CPU
    # on Linux and macOS, each with its own copy: one process here, so a reload shows the same one.
    useWorkers = 1
    useDevTools = True  # the toolbar of `nexy dev` on every page; False removes it
