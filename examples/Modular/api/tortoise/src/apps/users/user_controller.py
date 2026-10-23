
from nexy.decorators import Controller
from src.apps.users.user_service import UserService


@Controller()
class UserController:
    def __init__(self, svc: UserService):
        self.svc = svc

    async def get(self):
        return await self.svc.get_all()

    async def post(self, name: str, email: str):
        return await self.svc.create(name, email)
