
from nexy.decorators import Controller
from src.apps.users.user_service import UserService


@Controller()
class UserController:
    def __init__(self, svc: UserService):
        self.svc = svc

    def get(self):
        return self.svc.get_all()

    def post(self, name: str, email: str):
        return self.svc.create(name, email)
