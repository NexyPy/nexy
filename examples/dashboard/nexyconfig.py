import os

from dotenv import load_dotenv
from src.services.demo import prepare

from nexy.core.models import NexyConfigModel
from nexy.frontend import vue

load_dotenv()
prepare()  # the tables, and the demo data the first time


class NexyConfig(NexyConfigModel):
    useFF = vue()
    useTitle = "Ledger"
    useAliases = {"@": "src"}
    useVite = True
    useDevTools = True  # the toolbar of `nexy dev` on every page; False removes it
    # The session cookie is signed with this secret: anyone who knows it can sign in as anyone.
    useSession = {"secret_key": os.environ["SESSION_SECRET"]}
