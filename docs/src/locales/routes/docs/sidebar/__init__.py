from src.locales.routes.docs.sidebar.getting_started import GettingStartedI18n
from src.locales.routes.docs.sidebar.views import ViewsI18n
from src.locales.routes.docs.sidebar.fbr_router import FbrRouterI18n
from src.locales.routes.docs.sidebar.modular_router import ModularRouterI18n
from src.locales.routes.docs.sidebar.decorators import DecoratorsI18n
from src.locales.routes.docs.sidebar.components import ComponentsI18n
from src.locales.routes.docs.sidebar.config import ConfigI18n
from src.locales.routes.docs.sidebar.cli import CliI18n
from src.locales.routes.docs.sidebar.hooks import HooksI18n
from src.locales.routes.docs.sidebar.security import SecurityI18n
from src.locales.routes.docs.sidebar.databases import DatabasesI18n
from src.locales.routes.docs.sidebar.guides import GuidesI18n
from src.locales.routes.docs.sidebar.migrate import MigrateI18n
from src.locales.routes.docs.sidebar.fastapi import FastapiI18n
from src.locales.routes.docs.sidebar.router_toggle import RouterToggleI18n


class SidebarI18n:
    def __init__(self):
        self.getting_started = GettingStartedI18n()
        self.views = ViewsI18n()
        self.fbr_router = FbrRouterI18n()
        self.modular_router = ModularRouterI18n()
        self.decorators = DecoratorsI18n()
        self.components = ComponentsI18n()
        self.config = ConfigI18n()
        self.cli = CliI18n()
        self.hooks = HooksI18n()
        self.security = SecurityI18n()
        self.databases = DatabasesI18n()
        self.guides = GuidesI18n()
        self.migrate = MigrateI18n()
        self.fastapi = FastapiI18n()
        self.router_toggle = RouterToggleI18n()
