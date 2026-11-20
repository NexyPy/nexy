import os

from dotenv import load_dotenv

from nexy.core.models import NexyConfigModel
from nexy.frontend import svelte
from src.configs.db import create_tables

load_dotenv()
create_tables()


class NexyConfig(NexyConfigModel):
    useFF = svelte()
    useTitle = "Field Supply"
    useAliases = {"@": "src"}
    useVite = True
    useDevTools = True  # the toolbar of `nexy dev` on every page; False removes it
    # The cart lives in a cookie signed with this secret: anyone who knows it can forge a cart.
    useSession = {"secret_key": os.environ["SESSION_SECRET"]}
