from nexy.decorators import Module
from .app_controller import AppController

from .users.user_module import UsersModule



@Module()
class AppModule:
    controllers = [AppController]

    imports = [UsersModule]
